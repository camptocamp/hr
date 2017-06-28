from openerp import api, fields, models, exceptions


class BundleWizard(models.Model):
    _name = 'bundle.wizard'

    # BUNDLE NAME FROM bundle.xml BUTTON CONTEXT (default_bundle_name)
    bundle_name = fields.Char(string="Bundle Name")

    # GENERIC BUNDLE ID FROM NAME
    def get_bundle_id(self, bundle_name):
        return self.env['product.product'].search(
            [('name', '=ilike', bundle_name), ('is_bundle', '=', True)])

    # BUNDLE ID
    bundle_id = fields.Many2one(string='Bundle',
                                comodel_name='product.product')

    # BUNDLE ID FROM BUNDLE NAME
    @api.onchange('bundle_name')
    def _bundle_id(self):
        self.bundle_id = self.get_bundle_id(self.bundle_name)

    # BUNDLE VISIBILITY
    bundle_show = fields.Boolean(default=True)

    # BUNDLE PRODUCTS
    bundle_products = fields.Many2many(string="Products",
                                       comodel_name='bundle.product')

    # BUNDLE PRODUCTS FROM BUNDLE ID
    @api.onchange('bundle_id')
    def _bundle_products(self):
        self.bundle_products = [(0, 0, {'product_id': p.id,
                                        'product_quantity': 0})
                                for p in self.bundle_id.default_products]

    # BUNDLE PRODUCTS MUST HAVE POSITIVE QUANTITIES
    @api.constrains('bundle_products')
    def _bundle_products_constraints(self):
        if self.bundle_show:  # Constraints apply
            if any(p.product_quantity < 0 for p in self.bundle_products):
                raise exceptions.ValidationError(
                    'Bundle products cannot contain negative quantities')

    # BUNDLE DESCRIPTION
    bundle_description = fields.Char(string="Name")

    # BUNDLE DESCRIPTION FROM BUNDLE PRODUCTS
    @api.onchange('bundle_products')
    def _bundle_description(self):
        self.bundle_description = "%s [%s]" \
                                  % (self.bundle_name,
                                     ", ".join("%s: %.0f"
                                               % (p.product_name,
                                                  p.product_quantity)
                                               for p in
                                               self.bundle_products
                                               if p.product_quantity > 0))

    # BUNDLE PRICE
    bundle_price = fields.Float(string="Price",
                                compute='_bundle_price')  # Workaround to store readonly

    # BUNDLE PRICE FROM BUNDLE PRODUCTS
    @api.onchange('bundle_products')
    def _bundle_price(self):
        self.bundle_price = sum(
            p.product_total_price for p in self.bundle_products)

    # BUNDLE COST
    bundle_cost = fields.Float(string="Cost",
                               compute='_bundle_cost')  # Workaround to store readonly

    # BUNDLE COST FROM BUNDLE PRODUCTS
    @api.onchange('bundle_products')
    def _bundle_cost(self):
        self.bundle_cost = sum(
            p.product_total_cost for p in self.bundle_products)

    # BUNDLE QUANTITY
    bundle_quantity = fields.Integer(string="Quantity",
                                     default=1)

    # BUNDLE TOTAL PRICE
    bundle_total_price = fields.Float(string="Total Price",
                                      compute='_bundle_total_price')  # Workaround to store readonly

    # BUNDLE TOTAL PRICE FROM PRICE & QUANTITY
    @api.onchange('bundle_price', 'bundle_quantity')
    def _bundle_total_price(self):
        self.bundle_total_price = self.bundle_price * self.bundle_quantity

    # BUNDLE TOTAL COST
    bundle_total_cost = fields.Float(string="Total Cost",
                                     compute='_bundle_total_cost')  # Workaround to store readonly

    # BUNDLE TOTAL COST FROM COST & QUANTITY
    @api.onchange('bundle_cost', 'bundle_quantity')
    def _bundle_total_cost(self):
        self.bundle_total_cost = self.bundle_cost * self.bundle_quantity

    # ADD BUNDLE TO SALE ORDER
    def button_add_bundle(self):
        self.env['sale.order.line'].create(
            {'order_id': self._context['active_id'],
             'product_id': self.bundle_id.id,
             'name': self.bundle_description,
             'price_unit': self.bundle_price,
             'product_uom': self.bundle_id.uom_id.id,
             'product_uom_qty': self.bundle_quantity})
        return True
