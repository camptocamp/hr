# -*- coding: utf-8 -*-
# Author: Simone Orsi <simone.orsi@camptocamp.com>
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api
import odoo.addons.decimal_precision as dp
from collections import defaultdict


class SaleOrderSourceLineMixin(models.AbstractModel):
    _name = 'sale.order.source.line.mixin'

    # XXX: this must be not required as nowadays
    # we have no wiz id, just a NewId record instead.
    # Hence, we cannot just write non-existing lines to the wiz object.
    # To work around this we create all the lines and add them
    # to respective browse recordset.
    wiz_id = fields.Many2one(
        string='Wizard',
        comodel_name='wiz.sale.order.source',
    )
    supplier_id = fields.Many2one(
        string='Supplier',
        comodel_name='res.partner',
    )
    so_line_id = fields.Many2one(
        string='Sale order line',
        comodel_name='sale.order.line',
    )
    product_id = fields.Many2one(
        string='Product',
        comodel_name='product.product',
        related='so_line_id.product_id',
        readonly=True,
    )
    qty = fields.Float(related='so_line_id.product_uom_qty')
    uom_id = fields.Many2one(
        comodel_name='product.uom',
        string='UoM',
        related='so_line_id.product_uom',
        readonly=True,
    )


class SaleOrderSourceLineSource(models.TransientModel):
    _name = 'sale.order.line.source'
    _inherit = 'sale.order.source.line.mixin'


class SaleOrderSourceLineToSource(models.TransientModel):
    _name = 'sale.order.line.tosource'
    _inherit = 'sale.order.source.line.mixin'


class SaleOrderSourceLineSourcing(models.TransientModel):
    _name = 'sale.order.line.sourcing'
    _inherit = 'sale.order.source.line.mixin'

    source_line_id = fields.Many2one(
        string='Source line',
        comodel_name='sale.order.line.source',
        ondelete='set null',
    )
    price = fields.Float(
        string='Price',
        digits=dp.get_precision('Product Price'),
    )


class WizSaleOrderSource(models.TransientModel):
    _name = 'wiz.sale.order.source'
    _description = 'Manage sale orders sourcing'

    order_id = fields.Many2one(
        string='Sale Order',
        comodel_name='sale.order',
        required=True,
    )
    supplier_id = fields.Many2one(
        string='Supplier',
        comodel_name='res.partner',
    )
    line_ids = fields.One2many(
        comodel_name='sale.order.line.source',
        inverse_name='wiz_id',
        string='Lines',
    )
    sourcing_line_ids = fields.One2many(
        comodel_name='sale.order.line.sourcing',
        inverse_name='wiz_id',
        string='Lines sourcing',
    )
    to_source_line_ids = fields.Many2many(
        comodel_name='sale.order.line.tosource',
        string='Lines to source',
        compute='_compute_to_source_line_ids',
        relation='wiz_sale_order_source_tosource_rel',
        readonly=True,
    )
    sourced_line_ids = fields.Many2many(
        comodel_name='sale.order.line.tosource',
        string='Lines sourced already',
        compute='_compute_sourced_line_ids',
        relation='wiz_sale_order_sourcing_rel',
        readonly=True,
    )
    # This flag replaces the `source` button
    # as it is impossible to make the whole wizard
    # work fine w/ a button.
    # When you hit the button the wizard form is submitted
    # and a new wizard created and you gonna lose all data.
    # So, we use a flag, we make it appear like a button
    # and use an onchange to run the source action. :)
    source_it = fields.Boolean(string='Source')

    @property
    def source_model(self):
        return self.env['sale.order.line.source']

    @property
    def to_source_model(self):
        return self.env['sale.order.line.tosource']

    @property
    def sourcing_model(self):
        return self.env['sale.order.line.sourcing']

    def _get_computed_lines(self, has_supplier):
        source_lines = self.line_ids.filtered(
            lambda x: bool(x.supplier_id) == has_supplier
        )
        res = self.to_source_model.browse()
        for line in source_lines:
            data = line.copy_data()[0]
            res |= self.to_source_model.create(data)
        return res

    @api.depends('line_ids.supplier_id')
    def _compute_to_source_line_ids(self):
        has_supplier = False
        for item in self:
            item.to_source_line_ids = self._get_computed_lines(has_supplier)

    @api.depends('line_ids.supplier_id')
    def _compute_sourced_line_ids(self):
        has_supplier = True
        for item in self:
            item.sourced_line_ids = self._get_computed_lines(has_supplier)

    def _load_lines_from_order(self):
        self.ensure_one()
        domain = [
            ('order_id', '=', self.order_id.id),
            ('sourcing_purchase_line_id', '=', False),
        ]
        lines = self.env['sale.order.line'].search(domain)
        for line in lines:
            self.line_ids |= self.source_model.create({
                'wiz_id': self.id,
                'so_line_id': line.id,
            })

    def _load_sourcing_lines(self):
        self.ensure_one()
        lines = self.line_ids.filtered(
            lambda x: not x.supplier_id or x.supplier_id == self.supplier_id
        )
        for line in lines:
            data = line.copy_data()[0]
            data['supplier_id'] = self.supplier_id.id
            data['source_line_id'] = line.id
            self.sourcing_line_ids |= self.sourcing_model.create(data)

    def _reset_sourcing_lines(self):
        self.sourcing_line_ids = False

    def _get_available_suppliers(self):
        """All suppliers for all order lines' product w/out a supplier."""
        # FIXME: make more clear and performant
        supp_info = self.line_ids.filtered(
            lambda x: not x.supplier_id
        ).mapped('so_line_id.product_id').mapped('seller_ids')
        return supp_info.mapped('name')  # name is m2o to partner :/

    def _get_supplier_domain(self):
        suppliers = self._get_available_suppliers()
        return [('id', 'in', suppliers.ids)]

    @api.onchange('order_id')
    def onchange_order_id(self):
        if not self.order_id:
            return
        self._load_lines_from_order()
        self._load_sourcing_lines()
        return {
            'domain': {
                'supplier_id': self._get_supplier_domain(),
            }
        }

    @api.onchange('supplier_id')
    def onchange_supplier_id(self):
        self._reset_sourcing_lines()
        self._load_sourcing_lines()

    def action_source(self):
        self.sourcing_line_ids.mapped('source_line_id').write({
            'supplier_id': self.supplier_id.id,
        })

    @api.onchange('source_it')
    def onchange_source_it(self):
        if self.env.context.get('sourcing_now') or not self.source_it:
            return
        self.action_source()
        self.with_context(sourcing_now=True).write({
            'source_it': False,
            'supplier_id': False,
        })

    @api.multi
    def action_ok(self):
        self.ensure_one()
        created = self._create_orders()
        action = self.env.ref('purchase.purchase_rfq').copy_data()[0]
        action['domain'] = [('id', 'in', created)]
        return action

    def _purchase_line_value(self, wiz_line):
        data = {
            'product_id': wiz_line.product_id.id,
            'product_uom': wiz_line.uom_id.id,
            'product_qty': wiz_line.qty,
            'name': wiz_line.product_id.display_name,
            'price_unit': 1.0,
            'date_planned': fields.Date.today(),
            'sourced_sale_line_id': wiz_line.so_line_id.id,
        }
        return data

    def _create_orders(self):
        grouped = defaultdict(list)
        for line in self.line_ids:
            grouped[line.supplier_id].append(line)
        created = []
        for supplier, lines in grouped.iteritems():
            order_data = {
                'partner_id': supplier.id,
                'subscr_duration': 0,  # TODO
                'order_line': [
                    (0, 0, self._purchase_line_value(line)) for line in lines
                ]
            }
            order = self.env['purchase.order'].create(order_data)
            created.append(order.id)
        # link sale line to purchase line.
        # We can have more than one line w/ the same product
        # so we cannot just rely on product_id match.
        po_lines = self.env['purchase.order.line'].search(
            [('order_id', 'in', created)])
        mapping = po_lines.mapped(lambda x: (x.sourced_sale_line_id.id, x.id))
        self._update_so_lines(mapping)
        return created

    def _update_so_lines(self, mapping):
        """Link SO lines to PO lines.

        We might have tons of lines so here we
        update all SO lines at once w/ one single query.

        Mapping must be a list of tuple like `(SO line id, PO line id)`.
        """
        query = """
            UPDATE sale_order_line AS sol SET
                sourcing_purchase_line_id = c.sourcing_purchase_line_id
            FROM (VALUES {})
                AS c(id, sourcing_purchase_line_id)
            WHERE c.id = sol.id;
        """.format(','.join(['(%d, %d)' % (x[0], x[1]) for x in mapping]))
        self.env.cr.execute(query)
