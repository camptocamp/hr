from collections import defaultdict, OrderedDict
from odoo import models, fields, api, exceptions, _, SUPERUSER_ID


class DeliveryProject(models.Model):
    _name = 'delivery.project'
    _inherit = 'mail.thread'

    state = fields.Selection(
        string='Status',
        selection=[('kickoff', 'Kick-off'),
                   ('inprogress', 'In progress'),
                   ('hold', 'On-Hold'),
                   ('risk', 'At Risk'),
                   ('complete', 'Completed'),
                   ('cancel', 'Canceled')],
        default='kickoff',
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
    network_engineer_ids = fields.Many2many(
        string='Network Engineer',
        comodel_name='res.users',
        relation='delivery_net_eng_rel',
        track_visibility='onchange',
    )
    system_engineer_ids = fields.Many2many(
        string='System Engineer',
        comodel_name='res.users',
        relation='delivery_sys_eng_rel',
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
        string='Kick-off Date',
        track_visibility='onchange'
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

    jira_default_product_template_ids = fields.Many2many(
        comodel_name='jira.product.template',
        string='Jira Templates',
    )
    jira_project = fields.Many2one(
        comodel_name='jira.project',
        string='Project',
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
    progress_rate = fields.Float(
        string='Progress rate',
        compute='_compute_progress_rate_revenue',
        store=True
    )
    delivery_count = fields.Integer(
        string='Delivery',
        related='sale_order_id.delivery_count'
    )
    checklist_id = fields.Many2one(
        string='Checklist',
        comodel_name='delivery.checklist'
    )
    # checklist related fields
    cutomer_signed_order_form_attached = fields.Char(
        related='checklist_id.cutomer_signed_order_form_attached')
    customer_contact_information_available = fields.Char(
        related='checklist_id.customer_contact_information_available')
    network_diagram_docuement_attached = fields.Char(
        related='checklist_id.network_diagram_docuement_attached')
    network_diagram_ends_specied = fields.Char(
        related='checklist_id.network_diagram_ends_specied')
    network_diagram_cable_system_included = fields.Char(
        related='checklist_id.network_diagram_cable_system_included')
    network_diagram_docuemnt_matching_solution_to_deploy = fields.Char(
        related='checklist_id.network_diagram_docuemnt_'
                'matching_solution_to_deploy')
    odoo_sales_order_status_correct = fields.Char(
        related='checklist_id.odoo_sales_order_status_correct')
    odoo_sales_order_information_correct = fields.Char(
        related='checklist_id.odoo_sales_order_information_correct')
    odoo_sales_product_items_correct = fields.Char(
        related='checklist_id.odoo_sales_product_items_correct')
    odoo_dealsheet_status_correct = fields.Char(
        related='checklist_id.odoo_dealsheet_status_correct')
    odoo_dealsheet_line_items_correct = fields.Char(
        related='checklist_id.odoo_dealsheet_line_items_correct')
    odoo_dealsheet_project_management_included = fields.Char(
        related='checklist_id.odoo_dealsheet_project_management_included')
    odoo_dealsheet_net_sys_engineer_time_included = fields.Char(
        related='checklist_id.odoo_dealsheet_net_sys_engineer_time_included')
    odoo_dealsheet_procider_specified = fields.Char(
        related='checklist_id.odoo_dealsheet_procider_specified')
    odoo_dealsheetout_of_hours_activation_included = fields.Char(
        related='checklist_id.odoo_dealsheetout_of_hours_activation_included')
    admin_extra_notes = fields.Text(
        related='checklist_id.admin_extra_notes')
    admin_exception_identified = fields.Boolean(
        related='checklist_id.admin_exception_identified')
    # Order Forms
    ll_latency_available = fields.Char(
        related='checklist_id.ll_latency_available')
    ll_bandwidth_available = fields.Char(
        related='checklist_id.ll_bandwidth_available'
    )
    ll_handoff_available = fields.Char(
        related='checklist_id.ll_handoff_available'
    )
    ll_jumbo_frame_specified = fields.Char(
        related='checklist_id.ll_jumbo_frame_specified')
    ll_protection_specified = fields.Char(
        related='checklist_id.ll_protection_specified'
    )
    ll_test_resulted_specified = fields.Char(
        related='checklist_id.ll_test_resulted_specified'
    )
    ll_delivery_lead_time_specified = fields.Char(
        related='checklist_id.ll_delivery_lead_time_specified'
    )
    bb_latency_available = fields.Char(
        related='checklist_id.bb_latency_available')
    bb_bandwidth_available = fields.Char(
        related='checklist_id.bb_bandwidth_available'
    )
    bb_handoff_available = fields.Char(
        related='checklist_id.bb_handoff_available')
    bb_jumbo_frame_specified = fields.Char(
        related='checklist_id.bb_jumbo_frame_specified')
    bb_protection_specified = fields.Char(
        related='checklist_id.bb_protection_specified'
    )
    bb_test_resulted_specified = fields.Char(
        related='checklist_id.bb_test_resulted_specified')
    bb_delivery_lead_time_specified = fields.Char(
        related='checklist_id.bb_delivery_lead_time_specified')
    eq_delivery_lead_time_specified = fields.Char(
        related='checklist_id.eq_delivery_lead_time_specified')
    eq_qualtity_correct = fields.Char(
        related='checklist_id.eq_qualtity_correct')
    eq_support_included = fields.Char(
        related='checklist_id.eq_support_included')
    eq_rack_mount_included = fields.Char(
        related='checklist_id.eq_rack_mount_included')
    eq_power_plug_type_specified = fields.Char(
        related='checklist_id.eq_power_plug_type_specified')
    eq_power_redundancy_specified = fields.Char(
        related='checklist_id.eq_power_redundancy_specified')
    order_forms_extra_notes = fields.Text(
        related='checklist_id.order_forms_extra_notes')
    order_forms_exception_identified = fields.Boolean(
        related='checklist_id.order_forms_exception_identified')

    general = fields.Char(
        related='checklist_id.general')
    port_capacity = fields.Char(
        related='checklist_id.port_capacity'
    )
    handoff = fields.Char(
        related='checklist_id.handoff')

    ip_type = fields.Char(
        related='checklist_id.ip_type')
    ip_number_ip_address = fields.Char(
        related='checklist_id.ip_number_ip_address')
    ip_ipv4_or_ipv6_required = fields.Char(
        related='checklist_id.ip_ipv4_or_ipv6_required')
    ip_nb_port = fields.Char(
        related='checklist_id.ip_nb_port'
    )
    ip_bgp_details = fields.Char(
        related='checklist_id.ip_bgp_details')
    ip_bso_platform = fields.Char(
        related='checklist_id.ip_bso_platform')
    l2_routing_specificities = fields.Char(
        related='checklist_id.l2_routing_specificities')
    l2_bso_platform_to_be_used = fields.Char(
        related='checklist_id.l2_bso_platform_to_be_used')
    network_details_extra_notes = fields.Text(
        related='checklist_id.network_details_extra_notes')
    network_details_exception_identified = fields.Boolean(
        related='checklist_id.network_details_exception_identified')
    system_details_extra_notes = fields.Text(
        related='checklist_id.system_details_extra_notes')
    system_details_exception_identified = fields.Boolean(
        related='checklist_id.system_details_exception_identified')
    other_details_extra_notes = fields.Text(
        related='checklist_id.other_details_extra_notes')
    other_details_exception_identified = fields.Boolean(
        related='checklist_id.other_details_exception_identified')

    display_forecasted_date = fields.Date(
        string='Forecasted Date',
        compute='compute_display_forecasted_date',
        store=True
    )
    pickings_visibility = fields.Boolean(
        string='Picking Visible',
        compute='compute_pickings_visible'
    )

    @api.depends(
        'sale_order_id.picking_ids.pack_operation_product_ids.qty_done',
    )
    def _compute_progress_rate_revenue(self):
        for rec in self:
            product_price = defaultdict(lambda: 0)
            qty = defaultdict(lambda: 0)

            for order in rec.sale_order_id.order_line:
                product_price[
                    order.product_id.id
                ] += order.price_unit * order.product_uom_qty
                qty[order.product_id.id] += order.product_uom_qty

            average_price = {
                x: float(product_price[x]) / qty[x] if qty[x] != 0 else 0
                for x in product_price}

            if not rec.sale_order_id.picking_ids:
                rec.progress_rate = 100
                continue
            to_be_delivered, delivered = zip(*[
                (average_price.get(op.product_id.id) * op.product_qty,
                 average_price.get(op.product_id.id) * op.qty_done)
                for op in rec.sale_order_id.picking_ids.mapped(
                    'pack_operation_product_ids')])

            rec.progress_rate = 100 * sum(delivered) / sum(
                to_be_delivered) if sum(to_be_delivered) else 100

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

    @api.multi
    def export_project(self):
        self.ensure_one()
        client = self.get_jira_api_client()
        self.jira_key = self.create_epic(client)
        self.jira_url = self.env['jira.settings'].get(
        ).jira_url + '/browse/{}'.format(self.jira_key)
        try:
            account_id = self.get_assignee_jira_account_id(client)
            self.track_project()
            return client.assign_issue(self.jira_key, account_id)

        except Exception as e:
            raise exceptions.AccessError(_(e))

    def _construct_many2fields_domain(self):
        """
        :return: list; domain based on the many2one fields and their ids.
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
        self.write({'state': 'inprogress'})

    @api.multi
    def complete_project(self):
        self.ensure_one()
        self.write({'state': 'complete'})

    @api.multi
    def trigger_reset_to_draft(self):
        self.ensure_one()
        return self.env['pop.up.message'].show({
            'name': 'Confirm Deletion',
            'description': 'Are you sure you want to permanently remove the '
                           'corresponding Epic and its subtasks?'})

    @api.multi
    def _action_ok(self):
        return self.draft_project()

    @api.multi
    def draft_project(self):
        client = self.get_jira_api_client()
        children = self.get_children_keys(client, self.jira_key)
        for tupl in children.items()[::-1]:
            for key in tupl[1]:
                client.delete_issue(key)
            client.delete_issue(tupl[0])
        client.delete_issue(self.jira_key)
        self.jira_key = False
        self.state = 'kickoff'

    delivery_line_ids = fields.One2many(
        comodel_name='delivery.project.line',
        inverse_name='delivery_id',
        string='Order Lines')

    jira_url = fields.Char(
        string='JIRA Project URL',
    )

    @api.multi
    def get_delivery_lines(self):
        line_ids = []
        for line in self.sale_order_id.order_line:
            line_ids.append(self.env['delivery.project.line'].create(
                {
                    'name': line.name,
                    'delivery_id': self.id,
                    'order_line_id': line.id,
                }
            ).id)
        return line_ids

    @api.model
    def create(self, vals):
        rec = super(DeliveryProject, self).create(vals)
        line_ids = rec.get_delivery_lines()
        rec.write({
            'delivery_line_ids': [(6, 0, line_ids)]
        })
        template_ids = self.get_jira_default_product_template_ids()
        rec.write({
            'jira_default_product_template_ids': [(6, 0, template_ids.ids)],
            'jira_project': self.env['jira.project'].search([])[0].id
        })
        return rec

    @api.multi
    def action_open_jira_project(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': self.jira_url,
            'target': 'new'
        }

    @api.multi
    def action_view_deliveries(self):
        return self.sale_order_id.action_view_delivery()

    @api.multi
    def checklist_action(self):
        self.ensure_one()
        if not self.checklist_id:
            checklist_id = self.checklist_id.create({'delivery_id': self.id})
            self.write({'checklist_id': checklist_id.id})
        return {
            'type': 'ir.actions.act_window',
            'name': 'Kick-off checklist',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': self.checklist_id._name,
            'res_id': self.checklist_id.id,
            'views': [
                (self.env.ref('bso_delivery.checklist_form_view').id, 'form')],
            'target': 'new',
        }

    @api.multi
    def create_epic(self, client):
        # creating project epic
        epictype_id = None
        for issuetype in client.project(self.jira_project.key).issueTypes:
            if issuetype.name == 'Epic':
                epictype_id = issuetype.id
                break

        if not epictype_id:
            raise exceptions.ValidationError(
                _(
                    'Make sure the issue types in the template project are '
                    'identical to those in your target project')
            )
        fields = {
            'project': {'id': client.project(self.jira_project.key).id},
            'issuetype': {'id': int(epictype_id)},
            'summary': self.name,
            'reporter': {
                'accountId': self.get_assignee_jira_account_id(client)}
        }
        parent_epic = client.create_issue(fields)
        # create default template tasks
        for template in self.jira_default_product_template_ids:
            self.clone_template_to_issue(client, template.template_key,
                                         parent_epic.key)
        for line in self.delivery_line_ids:
            for template in line.jira_product_template_ids:
                self.clone_template_to_issue(
                    client, template.template_key, parent_epic.key, line.name
                )
        return parent_epic.key

    def clone_template_to_issue(self, client, template_key, parent_key,
                                issue_name=''):
        children_dict = self.get_children_keys(
            client, template_key, OrderedDict())
        if not children_dict:
            fields = self.get_issue_fields(
                client, template_key, issue_name)
            fields['parent'] = {'key': parent_key}
            client.create_issue(fields)
        for key in children_dict:
            fields = self.get_issue_fields(client, key, issue_name)
            fields['parent'] = {'key': parent_key}
            issue = client.create_issue(fields)
            for value in children_dict[key][::-1]:
                fields = self.get_issue_fields(client, value, issue_name)
                fields['parent'] = {'key': issue.key}
                client.create_issue(fields)

    def get_issue_fields(self, client, issue_key, issue_name):
        issue = client.issue(issue_key)
        for issuetype in client.project(self.jira_project.key).issueTypes:
            if issuetype.name == issue.fields.issuetype.get('name'):
                issuetype_id = issuetype.id
                break
        if not issuetype_id:
            raise exceptions.ValidationError(_(
                'Issue type not found, Make sure all the issue types in the '
                'template are as well in your target project'))

        fields = {
            'project': {'id': client.project(self.jira_project.key).id},
            'issuetype': {
                'id': issuetype_id
            },
            'summary': self.name if issue.fields.issuetype.get(
                'name') == 'Epic' else issue.fields.summary,
            'description': issue.fields.description
        }
        if issue.fields.issuetype.get('name') == 'Epic':
            fields['summary'] = self.name
        else:
            fields['summary'] = issue.fields.summary
            if issue_name:
                fields['summary'] = issue.fields.summary
        fields['assignee'] = {
            'accountId': self.get_assignee_jira_account_id(client)}
        fields['reporter'] = {
            'accountId': self.get_assignee_jira_account_id(client)}
        return fields

    @api.multi
    def get_jira_api_client(self):
        return self.env['jira.api']

    def get_children_keys(self, client, issue_key, children=OrderedDict()):
        """
        :param children: OrderDict
        :param client: jira api client
        :param issue_key: top level issue key
        :return: a hierarchy graph of issues within the issue epi_key
        e.g.
        {'parent': ['child1', 'child2'],
        'child1': ['child11', 'child12'],
        'child2':['child21',],
        'child11': ['child111']
        }
        """
        issue = client.issue(issue_key)
        immediate_children = self.get_immediate_children_keys(client,
                                                              issue_key)
        if immediate_children:
            children[issue.key] = immediate_children
        for child_key in immediate_children:
            self.get_children_keys(client, child_key, children)
        return children

    def get_immediate_children_keys(self, client, issue_key):
        jql = 'parent=%s' % issue_key
        ls = client.search_issues(jql)
        if not ls:
            return []
        return [child.key for child in ls]

    @api.multi
    def action_handover_send(self):
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
    def select_line_pop_up_action(self):
        self.ensure_one()
        view_id = self.env.ref(
            'bso_delivery.delivery_project_form_select_lines').id
        context = {'form_view_initial_mode': 'edit'}
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': self._name,
            'res_id': self.id,
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'target': 'new',
            'context': context
        }

    @api.multi
    def get_jira_default_product_template_ids(self):
        template_ids = self.env['jira.product.template'].search(
            [('default', '=', True)])
        return template_ids

    @api.multi
    def get_assignee_jira_account_id(self, client):
        return client.user(self.user_id.email).account_id

    @api.depends('delivery_line_ids.date_forecasted')
    def compute_display_forecasted_date(self):
        for rec in self:
            dates = rec.delivery_line_ids.mapped('date_forecasted')
            rec.display_forecasted_date = max(dates) if dates else False

    @api.model
    def compute_pickings_visible(self):
        for rec in self:
            uid = self.env.context.get('uid')
            rec.pickings_visibility = rec.company_id == rec.user_id.browse(
                uid).company_id if uid != SUPERUSER_ID else True
