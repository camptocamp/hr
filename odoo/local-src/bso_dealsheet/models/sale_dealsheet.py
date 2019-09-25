from collections import defaultdict

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SaleDealsheet(models.Model):
    _name = 'sale.dealsheet'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'sale_order_id ASC'

    state = fields.Selection(
        string='Status',
        selection=[
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('validated', 'Validated'),
            ('refused', 'Refused'),
        ],
        readonly=True,
        track_visibility='onchange',
        default='draft'
    )
    name = fields.Char(
        compute='compute_name',
        store=True
    )
    procure_ok = fields.Boolean(
        string='Procurable',
        compute='compute_procure_ok',
    )
    sale_order_id = fields.Many2one(
        string='Sale Order',
        comodel_name='sale.order',
        ondelete='cascade',
        readonly=True,
        required=True,
        copy=False,
    )
    sale_order_state = fields.Selection(
        string='Sale Order Status',
        related='sale_order_id.state',
        readonly=True,
        store=True,
    )
    company_id = fields.Many2one(
        related='sale_order_id.company_id',
        readonly=True,
        store=True,
    )
    project_id = fields.Many2one(
        related='sale_order_id.project_id',
        readonly=True,
        store=True,
    )
    partner_id = fields.Many2one(
        related='sale_order_id.partner_id',
        readonly=True,
        store=True,
    )
    duration = fields.Integer(
        related='sale_order_id.duration',
        readonly=True,
        store=True,
    )
    currency_id = fields.Many2one(
        related='sale_order_id.currency_id',
        readonly=True,
        store=True,
    )
    user_id = fields.Many2one(
        related='sale_order_id.user_id',
        readonly=True,
        store=True,
    )
    commitment_date = fields.Datetime(
        related='sale_order_id.commitment_date',
        readonly=True,
        store=True,
    )
    presale_id = fields.Many2one(
        string='Pre-Sale',
        comodel_name='res.users',
        readonly=True,
    )
    reviewer_id = fields.Many2one(
        string='Reviewer',
        comodel_name='res.users',
        readonly=True,
    )
    validated_date = fields.Datetime(
        string='Validated on',
        readonly=True,
    )
    refused_date = fields.Datetime(
        string='Refused on',
        readonly=True,
    )
    compute_lines = fields.One2many(
        string='Computed Lines',
        comodel_name='sale.dealsheet.line',
        inverse_name='dealsheet_id',
        compute='compute_compute_lines',
        domain=[('is_cost', '=', False), ('is_recurring', '=', True)],
        context={'default_is_cost': False, 'default_is_recurring': True},
        store=True,
    )
    mrc_lines = fields.One2many(
        string='MRCs',
        comodel_name='sale.dealsheet.line',
        inverse_name='dealsheet_id',
        domain=[('is_cost', '=', True), ('is_recurring', '=', True)],
        context={'default_is_cost': True, 'default_is_recurring': True},
        copy=True,
    )
    nrc_lines = fields.One2many(
        string='NRCs',
        comodel_name='sale.dealsheet.line',
        inverse_name='dealsheet_id',
        domain=[('is_cost', '=', True), ('is_recurring', '=', False)],
        context={'default_is_cost': True, 'default_is_recurring': False},
        copy=True,
    )
    nrc = fields.Monetary(
        string='NRC',
        currency_field='currency_id',
        compute='compute_nrc',
        store=True,
    )
    nrc_delivery = fields.Monetary(
        string='Delivery NRC',
        currency_field='currency_id',
        compute='compute_nrc_delivery',
        store=True,
    )
    nrr = fields.Monetary(
        string='NRR',
        currency_field='currency_id',
        compute='compute_nrr',
        store=True,
    )
    nrm = fields.Float(
        string='NRM (%)',
        compute='compute_nrm',
        store=True,
    )
    nrm_delivery = fields.Float(
        string='Delivery NRM (%)',
        compute='compute_nrm_delivery',
        store=True,
    )
    mrc = fields.Monetary(
        string='MRC',
        currency_field='currency_id',
        compute='compute_mrc',
        store=True,
    )
    mrc_delivery = fields.Monetary(
        string='Delivery MRC',
        currency_field='currency_id',
        compute='compute_mrc_delivery',
        store=True,
    )
    mrr = fields.Monetary(
        string='MRR',
        currency_field='currency_id',
        compute='compute_mrr',
        store=True,
    )
    mrm = fields.Float(
        string='MRM (%)',
        compute='compute_mrm',
        store=True,
    )
    mrm_delivery = fields.Float(
        string='Delivery MRM (%)',
        compute='compute_mrm_delivery',
        store=True,
    )
    cost = fields.Monetary(
        string='Cost',
        currency_field='currency_id',
        compute='compute_cost',
        store=True,
    )
    cost_delivery = fields.Monetary(
        string='Delivery Cost',
        currency_field='currency_id',
        compute='compute_cost_delivery',
        store=True,
    )
    revenue = fields.Monetary(
        string='Revenue',
        currency_field='currency_id',
        compute='compute_revenue',
        store=True,
    )
    margin = fields.Float(
        string='Margin (%)',
        compute='compute_margin',
        store=True,
    )
    margin_delivery = fields.Float(
        string='Delivery Margin (%)',
        compute='compute_margin_delivery',
        store=True,
    )
    purchase_order_ids = fields.One2many(
        string='Purchase Orders',
        comodel_name='purchase.order',
        inverse_name='dealsheet_id',
    )
    purchase_order_number = fields.Integer(
        string='Number of Purchase Orders',
        compute='_compute_purchase_order_number'
    )
    attachment_number = fields.Integer(
        string='Number of Attachments',
        compute='_compute_attachment_number'
    )

    @api.depends('purchase_order_ids')
    def _compute_purchase_order_number(self):
        for rec in self:
            rec.purchase_order_number = len(rec.purchase_order_ids)

    @api.multi
    def action_get_purchase_order_view(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window'].for_xml_id('purchase',
                                                           'purchase_rfq')
        res['domain'] = [('dealsheet_id', '=', self.id)]
        return res

    @api.multi
    def _compute_attachment_number(self):
        attachment_data = self.env['ir.attachment'].read_group(
            [('res_model', '=', self._name), ('res_id', 'in', self.ids)],
            ['res_id'], ['res_id'])
        attachment = dict(
            (data['res_id'], data['res_id_count']) for data in attachment_data)
        for rec in self:
            rec.attachment_number = attachment.get(rec.id, 0)

    @api.multi
    def action_get_attachment_view(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window'].for_xml_id('base',
                                                           'action_attachment')
        res['domain'] = [('res_model', '=', self._name),
                         ('res_id', 'in', self.ids)]
        res['context'] = {'default_res_model': self._name,
                          'default_res_id': self.id}
        return res

    # COMPUTES

    @api.depends('sale_order_id.name')
    def compute_name(self):
        for rec in self:
            rec.name = "%s Dealsheet" % rec.sale_order_id.name

    @api.depends('mrc_lines.purchase_order_line_id', 'mrc_lines.supplier_id',
                 'nrc_lines.purchase_order_line_id', 'nrc_lines.supplier_id')
    def compute_procure_ok(self):
        for rec in self:
            rec.procure_ok = bool(rec._get_procure_lines())

    @api.depends('sale_order_id.order_line')
    def compute_compute_lines(self):
        for rec in self:
            lines = rec.mrc_lines + rec.nrc_lines
            compute_lines = [(4, l.id, 0) for l in lines]

            order_lines = rec.sale_order_id.order_line
            exclude_order_lines = lines.mapped('sale_order_line_id')

            for order_line in order_lines:
                if order_line in exclude_order_lines:
                    continue
                compute_lines += self.get_lines(order_line)

            rec.compute_lines = compute_lines

    @api.depends('nrc_lines.cost')
    def compute_nrc(self):
        for rec in self:
            rec.nrc = sum(rec.mapped('nrc_lines.total_cost'))

    @api.depends('nrc_lines.cost_delivery')
    def compute_nrc_delivery(self):
        for rec in self:
            rec.nrc_delivery = sum(
                rec.mapped('nrc_lines.total_cost_delivery'))

    @api.depends('sale_order_id.order_line.price_subtotal')
    def compute_nrr(self):
        for rec in self:
            rec.nrr = sum(rec.sale_order_id.order_line.filtered(
                lambda r: not r.product_id.recurring_invoice).mapped(
                'price_subtotal'))

    @api.depends('nrc', 'nrr')
    def compute_nrm(self):
        for rec in self:
            rec.nrm = self.get_margin(rec.nrc, rec.nrr)

    @api.depends('nrc_delivery', 'nrr')
    def compute_nrm_delivery(self):
        for rec in self:
            rec.nrm_delivery = self.get_margin(rec.nrc_delivery, rec.nrr)

    @api.depends('mrc_lines.cost')
    def compute_mrc(self):
        for rec in self:
            rec.mrc = sum(rec.mapped('mrc_lines.total_cost'))

    @api.depends('mrc_lines.cost_delivery')
    def compute_mrc_delivery(self):
        for rec in self:
            rec.mrc_delivery = sum(
                rec.mapped('mrc_lines.total_cost_delivery'))

    @api.depends('sale_order_id.order_line.price_subtotal')
    def compute_mrr(self):
        for rec in self:
            rec.mrr = sum(rec.sale_order_id.order_line
                          .filtered(lambda r: r.product_id.recurring_invoice)
                          .mapped('price_subtotal'))

    @api.depends('mrc', 'mrr')
    def compute_mrm(self):
        for rec in self:
            rec.mrm = self.get_margin(rec.mrc, rec.mrr)

    @api.depends('mrc_delivery', 'mrr')
    def compute_mrm_delivery(self):
        for rec in self:
            rec.mrm_delivery = self.get_margin(rec.mrc_delivery, rec.mrr)

    @api.depends('mrc', 'duration', 'nrc')
    def compute_cost(self):
        for rec in self:
            rec.cost = rec.mrc * rec.duration + rec.nrc

    @api.depends('mrc_delivery', 'duration', 'nrc_delivery')
    def compute_cost_delivery(self):
        for rec in self:
            rec.cost_delivery = rec.mrc_delivery * rec.duration \
                                + rec.nrc_delivery

    @api.depends('mrr', 'duration', 'nrr')
    def compute_revenue(self):
        for rec in self:
            rec.revenue = rec.mrr * rec.duration + rec.nrr

    @api.depends('cost', 'revenue')
    def compute_margin(self):
        for rec in self:
            rec.margin = self.get_margin(rec.cost, rec.revenue)

    @api.depends('cost_delivery', 'revenue')
    def compute_margin_delivery(self):
        for rec in self:
            rec.margin_delivery = self.get_margin(rec.cost_delivery,
                                                  rec.revenue)

    # TOOLS

    @api.model
    def get_lines(self, order_line):
        if order_line.bundle_details_id.is_epl:
            lines = self.get_lines_epl(order_line)
        elif order_line.bundle_details_id:
            lines = self.get_lines_bundle(order_line)
        else:
            lines = self.get_lines_product(order_line)
        return [(0, 0, l) for l in lines]

    @api.model
    def get_lines_epl(self, order_line):
        bundle_details_id = order_line.bundle_details_id
        epl_bandwidth = bundle_details_id.epl_bandwidth
        lines = []
        for link in bundle_details_id.epl_route:
            data = self.get_line_data(
                True,
                order_line,
                order_line.product_id,
                "%.0fM %s" % (epl_bandwidth, link.link_id.name),
                order_line.product_uom_qty,
                link.mrc_mb * epl_bandwidth,
                order_line.product_id.sudo().company_id.partner_id.id,
                "monthly",
            )
            lines.append(data)
        if bundle_details_id.epl_backup:
            data = self.get_line_data(
                True,
                order_line,
                order_line.product_id,
                "%sM Protection" % epl_bandwidth,
                order_line.product_uom_qty,
                bundle_details_id.epl_backup_mrc,
                order_line.product_id.sudo().company_id.partner_id.id,
                "monthly",
            )
            lines.append(data)
        lines += self.get_lines_bundle_products(
            order_line, bundle_details_id.epl_products)
        return lines

    @api.model
    def get_lines_bundle(self, order_line):
        return self.get_lines_bundle_products(
            order_line, order_line.bundle_details_id.bundle_products)

    @api.model
    def get_lines_bundle_products(self, order_line, products):
        lines = []
        for line in products:
            if not line.quantity:
                continue
            data = self.get_line_data(
                True,
                order_line,
                line.product_id,
                line.description,
                line.quantity * order_line.product_uom_qty,
                line.mrc
            )
            lines.append(data)
            if line.nrr:
                data = self.get_line_data(
                    False,
                    order_line,
                    line.product_id,
                    line.description,
                    line.quantity * order_line.product_uom_qty,
                    0
                )
                lines.append(data)
        return lines

    @api.model
    def get_lines_product(self, order_line):
        data = self.get_line_data(
            order_line.product_id.recurring_invoice,
            order_line,
            order_line.product_id,
            order_line.name,
            order_line.product_uom_qty,
            order_line.product_id.standard_price
        )
        return [data]

    @api.model
    def get_line_data(self, is_recurring, sale_order_line_id, product_id,
                      description, quantity, cost, supplier_id=False,
                      frequency=False):
        return {
            'is_cost': True,
            'is_recurring': is_recurring,
            'sale_order_line_id': sale_order_line_id.id,
            'product_id': product_id.id,
            'description': description,
            'quantity': quantity,
            'cost': cost,
            'supplier_id': supplier_id,
            'frequency': frequency,
        }

    @api.model
    def get_margin(self, cost, revenue):
        if not cost and not revenue:
            return 0
        if not revenue:
            return -100
        return (1 - cost / revenue) * 100

    # ACTIONS

    @api.multi
    def action_create(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "sale.dealsheet",
            "res_id": self.id,
            "view_type": "form",
            "view_mode": "form",
            "flags": {'initial_mode': 'edit'},
        }

    @api.multi
    def action_request(self, sale_order_id):
        wizard_request_model = self.env['sale.dealsheet.wizard.request']
        wizard_request_id = wizard_request_model.create({
            'sale_order_id': sale_order_id
        })
        return {
            "name": "Select Presale",
            "type": "ir.actions.act_window",
            "res_model": "sale.dealsheet.wizard.request",
            "res_id": wizard_request_id.id,
            "view_type": "form",
            "view_mode": "form",
            "target": "new",
        }

    @api.multi
    def action_requested(self, sale_order_id, presale_id):
        dealsheet_id = self.sudo().create({
            'sale_order_id': sale_order_id.id
        })
        sale_order_id.update({
            'dealsheet_id': dealsheet_id.id
        })

        subject = "%s Requested" % dealsheet_id.name
        body = '<br>'.join(("Customer: %s" % dealsheet_id.partner_id.name,
                            "Duration: %s" % dealsheet_id.duration,
                            "Currency: %s" % dealsheet_id.currency_id.name,
                            "Revenue: %.2f" % dealsheet_id.revenue))

        dealsheet_id.message_subscribe_users(presale_id.id, [1])
        dealsheet_id.message_post(subject=subject,
                                  body=body,
                                  subtype='mt_comment')

    @api.multi
    def action_confirm(self):
        wizard_confirm_model = self.env['sale.dealsheet.wizard.confirm']
        wizard_confirm_id = wizard_confirm_model.create({
            'dealsheet_id': self.id
        })
        return {
            "name": "Select Reviewer",
            "type": "ir.actions.act_window",
            "res_model": "sale.dealsheet.wizard.confirm",
            "res_id": wizard_confirm_id.id,
            "view_type": "form",
            "view_mode": "form",
            "target": "new",
        }

    @api.multi
    def action_confirmed(self, reviewer_id):
        self.update({
            'state': 'confirmed',
            'presale_id': self.env.uid
        })

        subject = "%s Confirmed" % self.name
        body = '<br>'.join(("Customer: %s" % self.partner_id.name,
                            "Duration: %s" % self.duration,
                            "Currency: %s" % self.currency_id.name,
                            "Cost: %.2f" % self.cost,
                            "Revenue: %.2f" % self.revenue,
                            "Margin: %.2f%%" % self.margin))

        self.message_subscribe_users(reviewer_id.id, [1])
        self.message_post(subject=subject,
                          body=body,
                          subtype='mt_comment')

    @api.multi
    def action_validate(self):
        self.update({
            'state': 'validated',
            'reviewer_id': self.env.uid,
            'validated_date': fields.Datetime.now()
        })
        self._set_delivery_cost_defaults()

    def _set_delivery_cost_defaults(self):
        lines = self.env['sale.dealsheet.line'].search([
            ('dealsheet_id', '=', self.id),
        ])
        for l in lines:
            l.cost_delivery = l.cost

    @api.multi
    def action_refuse(self):
        wizard_refuse_model = self.env['sale.dealsheet.wizard.refuse']
        wizard_refuse_id = wizard_refuse_model.create({
            'dealsheet_id': self.id
        })
        return {
            "name": "Enter Reason",
            "type": "ir.actions.act_window",
            "res_model": "sale.dealsheet.wizard.refuse",
            "res_id": wizard_refuse_id.id,
            "view_type": "form",
            "view_mode": "form",
            "target": "new",
        }

    @api.multi
    def action_refused(self, reason):
        self.update({
            'state': 'refused',
            'reviewer_id': self.env.uid,
            'refused_date': fields.Datetime.now()
        })

        subject = "%s Refused" % self.name
        self.message_post(subject=subject,
                          body=reason,
                          subtype='mt_comment')

    @api.multi
    def action_reset_draft(self):
        self.ensure_one()
        self.update({
            'state': 'draft',
            'presale_id': False,
            'reviewer_id': False,
            'validated_date': False,
            'refused_date': False,
        })

    def action_procure(self):
        self.ensure_one()
        if self.env.user.company_id.id != self.company_id.id:
            raise UserError(
                _("Please change your current company (top right) to '%s'"
                  % self.company_id.name))
        grouped = self._get_procure_lines_grouped()
        for supplier_id, frequencies in grouped.iteritems():
            for frequency, lines in frequencies.iteritems():
                self._create_purchase_order(supplier_id, frequency, lines)
        return self.action_get_purchase_order_view()

    def _get_procure_lines_grouped(self):
        grouped = defaultdict(lambda: defaultdict(lambda: []))
        for l in self._get_procure_lines():
            grouped[l.supplier_id.id][l.frequency].append(l)
        return grouped

    def _get_procure_lines(self):
        return self.env['sale.dealsheet.line'].search([
            ('dealsheet_id', '=', self.id),
            ('supplier_id', '!=', False),
            ('purchase_order_line_id', '=', False),
        ])

    def _create_purchase_order(self, supplier_id, frequency, ds_lines):
        data = {
            'dealsheet_id': self.id,
            'company_id': self.company_id.id,
            'currency_id': self.currency_id.id,
            'partner_id': supplier_id,
        }
        if frequency:
            data.update({
                'supplier_invoicing_period': frequency,
                'subscr_date_start': self.commitment_date,
                'subscr_duration': self.duration,
                'continue_after_end': True,
            })
        order_id = self.env['purchase.order'].create(data.copy())
        order_id.onchange_partner_id()
        diff = self._get_onchange_diff(data, order_id)
        order_id.write(diff)
        for ds_line_id in ds_lines:
            self._create_purchase_order_line(order_id, ds_line_id)
        return order_id

    def _create_purchase_order_line(self, order_id, ds_line_id):
        data = {
            'order_id': order_id.id,
            'dealsheet_line_id': ds_line_id.id,
            'account_analytic_id': self.project_id.id,
            'name': ds_line_id.description,
            'date_planned': fields.Datetime.now(),
            'product_id': ds_line_id.product_id.id,
            'product_qty': ds_line_id.quantity,
            'product_uom': ds_line_id.product_id.uom_id.id,
            'price_unit': ds_line_id.cost_delivery,
        }
        order_line_id = self.env['purchase.order.line'].create(data.copy())
        order_line_id.onchange_product_id()
        diff = self._get_onchange_diff(data, order_line_id)
        order_line_id.write(diff)
        ds_line_id.purchase_order_line_id = order_line_id.id
        return order_line_id

    def _get_onchange_diff(self, data, record):
        diff = {}
        record_data = record.copy_data()[0]
        for key, value in data.iteritems():
            if value != record_data[key]:
                diff[key] = value
        return diff
