from odoo import models, fields, api


class BundleDetailsProduct(models.Model):
    _name = 'bundle.details.product'

    bundle_details_id = fields.Many2one(
        string='Bundle Details',
        comodel_name='bundle.details',
        ondelete='cascade',
        readonly=True
    )
    currency_id = fields.Many2one(
        related='bundle_details_id.currency_id',
        readonly=True,
        store=True
    )
    bundle_categ_id = fields.Many2one(
        related='bundle_details_id.bundle_categ_id',
        readonly=True,
        store=True
    )
    is_epl = fields.Boolean(
        related='bundle_details_id.is_epl',
        readonly=True,
        store=True
    )
    product_id = fields.Many2one(
        string='Product',
        comodel_name='product.product',
        required=True
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
        readonly=True,
        store=True
    )
    mrc_unit = fields.Monetary(
        string='MRC / Unit',
        compute='compute_mrc_unit',
        store=True
    )
    mrc = fields.Monetary(
        string='MRC',
        compute='compute_mrc',
        store=True
    )
    dflt_mrr_unit = fields.Monetary(
        string='Default MRR / Unit',
        compute='compute_dflt_mrr_unit',
        store=True
    )
    mrr_unit = fields.Monetary(
        string='MRR / Unit'
    )
    mrr = fields.Monetary(
        string='MRR',
        compute='compute_mrr',
        store=True
    )
    nrr_unit = fields.Monetary(
        string='NRR / Unit'
    )
    nrr = fields.Monetary(
        string='NRR',
        compute='compute_nrr',
        store=True
    )

    # COMPUTES

    @api.depends('product_id.currency_id', 'product_id.standard_price',
                 'currency_id')
    def compute_mrc_unit(self):
        for rec in self:
            rec.update({
                'mrc_unit': rec.product_id.currency_id.compute(
                    rec.product_id.standard_price, rec.currency_id)
            })

    @api.depends('mrc_unit', 'quantity')
    def compute_mrc(self):
        for rec in self:
            rec.update({
                'mrc': rec.mrc_unit * rec.quantity
            })

    @api.depends('product_id.currency_id', 'product_id.lst_price',
                 'currency_id')
    def compute_dflt_mrr_unit(self):
        for rec in self:
            rec.update({
                'dflt_mrr_unit': rec.product_id.currency_id.compute(
                    rec.product_id.lst_price, rec.currency_id)
            })

    @api.onchange('dflt_mrr_unit')
    def onchange_dflt_mrr_unit(self):
        for rec in self:
            rec.update({
                'mrr_unit': rec.dflt_mrr_unit
            })

    @api.depends('mrr_unit', 'quantity')
    def compute_mrr(self):
        for rec in self:
            rec.update({
                'mrr': rec.mrr_unit * rec.quantity
            })

    @api.depends('nrr_unit', 'quantity')
    def compute_nrr(self):
        for rec in self:
            rec.update({
                'nrr': rec.nrr_unit * rec.quantity
            })
