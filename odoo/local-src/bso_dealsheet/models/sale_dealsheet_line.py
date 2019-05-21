from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SaleDealsheetLine(models.Model):
    _name = 'sale.dealsheet.line'

    dealsheet_id = fields.Many2one(
        string='Dealsheet',
        comodel_name='sale.dealsheet',
        ondelete='cascade'
    )
    dealsheet_state = fields.Selection(
        string='Dealsheet Status',
        related='dealsheet_id.state',
        readonly=True
    )
    sale_order_state = fields.Selection(
        string='Sale Order Status',
        related='dealsheet_id.sale_order_state',
        readonly=True
    )
    is_locked = fields.Boolean(
        string='Is Locked',
        compute='compute_is_locked',
        store=True
    )
    is_cost = fields.Boolean(
        string='Is Cost'
    )
    is_recurring = fields.Boolean(
        string='Is Recurring'
    )
    currency_id = fields.Many2one(
        related='dealsheet_id.currency_id',
        readonly=True
    )
    sale_order_line_id = fields.Many2one(
        string='Sale Order Line',
        comodel_name='sale.order.line',
        ondelete='cascade'
    )
    product_id = fields.Many2one(
        string='Product',
        comodel_name='product.product',
        required=True
    )
    product_categ_id = fields.Many2one(
        string='Product Category',
        related='product_id.categ_id',
        readonly=True,
        store=True
    )
    description = fields.Char(
        string='Description'
    )
    quantity = fields.Integer(
        string='Quantity',
        required=True
    )
    uom_id = fields.Many2one(
        related='product_id.uom_id',
        readonly=True
    )
    cost = fields.Monetary(
        string='Unit Cost',
        currency_field='currency_id'
    )
    total_cost = fields.Monetary(
        string='Total Cost',
        currency_field='currency_id',
        compute='compute_total_cost',
        store=True
    )
    supplier_id = fields.Many2one(
        string='Supplier',
        comodel_name='res.partner',
        # required=True,
    )
    frequency = fields.Selection(
        string='Frequency',
        selection=[
            ('monthly', u"Monthly"),
            ('quarterly', u"Quarterly"),
            ('yearly', u"Yearly"),
        ],
    )
    cost_delivery = fields.Monetary(
        string='Delivery Unit Cost',
        currency_field='currency_id'
    )
    total_cost_delivery = fields.Monetary(
        string='Delivery Total Cost',
        currency_field='currency_id',
        compute='compute_total_cost_delivery',
        store=True
    )
    purchase_order_line_id = fields.Many2one(
        string='Purchase Order Line',
        comodel_name='purchase.order.line',
    )
    purchase_order_id = fields.Many2one(
        string='Purchase Order',
        related='purchase_order_line_id.order_id',
        readonly=True,
    )
    purchase_order_state = fields.Selection(
        string='Purchase Order State',
        related='purchase_order_id.state',
        readonly=True,
    )

    # OVERRIDES

    @api.model
    def create(self, vals):
        return super(SaleDealsheetLine, self.sudo()).create(vals)

    @api.multi
    def write(self, vals):
        return super(SaleDealsheetLine, self.sudo()).write(vals)

    @api.multi
    def unlink(self):
        if any(rec.is_locked for rec in self):
            raise UserError(_('You must reset DS to Draft before deleting.'))
        return super(SaleDealsheetLine, self.sudo()).unlink()

    # COMPUTES

    @api.depends('dealsheet_id.validated_date', 'dealsheet_id.refused_date')
    def compute_is_locked(self):
        for rec in self:
            if not rec.create_date:
                continue
            ds = rec.dealsheet_id
            ref_date = ds.validated_date or ds.refused_date
            rec.is_locked = rec.create_date < ref_date

    @api.depends('quantity', 'cost')
    def compute_total_cost(self):
        for rec in self:
            rec.total_cost = rec.quantity * rec.cost

    @api.depends('quantity', 'cost_delivery')
    def compute_total_cost_delivery(self):
        for rec in self:
            rec.total_cost_delivery = rec.quantity * rec.cost_delivery
