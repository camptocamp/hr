# -*- coding: utf-8 -*-
import math
import json
from lxml import etree

from odoo import models, api, fields, SUPERUSER_ID, exceptions, _
from odoo.addons.sale_contract.models.sale_order import SaleOrder as So


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    to_delete_line_ids = fields.One2many(
        comodel_name='sale.subscription.line',
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
        compute='compute_absolute_mrr',
        store=True
    )

    abs_mrr = fields.Monetary(
        string='Absolute MRR',
        compute='compute_absolute_mrr',
        store=True
    )

    @api.depends('mrr', 'to_delete_line_ids')
    def compute_absolute_mrr(self):
        for rec in self:
            rec.abs_mrr = rec.mrr - sum(
                rec.to_delete_line_ids.mapped('price_subtotal'))
            rec.new_mrr = max(0, rec.abs_mrr)
            rec.loss_mrr = abs(min(0, rec.abs_mrr))

    @api.multi
    def _compute_subscription(self):
        for order in self:
            if not self.env.context.get('no_update_subscription'):
                order.subscription_id = self.env['sale.subscription'].search(
                    [('analytic_account_id', '=', order.project_id.id)],
                    limit=1)

    @api.multi
    def action_confirm(self):
        if self.env.uid == SUPERUSER_ID:
            return self._action_ok()
        if (self.env.user.employee_ids.company_id !=
                self.env.user.company_id):
            return self.env['pop.up.message'].show({
                'name': 'Confirm',
                'description': 'You are not on your home entity, '
                               'Would you like to to proceed with this'
                               ' action anyway?',
            })

    @api.multi
    def action_invoice_create(self, grouped=False, final=False):
        res = super(SaleOrder, self).action_invoice_create(grouped, final)
        self.action_done()
        return res

    @api.multi
    def _action_ok(self):
        So.action_confirm = self.anterior_action_confirm_inherits_stack
        return super(SaleOrder, self).action_confirm()

    @api.multi
    def anterior_action_confirm_inherits_stack(self):
        for order in self:
            if order.partner_id not in order.message_partner_ids:
                order.message_subscribe([order.partner_id.id])
            order.state = 'sale'
            order.confirmation_date = fields.Datetime.now()
            if self.env.context.get('send_email'):
                order.force_quotation_send()
            order.order_line._action_procurement_create()
        if self.env['ir.values'].get_default(
                'sale.config.settings', 'auto_done_setting'):
            self.action_done()
        return True

    @api.multi
    def update_subscription(self):
        for order in self:
            if order.subscription_id:
                # no need for updates if the contract was juste created
                context = self.env.context
                if not context.get('no_upsell', dict()).get(order.id):
                    to_remove = [
                        (3, line_id) for line_id in self.to_delete_line_ids.ids
                    ]
                    order.subscription_id.sudo().write(
                        {'recurring_invoice_line_ids': to_remove,
                         'description': order.note,
                         'pricelist_id': order.pricelist_id.id})
                    order.subscription_id.sudo().set_open()
                    order.subscription_id.sudo().increment_period()
                    values = order.prepare_subscription_lines()
                    order.subscription_id.sudo().write(values)

                order.action_done()
        return True

    def prepare_subscription_lines(self):
        values = {'recurring_invoice_line_ids': []}
        for line in self.order_line:
            if line.product_id.recurring_invoice:
                recurring_line_id = False
                subs_lines_prodcuts = [
                    subscr_line.product_id for subscr_line in
                    self.subscription_id.recurring_invoice_line_ids.filtered(
                        lambda x: x.to_be_deleted is False)
                ]
                if line.product_id in subs_lines_prodcuts:
                    for subscr_line in \
                            self.subscription_id.recurring_invoice_line_ids:
                        if (subscr_line.product_id == line.product_id and
                                subscr_line.product_id.mergeable and
                                subscr_line.uom_id == line.product_uom):
                            recurring_line_id = subscr_line.id
                            quantity = subscr_line.sold_quantity
                            break
                if recurring_line_id:
                    values['recurring_invoice_line_ids'].append(
                        (1, recurring_line_id, {
                            'sold_quantity': quantity + line.product_uom_qty,
                        }))
                else:
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

    @api.multi
    def replace_action(self):
        self.ensure_one()
        self.to_delete_line_ids = self.to_delete_line_ids.filtered(
            lambda x: x.to_be_deleted)
        if not self.to_delete_line_ids:
            raise exceptions.ValidationError(_(
                'Please Select at lease one line to be %s, '
                'or you might need to use the Upsell option!' % self.order_type
            ))
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_type': 'form',
            'view_mode': 'form'
        }

    @api.model
    def fields_view_get(self, *args, **kwargs):
        res = super(SaleOrder, self).fields_view_get(*args, **kwargs)
        doc = etree.XML(res['arch'])
        if res['name'] == 'sale.order.form':
            for node in doc.xpath("//field"):
                if node.get('name') not in (
                        'duration', 'order_line'):
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
