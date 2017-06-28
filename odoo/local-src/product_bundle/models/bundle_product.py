from openerp import api, fields, models


class BundleProduct(models.Model):
    _name = 'bundle.product'

    product_id = fields.Many2one(string='Product',
                                 comodel_name='product.product',
                                 required=True)

    product_quantity = fields.Integer(string="Quantity",
                                      required=True)

    product_name = fields.Char(string='Name',
                               related='product_id.display_name',
                               readonly=True)

    product_price = fields.Float(string='Price per Unit',
                                 related='product_id.lst_price',
                                 readonly=True)

    product_cost = fields.Float(string='Cost per Unit',
                                related='product_id.standard_price',
                                readonly=True)

    product_uom = fields.Many2one(string="Unit of Measure",
                                  related='product_id.uom_id',
                                  readonly=True)

    # PRODUCT TOTALS FROM PRICE, COST & QUANTITY
    @api.one
    @api.depends('product_price', 'product_quantity')
    def _product_totals(self):
        self.product_total_price = self.product_price * self.product_quantity
        self.product_total_cost = self.product_cost * self.product_quantity

    product_total_price = fields.Float(string='Price',
                                       compute='_product_totals')

    product_total_cost = fields.Float(string='Cost',
                                      compute='_product_totals')
