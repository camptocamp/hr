from datetime import date

from odoo import models, fields, api


class CeaseOrder(models.Model):
    _name = 'cease.order'
    _inherit = ['mail.thread']

    name = fields.Char(
        string='Name'
    )
    submitter = fields.Many2one(
        string='Submitter',
        comodel_name='res.users',
        default=lambda self: self.env.user
    )
    confirmation_date = fields.Date(
        string='Confirmation Date',
        track_visibility='onchange',
    )

    state = fields.Selection(
        [('draft', 'New'),
         ('confirm', 'Confirmed'),
         ('cease', 'Ceased'),
         ('hold', 'On Hold'),
         ('abort', 'Aborted')],
        string='Status',
        default='draft',
        track_visibility='onchange',
    )
    processing_stage = fields.Selection(
        [('checkinfo', 'Checking Information'),
         ('awaitinfo', 'Awaiting Information'),
         ('createform', 'Creating Form'),
         ('withcustomer', 'with Customer'),
         ('valid', 'Validated'),
         ],
        string='Processing Stage',
        default='checkinfo',
        track_visibility='onchange'
    )

    subscription_id = fields.Many2one(
        string='Subscription',
        comodel_name='sale.subscription',
        store=True,
        track_visibility='onchange'
    )
    user_id = fields.Many2one(
        string='Salesperson',
        related='subscription_id.user_id'
    )

    # can not be related, related fields dont work with _track_subtype
    company_id = fields.Many2one(
        string='Company',
        comodel_name='res.company'
    )
    partner_id = fields.Many2one(
        string='Customer',
        related='subscription_id.partner_id',
        store=True
    )
    customer_contact = fields.Many2one(
        string='Customer contact',
        comodel_name='res.partner',
        domain="[('parent_id', '=', partner_id)]"
    )
    provisioning_contact = fields.Many2one(
        string='Provisioning Contact',
        comodel_name='res.partner',
        domain="[('parent_id', '=', partner_id)]"
    )
    notice_period = fields.Integer(
        string='Notice Period (days)',
    )
    requested_date = fields.Date(
        string='Requested Date'
    )

    project_id = fields.Many2one(
        string='Project',
        related='subscription_id.analytic_account_id',
        store=True
    )
    cease_date = fields.Date(
        string='Cease Date',
        track_visibility='onchange',
    )
    forecast_date = fields.Date(
        string='Forecast Date',
        track_visibility='onchange',
        oldname='forcast_date'
    )
    cease_line_ids = fields.One2many(
        string='Cease Lines',
        comodel_name='cease.order.line',
        inverse_name='cease_id'
    )
    close_reason_id = fields.Many2one(
        string='Reason',
        comodel_name='sale.subscription.close.reason'
    )
    reason_description = fields.Text(
        string='Reason Description'
    )
    notes = fields.Text(
        string='Notes'
    )
    purchase_count = fields.Integer(
        string='Purchase Count',
        compute='compute_purchase_count',
    )
    cease_type = fields.Selection(
        [('partial', 'Partial'), ('full', 'Full')],
        string='Cease Type',
        compute='compute_cease_type',
        store=True,
    )
    currency_id = fields.Many2one(
        string='Currency',
        related='subscription_id.currency_id',
        store=True
    )
    usd_currency_id = fields.Many2one(
        string='USD Currency',
        comodel_name='res.currency',
        default=lambda self: self.currency_id.browse(3),
        readonly=True
    )
    loss_mrr = fields.Monetary(
        string='Loss MRR',
        currency_field='currency_id',
        compute='_compute_loss_mrr',
        store=True
    )
    loss_mrr_usd = fields.Monetary(
        string='Loss MRR USD',
        currency_field='currency_id',
        compute='_compute_loss_mrr_usd',
        store=True
    )
    rate_usd = fields.Float(
        string='Rate USD',
        compute='_compute_rate_usd',
        store=True
    )

    @api.depends('currency_id', 'confirmation_date', 'cease_date')
    def _compute_rate_usd(self):
        for rec in self:
            dates = [rec.create_date]
            if rec.confirmation_date:
                dates.append(rec.confirmation_date)
            if rec.cease_date:
                dates.append(rec.cease_date)
            if rec.currency_id.id == rec.usd_currency_id.id:
                rec.rate_usd = 1
            else:
                if rec.currency_id.rate != 0:
                    rec.rate_usd = rec.currency_id.with_context({
                        'company_id': rec.company_id.id,
                        'date': dates[-1],
                    })._get_conversion_rate(rec.currency_id,
                                            rec.usd_currency_id)

    @api.depends('cease_line_ids', 'close_reason_id')
    def _compute_loss_mrr(self):
        for rec in self:
            if rec.close_reason_id.is_revenue_loss:
                rec.loss_mrr = sum(rec.cease_line_ids.mapped('price_subtotal'))

    @api.depends('loss_mrr', 'rate_usd')
    def _compute_loss_mrr_usd(self):
        for rec in self:
            rec.loss_mrr_usd = rec.loss_mrr * rec.rate_usd

    @api.multi
    def _get_ac_purchase_ids(self):
        return self.env['purchase.order.line'].sudo().search(
            [('account_analytic_id', '=', self.project_id.id)]).mapped(
            'order_id').ids

    @api.multi
    def action_get_purchases(self):
        self.ensure_one()
        purchase_ids = self._get_ac_purchase_ids()
        view_id = self.env.ref('purchase.purchase_order_tree').id
        return {
            'name': 'Purchases',
            'view_type': 'form',
            'view_mode': 'tree',
            'view_id': view_id,
            'domain': [('id', 'in', purchase_ids)],
            'res_model': 'purchase.order',
            'type': 'ir.actions.act_window',
            'target': 'current'}

    @api.multi
    def compute_purchase_count(self):
        for rec in self:
            rec.purchase_count = len(rec._get_ac_purchase_ids())

    @api.multi
    def action_confirm(self):
        self.ensure_one()
        return self.write(
            {'state': 'confirm', 'confirmation_date': date.today()})

    @api.multi
    def action_cease(self):
        self.ensure_one()
        self.cease_date = date.today()
        self._update_subscription()
        return self.write({'state': 'cease'})

    @api.multi
    def _update_subscription(self):
        if self.cease_type == 'full':
            self.subscription_id.sudo().write({
                'close_reason_id': self.close_reason_id.id,
                'date_cancelled': self.cease_date,
                'date': self.cease_date
            })
            return self.subscription_id.sudo().set_close()
        else:
            to_remove = [
                (3, line_id) for line_id in self.cease_line_ids.mapped(
                    'subscription_line_id').ids]
            return self.subscription_id.sudo().write(
                {'recurring_invoice_line_ids': to_remove})

    @api.model
    def create(self, vals):
        if 'subscription_id' in vals:
            vals['company_id'] = self.subscription_id.browse(
                vals['subscription_id']).company_id.id
        res = super(CeaseOrder, self).create(vals)
        res.write({'name': '{0}{1:05d}'.format('CO', res.id)})
        return res

    @api.multi
    def action_hold(self):
        self.ensure_one()
        self.state = 'hold'

    @api.multi
    def action_abort(self):
        self.ensure_one()
        self.state = 'abort'

    @api.multi
    def action_draft(self):
        self.ensure_one()
        self.state = 'draft'

    @api.multi
    def action_next_processing_stage(self):
        self.ensure_one()
        selection = self._fields['processing_stage'].selection
        for index, value in enumerate(selection):
            if value[0] == self.processing_stage and index != len(
                    selection) - 1:
                self.write({'processing_stage': selection[index + 1][0]})
                break

    @api.multi
    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'state' in init_values and self.state == 'draft':
            return 'bso_subscription_cease.mt_cease_created'
        return super(CeaseOrder, self)._track_subtype(init_values)

    @api.depends('cease_line_ids')
    def compute_cease_type(self):
        for rec in self:
            if len(rec.cease_line_ids) == len(
                    rec.subscription_id.recurring_invoice_line_ids):
                rec.cease_type = 'full'
            else:
                rec.cease_type = 'partial'
