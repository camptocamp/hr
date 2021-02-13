from collections import OrderedDict

from odoo import models, fields, api, exceptions, _
from odoo.exceptions import AccessError


class DeliveryProject(models.AbstractModel):
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

    kickoff_date = fields.Date(
        string='Kick-off Date',
        track_visibility='onchange'
    )
    date_signed = fields.Date(
        string='Signed Date',
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
        string='Jira Templates',
        comodel_name='jira.product.template',
    )
    jira_project = fields.Many2one(
        comodel_name='jira.project',
        string='Project',
        default=lambda self: self.jira_project.search([], limit=1)
    )

    jira_key = fields.Char(
        string='JIRA Key',
        size=10,
        track_visibility='onchange',
    )

    progress_rate = fields.Float(
        string='Progress rate',
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
        related='checklist_id.'
                'network_diagram_docuemnt_matching_solution_to_deploy')
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

    is_officer = fields.Boolean(
        string='Is Officer',
        compute='_compute_is_officer'
    )

    @api.multi
    def _compute_is_officer(self):
        for rec in self:
            rec.is_officer = rec.env.user.has_group(
                'bso_delivery.group_delivery_officer'
            ) and not rec.env.user.has_group(
                'bso_delivery.group_delivery_manager')

    @api.multi
    def _compute_attachment_number(self):
        for rec in self:
            attachment_data = rec.env['ir.attachment'].read_group(
                rec._construct_many2fields_domain(),
                ['res_id'], ['res_id'])
            attachment = dict((data['res_id'], data['res_id_count'])
                              for data in attachment_data)
            rec.attachment_number = int(attachment.get(rec.id, 0))
            for field in rec.many2one_fields():
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
        self.jira_key = self.create_epic(client).key
        self.jira_url = self.env['jira.settings'].get(
        ).jira_url + '/browse/{}'.format(self.jira_key)
        try:
            account_id = self.get_assignee_jira_account_id(client)
            self.track_project()
            return client.assign_issue(self.jira_key, account_id)

        except Exception as e:
            raise AccessError(_(e))

    def _construct_many2fields_domain(self):
        """
        :return: list; domain based on the many2one fields and their ids.
        format of the returned domain ['|', '&' , A, B, '&', C, D]
        """
        many2one_fields = self.many2one_fields()
        domain = list()
        for res_id, model_name in many2one_fields:
            domain.append('|')
            domain.append('&')
            domain.append(('res_id', '=', res_id))
            domain.append(('res_model', '=', model_name))

        # domain.pop(-4) removes the the last unwanted '|' added by the for
        # loop from the domain
        domain.pop(-4)
        return domain

    @api.multi
    def many2one_fields(self):
        return []

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

    jira_url = fields.Char(
        string='JIRA Project URL',
    )

    @api.multi
    def action_open_jira_project(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': self.jira_url,
            'target': 'new'
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
        if 'description' in self.fields_get_keys():
            name = '{} {}'.format(self.name, self.description)
        else:
            name = self.name

        fields = {
            'project': {'id': client.project(self.jira_project.key).id},
            'issuetype': {'id': int(epictype_id)},
            'summary': name,
            'reporter': {
                'accountId': self.get_assignee_jira_account_id(client)}
        }
        parent_epic = client.create_issue(fields)
        # create default template tasks
        for template in self.jira_default_product_template_ids:
            self.clone_template_to_issue(client, template.template_key,
                                         parent_epic.key)
        return parent_epic

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
    def select_line_pop_up_action(self):
        view_id = self.env.ref('bso_delivery.delivery_choose_report_line')
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': self.id,
            'res_model': self._name,
            'views': [(view_id.id, 'form')],
            'view_id': view_id.id,
            'target': 'new',
        }

    @api.multi
    def get_assignee_jira_account_id(self, client):
        return client.user(self.user_id.email).account_id

    @api.model
    def create(self, vals):
        rec = super(DeliveryProject, self).create(vals)
        default_jira_project = self.env['jira.project'].search([], limit=1)
        values = {}
        if default_jira_project:
            values['jira_project'] = default_jira_project.id
        rec.write(values)
        return rec
