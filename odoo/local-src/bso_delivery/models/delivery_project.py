from collections import defaultdict
from math import ceil
import urlparse

from odoo import models, fields, api, exceptions, _


class DeliveryProject(models.Model):
    _name = 'delivery.project'
    _inherit = 'mail.thread'

    state = fields.Selection(
        string='Status',
        selection=[('draft', 'Draft'),
                   ('track', 'On-Track'),
                   ('hold', 'On-Hold'),
                   ('risk', 'At Risk'),
                   ('cancel', 'Cancelled'),
                   ('complete', 'Completed'),
                   ('canceled', 'Canceled')],
        default='draft',
        track_visibility='onchange',
    )
    name = fields.Char(
        string='Project Name',
        track_visibility='onchange',
    )
    user_id = fields.Many2one(
        string='SDM',
        comodel_name='res.users',
        track_visibility='onchange',
    )
    sale_order_id = fields.Many2one(
        string='Sale Order',
        comodel_name='sale.order',
        required=True
    )
    company_id = fields.Many2one(
        related='sale_order_id.company_id',
        readonly=True
    )
    customer_id = fields.Many2one(
        related='sale_order_id.partner_id',
        readonly=True
    )
    dealsheet_id = fields.Many2one(
        related='sale_order_id.dealsheet_id',
        readonly=True
    )
    currency_id = fields.Many2one(
        related='sale_order_id.currency_id',
        readonly=True
    )
    nrr = fields.Monetary(
        related='dealsheet_id.nrr',
        readonly=True
    )
    mrr = fields.Monetary(
        related='dealsheet_id.mrr',
        readonly=True
    )
    kickoff_date = fields.Date(
        string='Kick-off Date'
    )
    date_signed = fields.Date(
        string='Signed Date',
    )

    date_cease_requested = fields.Date(
        string='Requested Cease Date'
    )
    notes = fields.Text(
        string='Notes'
    )

    # ATTACHMENTS

    attachment_number = fields.Integer(
        string='Number of Attachments',
        compute='_compute_attachment_number'
    )

    backend_id = fields.Many2one(
        comodel_name='jira.backend',
        string='Jira Backend',
        default=lambda self: self.env['jira.backend'].search([], limit=1),
        readonly=True
    )

    gaia_template = fields.Many2one(
        comodel_name='gaia.template',
        string='Gaia template',
    )

    sync_issue_type_ids = fields.Many2many(
        comodel_name='jira.issue.type',
        string='Issue Levels to Synchronize',
        default=lambda self: self.env['jira.issue.type'].search([]).ids,
        domain='[("backend_id", "=", backend_id)]',
    )

    jira_key = fields.Char(
        string='JIRA Key',
        size=10,
        track_visibility='onchange',
    )

    analytic_account_id = fields.Many2one(
        string='Analyric Account',
        related='sale_order_id.project_id',
        readonly=True
    )

    project_project = fields.Many2one(
        string='Project',
        comodel_name='project.project',
        readonly=True
    )

    progress_rate = fields.Float(
        string='Progress rate',
        compute='_compute_progress_rate_revenue',
        store=True
    )
    delivery_count = fields.Integer(
        string='Delivery',
        related='sale_order_id.delivery_count'
    )

    @api.depends(
        'sale_order_id.picking_ids.pack_operation_product_ids.qty_done',
    )
    def _compute_progress_rate_revenue(self):
        for rec in self:
            product_price = defaultdict(lambda: 0)
            qty = defaultdict(lambda: 0)

            for order in rec.sale_order_id.order_line:
                product_price[order.product_id.id] += \
                    order.price_unit * order.product_uom_qty

                qty[order.product_id.id] += order.product_uom_qty

            average_price = {x: float(product_price[x]) / qty[x] for x in
                             product_price}
            prod = 0
            if not rec.sale_order_id.picking_ids:
                rec.progress_rate = 100
            else:
                for picking_id in rec.sale_order_id.picking_ids:
                    for pack_operation in \
                            picking_id.pack_operation_product_ids:
                        prod += pack_operation.qty_done * average_price.get(
                            picking_id.product_id.id, 0)
                total = rec.sale_order_id.amount_untaxed
                try:
                    rec.progress_rate = ceil(100 * prod / total)
                except ZeroDivisionError:
                    rec.progress_rate = 0

    @api.multi
    def _compute_attachment_number(self):
        attachment_data = self.env['ir.attachment'].read_group(
            self._construct_many2fields_domain(),
            ['res_id'], ['res_id'])
        attachment = dict((data['res_id'], data['res_id_count'])
                          for data in attachment_data)
        for rec in self:
            rec.attachment_number = int(attachment.get(rec.id, 0))
            for field in self.many2one_fields():
                rec.attachment_number += int(attachment.get(field[0], 0))

    @api.multi
    def action_get_attachment_view(self):
        self.ensure_one()
        res = self.env['ir.actions.act_window'].for_xml_id(
            'base',
            'action_attachment'
        )
        res['domain'] = self._construct_many2fields_domain()
        res['context'] = {'default_res_model': self._name,
                          'default_res_id': self.id}
        return res

    @api.constrains('jira_key')
    def check_jira_key(self):
        if self.backend_id.jira_key_exist(self.jira_key):
            raise exceptions.ValidationError(
                _('JIRA key {} is already in use'.format(self.jira_key))
            )
        for project in self:
            if not project.jira_key:
                continue
            valid = self.env['jira.project.project']._jira_key_valid
            if not valid(project.jira_key):
                raise exceptions.ValidationError(
                    _('{} is not a valid JIRA Key'.format(project.jira_key))
                )

    def _get_default_issues_types(self):
        return self.env['jira.issue.type'].search([]).ids

    def get_issue_type_ids(self):
        return self.sync_issue_type_ids.ids

    def create_project(self):
        jira_bind_ids = {'backend_id': self.backend_id.id,
                         'project_template': 'gaia',
                         'project_template_gaia': self.gaia_template.name,
                         'project_template_shared': False,
                         'sync_issue_type_ids': [
                             (6, 0, self.get_issue_type_ids())]
                         }
        data = {
            'user_id': self.user_id.id,
            'analytic_account_id': self.analytic_account_id.id,
            'partner_id': self.customer_id.id,
            'name': self.name,
            'company_id': self.company_id.id,
            'jira_key': self.jira_key,
            'jira_bind_ids': [(0, 0, jira_bind_ids)],
            'alias_id': False,
        }

        self.project_project = self.env['project.project'].create(data)
        self.update({
            'state': 'track',
            'delivery_line_ids': [(6, 0, self.create_delivery_lines())]
        })
        return True

    @api.multi
    def write(self, vals):
        self.project_project.write(vals)
        return super(DeliveryProject, self).write(vals)

    def _construct_many2fields_domain(self):
        """
        :return: list; domain based on the many2one fields and their ids
        format of the returned domain ['|', '&' , A, B, '&', C, D]
        """
        many2one_fields = self.many2one_fields()
        domain = list()
        for res_id, model_name in \
                many2one_fields:
            domain.append('|')
            domain.append('&')
            domain.append(('res_id', '=', res_id))
            domain.append(('res_model', '=', model_name))

        # domain.pop(-4) removes the the last unwanted '|' added by the for
        # loop from the domain
        domain.pop(-4)
        return domain

    def many2one_fields(self):
        """ :return: list of tuples containing the many2one target fields
        and their ids
        """
        many2one_fields = list()
        if self.id:
            many2one_fields.append((self.id, self._name))
        if self.sale_order_id.id:
            many2one_fields.append((self.sale_order_id.id, 'sale.order'))
        if self.dealsheet_id.id:
            many2one_fields.append((self.dealsheet_id.id, 'sale.dealsheet'))
        if self.project_project.id:
            many2one_fields.append((self.project_project.id, 'project.project')
                                   )
        for picking_id in self.dealsheet_id.purchase_order.picking_ids or []:
            many2one_fields.append((picking_id.id, 'stock.picking'))

        for picking_id in self.sale_order_id.picking_ids or []:
            many2one_fields.append((picking_id.id, 'stock.picking'))

        return many2one_fields

    @api.multi
    def hold_project(self):
        self.ensure_one()
        self.write({'state': 'hold'})

    @api.multi
    def risk_project(self):
        self.ensure_one()
        self.write({'state': 'risk'})

    @api.multi
    def cancel_project(self):
        self.ensure_one()
        self.write({'state': 'cancel'})

    @api.multi
    def track_project(self):
        self.ensure_one()
        self.write({'state': 'track'})

    @api.multi
    def complete_project(self):
        self.ensure_one()
        self.write({'state': 'complete'})

    @api.multi
    def draft_project(self):
        self.ensure_one()
        self.write({'state': 'draft'})

    delivery_line_ids = fields.One2many(
        comodel_name='delivery.project.line',
        inverse_name='delivery_id',
        string='Order Lines')

    def create_delivery_lines(self):
        line_ids = []
        for line in self.sale_order_id.order_line:
            line_ids.append(self.env['delivery.project.line'].create(
                {
                    'name': line.name,
                    'delivery_id': self.id,
                    'sale_order_line_id': line.id,
                }
            ).id)
        return line_ids

    jira_url = fields.Char(
        string='JIRA Project URL',
        compute='compute_jira_url',
        store=True
    )

    @api.depends('jira_key')
    def compute_jira_url(self):
        for project in self:
            jira_projects_url = self.env['res.api'].search(
                [('api_id', '=', 'jira_projects')]).endpoint
            project.jira_url = urlparse.urljoin(jira_projects_url,
                                                project.jira_key)

    @api.multi
    def action_open_jira_project(self):
        return {
            'type': 'ir.actions.act_url',
            'url': self.jira_url,
            'target': 'new'
        }

    @api.multi
    def action_view_deliveries(self):
        action = self.env.ref('stock.action_picking_tree_all').read()[0]

        pickings = self.mapped('sale_order_id.picking_ids')
        if len(pickings) > 1:
            action['domain'] = [('id', 'in', pickings.ids)]
        elif pickings:
            action['views'] = [
                (self.env.ref('stock.view_picking_form').id, 'form')]
            action['res_id'] = pickings.id
        return action
