# -*- coding: utf-8 -*-
import json
import logging

import werkzeug
from odoo.http import request

from odoo import http

_logger = logging.getLogger(__name__)


class AccountManagerController(http.Controller):

    @http.route(
        '/api/account_by_ubersmith_client_id/<int:ubersmith_client_id>',
        type='http', auth='none')
    def get_account_by_ubersmith_client_id(self, ubersmith_client_id):
        partner = request.env['ubersmith.client'].sudo().search([
            ('client_id', '=', ubersmith_client_id)
        ]).odoo_partner_id
        res = self._get_account_info(partner)
        return self._response(res)

    @http.route('/api/account_by_partner_id/<int:partner_id>',
                type='http', auth='none')
    def get_account_by_partner_id(self, partner_id):
        partner = request.env['res.partner'].sudo().browse(partner_id)
        res = self._get_account_info(partner)
        return self._response(res)

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
        return self._response(partners)

    @http.route('/api/customer/<int:customer_id>', type='http', auth='none')
    def get_customer(self, customer_id):
        fields = self._remove_images()
        partners = request.env['res.partner'].sudo().search_read([
            ('customer', '=', True),
            ('is_company', '=', True),
            ('id', '=', customer_id)
        ], fields=fields)
        return self._response(partners)

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
        return self._response(contacts)

    @http.route('/api/contact/<int:contact_id>', type='http', auth='none')
    def get_contact(self, contact_id):
        fields = self._remove_images()
        contacts = request.env['res.partner'].sudo().search_read([
            ('is_company', '=', False),
            ('id', '=', contact_id)
        ], fields=fields)
        return self._response(contacts)

    @http.route('/api/partner/image/<int:partner_id>', type='http',
                auth='none')
    def get_partner_image(self, partner_id, image='all'):
        if image == 'all':
            fields = ['image', 'image_medium', 'image_small']
        else:
            fields = [image]
        partner = request.env['res.partner'].sudo().search_read([
            ('id', '=', partner_id)
        ], fields=fields)
        return self._response(partner)

    @http.route('/api/subscriptions/<int:customer_id>', type='http',
                auth='none')
    def get_subscriptions(self, customer_id, offset=0, limit=None):
        sub_model = request.env['sale.subscription']
        sub_line_model = request.env['sale.subscription.line']
        subscriptions = sub_model.sudo().search_read([
            ('partner_id', '=', customer_id)
        ], offset=int(offset), limit=int(limit) if limit else None)
        for subscription in subscriptions:
            line_ids = subscription['recurring_invoice_line_ids']
            line_records = sub_line_model.sudo().browse(line_ids)
            subscription['recurring_invoice_line_ids'] = line_records.read()
        return self._response(subscriptions)

    @http.route('/api/subscription/<int:subscription_id>', type='http',
                auth='none')
    def get_subscription(self, subscription_id):
        sub_model = request.env['sale.subscription']
        sub_line_model = request.env['sale.subscription.line']
        subscription = sub_model.sudo().search_read([
            ('id', '=', subscription_id)
        ])
        if not subscription:
            return
        line_ids = subscription[0]['recurring_invoice_line_ids']
        line_records = sub_line_model.sudo().browse(line_ids)
        subscription[0]['recurring_invoice_line_ids'] = line_records.read()
        return self._response(subscription[0])

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
        return self._response(invoices)

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

    @http.route('/api/employees', type='http', auth='none')
    def get_employees(self, offset=0, limit=None):
        fields = [
            'firstname',
            'lastname',
            # Public Information
            'address_id',
            'mobile_phone',
            'work_location',
            'work_email',
            'work_phone',
            'department_id',
            'job_id',
            'title',
            'partial_time',
            'parent_id',
            'coach_id',
            'manager',
            'family_id',
            'calendar_id',
            'notes',
            # HR Settings
            'company_id',
            'user_login',
            'crt_date_start',
            'user_id'
        ]
        employees = request.env['hr.employee'].sudo().search_read(
            [], fields=fields, offset=int(offset),
            limit=int(limit) if limit else None)
        for e in employees:
            user_id = e['user_id'][0] if e['user_id'] else False
            user = request.env['res.users'].sudo().browse(user_id)
            e['has_odoo_login'] = user.active
        return self._response(employees)

    @staticmethod
    def _response(res):
        headers = {'Content-Type': 'application/json'}
        return werkzeug.wrappers.Response(
            json.dumps(res), status=200, headers=headers)
