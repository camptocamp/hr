from odoo import models, fields, api, exceptions, _
import math


class BundleDetails(models.Model):
    _name = 'bundle.details'

    # VISIBILITY VARIABLES

    show_bundle = fields.Boolean(
        compute='compute_visibility',
        store=True
    )
    show_epl = fields.Boolean(
        compute='compute_visibility',
        store=True
    )

    # SALE ORDER VARIABLES

    # Set from sale_order.py button xml (default_sale_order_id)
    sale_order_id = fields.Many2one(
        string='Sale Order',
        comodel_name='sale.order',
        ondelete='cascade',
        required=True
    )
    currency_id = fields.Many2one(
        related='sale_order_id.currency_id',
        readonly=True
    )
    sale_order_line_id_mrc = fields.Many2one(
        string='Sale Order Line MRC',
        comodel_name='sale.order.line',
        ondelete='cascade'
    )
    sale_order_line_id_nrc = fields.Many2one(
        string='Sale Order Line NRC',
        comodel_name='sale.order.line',
    )

    # BUNDLE VARIABLES

    # Set from sale_order.py button xml (default_bundle_id)
    bundle_id = fields.Many2one(
        string='Bundle',
        comodel_name='product.product'
    )
    bundle_categ_id = fields.Many2one(
        related='bundle_id.categ_id',
        readonly=True
    )
    bundle_products = fields.One2many(
        string='Products',
        comodel_name='bundle.details.product',
        inverse_name='bundle_details_id'
    )
    bundle_quantity = fields.Integer(
        string='Quantity',
        default=1
    )
    bundle_name = fields.Char(
        string='Bundle Name'
    )
    bundle_discount = fields.Integer(
        string='Bundle Discount (%)',
        default=0
    )
    bundle_price_per_unit = fields.Float(
        string='Price/Unit',
        compute='compute_bundle_price_per_unit'
    )
    bundle_cost_per_unit = fields.Float(
        string='Cost/Unit',
        compute='compute_bundle_cost_per_unit'
    )
    bundle_price = fields.Float(
        string='Bundle MRR',
        compute='compute_bundle_price'
    )
    bundle_cost = fields.Float(
        string='Bundle MRC',
        compute='compute_bundle_cost'
    )
    bundle_price_upfront = fields.Float(
        string='Bundle NRR'
    )

    # VISIBILITY

    @api.depends('bundle_id.is_bundle_epl')
    def compute_visibility(self):
        for rec in self:
            rec.update({
                'show_bundle': not rec.bundle_id.is_bundle_epl,
                'show_epl': rec.bundle_id.is_bundle_epl
            })

    # BUNDLE ONCHANGES

    @api.onchange('show_bundle')
    def onchange_show_bundle(self):
        for rec in self:
            if not rec.show_bundle:
                continue
            rec.update({
                'bundle_products': [
                    (0, 0, {'bundle_categ_id': rec.bundle_id.categ_id,
                            'product_id': p.product_id,
                            'quantity': p.quantity})
                    for p in rec.bundle_id.products
                ]
            })
            for bdp in rec.bundle_products:
                bdp.onchange_product_id()  # Compute default price_per_unit

    @api.onchange('bundle_products')
    def onchange_bundle_products(self):
        for rec in self:
            bundle_details = self.get_bundle_details(rec.bundle_products)
            rec.update({
                'bundle_name': "%s [%s]" % (rec.bundle_id.name,
                                            bundle_details)
            })

    # BUNDLE COMPUTES

    @api.depends('bundle_products.price', 'bundle_discount')
    def compute_bundle_price_per_unit(self):
        for rec in self:
            res = sum(rec.mapped('bundle_products.price'))
            res *= self.get_factor_from_percent(rec.bundle_discount)
            rec.update({
                'bundle_price_per_unit': res
            })

    @api.depends('bundle_products.cost')
    def compute_bundle_cost_per_unit(self):
        for rec in self:
            res = sum(rec.mapped('bundle_products.cost'))
            rec.update({
                'bundle_cost_per_unit': res
            })

    @api.depends('bundle_price_per_unit', 'bundle_quantity')
    def compute_bundle_price(self):
        for rec in self:
            res = rec.bundle_price_per_unit * rec.bundle_quantity
            rec.update({
                'bundle_price': res
            })

    @api.depends('bundle_cost_per_unit', 'bundle_quantity')
    def compute_bundle_cost(self):
        for rec in self:
            res = rec.bundle_cost_per_unit * rec.bundle_quantity
            rec.update({
                'bundle_cost': res
            })

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
                                self.bundle_price_per_unit,
                                self.bundle_price_upfront)

    @api.model
    def bundle_save(self, bundle_id, bundle_name, qty, uom_id, mrc, nrc):
        self._bundle_save_mrc(bundle_id, bundle_name, qty, mrc, uom_id)
        self._bundle_save_nrc(bundle_id, nrc)
        return {'type': 'ir.actions.act_close_wizard_and_reload_view'}

    @api.model
    def _bundle_save_mrc(self, bundle_id, bundle_name, qty, price, uom_id):
        if not price:
            raise exceptions.ValidationError(_("Bundle must have MRR"))

        self._create_or_update_line(bundle_id, uom_id, price, bundle_name, qty,
                                    recurring=True)

    @api.model
    def _bundle_save_nrc(self, bundle_id, price):
        if not price:
            self.sale_order_line_id_nrc.unlink()
            return

        uom_id = bundle_id.bundle_upfront_uom_id
        description = bundle_id.name + " Project Management"
        self._create_or_update_line(bundle_id, uom_id, price, description, 1,
                                    recurring=False)

    @api.model
    def _create_or_update_product(self, bundle_id, uom_id, price, recurring):
        if recurring:
            product_name = bundle_id.name + " MRC"
            product_type = "consu"
            recurring_invoice = True
            invoice_policy = "delivery"
        else:
            product_name = bundle_id.name + " NRC"
            product_type = "service"
            recurring_invoice = False
            invoice_policy = "order"

        company_id = self.sale_order_id.company_id
        currency_id = company_id.currency_id
        list_price = self.currency_id.sudo().compute(
            from_amount=price,
            to_currency=currency_id,
            round=False
        )

        data = {'name': product_name,
                'type': product_type,
                'categ_id': bundle_id.categ_id.id,
                'list_price': self.get_rounded_upper_decimal(list_price),
                'uom_id': uom_id.id,
                'uom_po_id': uom_id.id,
                'company_id': company_id.id,
                'recurring_invoice': recurring_invoice,
                'invoice_policy': invoice_policy,
                'sale_ok': True,
                'purchase_ok': True,
                'can_be_expensed': False,
                'active': False}

        if recurring:
            product_id = self.sale_order_line_id_mrc.product_id
        else:
            product_id = self.sale_order_line_id_nrc.product_id

        if product_id:
            product_id.sudo().update(data)
        else:
            product_id = self.env['product.product'].sudo().create(data)
            product_id.sudo().product_tmpl_id.active = False

        return product_id

    @api.model
    def _create_or_update_line(self, bundle_id, uom_id, price, description,
                               quantity, recurring):
        product_id = self._create_or_update_product(bundle_id, uom_id, price,
                                                    recurring)

        data = {'order_id': self.sale_order_id.id,
                'bundle_details_id': self.id if recurring else False,
                'product_id': product_id.id,
                'name': description,
                'product_uom_qty': quantity,
                'product_uom': product_id.uom_id.id,
                'price_unit': self.get_rounded_upper_decimal(price)}

        if recurring:
            line_id = self.sale_order_line_id_mrc
        else:
            line_id = self.sale_order_line_id_nrc

        if line_id:
            line_id.sudo().update(data)
        else:
            line_id = self.env['sale.order.line'].sudo().create(data)
            product_id.sudo().sale_order_line_id = line_id
            if recurring:
                self.sale_order_line_id_mrc = line_id
            else:
                self.sale_order_line_id_nrc = line_id

        return line_id

    # TOOLS

    @api.model
    def get_bundle_details(self, bundle_products):
        details = []
        for product in bundle_products:
            if product.quantity <= 0:
                continue
            detail = [product.product_id.name]
            if product.description:
                detail.append(" (%s)" % product.description)
            detail.append(": %s" % product.quantity)
            details.append("".join(detail))
        return ", ".join(details)

    @api.model
    def get_factor_from_percent(self, x):
        return 1 - x / 100.0

    @api.model
    def get_rounded_upper_decimal(self, x):
        precision = self.env['decimal.precision'].search(
            [('name', '=', 'Product Price')]).digits
        factor = 10 ** precision
        return math.ceil(x * factor) / factor
