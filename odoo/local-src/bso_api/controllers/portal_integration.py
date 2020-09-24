# -*- coding: utf-8 -*-
import logging

from odoo.http import request

from odoo import http
from utils import _response

_logger = logging.getLogger(__name__)


class PortalIntegrationController(http.Controller):

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
        fields = self._remove_images()
        partners = request.env['res.partner'].sudo().search_read([
            ('customer', '=', True),
            ('is_company', '=', True),
        ], fields=fields, offset=int(offset),
            limit=int(limit) if limit else None)
        return _response(partners)

    @http.route('/api/customer/<int:customer_id>', type='http', auth='none')
    def get_customer(self, customer_id):
        fields = self._remove_images()
        partners = request.env['res.partner'].sudo().search_read([
            ('customer', '=', True),
            ('is_company', '=', True),
            ('id', '=', customer_id),
            '|',
            ('active', '=', True),
            ('active', '=', False),
        ], fields=fields)
        return _response(partners)

    @staticmethod
    def _remove_images():
        fields = request.env['res.partner'].fields_get().keys()
        fields.remove('image')
        fields.remove('image_medium')
        fields.remove('image_small')
        return fields

    @http.route('/api/contacts/<int:customer_id>', type='http', auth='none')
    def get_contacts(self, customer_id, offset=0, limit=None):
        fields = self._remove_images()
        contacts = request.env['res.partner'].sudo().search_read([
            ('is_company', '=', False),
            ('parent_id', '=', customer_id)
        ], fields=fields, offset=int(offset),
            limit=int(limit) if limit else None)
        return _response(contacts)

    @http.route('/api/contact/<int:contact_id>', type='http', auth='none')
    def get_contact(self, contact_id):
        fields = self._remove_images()
        contacts = request.env['res.partner'].sudo().search_read([
            ('is_company', '=', False),
            ('id', '=', contact_id),
            '|',
            ('active', '=', True),
            ('active', '=', False),
        ], fields=fields)
        return _response(contacts)

    @http.route('/api/partner/image/<int:partner_id>', type='http',
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

    @http.route('/api/subscriptions/<int:customer_id>', type='http',
                auth='none')
    def get_subscriptions(self, customer_id, offset=0, limit=None):
        sub_model = request.env['sale.subscription']
        sub_line_model = request.env['sale.subscription.line']
        fields = sub_model.fields_get().keys()
        fields.remove('immediate_child_subscription_count')
        subscriptions = sub_model.sudo().search_read([
            ('partner_id', '=', customer_id)
        ], fields=fields, offset=int(offset),
            limit=int(limit) if limit else None)
        for subscription in subscriptions:
            line_ids = subscription['recurring_invoice_line_ids']
            line_records = sub_line_model.sudo().browse(line_ids)
            subscription['recurring_invoice_line_ids'] = line_records.read()
        return _response(subscriptions)

    @http.route('/api/subscription/<int:subscription_id>', type='http',
                auth='none')
    def get_subscription(self, subscription_id):
        sub_model = request.env['sale.subscription']
        sub_line_model = request.env['sale.subscription.line']
        fields = sub_model.fields_get().keys()
        fields.remove('immediate_child_subscription_count')
        subscription = sub_model.sudo().search_read([
            ('id', '=', subscription_id),
            '|',
            ('active', '=', True),
            ('active', '=', False),
        ], fields=fields)
        if not subscription:
            return
        line_ids = subscription[0]['recurring_invoice_line_ids']
        line_records = sub_line_model.sudo().browse(line_ids)
        subscription[0]['recurring_invoice_line_ids'] = line_records.read()
        return _response(subscription[0])

    @http.route('/api/invoices/<int:subscription_id>', type='http',
                auth='none')
    def get_invoices(self, subscription_id, offset=0, limit=None):
        sub_model = request.env['sale.subscription']
        invoice_model = request.env['account.invoice']
        invoice_line_model = request.env['account.invoice.line']
        subscription = sub_model.sudo().browse(
            subscription_id)
        invoices = invoice_model.sudo().search_read([
            ('name', '=', subscription.code),
        ], offset=int(offset), limit=int(limit) if limit else None)
        for invoice in invoices:
            lines_ids = invoice['invoice_line_ids']
            line_records = invoice_line_model.sudo().browse(lines_ids)
            invoice['invoice_line_ids'] = line_records.read()
        return _response(invoices)

    @http.route('/api/invoice_pdf/<int:invoice_id>', type='http',
                auth='none')
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
