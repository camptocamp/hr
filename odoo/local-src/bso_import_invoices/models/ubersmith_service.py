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
    circuit_id = fields.Char(
        string="Circuit ID",
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
    cost = fields.Float(
        string="Cost"
    )
    client_id = fields.Many2one(
        string="Ubersmith Client",
        comodel_name="ubersmith.client"
    )
    start = fields.Date(
        string="Billing Start"
    )
    end = fields.Date(
        string="End"
    )
    renewdate = fields.Date(
        string="Renewal Date"
    )
    activation_date = fields.Date(
        string="Activation Date"
    )
    period = fields.Selection([
        ('0', 'One Time'),
        ('1', 'Monthly'),
        ('2', 'Bi-monthly'),
        ('3', 'Quarterly'),
        ('6', 'Semi'),
        ('12', 'Annual'),
    ])
    post_renew = fields.Boolean(
        string='Bill in arrears',
    )
    bill_prior = fields.Boolean(
        string='Bill in advance',
    )
    quantity = fields.Float(
        string="Quantity",
    )
    desserv = fields.Char(
        string="Description",
    )
    discount = fields.Float(
        string="Discount"
    )
    term_id = fields.Many2one(
        string="Term ID",
        comodel_name="ubersmith.contract.term"
    )
    status = fields.Selection(
        string="Status",
        selection=[
            ('0', 'Deactivated'),
            ('1', 'Active'),
            ('2', 'Pending'),
            ('3', 'Suspended'),
            ('4', 'Cancelled'),
        ]
    )
    odoo_subscription_id = fields.Many2one(
        string="Suscription",
        comodel_name="sale.subscription"
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
            ui = self.env['ubersmith.invoice']
            return self.create({
                'service_id': service_dict['packid'],
                'circuit_id': service_dict.get('metadata', {}).get(
                    'service_id'),
                'discount_type': self._get_discount_type(
                    service_dict['discount_type']),
                'bill_type': self._get_bill_type(
                    service_dict['bill_type']),
                'price': service_dict['price'],
                'plan_id': plan_id,
                'cost': service_dict['cost'],
                'term_id': self._get_term_id(service_dict['contract_term_id']),
                'period': service_dict['period'],
                'status': service_dict['active'],
                'bill_prior': service_dict['bill_prior'],
                'post_renew': service_dict['post_renew'],
                'quantity': service_dict['quantity'],
                'desserv': service_dict['desserv'],
                'discount': service_dict['discount'],
                'start': ui.convert_timestamp_to_date(
                    service_dict['start']),
                'end': ui.convert_timestamp_to_date(
                    service_dict['end']),
                'renewdate': ui.convert_timestamp_to_date(
                    service_dict['renewdate']),
                'activation_date': ui.convert_timestamp_to_date(
                    service_dict['activation_date']),
                'client_id': self._get_client(service_dict['clientid']),
            })
        service.sync_service(service_dict)

    def _get_term_id(self, term_id):
        return self.env['ubersmith.contract.term'].search([
            ('contract_term_id', '=', term_id)
        ]).id

    def _get_client(self, clientid):
        return self.env['ubersmith.client'].search([
            ('client_id', '=', clientid)
        ]).id

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
        usp = self.env['ubersmith.service.plan']
        ui = self.env['ubersmith.invoice']
        service_values = {}
        bill_type = self._get_bill_type(service_dict.get('bill_type'))
        if self.bill_type != bill_type:
            service_values['bill_type'] = bill_type
        # discount_type = self._get_discount_type(
        #     service_dict.get('discount_type'))
        # if self.discount_type != discount_type:
        #     service_values['discount_type'] = discount_type
        if self.price != service_dict['price']:
            service_values['price'] = service_dict['price']
        if self.plan_id.plan_id != service_dict['plan_id']:
            service_values['plan_id'] = \
                self.env['ubersmith.service.plan'].search([
                    ('plan_id', '=', service_dict['plan_id'])
                ]).id
        price = usp.convert_to_float(service_dict['price'])
        if self.price != price:
            service_values['price'] = price
        term_id = self._get_term_id(service_dict['contract_term_id'])
        if self.term_id.id != term_id:
            service_values['term_id'] = term_id
        cost = usp.convert_to_float(service_dict['cost'])
        if self.cost != cost:
            service_values['cost'] = cost
        if self.status != service_dict['active']:
            service_values['status'] = service_dict['active']
        if self.period != service_dict['period']:
            service_values['period'] = service_dict['period']
        bill_prior = usp.convert_to_bool(service_dict['bill_prior'])
        if self.bill_prior != bill_prior:
            service_values['bill_prior'] = bill_prior
        post_renew = usp.convert_to_bool(service_dict['post_renew'])
        if self.post_renew != post_renew:
            service_values['post_renew'] = post_renew
        quantity = usp.convert_to_float(service_dict['quantity'])
        if self.quantity != quantity:
            service_values['quantity'] = quantity
        start = ui.convert_timestamp_to_date(service_dict['start'])
        if self.start != start:
            service_values['start'] = fields.Date.to_string(start)
        end = ui.convert_timestamp_to_date(service_dict['end'])
        if self.end != end:
            service_values['end'] = fields.Date.to_string(end)
        renewdate = ui.convert_timestamp_to_date(service_dict['renewdate'])
        if self.renewdate != renewdate:
            service_values['renewdate'] = fields.Date.to_string(renewdate)
        activation_date = ui.convert_timestamp_to_date(
            service_dict['activation_date'])
        if self.activation_date != activation_date:
            service_values['activation_date'] = fields.Date.to_string(
                activation_date)
        if self.client_id.client_id != service_dict['clientid']:
            service_values['client_id'] = self._get_client(
                service_dict['clientid'])
        if self.status != service_dict['active']:
            service_values['status'] = service_dict['active']
        circuit_id = service_dict.get('metadata', {}).get('service_id')
        if self.circuit_id != circuit_id:
            service_values['circuit_id'] = circuit_id
        if self.desserv != service_dict['desserv']:
            service_values['desserv'] = service_dict['desserv']
        self.write(service_values)

    def get_service(self, service_id):
        return self.search([
            ('service_id', '=', service_id)
        ])
