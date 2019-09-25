# -*- coding: utf-8 -*-
import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)


class UbersmithService(models.Model):
    _name = 'ubersmith.service'
    _rec_name = 'service_id'

    service_id = fields.Char(
        string="Service ID",
    )
    bill_type = fields.Selection([
        ('period', 'By period'),
        ('month', 'By month'),
        ('other', 'Other'),
    ])
    discount_type = fields.Selection([
        ('percentage', 'Percentage'),
        ('value', 'Value'),
        ('other', 'Other'),
    ])
    price = fields.Float(
        string="Price"
    )
    plan_id = fields.Many2one(
        string="Service Plan",
        comodel_name="ubersmith.service.plan"
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )

    def create_or_sync_services(self):
        clients = self.env['ubersmith.client'].search([])
        for client in clients:
            client.create_or_sync_client_services()

    def create_or_sync_service(self, service_dict):
        service = self.search([
            ('service_id', '=', service_dict['packid'])
        ])
        if not service:
            plan_id = self.env['ubersmith.service.plan'].search([
                ('plan_id', '=', service_dict['plan_id'])
            ]).id
            return self.create({
                'service_id': service_dict['packid'],
                'discount_type': self._get_discount_type(
                    service_dict['discount_type']),
                'bill_type': self._get_bill_type(
                    service_dict['bill_type']),
                'price': service_dict['price'],
                'plan_id': plan_id,
            })
        service.sync_service(service_dict)

    @staticmethod
    def _get_discount_type(discount_type):
        if discount_type == '0':
            return 'percentage'
        elif discount_type == '1':
            return 'value'
        else:
            return 'other'

    @staticmethod
    def _get_bill_type(bill_type):
        if bill_type == '0':
            return 'period'
        elif bill_type == '1':
            return 'month'
        else:
            return 'other'

    def sync_service(self, service_dict):
        service_values = {}
        bill_type = self._get_bill_type(service_dict.get('bill_type'))
        if self.bill_type != bill_type:
            service_values['bill_type'] = bill_type
        discount_type = self._get_discount_type(
            service_dict.get('discount_type'))
        if self.discount_type != discount_type:
            service_values['discount_type'] = discount_type
        if self.price != service_dict['price']:
            service_values['price'] = service_dict['price']
        if self.plan_id.plan_id != service_dict['plan_id']:
            service_values['plan_id'] = \
                self.env['ubersmith.service.plan'].search([
                    ('plan_id', '=', service_dict['plan_id'])
                ]).id
        self.write(service_values)

    def get_service(self, service_id):
        return self.search([
            ('service_id', '=', service_id)
        ])
