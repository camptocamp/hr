from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class BundleDetails(models.Model):
    _name = 'bundle.details'

    sale_order_id = fields.Many2one(
        string='Sale Order',
        comodel_name='sale.order',
        ondelete='cascade',
        required=True
    )
    currency_id = fields.Many2one(
        related='sale_order_id.currency_id',
        readonly=True,
        store=True
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
    bundle_id = fields.Many2one(
        string='Bundle',
        comodel_name='product.product',
        required=True
    )
    bundle_categ_id = fields.Many2one(
        related='bundle_id.categ_id',
        readonly=True,
        store=True
    )
    is_epl = fields.Boolean(
        related='bundle_id.is_epl',
        readonly=True,
        store=True
    )
    bundle_name = fields.Char(
        string='Name',
        compute='compute_bundle_name',
        store=True
    )
    bundle_description = fields.Text(
        string='Description',
        compute='compute_bundle_description',
        store=True
    )
    bundle_products = fields.One2many(
        string='Products',
        comodel_name='bundle.details.product',
        inverse_name='bundle_details_id',
        domain=[('is_epl', '=', False)],
        context={'default_is_epl': False}
    )
    bundle_mrc = fields.Float(
        string='MRC',
        compute='compute_bundle_mrc',
        store=True
    )
    bundle_mrr = fields.Float(
        string='MRR',
        compute='compute_bundle_mrr',
        store=True
    )
    bundle_nrr = fields.Float(
        string='NRR'
    )

    # BUNDLE ONCHANGES

    @api.onchange('bundle_id')
    def set_products(self):
        for rec in self:
            field = 'epl_products' if rec.is_epl else 'bundle_products'
            rec.update({
                field: [(0, 0, {
                    'product_id': p.id
                }) for p in rec.bundle_id.products]
            })
            for bp in rec.bundle_products:
                bp.onchange_dflt_mrr_unit()

    # BUNDLE COMPUTES

    @api.depends('bundle_products.product_id', 'bundle_products.quantity')
    def compute_bundle_name(self):
        for rec in self:
            bundle_name = []
            for p in rec.bundle_products:
                if not p.quantity:
                    continue
                item = "%s: %s" % (p.product_id.display_name, p.quantity)
                bundle_name.append(item)
            rec.update({
                'bundle_name': ', '.join(bundle_name)
            })

    @api.depends('bundle_products.product_id', 'bundle_products.description',
                 'bundle_products.quantity')
    def compute_bundle_description(self):
        for rec in self:
            bundle_description = []
            for p in rec.bundle_products:
                if not p.quantity:
                    continue
                item_description = " (%s)" if p.description else ""
                item = "%s%s: %s" % (p.product_id.display_name,
                                     item_description,
                                     p.quantity)
                bundle_description.append(item)
            rec.update({
                'bundle_description': '\n'.join(bundle_description)
            })

    @api.depends('bundle_products.mrc')
    def compute_bundle_mrc(self):
        for rec in self:
            rec.update({
                'bundle_mrc': sum(rec.mapped('bundle_products.mrc'))
            })

    @api.depends('bundle_products.mrr')
    def compute_bundle_mrr(self):
        for rec in self:
            rec.update({
                'bundle_mrr': sum(rec.mapped('bundle_products.mrr'))
            })

    # BUNDLE CONSTRAINTS

    # BUNDLE PRODUCTS MUST HAVE POSITIVE QUANTITIES
    @api.constrains('bundle_products')
    def constraints_bundle_products(self):
        for rec in self:
            if any(p.quantity < 0 for p in rec.bundle_products):
                raise ValidationError(_("Negative quantity on Products"))

    # BUNDLE ADD/SAVE

    @api.multi
    def button_bundle_save(self):
        return self.bundle_save(self.bundle_name,
                                self.bundle_description,
                                self.bundle_mrr,
                                self.bundle_nrr)

    @api.model
    def bundle_save(self, name, description, mrr, nrr):
        if mrr <= 0:
            raise ValidationError(_("Invalid MRR Value"))
        product_mrc = self._get_product_mrc(name)
        self._set_line(product_mrc, description, mrr)
        if nrr > 0:
            product_nrc = self.bundle_id.nrc_product
            self._set_line(product_nrc, product_nrc.name, nrr)
        elif self.sale_order_line_id_nrc:
            self.sale_order_line_id_nrc.unlink()
        return {'type': 'ir.actions.act_close_wizard_and_reload_view'}

    @api.model
    def _get_product_mrc(self, name):
        product = self.sale_order_line_id_mrc.product_id
        if not product:
            product = self.bundle_id.sudo().copy()
            product.product_tmpl_id.sudo().write({
                'active': False,
                'is_bundle': False,
                'is_epl': False,
                'nrc_product': False,
                'products': False,
            })
        product.product_tmpl_id.sudo().write({'name': name})
        return product

    @api.model
    def _set_line(self, product_id, description, price):
        data = {
            'order_id': self.sale_order_id.id,
            'product_id': product_id.id,
            'name': description,
            'price_unit': price
        }
        if product_id.recurring_invoice:
            data['bundle_details_id'] = self.id
            line = self.sale_order_line_id_mrc
        else:
            line = self.sale_order_line_id_nrc
        if line:
            line.update(data)
        else:
            line = self.env['sale.order.line'].create(data)
            if product_id.recurring_invoice:
                product_id.sudo().write({'sale_order_line_id': line.id})
                self.sale_order_line_id_mrc = line
            else:
                self.sale_order_line_id_nrc = line
