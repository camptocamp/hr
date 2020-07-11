from odoo import models, fields, api
from datetime import datetime


class DeliveryChecklist(models.Model):
    _name = 'delivery.checklist'

    delivery_id = fields.Many2one(
        string='Delivery Project',
        comodel_name='delivery.project'
    )

    cutomer_signed_order_form_attached = fields.Char(
        string='Customer signed order form attached?')
    customer_contact_information_available = fields.Char(
        string='Customer contact information available?')
    network_diagram_docuement_attached = fields.Char(
        string='Network diagram - Document attached?')
    network_diagram_ends_specied = fields.Char(
        string='Network diagram - A-end/B-end specified?')
    network_diagram_cable_system_included = fields.Char(
        string='Network diagram - Cable system included?')
    network_diagram_docuemnt_matching_solution_to_deploy = fields.Char(
        string='Network diagram - Document matching solution to deploy?')
    odoo_sales_order_status_correct = fields.Char(
        string='Odoo sales - Order status correct?')
    odoo_sales_order_information_correct = fields.Char(
        string='Odoo sales - Order information correct?')
    odoo_sales_product_items_correct = fields.Char(
        string='Odoo sales - Product items correct?')
    odoo_dealsheet_status_correct = fields.Char(
        string='Odoo Dealsheet - Status correct?')
    odoo_dealsheet_line_items_correct = fields.Char(
        string='Odoo Dealsheet - Line items correct?')
    odoo_dealsheet_project_management_included = fields.Char(
        string='Odoo Dealsheet - Project Management included?')
    odoo_dealsheet_net_sys_engineer_time_included = fields.Char(
        string='Odoo Dealsheet - Network/System Engineer time included?')
    odoo_dealsheet_procider_specified = fields.Char(
        string='Odoo Dealsheet - Provider specified/correct?')
    odoo_dealsheetout_of_hours_activation_included = fields.Char(
        string='Odoo Dealsheet - Out of hours activation included?')
    admin_extra_notes = fields.Text(
        string='Extra Notes'
    )
    admin_exception_identified = fields.Boolean(
        string='Exception identified?'
    )
    # Order Forms
    ll_latency_available = fields.Char(
        string='LL - Latency available?'
    )
    ll_bandwidth_available = fields.Char(
        string='LL - Bandwidth available?'
    )
    ll_handoff_available = fields.Char(
        string='LL - Handoff (both end) available?'
    )
    ll_jumbo_frame_specified = fields.Char(
        string='LL - Jumbo frame (min 9200) specified?'
    )
    ll_protection_specified = fields.Char(
        string='LL - Protection/resiliency specified?'
    )
    ll_test_resulted_specified = fields.Char(
        string='LL - Test resulted specified/included?'
    )
    ll_delivery_lead_time_specified = fields.Char(
        string='LL - Delivery Lead Time specified?'
    )
    bb_latency_available = fields.Char(
        string='BB - Latency available?'
    )
    bb_bandwidth_available = fields.Char(
        string='BB - Bandiwidth available?'
    )
    bb_handoff_available = fields.Char(
        string='BB - Handoff (both end) available?'
    )
    bb_jumbo_frame_specified = fields.Char(
        string='BB - Jumbo frame (min 9200) specified?'
    )
    bb_protection_specified = fields.Char(
        string='BB - Protection/resiliency specified?'
    )
    bb_test_resulted_specified = fields.Char(
        string='BB - Test resulted specified/included?'
    )
    bb_delivery_lead_time_specified = fields.Char(
        string='BB - Delivery Lead Time specified?'
    )
    eq_delivery_lead_time_specified = fields.Char(
        string='Eq - Delivery Lead time specified?'
    )
    eq_qualtity_correct = fields.Char(
        string='Eq - Quantity correct?'
    )
    eq_support_included = fields.Char(
        string='Eq - Support included?'
    )
    eq_rack_mount_included = fields.Char(
        string='Eq - Rack mount included?'
    )
    eq_power_plug_type_specified = fields.Char(
        string='Eq - Power plug type specified/correct?'
    )
    eq_power_redundancy_specified = fields.Char(
        string='Eq - Power redundancy specified/correct?'
    )
    order_forms_extra_notes = fields.Text(
        string='Extra Notes'
    )
    order_forms_exception_identified = fields.Boolean(
        string='Exception identified?'
    )

    general = fields.Char(
        string='General'
    )
    port_capacity = fields.Char(
        string='Port capacity (1G/10G)'
    )
    handoff = fields.Char(
        string='Handoff'
    )

    ip_type = fields.Char(
        string='IP - Type (Static/Direct/BGP)'
    )
    ip_number_ip_address = fields.Char(
        string='IP - Number IP address (/xx)'
    )
    ip_ipv4_or_ipv6_required = fields.Char(
        string='IP - IPv4 or IPv6 required?'
    )
    ip_nb_port = fields.Char(
        string='IP - Nb Port'
    )
    ip_bgp_details = fields.Char(
        string='IP - BGP details (full view/ customer AS, prefixes),...'
    )
    ip_bso_platform = fields.Char(
        string='IP - Which BSO platform (Brocade, Extreme)?'
    )

    l2_routing_specificities = fields.Char(
        string='L2 - Routing specificities?'
    )
    l2_bso_platform_to_be_used = fields.Char(
        string='L2 - BSO platform to be used (Coriant, Extreme, other)?'
    )
    network_details_extra_notes = fields.Text(
        string='Extra Notes'
    )
    network_details_exception_identified = fields.Boolean(
        string='Exception identified?'
    )
    system_details_extra_notes = fields.Text(
        string='Extra Notes'
    )
    system_details_exception_identified = fields.Boolean(
        string='Exception identified?'
    )
    other_details_extra_notes = fields.Text(
        string='Extra Notes'
    )
    other_details_exception_identified = fields.Boolean(
        string='Exception identified?'
    )

    @api.multi
    def create(self, vals):
        self.delivery_id.update({'kickoff_date': datetime.now()})
        return super(DeliveryChecklist, self).create(vals)

    @api.multi
    def kickoff_action(self):
        self.delivery_id.update(
            {'kickoff_date': datetime.now(), 'state': 'inprogress'})

