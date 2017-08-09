from openerp import api, fields, models


class BundleDetailsProduct(models.Model):
    _name = 'bundle.details.product'

    bundle_details_id = fields.Many2one(string='Bundle Details',
                                        comodel_name='bundle.details')

    bundle_details_epl_id = fields.Many2one(string='Bundle Details EPL',
                                            comodel_name='bundle.details')

    product_id = fields.Many2one(string='Product',
                                 comodel_name='product.product',
                                 required=True)

    product_quantity = fields.Integer(string="Quantity",
                                      required=True)

    product_name = fields.Char(string='Name',
                               related='product_id.display_name',
                               readonly=True)

    product_price = fields.Float(string='Price',
                                 related='product_id.lst_price',
                                 readonly=True)

    product_cost = fields.Float(string='Cost',
                                related='product_id.standard_price',
                                readonly=True)

    product_uom = fields.Many2one(string="Unit of Measure",
                                  related='product_id.uom_id',
                                  readonly=True)

    product_total_price = fields.Float(string='Total',
                                       compute='_product_total_price')

    product_total_cost = fields.Float(string='Total Cost',
                                      compute='_product_total_cost')

    # PRODUCT TOTAL PRICE FROM PRICE & QUANTITY
    @api.depends('product_price', 'product_quantity')
    def _product_total_price(self):
        for rec in self:
            rec.product_total_price = rec.product_price * rec.product_quantity

    # PRODUCT TOTAL COST FROM COST & QUANTITY
    @api.depends('product_cost', 'product_quantity')
    def _product_total_cost(self):
        for rec in self:
            rec.product_total_cost = rec.product_cost * rec.product_quantity
