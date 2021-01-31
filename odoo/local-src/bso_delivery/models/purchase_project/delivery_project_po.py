from collections import defaultdict

from odoo import models, fields, api

REPORT_EXTERNAL_ID = 'bso_delivery.email_template_send_factsheet'


class DeliveryProjectPO(models.Model):
    _name = 'delivery.project.po'
    _inherit = 'delivery.project'

    delivery_line_ids = fields.One2many(
        comodel_name='delivery.line.po',
        inverse_name='delivery_id'
    )
    description = fields.Char(
        string='Description'
    )

    network_engineer_ids = fields.Many2many(
        string='Network Engineer',
        comodel_name='res.users',
        relation='network_engineer_po_delivery_rel'
    )

    system_engineer_ids = fields.Many2many(
        string='System Engineer',
        comodel_name='res.users',
        relation='system_engineer_po_delivery_rel'
    )

    order_ids = fields.One2many(
        string='Purchases',
        comodel_name='purchase.order',
        inverse_name='delivery_project_id',
        required=True
    )
    order_ids_count = fields.Integer(
        string='Purchases',
        compute='compute_order_ids_count',
        store=True
    )
    usd_currency_id = fields.Many2one(
        string='USD Currency',
        comodel_name='res.currency',
        default=lambda self: self.usd_currency_id.browse(3),
        readonly=True,
    )
    amount_total_usd = fields.Monetary(
        string='Amount Total',
        compute='_compute_amount_total_usd',
        currency_field='usd_currency_id',
        store=True,
    )

    delivery_count = fields.Integer(
        string='Delivery',
        compute='compute_delivery_count',
        store=True
    )
    pickings_visibility = fields.Boolean(
        string='Picking Visible',
        compute='compute_pickings_visible'
    )
    pmo_director_id = fields.Many2one(
        comodel_name='hr.employee',
        default=lambda self: self.get_pmo_director()
    )

    @api.multi
    def get_pmo_director(self):
        return self.pmo_director_id.search(
            [('title', '=', 'PMO Director')], limit=1).id

    def many2one_fields(self):
        """ :return: list of tuples containing the many2one target fields
        and their ids
        """
        self_sudo = self.sudo()
        many2one_fields = list()
        if self_sudo:
            many2one_fields.append((self_sudo.id, self_sudo._name))
        for order in self.order_ids:
            many2one_fields.append((order.id, order._name))
        for picking_id in (self_sudo.order_ids.mapped('picking_ids') or []):
            many2one_fields.append((picking_id.id, picking_id._name))
        return many2one_fields

    @api.depends('order_ids')
    def compute_delivery_count(self):
        for rec in self:
            rec.delivery_count = len(rec.get_picking_ids())

    @api.multi
    def action_view_picking(self):
        action = self.env.ref('stock.action_picking_tree').read()[0]
        pick_ids = self.get_picking_ids()
        action['context'] = {}
        if len(pick_ids) > 1:
            action['domain'] = "[('id','in',[" + ','.join(
                map(str, pick_ids)) + "])]"
        if len(pick_ids) == 1:
            res = self.env.ref('stock.view_picking_form', False)
            action['views'] = [(res and res.id or False, 'form')]
            action['res_id'] = pick_ids and pick_ids[0] or False
        return action

    @api.multi
    def get_picking_ids(self):
        self.ensure_one()
        return self.order_ids.mapped('picking_ids').ids

    @api.depends('order_ids')
    def _compute_amount_total_usd(self):
        for rec in self:
            rec.amount_total_usd = sum(
                rec.order_ids.mapped('amount_total_usd'))

    @api.multi
    def write(self, vals):
        # prevent removing purchase.order from db
        unlink_operator = [
            i for i, order in enumerate(vals.get('order_ids', [[0]])) if
            order[0] == 2]
        for i in unlink_operator:
            vals['order_ids'][i][0] = 3
        res = super(DeliveryProjectPO, self).write(vals)
        for rec in self:
            if 'order_ids' in vals:
                rec.create_delivery_lines(rec.order_ids.ids)
        return res

    @api.model
    def create(self, vals):
        rec = super(DeliveryProjectPO, self.sudo()).create(vals)
        rec.create_delivery_lines(rec.order_ids.ids)
        template_ids = rec.get_jira_default_product_template_ids()
        rec.write({'name': '{0}{1:05d}'.format('PRJ', rec.id),
                   'jira_default_product_template_ids': [
                       (4, template_ids.ids)]
                   })
        rec.update_progress_rate_revenue()
        return rec

    @api.multi
    def create_delivery_lines(self, order_ids):
        self.ensure_one()
        self_sudo = self.sudo()
        line_ids = []
        for line in self_sudo.order_ids.browse(order_ids).mapped('order_line'):
            values = {
                'name': line.name,
                'delivery_id': self_sudo.id,
                'order_line_id': line.id,
            }
            line_ids.append(self_sudo.delivery_line_ids.create(values).id)
        self_sudo.write({'delivery_line_ids': [(6, 0, line_ids)]})

    @api.multi
    def compute_pickings_visible(self):
        for rec in self:
            rec.pickings_visibility = rec.delivery_count != 0

    @api.multi
    def action_purchases(self):
        return {
            'name': 'Purchases',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': self.order_ids._name,
            'domain': [('id', 'in', self.order_ids.ids)],
            'type': 'ir.actions.act_window',
            'target': 'current',
        }

    @api.depends('order_ids')
    def compute_order_ids_count(self):
        for rec in self:
            rec.order_ids_count = len(rec.order_ids)

    @api.multi
    def action_document_send(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = self.env.ref(REPORT_EXTERNAL_ID)
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
            ['&', ('default', '=', True), ('template_type', '=', 'purchase')])
        return template_ids

    @api.multi
    def update_progress_rate_revenue(self):
        self.ensure_one()
        self_sudo = self.sudo()

        if not self_sudo.order_ids.mapped('picking_ids'):
            self_sudo.progress_rate = 100
            return

        product_price = defaultdict(lambda: 0)
        qty = defaultdict(lambda: 0)

        for order in self_sudo.order_ids.mapped('order_line'):
            product_price[
                order.product_id.id
            ] += order.price_unit * order.product_qty
            qty[order.product_id.id] += order.product_qty

        average_price = {
            x: float(product_price[x]) / qty[x] if qty[x] != 0 else 0
            for x in product_price}

        def calc_price(op):
            return (average_price.get(op.product_id.id) * op.product_qty,
                    average_price.get(op.product_id.id) * op.qty_done)

        to_be_delivered, delivered = zip(*map(
            calc_price,
            self_sudo.order_ids.mapped('picking_ids').mapped(
                'pack_operation_product_ids')
        ))
        self_sudo.progress_rate = 100 * sum(delivered) / sum(
            to_be_delivered) if sum(to_be_delivered) else 100

    @api.multi
    def create_epic(self, client):
        epic = super(DeliveryProjectPO, self).create_epic(client)
        for line in self.delivery_line_ids:
            for template in line.jira_product_template_ids:
                self.clone_template_to_issue(
                    client, template.template_key, epic.key, line.name
                )
        return epic

    @api.multi
    def checklist_action(self):
        self.ensure_one()
        if not self.checklist_id:
            checklist_id = self.checklist_id.create(
                {'delivery_po_id': self.id})
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
