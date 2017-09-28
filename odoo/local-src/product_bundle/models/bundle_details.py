from odoo import models, fields, api, exceptions, _


class BundleDetails(models.Model):
    _name = 'bundle.details'

    # VISIBILITY VARIABLES

    show_bundle = fields.Boolean(
        compute='compute_show_bundle'
    )
    show_epl = fields.Boolean(
        compute='compute_show_epl'
    )

    # SALE ORDER VARIABLES

    # Set from sale_order.py button xml (default_sale_order_id)
    sale_order_id = fields.Many2one(
        string='Sale Order',
        comodel_name='sale.order',
        required=True
    )
    sale_order_currency_id = fields.Many2one(
        string='Sale Order Currency',
        related='sale_order_id.currency_id'
    )
    sale_order_line_id = fields.Many2one(
        string='Sale Order Line',
        comodel_name='sale.order.line',
        ondelete='cascade'
    )

    # BUNDLE VARIABLES

    # Set from sale_order.py button xml (default_bundle_id)
    bundle_id = fields.Many2one(
        string='Bundle',
        comodel_name='product.product'
    )
    bundle_categ_id = fields.Many2one(
        string='Bundle Category',
        related='bundle_id.categ_id',
        readonly=True
    )
    bundle_products = fields.One2many(
        string='Products',
        comodel_name='bundle.details.product',
        inverse_name='bundle_details_id',
    )
    bundle_name = fields.Char(
        string='Bundle Name'
    )
    bundle_price_per_unit = fields.Monetary(
        string='Price/Unit',
        currency_field='sale_order_currency_id',
        compute='compute_bundle_price_per_unit'
    )
    bundle_cost_per_unit = fields.Monetary(
        string='Cost/Unit',
        currency_field='sale_order_currency_id',
        compute='compute_bundle_cost_per_unit'
    )
    bundle_quantity = fields.Integer(
        string='Quantity',
        default=1
    )
    bundle_price = fields.Monetary(
        string='Bundle Price',
        currency_field='sale_order_currency_id',
        compute='compute_bundle_price'
    )
    bundle_cost = fields.Monetary(
        string='Bundle Cost',
        currency_field='sale_order_currency_id',
        compute='compute_bundle_cost'
    )

    # VISIBILITY COMPUTES

    @api.depends('bundle_id')
    def compute_show_bundle(self):
        for rec in self:
            rec.show_bundle = not rec.bundle_id.is_bundle_epl

    @api.depends('bundle_id')
    def compute_show_epl(self):
        for rec in self:
            rec.show_epl = rec.bundle_id.is_bundle_epl

    # BUNDLE ONCHANGES

    @api.onchange('show_bundle')
    def onchange_show_bundle(self):
        for rec in self:
            if not rec.show_bundle:
                continue
            rec.bundle_products = [
                (0, 0, {'currency_id': rec.sale_order_currency_id,
                        'product_id': p.product_id,
                        'quantity': p.quantity})
                for p in rec.bundle_id.products]

    @api.onchange('bundle_products')
    def onchange_bundle_products(self):
        for rec in self:
            bundle_details = ", ".join("%s: %s" % (p.name, p.quantity)
                                       for p in rec.bundle_products
                                       if p.quantity > 0)
            rec.bundle_name = "%s [%s]" % (rec.bundle_id.name,
                                           bundle_details)

    # BUNDLE COMPUTES

    @api.depends('bundle_products')
    def compute_bundle_price_per_unit(self):
        for rec in self:
            rec.bundle_price_per_unit = sum(
                p.price for p in rec.bundle_products)

    @api.depends('bundle_products')
    def compute_bundle_cost_per_unit(self):
        for rec in self:
            rec.bundle_cost_per_unit = sum(
                p.cost for p in rec.bundle_products)

    @api.depends('bundle_price_per_unit', 'bundle_quantity')
    def compute_bundle_price(self):
        for rec in self:
            rec.bundle_price = rec.bundle_price_per_unit * rec.bundle_quantity

    @api.depends('bundle_cost_per_unit', 'bundle_quantity')
    def compute_bundle_cost(self):
        for rec in self:
            rec.bundle_cost = rec.bundle_cost_per_unit * rec.bundle_quantity

    # BUNDLE CONSTRAINTS

    # BUNDLE PRODUCTS MUST HAVE POSITIVE QUANTITIES
    @api.constrains('bundle_products')
    def constraints_bundle_products(self):
        for rec in self:
            if not rec.show_bundle:  # Constraints do not apply
                continue
            if any(p.quantity < 0 for p in rec.bundle_products):
                raise exceptions.ValidationError(
                    _("Bundle products cannot contain negative quantities"))

    # BUNDLE QUANTITY MUST BE POSITIVE
    @api.constrains('bundle_quantity')
    def constraints_bundle_quantity(self):
        for rec in self:
            if not rec.show_bundle:  # Constraints do not apply
                continue
            if rec.bundle_quantity <= 0:
                raise exceptions.ValidationError(
                    _("Bundle quantity must be a positive integer"))

    # BUNDLE ADD/SAVE

    @api.multi
    def button_bundle_save(self):
        return self.bundle_save(self.bundle_id,
                                self.bundle_name,
                                self.bundle_quantity,
                                self.bundle_id.uom_id,
                                self.bundle_price_per_unit)

    @api.model
    def bundle_save(self, bundle_id, bundle_name, quantity, uom_id,
                    price_per_unit):
        product_id = self._product_create(bundle_id, uom_id, price_per_unit)
        line_data = {'order_id': self.sale_order_id.id,
                     'bundle_details_id': self.id,
                     'product_id': product_id.id,
                     'name': bundle_name,
                     'product_uom_qty': quantity,
                     'product_uom': uom_id.id,
                     'price_unit': price_per_unit}
        if not self.sale_order_line_id:
            line_id = self.env['sale.order.line'].create(line_data)
            self.sale_order_line_id = line_id
        else:
            old_product_id = self.sale_order_line_id.product_id
            self.sale_order_line_id.update(line_data)
            old_product_id.unlink()
        return True

    @api.model
    def _product_create(self, bundle_id, uom_id, price_per_unit):
        company_id = self.sale_order_id.company_id
        currency_id = company_id.currency_id
        list_price = self.sale_order_currency_id.sudo().compute(
            from_amount=price_per_unit,
            to_currency=currency_id
        )
        return self.env['product.product'].create({
            'name': bundle_id.name,
            'type': 'consu',  # consu / service
            'categ_id': bundle_id.categ_id.id,
            'list_price': list_price,
            'uom_id': uom_id.id,
            'company_id': company_id.id,
            'recurring_invoice': True,  # True / False,
            'invoice_policy': 'delivery',  # order / delivery
            'active': False
        })
