# -*- coding: utf-8 -*-
import json
from lxml import etree
from datetime import date

from odoo import models, api, fields, exceptions


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    order_type = fields.Selection(
        default='create'
    )
    to_delete_line_ids = fields.One2many(
        comodel_name='sale.order.sub_line_remove',
        inverse_name='unlink_order_id'
    )
    rel_amount_untaxed = fields.Monetary(
        related='amount_untaxed'
    )
    rel_amount_tax = fields.Monetary(
        related='amount_tax'
    )
    rel_amount_total = fields.Monetary(
        related='amount_total'
    )
    loss_mrr = fields.Monetary(
        string='Loss MRR',
        currency_field='currency_id',
        compute='_compute_loss_mrr',
        store=True
    )

    abs_mrr = fields.Monetary(
        string='Absolute MRR',
        compute='_compute_absolute_mrr',
        store=True
    )
    new_mrr = fields.Monetary(
        string='New MRR',
        currency_field='currency_id',
        compute='_compute_new_mrr',
        store=True
    )
    abs_mrr_usd = fields.Monetary(
        string='Abs MRR USD',
        compute='_compute_abs_mrr_usd',
        currency_field='usd_currency_id',
        store=True
    )
    loss_mrr_usd = fields.Monetary(
        string='Loss MRR USD',
        compute='_compute_loss_mrr_usd',
        currency_field='usd_currency_id',
        store=True
    )
    increment_subscription_period = fields.Boolean(
        string='Increment Subscription Period',
        default=lambda order: order.order_type in ('renew', 'replace')
    )

    @api.depends('mrr', 'to_delete_line_ids')
    def _compute_absolute_mrr(self):
        for rec in self:
            rec.abs_mrr = rec.mrr - sum(
                rec.to_delete_line_ids.mapped('price_subtotal'))

    @api.depends('abs_mrr')
    def _compute_loss_mrr(self):
        for rec in self:
            rec.loss_mrr = abs(min(0, rec.abs_mrr))

    @api.depends('abs_mrr')
    def _compute_new_mrr(self):
        for rec in self:
            rec.new_mrr = max(0, rec.abs_mrr)

    @api.multi
    def _compute_subscription(self):
        for order in self:
            if not self.env.context.get('no_update_subscription'):
                order.subscription_id = self.env['sale.subscription'].search(
                    [('analytic_account_id', '=', order.project_id.id)],
                    limit=1)

    @api.multi
    def action_confirm(self):
        self.ensure_one()
        confirm = super(SaleOrder, self.with_context(
            no_update_subscription=True)).action_confirm()
        self._deliver_pickings_on_renewal_confirmation()
        return confirm

    @api.multi
    def _deliver_pickings_on_renewal_confirmation(self):
        self_sudo = self.sudo()
        if self_sudo.order_type == 'renew':
            wiz_view = self_sudo.sudo().picking_ids.do_new_transfer()
            return self_sudo.env[wiz_view.get('res_model')].browse(
                wiz_view.get('res_id')).process()

    @api.multi
    def action_invoice_create(self, grouped=False, final=False):
        res = super(SaleOrder, self).action_invoice_create(grouped, final)
        self.action_done()
        return res

    @api.multi
    def update_subscription(self):
        for order in self:
            to_delete_sub_line_ids = order.to_delete_line_ids.mapped(
                'subscription_line_id')
            modified_sub_ids = to_delete_sub_line_ids.mapped(
                'analytic_account_id')
            to_delete_sub_line_ids.sudo().write({'analytic_account_id': False})

            if order.subscription_id:
                if order.increment_subscription_period:
                    order.subscription_id.sudo().write({
                        'description': order.note,
                        'pricelist_id': order.pricelist_id.id
                    })
                    order.subscription_id.sudo().set_open()
                    order.subscription_id.sudo().increment_period()
                values = order.prepare_subscription_lines()
                order.subscription_id.sudo().write(values)
                order.action_done()

            merged_reason_id = order.subscription_id.close_reason_id.search(
                [('name', '=', 'Merged')])
            for sub in modified_sub_ids:
                if not len(sub.recurring_invoice_line_ids):
                    sub.sudo().write({
                        'close_reason_id': merged_reason_id.id,
                        'date_cancelled': date.today(),
                    })
                    sub.set_close()
        return True

    def prepare_subscription_lines(self):
        values = {'recurring_invoice_line_ids': []}
        for line in self.order_line:
            if line.product_id.recurring_invoice:
                values['recurring_invoice_line_ids'].append(
                    (0, 0,
                     {'product_id': line.product_id.id,
                      'analytic_account_id': self.subscription_id.id,
                      'name': line.name,
                      'sold_quantity': line.product_uom_qty,
                      'uom_id': line.product_uom.id,
                      'price_unit': line.price_unit,
                      'discount': line.discount if
                      line.order_id.order_type == 'renew'
                      else False,
                      }))
        return values

    @api.model
    def fields_view_get(self, *args, **kwargs):
        res = super(SaleOrder, self).fields_view_get(*args, **kwargs)
        doc = etree.XML(res['arch'])
        if res['name'] == 'sale.order.form':
            renew_editable_fields = self.get_renew_editable_fields()
            for node in doc.xpath("//field"):
                if node.get('name') not in renew_editable_fields:
                    modifiers_dict = json.loads(node.get('modifiers'))
                    if modifiers_dict.get('readonly') is True:
                        pass
                    elif not modifiers_dict.get('readonly', False):
                        modifiers_dict['readonly'] = [
                            ('order_type', '=', 'renew')]
                    else:
                        modifiers_dict['readonly'].insert(0, '|')
                        modifiers_dict['readonly'].append(
                            ('order_type', '=', 'renew'))
                    node.set('modifiers', json.dumps(modifiers_dict))
            res['arch'] = etree.tostring(doc)
        return res

    @api.depends('abs_mrr', 'rate_usd')
    def _compute_abs_mrr_usd(self):
        for rec in self:
            rec.abs_mrr_usd = rec.abs_mrr * rec.rate_usd

    @api.depends('loss_mrr', 'rate_usd')
    def _compute_loss_mrr_usd(self):
        for rec in self:
            rec.loss_mrr_usd = rec.loss_mrr * rec.rate_usd

    def get_renew_editable_fields(self):
        return ('duration', 'order_line', 'user_id', 'tag_ids', 'team_id',
                'company_id', 'client_order_ref', 'note')

    @api.multi
    def write(self, vals):
        for rec in self:
            # prevent adding/removing new sale.order.line to a renewal SO,
            # allow update
            order_lines_domain = vals.get('order_line', [[1]])[0]
            if rec.order_type == 'renew' and order_lines_domain[0] != 1:
                format_string = ('add', 'to') if vals.get(
                    'order_line', [[1]])[0][0] == 4 else ('remove', 'from')
                raise exceptions.ValidationError(
                    'You can not %s lines %s a renewal sale order' %
                    format_string)
            return super(SaleOrder, self).write(vals)
