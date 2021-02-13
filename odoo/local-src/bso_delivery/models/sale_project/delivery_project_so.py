from collections import defaultdict

from odoo import models, fields, api


class DeliveryProjectSO(models.Model):
    _name = 'delivery.project.so'
    _inherit = 'delivery.project'

    delivery_line_ids = fields.One2many(
        comodel_name='delivery.line.so',
        inverse_name='delivery_id'
    )
    network_engineer_ids = fields.Many2many(
        string='Network Engineer',
        comodel_name='res.users',
        relation='network_engineer_so_delivery_rel'
    )

    system_engineer_ids = fields.Many2many(
        string='System Engineer',
        comodel_name='res.users',
        relation='system_engineer_so_delivery_rel'
    )
    order_id = fields.Many2one(
        string='Sale Order',
        comodel_name='sale.order',
        required=True
    )
    company_id = fields.Many2one(
        related='order_id.company_id',
        readonly=True,
        store=True
    )
    customer_id = fields.Many2one(
        related='order_id.partner_id',
        readonly=True,
        store=True
    )
    dealsheet_id = fields.Many2one(
        related='order_id.dealsheet_id',
        readonly=True,
        store=True
    )
    currency_id = fields.Many2one(
        related='order_id.currency_id',
        readonly=True,
        store=True
    )
    analytic_account_id = fields.Many2one(
        string='Analytic Account',
        related='order_id.project_id',
        readonly=True,
        store=True
    )
    delivery_count = fields.Integer(
        string='Delivery',
        related='order_id.delivery_count'
    )
    nrr = fields.Monetary(
        related='dealsheet_id.nrr',
        readonly=True
    )
    mrr = fields.Monetary(
        related='dealsheet_id.mrr',
        readonly=True
    )
    pickings_visibility = fields.Boolean(
        string='Picking Visible',
        compute='compute_pickings_visible'
    )
    display_forecasted_date = fields.Date(
        string='Forecasted Date',
        compute='compute_display_forecasted_date',
        store=True
    )
    display_sla_date = fields.Date(
        string='SLA Date',
        compute='compute_display_sla_date',
        store=True
    )

    def many2one_fields(self):
        """ :return: list of tuples containing the many2one target fields
        and their ids
        """
        self_sudo = self.sudo()
        many2one_fields = list()
        if self_sudo:
            many2one_fields.append((self_sudo.id, self_sudo._name))
        if self_sudo.order_id:
            many2one_fields.append(
                (self.order_id.id, self_sudo.order_id._name))
        if self_sudo.dealsheet_id:
            many2one_fields.append(
                (self_sudo.dealsheet_id.id, self_sudo.dealsheet_id._name))
        for picking_id in self_sudo.order_id.picking_ids or []:
            many2one_fields.append((picking_id.id, 'stock.picking'))

        return many2one_fields

    @api.multi
    def get_delivery_lines(self):
        line_ids = []
        for line in self.order_id.order_line:
            line_ids.append(self.env['delivery.line.so'].create(
                {
                    'name': line.name,
                    'delivery_id': self.id,
                    'order_line_id': line.id,
                }
            ).id)
        return line_ids

    @api.model
    def create(self, vals):
        rec = super(DeliveryProjectSO, self).create(vals)
        rec.update_progress_rate_revenue()
        line_ids = rec.get_delivery_lines()
        template_ids = self.get_jira_default_product_template_ids()
        values = {
            'jira_default_product_template_ids': [
                (4, template_ids.ids)],
            'delivery_line_ids': [(6, 0, line_ids)]
        }
        rec.write(values)
        return rec

    @api.multi
    def action_view_picking(self):
        return self.order_id.action_view_delivery()

    @api.multi
    def update_progress_rate_revenue(self):
        self.ensure_one()
        self_sudo = self.sudo()

        if not self_sudo.order_id.picking_ids:
            self_sudo.progress_rate = 100
            return

        product_price = defaultdict(lambda: 0)
        qty = defaultdict(lambda: 0)

        for order in self_sudo.order_id.order_line:
            product_price[
                order.product_id.id
            ] += order.price_unit * order.product_uom_qty
            qty[order.product_id.id] += order.product_uom_qty

        average_price = {
            x: float(product_price[x]) / qty[x] if qty[x] != 0 else 0
            for x in product_price}

        def calc_price(op):
            return (average_price.get(op.product_id.id) * op.product_qty,
                    average_price.get(op.product_id.id) * op.qty_done)

        to_be_delivered, delivered = zip(*map(
            calc_price,
            self_sudo.order_id.picking_ids.mapped(
                'pack_operation_product_ids')
        ))
        self_sudo.progress_rate = 100 * sum(delivered) / sum(
            to_be_delivered) if sum(to_be_delivered) else 100

    @api.multi
    def compute_pickings_visible(self):
        for rec in self:
            rec.pickings_visibility = rec.company_id == rec.user_id.browse(
                self.env.uid).company_id or rec.delivery_count == 0

    @api.multi
    def action_document_send(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = self.env.ref(
                'bso_delivery.email_template_send_handover')
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(
                'mail',
                'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = {
            'default_model': self._name,
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id.id,
            'default_composition_mode': 'comment',
        }
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    @api.multi
    def get_jira_default_product_template_ids(self):
        template_ids = self.env['jira.product.template'].search(
            ['&', ('default', '=', True), ('template_type', '=', 'sale')])
        return template_ids

    @api.multi
    def create_epic(self, client):
        epic = super(DeliveryProjectSO, self).create_epic(client)
        for line in self.delivery_line_ids:
            for template in line.jira_product_template_ids:
                self.clone_template_to_issue(
                    client, template.template_key, epic.key, line.name
                )
        return epic

    @api.depends('delivery_line_ids.date_forecasted')
    def compute_display_forecasted_date(self):
        for rec in self:
            rec.display_forecasted_date = min(
                rec.delivery_line_ids.mapped('date_forecasted'))

    @api.depends('delivery_line_ids.date_sla')
    def compute_display_sla_date(self):
        for rec in self:
            sla_dates = rec.delivery_line_ids.mapped('date_sla')
            if sla_dates:
                rec.display_sla_date = min(sla_dates)

    @api.multi
    def checklist_action(self):
        self.ensure_one()
        if not self.checklist_id:
            checklist_id = self.checklist_id.create(
                {'delivery_so_id': self.id})
            self.write({'checklist_id': checklist_id.id})
        return {
            'type': 'ir.actions.act_window',
            'name': 'Kick-off checklist',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': self.checklist_id._name,
            'res_id': self.checklist_id.id,
            'views': [
                (self.env.ref('bso_delivery.checklist_form_view').id,
                 'form')],
            'target': 'new',
        }
