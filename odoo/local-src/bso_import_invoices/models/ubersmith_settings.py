# -*- coding: utf-8 -*-
import logging
from datetime import datetime

from odoo import models, fields, exceptions, api

_logger = logging.getLogger(__name__)


class UbersmithSettings(models.Model):
    _name = 'ubersmith.settings'

    _sql_constraints = [
        ('unique_name', 'UNIQUE (name)', "Settings already exists")
    ]
    name = fields.Char(
        default='Settings',
        readonly=True
    )
    url = fields.Char(
        string="URL",
        required=True,
    )
    username = fields.Char(
        string="Username",
        required=True,
    )
    api_token = fields.Char(
        string="API token",
        required=True,
    )
    invoice_state = fields.Selection(
        selection=[('0', 'Unpaid'),
                   ('1', 'Paid'),
                   ('2', 'Disregarded'),
                   ('all', 'All')],
        default='all',
        string="Invoice State",
    )
    service_state = fields.Selection(
        selection=[('0', 'All active, recurring, unpaid, one-time services'),
                   ('1', 'Active recurring services'),
                   ('2', 'Active one time services'),
                   ('3', 'All services'),
                   ('4', 'All active services')],
        default='3',
        string="Service State"
    )
    service_plan_state = fields.Selection(
        selection=[('1', 'Active plans'),
                   ('0', 'Deactivated plans'),
                   ('2', 'All')],
        default='2',
        string="Service plan State",
    )
    invoice_generation_date = fields.Datetime(
        string='Invoices generated since'
    )
    invoice_generation_timestamp = fields.Float(
        string='Invoices generated since',
        compute='_compute_invoice_generation_timestamp',
        store=True,
        digits=(15, 0)
    )

    def get(self):
        record = self._get()
        if not record:
            raise exceptions.ValidationError(
                "Settings not found, please check settings menu")
        return record

    def _get(self):
        return self.search([], order='id DESC', limit=1)

    def action_settings(self):
        return {
            "name": "Settings",
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "target": "inline",
            "res_model": self._name,
            "res_id": self._get().id,
        }

    def get_invoice_state(self):
        state = self.invoice_state
        return state if state == 'all' else int(state)

    def get_service_state(self):
        return int(self.service_state)

    def get_service_plan_state(self):
        return int(self.service_plan_state)

    @api.multi
    @api.depends('invoice_generation_date')
    def _compute_invoice_generation_timestamp(self):
        for rec in self:
            if not rec.invoice_generation_date:
                continue
            timestamp = rec.get_invoice_generation_timestamp()
            rec.invoice_generation_timestamp = timestamp

    def get_invoice_generation_timestamp(self):
        if not self.invoice_generation_date:
            return False
        u_invoice_model = self.env['ubersmith.invoice']
        since = self.invoice_generation_date
        epoch = datetime(1970, 1, 1)
        since_dt = fields.Datetime.from_string(since)
        since_dt_user_tz = u_invoice_model.convert_dt_to_user_tz(since_dt)
        epoch_user_tz = u_invoice_model.convert_dt_to_user_tz(epoch)
        return (since_dt_user_tz - epoch_user_tz).total_seconds()

    def create_or_sync_ubersmith_data(self):
        api = self.env['ubersmith.api']
        self_session = self.with_context(session=api._get_session())
        brand_model = self_session.env['ubersmith.brand']
        client_model = self_session.env['ubersmith.client']
        invoice_model = self.env['ubersmith.invoice']
        brands = api.get_brands()
        _logger.info('Brands, service plans and taxes import/sync in progress')
        for brand_id, brand_dict in brands.iteritems():
            brand = brand_model.create_or_sync_brand(brand_dict)
            brand.create_or_sync_brand_service_plans()
            brand.create_or_sync_brand_taxes()
            _logger.info('%s plans & taxes imported/synced' % brand.class_name)
        clients_dict = api.get_clients()
        c = 0
        for client_id, client_dict in clients_dict.iteritems():
            c += 1
            client = client_model.create_or_sync_client(clients_dict,
                                                        client_id)
            client.create_or_sync_client_services()
            client.create_or_sync_client_ubersmith_invoices()
            invoice_model.log_progress(c, len(clients_dict),
                                       'service & invoice')

    def import_ubersmith_brands(self):
        return self.env['ubersmith.brand'].create_or_sync_brands()

    def import_ubersmith_service_plans(self):
        self.import_ubersmith_brands()
        return self.env['ubersmith.service.plan'].create_or_sync_plans()

    def import_ubersmith_taxes(self):
        self.import_ubersmith_brands()
        return self.env['ubersmith.tax'].create_or_sync_taxes()

    def import_ubersmith_clients(self):
        return self.env['ubersmith.client'].create_or_sync_clients()

    def import_ubersmith_services(self):
        api = self.env['ubersmith.api']
        self_session = self.with_context(session=api._get_session())
        self_session.import_ubersmith_clients()
        return self_session.env['ubersmith.service'].create_or_sync_services()

    def add_manual_updates(self):
        product_id = self.env['product.product'].search([
            ('name', '=', 'MRC Cross')
        ]).id
        self.env['ubersmith.service.plan'].search([]).write({
            'odoo_product_id': product_id
        })

    def undo_manual_updates(self):
        self.env['ubersmith.service.plan'].search([]).write({
            'odoo_product_id': False
        })

    def import_ubersmith_invoices(self):
        api = self.env['ubersmith.api']
        self_session = self.with_context(session=api._get_session())
        self_session.import_ubersmith_clients()
        for client in self_session.env['ubersmith.client'].search([]):
            client.create_or_sync_client_ubersmith_invoices()

    def create_odoo_invoices(self):
        self.env['ubersmith.invoice'].create_odoo_invoices()
