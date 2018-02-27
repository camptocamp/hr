from odoo import models, fields, api


class SaleDealsheet(models.Model):
    _name = 'sale.dealsheet'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'sale_order_id ASC'

    state = fields.Selection(
        string='Status',
        selection=[('draft', 'Draft'),
                   ('confirm', 'Confirmed'),
                   ('validate', 'Validated'),
                   ('refuse', 'Refused')],
        default='draft',
        track_visibility='always'
    )
    name = fields.Char(
        compute='compute_name',
        store=True
    )
    user_id = fields.Many2one(
        string='Salesperson',
        comodel_name='res.users',
        required=True
    )
    presale_id = fields.Many2one(
        string='Pre-Sale',
        comodel_name='res.users',
    )
    reviewer_id = fields.Many2one(
        string='Reviewer',
        comodel_name='res.users',
    )
    date_validated = fields.Datetime(
        string='Validated At'
    )
    date_refused = fields.Datetime(
        string='Refused At'
    )
    sale_order_id = fields.Many2one(
        string='Sale Order',
        comodel_name='sale.order',
        ondelete='cascade',
        required=True,
        readonly=True
    )
    partner_id = fields.Many2one(
        related='sale_order_id.partner_id',
        readonly=True,
        store=True
    )
    duration = fields.Integer(
        related='sale_order_id.duration',
        readonly=True,
        store=True
    )
    currency_id = fields.Many2one(
        related='sale_order_id.currency_id',
        readonly=True,
        store=True
    )
    compute_line = fields.One2many(
        string='Computed Lines',
        comodel_name='sale.dealsheet.line',
        inverse_name='dealsheet_id',
        compute='compute_compute_line',
        domain=[('is_cost', '=', False), ('is_recurring', '=', True)],
        context={'default_is_cost': False, 'default_is_recurring': True},
        store=True
    )
    cost_line = fields.One2many(
        string='Recurring Costs',
        comodel_name='sale.dealsheet.line',
        inverse_name='dealsheet_id',
        domain=[('is_cost', '=', True), ('is_recurring', '=', True)],
        context={'default_is_cost': True, 'default_is_recurring': True}
    )
    cost_upfront_line = fields.One2many(
        string='Non Recurring Costs',
        comodel_name='sale.dealsheet.line',
        inverse_name='dealsheet_id',
        domain=[('is_cost', '=', True), ('is_recurring', '=', False)],
        context={'default_is_cost': True, 'default_is_recurring': False}
    )
    cost_upfront = fields.Float(
        string='Non Recurring Cost',
        compute='compute_cost_upfront',
        store=True
    )
    price_upfront = fields.Float(
        string='Non Recurring Revenue',
        compute='compute_price_upfront',
        store=True
    )
    margin_upfront = fields.Float(
        string='Non Recurring Margin (%)',
        compute='compute_margin_upfront',
        store=True
    )
    cost = fields.Float(
        string='Recurring Cost',
        compute='compute_cost',
        store=True
    )
    price = fields.Float(
        string='Recurring Revenue',
        compute='compute_price',
        store=True
    )
    margin = fields.Float(
        string='Recurring Margin (%)',
        compute='compute_margin',
        store=True
    )
    cost_total = fields.Float(
        string='Total Cost',
        compute='compute_cost_total',
        store=True
    )
    price_total = fields.Float(
        string='Total Revenue',
        compute='compute_price_total',
        store=True
    )
    margin_total = fields.Float(
        string='Total Margin (%)',
        compute='compute_margin_total',
        store=True
    )
    summary = fields.One2many(
        string='Summary',
        comodel_name='sale.dealsheet.summary.line',
        inverse_name='dealsheet_id',
        default=lambda self: self.get_default_summary(),
        readonly=True
    )

    # DEFAULTS

    @api.model
    def get_default_summary(self):
        return [(0, 0, {'type': t}) for t in
                ('non_recurring', 'recurring', 'total')]

    # COMPUTES

    @api.depends('sale_order_id.name')
    def compute_name(self):
        for rec in self:
            rec.update({
                'name': "%s Dealsheet" % rec.sale_order_id.name
            })

    @api.depends('sale_order_id.order_line')
    def compute_compute_line(self):
        for rec in self:
            cost_lines = rec.cost_line + rec.cost_upfront_line
            compute_lines = [(4, cl.id, 0) for cl in cost_lines]

            order_lines = rec.sale_order_id.order_line
            exclude_order_lines = cost_lines.mapped('sale_order_line_id')

            for order_line in order_lines:
                if order_line in exclude_order_lines:
                    continue
                compute_lines += self.get_cost_lines(order_line)

            rec.update({
                'compute_line': compute_lines
            })

    @api.depends('cost_upfront_line.cost')
    def compute_cost_upfront(self):
        for rec in self:
            rec.update({
                'cost_upfront': sum(rec.mapped('cost_upfront_line.cost'))
            })

    @api.depends('sale_order_id.order_line.price_subtotal')
    def compute_price_upfront(self):
        for rec in self:
            rec.update({
                'price_upfront': sum(
                    l.price_subtotal for l in rec.sale_order_id.order_line
                    if not l.product_id.recurring_invoice)
            })

    @api.depends('cost_upfront', 'price_upfront')
    def compute_margin_upfront(self):
        for rec in self:
            rec.update({
                'margin_upfront': self.get_margin(rec.cost_upfront,
                                                  rec.price_upfront)
            })

    @api.depends('cost_line.cost')
    def compute_cost(self):
        for rec in self:
            rec.update({
                'cost': sum(rec.mapped('cost_line.cost'))
            })

    @api.depends('sale_order_id.order_line.price_subtotal')
    def compute_price(self):
        for rec in self:
            rec.update({
                'price': sum(
                    l.price_subtotal for l in rec.sale_order_id.order_line
                    if l.product_id.recurring_invoice)
            })

    @api.depends('cost', 'price')
    def compute_margin(self):
        for rec in self:
            rec.update({
                'margin': self.get_margin(rec.cost, rec.price)
            })

    @api.depends('cost', 'duration', 'cost_upfront')
    def compute_cost_total(self):
        for rec in self:
            rec.update({
                'cost_total': rec.cost * rec.duration + rec.cost_upfront
            })

    @api.depends('price', 'duration', 'price_upfront')
    def compute_price_total(self):
        for rec in self:
            rec.update({
                'price_total': rec.price * rec.duration + rec.price_upfront
            })

    @api.depends('cost_total', 'price_total')
    def compute_margin_total(self):
        for rec in self:
            rec.update({
                'margin_total': self.get_margin(rec.cost_total,
                                                rec.price_total)
            })

    # ACTIONS

    @api.multi
    def action_create(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "sale.dealsheet",
            "res_id": self.id,
            "view_type": "form",
            "view_mode": "form",
        }

    @api.multi
    def action_request(self):
        wizard_request_model = self.env['sale.dealsheet.wizard.request']
        wizard_request_id = wizard_request_model.sudo(self.user_id).create({
            'dealsheet_id': self.id
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
    def action_requested(self, presale_id):
        subject = "%s Requested" % self.name

        customer_str = "Customer: %s" % self.partner_id.name
        currency_str = "Currency: %s" % self.currency_id.name
        revenue_str = "Revenue: %.2f" % self.price_total

        body = '<br>'.join((customer_str, currency_str, revenue_str))

        self.message_subscribe_users(presale_id.id, [1])
        self.message_post(subject=subject,
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
            'state': 'confirm',
            'presale_id': self.env.uid
        })

        subject = "%s Confirmed" % self.name

        customer_str = "Customer: %s" % self.partner_id.name
        currency_str = "Currency: %s" % self.currency_id.name
        cost_str = "Cost: %.2f" % self.cost_total
        revenue_str = "Revenue: %.2f" % self.price_total
        margin_str = "Margin: %.2f%s" % (self.margin_total, '%')

        body = '<br>'.join(
            (customer_str, currency_str, cost_str, revenue_str, margin_str))

        self.message_subscribe_users(reviewer_id.id, [1])
        self.message_post(subject=subject,
                          body=body,
                          subtype='mt_comment')

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
            'state': 'refuse',
            'reviewer_id': self.env.uid,
            'date_refused': fields.Datetime.now()
        })

        subject = "%s Refused" % self.name
        self.message_post(subject=subject,
                          body=reason,
                          subtype='mt_comment')

    @api.multi
    def action_validate(self):
        self.update({
            'state': 'validate',
            'reviewer_id': self.env.uid,
            'date_validated': fields.Datetime.now()
        })

    def _load_win_action(self, act, **kw):
        act = self.env.ref(act)
        action = act.copy_data()[0]
        action['context'] = self._context.copy()
        action.update(kw)
        return action

    @api.multi
    def action_procure(self):
        action = self._load_win_action(
            'bso_dealsheet.act_wiz_sale_dealsheet_source')
        action['context']['default_dealsheet_id'] = self.id
        return action

    # TOOLS

    @api.model
    def get_cost_lines(self, order_line):
        if order_line.bundle_details_id.show_epl:
            cost_lines = self.get_lines_epl(order_line)
        elif order_line.bundle_details_id.show_bundle:
            cost_lines = self.get_lines_bundle(order_line)
        else:
            cost_lines = self.get_lines_product(order_line)
        return [(0, 0, l) for l in cost_lines]

    @api.model
    def get_lines_epl(self, order_line):
        bundle_details_id = order_line.bundle_details_id
        epl_bandwidth = bundle_details_id.epl_bandwidth
        epl_product_id = bundle_details_id.bundle_id
        lines = []
        for link in bundle_details_id.epl_route:
            data = self.get_line_data(
                epl_product_id.recurring_invoice,
                order_line,
                epl_product_id,
                link.link_id.name,
                order_line.product_uom_qty,
                link.cost_per_mb * epl_bandwidth,
                link.price_per_mb * epl_bandwidth
            )
            lines.append(data)
        for line in bundle_details_id.epl_products:
            if not line.quantity:
                continue
            data = self.get_line_data(
                line.product_id.recurring_invoice,
                order_line,
                line.product_id,
                line.description,
                line.quantity,
                line.cost,
                line.price
            )
            lines.append(data)
        return lines

    @api.model
    def get_lines_bundle(self, order_line):
        bundle_details_id = order_line.bundle_details_id
        bundle_qty = order_line.product_uom_qty
        lines = []
        for line in bundle_details_id.bundle_products:
            if not line.quantity:
                continue
            data = self.get_line_data(
                line.product_id.recurring_invoice,
                order_line,
                line.product_id,
                line.description,
                line.quantity * bundle_qty,
                line.cost,
                line.price
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
            order_line.product_id.standard_price,
            order_line.price_unit * order_line.product_uom_qty
        )
        return [data]

    @api.model
    def get_line_data(self, is_recurring, sale_order_line_id, product_id,
                      description, quantity, cost, price):
        return {'is_cost': True,
                'is_recurring': is_recurring,
                'sale_order_line_id': sale_order_line_id.id,
                'product_id': product_id.id,
                'description': description,
                'quantity': quantity,
                'cost': cost,
                'price': price}

    @api.model
    def get_margin(self, cost, revenue):
        if revenue:
            return (1 - cost / revenue) * 100
