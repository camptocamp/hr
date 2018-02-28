# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api
import odoo.addons.decimal_precision as dp


class SaleDealsheetSourceLineMixin(models.AbstractModel):
    _name = 'sale.dealsheet.source.line.mixin'

    # # TODO Check if needed
    # # XXX: this must be not required as nowadays
    # # we have no wiz id, just a NewId record instead.
    # # Hence, we cannot just write non-existing lines to the wiz object.
    # # To work around this we create all the lines and add them
    # # to respective browse recordset.
    wiz_id = fields.Many2one(
        string='Wizard',
        comodel_name='wiz.sale.dealsheet.source',
    )
    supplier_id = fields.Many2one(
        string='Supplier',
        comodel_name='res.partner',
    )
    dealsheet_line_id = fields.Many2one(
        string='Dealsheet line',
        comodel_name='sale.dealsheet.line',
    )

    duration = fields.Integer(related="dealsheet_line_id.duration")
    product_id = fields.Many2one(
        string='Product',
        comodel_name='product.product',
        related='dealsheet_line_id.product_id',
        readonly=True,
    )
    qty = fields.Integer(related='dealsheet_line_id.quantity')
    uom_id = fields.Many2one(
        comodel_name='product.uom',
        string='UoM',
        related='dealsheet_line_id.uom_id',
        readonly=True,
    )
    price = fields.Float(
        string='Price',
        digits=dp.get_precision('Product Price'),
    )


class SaleDealsheetSourceLineSource(models.TransientModel):
    _name = 'sale.dealsheet.line.source'
    _inherit = 'sale.dealsheet.source.line.mixin'


class SaleDealsheetSourceLineToSource(models.TransientModel):
    _name = 'sale.dealsheet.line.tosource'
    _inherit = 'sale.dealsheet.source.line.mixin'


class SaleDealsheetSourceLineSourcing(models.TransientModel):
    _name = 'sale.dealsheet.line.sourcing'
    _inherit = 'sale.dealsheet.source.line.mixin'

    source_line_id = fields.Many2one(
        string='Source line',
        comodel_name='sale.dealsheet.line.source',
        ondelete='set null',
    )


class WizSaleDealsheetSource(models.TransientModel):

    _name = 'wiz.sale.dealsheet.source'
    _description = 'Manage dealsheet sourcing'

    dealsheet_id = fields.Many2one(
        string='Sale Dealsheet',
        comodel_name='sale.dealsheet',
        required=True,
    )
    supplier_id = fields.Many2one(
        string='Supplier',
        comodel_name='res.partner',
    )
    line_ids = fields.One2many(
        comodel_name='sale.dealsheet.line.source',
        inverse_name='wiz_id',
        string='Lines',
    )
    sourcing_line_ids = fields.One2many(
        comodel_name='sale.dealsheet.line.sourcing',
        inverse_name='wiz_id',
        string='Lines sourcing',
    )
    to_source_line_ids = fields.Many2many(
        comodel_name='sale.dealsheet.line.tosource',
        string='Lines to source',
        compute='_compute_to_source_line_ids',
        relation='wiz_sale_dealsheet_source_tosource_rel',
        readonly=True,
    )
    sourced_line_ids = fields.Many2many(
        comodel_name='sale.dealsheet.line.tosource',
        string='Lines sourced already',
        compute='_compute_sourced_line_ids',
        relation='wiz_sale_dealsheet_sourcing_rel',
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
        return self.env['sale.dealsheet.line.source']

    @property
    def to_source_model(self):
        return self.env['sale.dealsheet.line.tosource']

    @property
    def sourcing_model(self):
        return self.env['sale.dealsheet.line.sourcing']

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

    def _load_lines_from_dealsheet(self):
        self.ensure_one()
        domain = [
            ('dealsheet_id', '=', self.dealsheet_id.id),
            ('sourcing_purchase_line_id', '=', False),
        ]
        lines = self.env['sale.dealsheet.line'].search(domain)
        for line in lines:
            self.line_ids |= self.source_model.create({
                'wiz_id': self.id,
                'dealsheet_line_id': line.id,
            })

    def _load_sourcing_lines(self):
        self.ensure_one()
        lines = self.line_ids.filtered(
            lambda x: not x.supplier_id or x.supplier_id == self.supplier_id
        )
        for line in lines:
            supplierinfo = line.product_id._select_seller(
                partner_id=self.supplier_id,
                quantity=line.qty,
                date=fields.Date.today(),
                uom_id=line.uom_id)

            data = line.copy_data()[0]
            data['supplier_id'] = self.supplier_id.id
            data['source_line_id'] = line.id
            data['price'] = supplierinfo.price
            self.sourcing_line_ids |= self.sourcing_model.create(data)

    def _reset_sourcing_lines(self):
        self.sourcing_line_ids = False

    def _get_available_suppliers(self):
        """All suppliers for all order lines' product w/out a supplier."""
        # FIXME: make more clear and performant
        supp_info = self.line_ids.filtered(
            lambda x: not x.supplier_id
        ).mapped('dealsheet_line_id.product_id').mapped('seller_ids')
        return supp_info.mapped('name')  # name is m2o to partner :/

    def _get_supplier_domain(self):
        suppliers = self._get_available_suppliers()
        return [('id', 'in', suppliers.ids)]

    @api.onchange('dealsheet_id')
    def onchange_dealsheet_id(self):
        if not self.dealsheet_id:
            return
        self._load_lines_from_dealsheet()
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
        self.with_context(sourcing_now=True).update({
            'source_it': False,
            'supplier_id': False,
        })

    @api.multi
    def action_ok(self):
        self.ensure_one()
        created = self._create_purchase_orders()
        action = self.env.ref('purchase.purchase_rfq').copy_data()[0]
        action['domain'] = [('id', 'in', created)]
        return action

    def _purchase_line_value(self, wiz_line):
        data = {
            'product_id': wiz_line.product_id.id,
            'product_uom': wiz_line.uom_id.id,
            'product_qty': wiz_line.qty,
            'name': wiz_line.product_id.display_name,
            'price_unit': wiz_line.price,
            'date_planned': fields.Date.today(),
            'sourced_dealsheet_line_id': wiz_line.dealsheet_line_id.id,
            # 'account_analytic_id':
            # wiz_line.dealsheet_line_id.dealsheet_id.project_id.id,
        }
        return data

    def _create_purchase_orders(self):
        group = {}
        for line in self.line_ids:
            if line.supplier_id.id in group:
                if line.duration in group[line.supplier_id.id]:
                    group[line.supplier_id.id][line.duration].append(line)
                else:
                    group[line.supplier_id.id].update({line.duration: [line]})
            else:
                group[line.supplier_id.id] = {line.duration: [line]}
        created = []
        for supplier, lines_dict in group.iteritems():
            for duration, lines in lines_dict.iteritems():
                order_data = {
                    'partner_id': supplier,
                    'subscr_duration': duration,
                    'order_line': [
                        (0, 0, self._purchase_line_value(
                            line)) for line in lines
                    ]
                }
                order = self.env['purchase.order'].create(order_data)
                for line in order.order_line:
                    line.onchange_product_id()
                print order.id
                created.append(order.id)

        # link sale line to purchase line.
        # We can have more than one line w/ the same product
        # so we cannot just rely on product_id match.
        po_lines = self.env['purchase.order.line'].search(
            [('order_id', 'in', created)])
        mapping = po_lines.mapped(lambda x: (x.sourced_dealsheet_line_id.id, x.id))
        self._update_dealsheet_lines(mapping)
        return created

    def _update_dealsheet_lines(self, mapping):
        """Link SO lines to PO lines.

        We might have tons of lines so here we
        update all SO lines at once w/ one single query.

        Mapping must be a list of tuple like `(SO line id, PO line id)`.
        """
        query = """
                UPDATE sale_dealsheet_line AS sol SET
                    sourcing_purchase_line_id = c.sourcing_purchase_line_id
                FROM (VALUES {})
                    AS c(id, sourcing_purchase_line_id)
                WHERE c.id = sol.id;
            """.format(','.join(['(%d, %d)' % (x[0], x[1]) for x in mapping]))
        self.env.cr.execute(query)
