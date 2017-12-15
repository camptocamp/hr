from odoo import models, fields, api


class SaleDealsheet(models.Model):
    _name = 'sale.dealsheet'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'sale_order_id ASC'

    state = fields.Selection(
        string='Status',
        selection=[('draft', 'Draft'),
                   ('confirmed', 'Confirmed'),
                   ('refused', 'Refused'),
                   ('validated', 'Validated')],
        default='draft',
        track_visibility='always'
    )
    name = fields.Char(
        default='Dealsheet',
        readonly=True
    )
    user_filled = fields.Many2one(
        string='Filled By',
        comodel_name='res.users',
    )
    user_reviewed = fields.Many2one(
        string='Reviewed By',
        comodel_name='res.users',
    )
    date_validated = fields.Datetime(
        string='Validated At'
    )
    date_refused = fields.Datetime(
        string='Refused At'
    )
    sale_order_id = fields.Many2one(
        string='Sale Order',
        comodel_name='sale.order',
        ondelete='cascade',
        required=True
    )
    partner_id = fields.Many2one(
        related='sale_order_id.partner_id',
        readonly=True,
        store=True
    )
    duration = fields.Integer(
        related='sale_order_id.duration',
        readonly=True,
        store=True
    )
    currency_id = fields.Many2one(
        related='sale_order_id.currency_id',
        readonly=True,
        store=True,
        track_visibility='always'

    )
    cost_line = fields.One2many(
        string='Recurring Costs',
        comodel_name='sale.dealsheet.line',
        inverse_name='dealsheet_id',
        domain=[('is_recurring', '=', True)],
        context={'default_is_recurring': True}
    )
    cost_upfront_line = fields.One2many(
        string='Non Recurring Costs',
        comodel_name='sale.dealsheet.line',
        inverse_name='dealsheet_id',
        domain=[('is_recurring', '=', False)],
        context={'default_is_recurring': False}
    )
    cost_upfront = fields.Float(
        string='Non Recurring Cost',
        compute='compute_cost_upfront',
        store=True
    )
    price_upfront = fields.Float(
        string='Non Recurring Revenue',
        compute='compute_price_upfront',
        store=True
    )
    margin_upfront = fields.Float(
        string='Non Recurring Margin (%)',
        compute='compute_margin_upfront',
        store=True
    )
    cost = fields.Float(
        string='Recurring Cost',
        compute='compute_cost',
        store=True
    )
    price = fields.Float(
        string='Recurring Revenue',
        compute='compute_price',
        store=True
    )
    margin = fields.Float(
        string='Recurring Margin (%)',
        compute='compute_margin',
        store=True
    )
    cost_total = fields.Float(
        string='Total Cost',
        compute='compute_cost_total',
        store=True,
        track_visibility='always'
    )
    price_total = fields.Float(
        string='Total Revenue',
        compute='compute_price_total',
        store=True,
        track_visibility='always'
    )
    margin_total = fields.Float(
        string='Total Margin (%)',
        compute='compute_margin_total',
        store=True,
        track_visibility='always'
    )
    summary = fields.One2many(
        string='Summary',
        comodel_name='sale.dealsheet.summary.line',
        inverse_name='dealsheet_id',
        default=lambda self: self.get_default_summary(),
        readonly=True
    )

    # ONCREATE

    @api.model
    def create(self, values):
        dealsheet_id = super(SaleDealsheet, self).create(values)
        line_ids = self.get_lines(dealsheet_id)
        dealsheet_id.cost_line = line_ids
        return dealsheet_id

    @api.model
    def get_lines(self, did):
        sale_order_lines = did.sale_order_id.order_line

        lines = []
        for line in sale_order_lines:
            if line.bundle_details_id.show_epl:
                lines += self.get_lines_epl(line)
            elif line.bundle_details_id.show_bundle:
                lines += self.get_lines_bundle(line)
            else:
                lines += self.get_lines_product(line)

        return [(0, 0, l) for l in lines]

    @api.model
    def get_lines_epl(self, order_line):
        epl_bandwidth = order_line.product_uom_qty
        epl_product_id = order_line.bundle_details_id.bundle_id
        lines = []
        for link in order_line.bundle_details_id.epl_route:
            data = {'sale_order_line_id': order_line.id,
                    'product_id': epl_product_id,
                    'description': link.link_id.name,
                    'quantity': epl_bandwidth,
                    'cost': link.cost_per_mb * epl_bandwidth,
                    'is_recurring': epl_product_id.recurring_invoice}
            lines.append(data)
        for line in order_line.bundle_details_id.epl_products:
            if not line.quantity:
                continue
            data = {'sale_order_line_id': order_line.id,
                    'product_id': line.product_id.id,
                    'description': line.description,
                    'quantity': line.quantity,
                    'cost': line.cost,
                    'is_recurring': line.product_id.recurring_invoice}
            lines.append(data)
        return lines

    @api.model
    def get_lines_bundle(self, order_line):
        bundle_qty = order_line.product_uom_qty
        lines = []
        for line in order_line.bundle_details_id.bundle_products:
            if not line.quantity:
                continue
            data = {'sale_order_line_id': order_line.id,
                    'product_id': line.product_id.id,
                    'description': line.description,
                    'quantity': line.quantity * bundle_qty,
                    'cost': line.cost,
                    'is_recurring': line.product_id.recurring_invoice}
            lines.append(data)
        return lines

    @api.model
    def get_lines_product(self, order_line):
        data = {'sale_order_line_id': order_line.id,
                'product_id': order_line.product_id.id,
                'description': order_line.name,
                'quantity': order_line.product_uom_qty,
                'cost': order_line.product_id.standard_price,
                'is_recurring': order_line.product_id.recurring_invoice}
        return [data]

    # DEFAULTS

    @api.model
    def get_default_summary(self):
        return [(0, 0, {'type': t}) for t in
                ('non_recurring', 'recurring', 'total')]

    # COMPUTES

    @api.depends('cost_upfront_line.cost')
    def compute_cost_upfront(self):
        for rec in self:
            rec.update({
                'cost_upfront': sum(rec.mapped('cost_upfront_line.cost'))
            })

    @api.depends('sale_order_id.order_line.price_subtotal')
    def compute_price_upfront(self):
        for rec in self:
            rec.update({
                'price_upfront': sum(
                    l.price_subtotal for l in rec.sale_order_id.order_line
                    if not l.product_id.recurring_invoice)
            })

    @api.depends('cost_upfront', 'price_upfront')
    def compute_margin_upfront(self):
        for rec in self:
            rec.update({
                'margin_upfront': self.get_margin(rec.cost_upfront,
                                                  rec.price_upfront)
            })

    @api.depends('cost_line.cost')
    def compute_cost(self):
        for rec in self:
            rec.update({
                'cost': sum(rec.mapped('cost_line.cost'))
            })

    @api.depends('sale_order_id.order_line.price_subtotal')
    def compute_price(self):
        for rec in self:
            rec.update({
                'price': sum(
                    l.price_subtotal for l in rec.sale_order_id.order_line
                    if l.product_id.recurring_invoice)
            })

    @api.depends('cost', 'price')
    def compute_margin(self):
        for rec in self:
            rec.update({
                'margin': self.get_margin(rec.cost, rec.price)
            })

    @api.depends('cost', 'duration', 'cost_upfront')
    def compute_cost_total(self):
        for rec in self:
            rec.update({
                'cost_total': rec.cost * rec.duration + rec.cost_upfront
            })

    @api.depends('price', 'duration', 'price_upfront')
    def compute_price_total(self):
        for rec in self:
            rec.update({
                'price_total': rec.price * rec.duration + rec.price_upfront
            })

    @api.depends('cost_total', 'price_total')
    def compute_margin_total(self):
        for rec in self:
            rec.update({
                'margin_total': self.get_margin(rec.cost_total,
                                                rec.price_total)
            })

    # TOOLS

    @api.model
    def get_margin(self, cost, revenue):
        if revenue:
            return (1 - cost / revenue) * 100

    # ACTIONS

    @api.multi
    def action_confirm(self):
        wizard_id = self.env['sale.dealsheet.wizard'].create({
            'dealsheet_id': self.id
        })
        return {
            "name": "Select Technical Reviewer",
            "type": "ir.actions.act_window",
            "res_model": "sale.dealsheet.wizard",
            "res_id": wizard_id.id,
            "view_type": "form",
            "view_mode": "form",
            "target": "new",
        }

    @api.multi
    def action_validate(self):
        self.update({
            'state': 'validated'
        })

    @api.multi
    def action_refuse(self):
        self.update({
            'state': 'refused'
        })
