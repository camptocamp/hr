# -*- coding: utf-8 -*-
import logging

from odoo.http import request

from odoo import http
from utils import _response

_logger = logging.getLogger(__name__)


class PortalIntegrationController(http.Controller):
    partner_fields = [
        'signup_valid',
        'sale_warn',
        'sale_order_count',
        'invoice_warn',
        'purchase_order_count',
        'contact_address',
        'property_product_pricelist',
        'signup_url',
        'journal_item_count',
        'parent_name',
        'search_relation_date',
        'display_name',
        'opt_out',
        'title',
        'company_id',
        'commercial_company_name',
        'parent_id',
        'customer_payment_mode_id',
        'contracts_count',
        'employee',
        'supplier_invoice_count',
        'count_pending_changesets',
        'customer',
        'fax',
        'child_ids',
        'lead_id',
        'user_ids',
        'calendar_last_notif_ack',
        'unreconciled_aml_ids',
        'phonecall_count',
        'name',
        'debit_limit',
        'bso_companies',
        'signup_token',
        'contract_ids',
        'commercial_partner_id',
        'total_invoiced',
        'notify_email',
        'has_unreconciled_entries',
        'generate_lead',
        'currency_id',
        'street',
        'payment_next_action_date',
        'task_ids',
        'country_id',
        'tz_offset',
        'invoice_send_method',
        'relation_all_ids',
        'debit',
        'supplier',
        'ref',
        'email',
        'tz',
        'picking_warn',
        'street3',
        'city',
        'street2',
        'barcode',
        'changeset_ids',
        'opportunity_ids',
        'search_relation_partner_id',
        'active',
        'issued_total',
        'signup_expiration',
        'property_account_payable_id',
        'credit',
        'payment_next_action',
        'payment_note',
        'comment',
        'subscription_count',
        'purchase_warn',
        'color',
        'automatic_supplier_invoicing',
        'invoice_ids',
        'team_id',
        'mandate_count',
        'trust',
        'property_payment_term_id',
        'phonecall_ids',
        'user_id',
        'supplier_invoicing_period',
        'ref_company_ids',
        'email_formatted',
        'im_status',
        'last_website_so_id',
        'last_time_entries_checked',
        'type',
        'opportunity_count',
        'function',
        'picking_warn_msg',
        'zip',
        'relation_count',
        'payment_token_count',
        'activities_count',
        'phone',
        'search_relation_type_id',
        'payment_token_ids',
        'payment_responsible_id',
        'property_purchase_currency_id',
        'property_supplier_payment_term_id',
        'sale_order_ids',
        'total_due',
        'vat',
        'state_id',
        'invoice_warn_msg',
        'website',
        'valid_mandate_id',
        'company_type',
        'group_supplier_invoice',
        'signup_type',
        'property_account_receivable_id',
        'partner_share',
        'meeting_ids',
        'date',
        'self',
        'bank_account_count',
        'id',
        'property_account_position_id',
        'company_name',
        'search_relation_partner_category_id',
        'lastname',
        'property_stock_supplier',
        'supplier_invoicing_mode',
        'is_company',
        'bank_ids',
        'firstname',
        'write_date',
        'property_stock_customer',
        'category_id',
        'lang',
        'credit_limit',
        'meeting_count',
        'purchase_warn_msg',
        'mobile',
        'device_identity_ids',
        'sale_warn_msg',
        'supplier_payment_mode_id',
        'task_count']

    subscription_fields = [
        'project_count',
        'project_ids',
        'all_child_ids',
        'subscription_count',
        'company_id',
        'currency_id',
        'recurring_mandatory_lines',
        'date_next_invoice_period_start',
        'recurring_next_date',
        'duration',
        'customer_prior_notice',
        'partner_id',
        'date_cancelled',
        'description',
        'analytic_account_id',
        'asset_category_id',
        'uuid',
        'use_tasks',
        'date_start',
        'recurring_amount_tax',
        'id',
        'sale_order_count',
        'state',
        'recurring_option_lines',
        'debit',
        'recurring_total',
        'pricelist_id',
        'subscription_ids',
        'website_url',
        'old_ref',
        'recurring_inactive_lines',
        'recurring_amount_total',
        'code',
        'company_uom_id',
        'parent_ids',
        'credit',
        'period_total',
        'payment_mode_id',
        'write_date',
        'date',
        'payment_token_id',
        'user_id',
        'active',
        'display_name',
        'all_child_self_included_ids',
        'invoice_count',
        'name',
        'invoice_ids',
        'recurring_custom_lines',
        'immediate_child_ids',
        'recurring_interval',
        'automatic_renewal',
        'invoice_line_ids',
        'close_reason_id',
        'tag_ids',
        'line_ids',
        'recurring_rule_type',
        'balance',
        'template_id',
        'recurring_invoice_line_ids'
    ]

    invoice_fields = [
        'comment',
        'mandate_id',
        'date_due',
        'is_disputed',
        'dispute_line_ids',
        'partner_bank_id',
        'campaign_id',
        'company_id',
        'company_currency_id',
        'amount_total_company_signed',
        'payment_move_line_ids',
        'payments_widget',
        'mandate_required',
        'partner_id',
        'purchase_id',
        'display_name',
        'reference',
        'residual_company_signed',
        'amount_total_signed',
        'payment_mode_id',
        'journal_id',
        'id',
        'amount_tax',
        'state',
        'auto_invoice_id',
        'fiscal_position_id',
        'bank_account_required',
        'incoterms_id',
        'sent',
        'invoice_line_ids',
        'account_id',
        'payment_ids',
        'reconciled',
        'origin',
        'residual',
        'move_name',
        'reference_type',
        'date_invoice',
        'payment_term_id',
        'outstanding_credits_debits_widget',
        'write_date',
        'residual_signed',
        'date',
        'amount_untaxed',
        'auto_generated',
        'move_id',
        'amount_total',
        'amount_untaxed_signed',
        'currency_id',
        'refund_invoice_id',
        'name',
        'partner_shipping_id',
        'user_id',
        'payment_order_ok',
        'type',
        'team_id',
        'number',
        'tax_line_ids',
        'medium_id',
        'source_id',
        'has_outstanding',
        'commercial_partner_id']

    @http.route(
        '/api/account_by_ubersmith_client_id/<int:ubersmith_client_id>',
        type='http', auth='none')
    def get_account_by_ubersmith_client_id(self, ubersmith_client_id):
        partner = request.env['ubersmith.client'].sudo().search([
            ('client_id', '=', ubersmith_client_id),
        ]).odoo_partner_id
        res = self._get_account_info(partner)
        return _response(res)

    @http.route('/api/account_by_partner_id/<int:partner_id>',
                type='http', auth='none')
    def get_account_by_partner_id(self, partner_id):
        partner = request.env['res.partner'].sudo().browse(partner_id)
        res = self._get_account_info(partner)
        return _response(res)

    @staticmethod
    def _get_account_info(partner):
        account = partner.user_id
        if not account:
            return {}
        employee = request.env['hr.employee'].sudo().search([
            ('user_id', '=', account.id)
        ])
        return {
            'name': account.name,
            'email': account.partner_id.email,
            'mobile_phone': employee.mobile_phone,
            'work_phone': employee.work_phone
        }

    @http.route('/api/customers', type='http', auth='none')
    def get_customers(self, offset=0, limit=None):
        partners = request.env['res.partner'].sudo().search_read([
            ('customer', '=', True),
            ('is_company', '=', True),
        ], fields=self.partner_fields, offset=int(offset),
            limit=int(limit) if limit else None)
        return _response(partners)

    @http.route('/api/customers/<int:customer_id>', type='http', auth='none')
    def get_customer(self, customer_id):
        partners = request.env['res.partner'].sudo().search_read([
            ('customer', '=', True),
            ('is_company', '=', True),
            ('id', '=', customer_id),
            '|',
            ('active', '=', True),
            ('active', '=', False),
        ], fields=self.partner_fields)
        return _response(partners)

    @http.route('/api/contacts/<int:contact_id>', type='http', auth='none')
    def get_contact(self, contact_id):
        contacts = request.env['res.partner'].sudo().search_read([
            ('is_company', '=', False),
            ('id', '=', contact_id),
            '|',
            ('active', '=', True),
            ('active', '=', False),
        ], fields=self.partner_fields)
        return _response(contacts)

    @http.route('/api/contacts', type='http', auth='none')
    def get_contacts(self, parent_id=None, offset=0, limit=None):
        domain = [
            ('is_company', '=', False),
        ]
        if parent_id:
            domain.append(('parent_id', '=', int(parent_id)))
        contacts = request.env['res.partner'].sudo().search_read(
            domain, fields=self.partner_fields, offset=int(offset),
            limit=int(limit) if limit else None)
        return _response(contacts)

    @http.route('/api/partners/<int:partner_id>/image', type='http',
                auth='none')
    def get_partner_image(self, partner_id, image='all'):
        if image == 'all':
            fields = ['image', 'image_medium', 'image_small']
        else:
            fields = [image]
        partner = request.env['res.partner'].sudo().search_read([
            ('id', '=', partner_id),
            '|',
            ('active', '=', True),
            ('active', '=', False),
        ], fields=fields)
        return _response(partner)

    @http.route('/api/subscriptions', type='http', auth='none')
    def get_subscriptions(self, customer_id=None, offset=0, limit=None):
        sub_model = request.env['sale.subscription']
        sub_line_model = request.env['sale.subscription.line']
        domain = []
        if customer_id:
            domain.append(('partner_id', '=', int(customer_id)))
        subscriptions = sub_model.sudo().search_read(
            domain=domain, fields=self.subscription_fields, offset=int(offset),
            limit=int(limit) if limit else None)
        for subscription in subscriptions:
            line_ids = subscription['recurring_invoice_line_ids']
            line_records = sub_line_model.sudo().browse(line_ids)
            subscription['recurring_invoice_line_ids'] = line_records.read()
        return _response(subscriptions)

    @http.route('/api/subscriptions/<int:subscription_id>', type='http',
                auth='none')
    def get_subscription(self, subscription_id):
        sub_model = request.env['sale.subscription']
        sub_line_model = request.env['sale.subscription.line']
        subscription = sub_model.sudo().search_read([
            ('id', '=', subscription_id),
        ], fields=self.subscription_fields)
        if not subscription:
            return
        line_ids = subscription[0]['recurring_invoice_line_ids']
        line_records = sub_line_model.sudo().browse(line_ids)
        subscription[0]['recurring_invoice_line_ids'] = line_records.read()
        return _response(subscription[0])

    @http.route('/api/invoices', type='http', auth='none')
    def get_invoices(self, subscription_id=None, offset=0, limit=None):
        sub_model = request.env['sale.subscription']
        invoice_model = request.env['account.invoice']
        invoice_line_model = request.env['account.invoice.line']
        domain = []
        if subscription_id:
            subscription = sub_model.sudo().browse(int(subscription_id))
            domain.append(('name', '=', subscription.code))
        invoices = invoice_model.sudo().search_read(
            domain=domain, fields=self.invoice_fields, offset=int(offset),
            limit=int(limit) if limit else None)
        for invoice in invoices:
            lines_ids = invoice['invoice_line_ids']
            line_records = invoice_line_model.sudo().browse(lines_ids)
            invoice['invoice_line_ids'] = line_records.read()
        return _response(invoices)

    @http.route('/api/invoices/<int:invoice_id>', type='http', auth='none')
    def get_invoice(self, invoice_id):
        invoice_model = request.env['account.invoice']
        invoice_line_model = request.env['account.invoice.line']
        invoice = invoice_model.sudo().search_read([
            ('id', '=', invoice_id),
        ], fields=self.invoice_fields)
        if not invoice:
            return
        lines_ids = invoice[0]['invoice_line_ids']
        line_records = invoice_line_model.sudo().browse(lines_ids)
        invoice[0]['invoice_line_ids'] = line_records.read()
        return _response(invoice[0])

    @http.route('/api/invoices/<int:invoice_id>/pdf', type='http', auth='none')
    def get_invoice_pdf(self, invoice_id):
        pdf = request.env['report'].sudo().get_pdf([invoice_id],
                                                   'account.report_invoice')
        invoice = request.env['account.invoice'].sudo().browse(invoice_id)
        headers = [
            ('Content-Type', 'application/pdf'), ('Content-Length', len(pdf)),
            ('Content-Disposition',
             'attachment; filename=%s.pdf;' % invoice.number)
        ]
        return request.make_response(pdf, headers=headers)
