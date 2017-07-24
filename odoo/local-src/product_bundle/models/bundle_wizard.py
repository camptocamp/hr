from openerp import api, fields, models, exceptions


class BundleWizard(models.Model):
    _name = 'bundle.wizard'

    # SALE ORDER FROM bundle.xml BUTTON CONTEXT (default_sale_order_id)
    sale_order_id = fields.Many2one(string='Sale Order',
                                    comodel_name='sale.order',
                                    required=True)

    # SALE ORDER LINE SET AFTER SAVING BUNDLE
    sale_order_line_id = fields.Many2one(string="Sale Order Line",
                                         comodel_name='sale.order.line',
                                         ondelete='cascade',
                                         required=True)

    # BUNDLE NAME FROM bundle.xml BUTTON CONTEXT (default_bundle_name)
    bundle_name = fields.Char(string="Bundle Name")

    # BUNDLE VISIBILITY
    bundle_show = fields.Boolean(default=True)

    # BUNDLE ID
    bundle_id = fields.Many2one(string='Bundle',
                                comodel_name='product.product')

    # BUNDLE PRODUCTS
    bundle_products = fields.Many2many(string="Products",
                                       comodel_name='bundle.product')

    # BUNDLE DESCRIPTION
    bundle_description = fields.Char(string="Name")

    # BUNDLE PRICE
    bundle_price = fields.Float(string="Price",
                                compute='_bundle_price')

    # BUNDLE COST
    bundle_cost = fields.Float(string="Cost",
                               compute='_bundle_cost')

    # BUNDLE QUANTITY
    bundle_quantity = fields.Integer(string="Quantity",
                                     default=0)

    # BUNDLE TOTAL PRICE
    bundle_total_price = fields.Float(string="Total Price",
                                      compute='_bundle_total_price')

    # BUNDLE TOTAL COST
    bundle_total_cost = fields.Float(string="Total Cost",
                                     compute='_bundle_total_cost')

    # GENERIC GET BUNDLE ID FROM NAME
    @api.model
    def get_bundle_id(self, bundle_name):
        return self.env['product.product'].search(
            [('name', '=ilike', bundle_name), ('is_bundle', '=', True)])

    # BUNDLE ID FROM BUNDLE NAME
    @api.multi
    @api.onchange('bundle_name')
    def _bundle_id(self):
        for rec in self:
            rec.bundle_id = self.get_bundle_id(rec.bundle_name)

    # BUNDLE PRODUCTS FROM BUNDLE ID
    @api.multi
    @api.onchange('bundle_id')
    def _bundle_products(self):
        for rec in self:
            rec.bundle_products = [(0, 0, {'product_id': p.id,
                                           'product_quantity': 0})
                                   for p in rec.bundle_id.default_products]

    # BUNDLE DESCRIPTION FROM BUNDLE PRODUCTS
    @api.multi
    @api.onchange('bundle_products')
    def _bundle_description(self):
        for rec in self:
            rec.bundle_description = "%s [%s]" \
                                     % (rec.bundle_name,
                                        ", ".join("%s: %.0f"
                                                  % (p.product_name,
                                                     p.product_quantity)
                                                  for p in
                                                  rec.bundle_products
                                                  if p.product_quantity > 0))

    # BUNDLE PRICE FROM BUNDLE PRODUCTS
    @api.multi
    @api.depends('bundle_products')
    def _bundle_price(self):
        for rec in self:
            rec.bundle_price = sum(
                p.product_total_price for p in rec.bundle_products)

    # BUNDLE COST FROM BUNDLE PRODUCTS
    @api.multi
    @api.depends('bundle_products')
    def _bundle_cost(self):
        for rec in self:
            rec.bundle_cost = sum(
                p.product_total_cost for p in rec.bundle_products)

    # BUNDLE TOTAL PRICE FROM PRICE & QUANTITY
    @api.multi
    @api.depends('bundle_price', 'bundle_quantity')
    def _bundle_total_price(self):
        for rec in self:
            rec.bundle_total_price = rec.bundle_price * rec.bundle_quantity

    # BUNDLE TOTAL COST FROM COST & QUANTITY
    @api.multi
    @api.depends('bundle_cost', 'bundle_quantity')
    def _bundle_total_cost(self):
        for rec in self:
            rec.bundle_total_cost = rec.bundle_cost * rec.bundle_quantity

    # BUNDLE PRODUCTS MUST HAVE POSITIVE QUANTITIES
    @api.multi
    @api.constrains('bundle_products')
    def _bundle_products_constraints(self):
        for rec in self:
            if rec.bundle_show:  # Constraints apply
                if any(p.product_quantity < 0 for p in
                       rec.bundle_products):
                    raise exceptions.ValidationError(
                        "Bundle products cannot contain negative quantities")

    # BUNDLE QUANTITY MUST BE POSITIVE
    @api.multi
    @api.constrains('bundle_quantity')
    def _bundle_quantity_constraints(self):
        for rec in self:
            if rec.bundle_show:  # Constraints apply
                if rec.bundle_quantity <= 0:
                    raise exceptions.ValidationError(
                        "Bundle quantity must be a positive integer")

    # ADD BUNDLE TO SALE ORDER
    @api.multi
    def button_bundle_save(self):
        return self.sale_order_line_save(
            product=self.bundle_id,
            description=self.bundle_description,
            quantity=self.bundle_quantity,
            unit_measure=self.bundle_id.uom_id,
            unit_price=self.bundle_price
        )

    @api.model
    def sale_order_line_save(self, product, description, quantity,
                             unit_measure, unit_price):
        if self.sale_order_line_id:  # EDIT MODE
            return self._sale_order_line_update(description, quantity,
                                                unit_price)
        else:  # CREATE MODE
            return self._sale_order_line_create(product, description, quantity,
                                                unit_measure, unit_price)

    @api.model
    def _sale_order_line_create(self, product, description, quantity,
                                unit_measure, unit_price):
        sale_order_line_id = self.env['sale.order.line'].create(
            {'order_id': self.sale_order_id.id,
             'bundle_wizard_id': self.id,
             'product_id': product.id,
             'name': description,
             'product_uom_qty': quantity,
             'product_uom': unit_measure.id,
             'price_unit': unit_price
             })
        self.sale_order_line_id = sale_order_line_id
        return True

    @api.model
    def _sale_order_line_update(self, description, quantity, unit_price):
        self.sale_order_line_id.update(
            {'name': description,
             'product_uom_qty': quantity,
             'price_unit': unit_price
             })
        return True
