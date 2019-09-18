# -*- coding: utf-8 -*-

from odoo import models, fields, api


class UbersmithClient(models.Model):
    _name = 'ubersmith.client'
    _rec_name = 'client_id'

    client_id = fields.Char(
        string="Client ID",
    )
    first = fields.Char(
        string="First Name",
    )
    last = fields.Char(
        string="Last Name",
    )
    full_name = fields.Char(
        string="Full Name",
    )
    company = fields.Char(
        string="Company",
    )
    phone = fields.Char(
        string="Phone",
    )
    email = fields.Char(
        string="Email",
    )
    fax = fields.Char(
        string="Fax",
    )
    address = fields.Char(
        string="Street Address",
    )
    city = fields.Char(
        string="City",
    )
    state = fields.Char(
        string="State/Province",
    )
    zip = fields.Char(
        string="Zip/Postcode",
    )
    country = fields.Char(
        string="Country",
    )
    vat_number = fields.Char(
        string="VAT",
    )
    grace_due = fields.Boolean(
        string="Due Date Method",
        help='''0 = Grace Period 
                (invoice is due 'datepay' days after generation)
                1 = Static Due Date 
                (invoice is due on 'datedue' day of the month, 
                only applicable to monthly invoicing)'''
    )
    discount_type = fields.Selection(
        string='Discount type',
        selection=[('percentage', 'Percentage'),
                   ('value', 'Value')],
    )
    datepay = fields.Integer(
        string="Grace Period",
        help="Number of days after which the invoice will be due."
    )
    datesend = fields.Integer(
        string="Invoice Send Date",
        help='''Day of the month client will be invoiced (monthly invoicing
                only).'''
    )
    datedue = fields.Integer(
        string="Invoice Due Date",
        help='''Day of the month on which the invoice is due.
                If datedue is less than or equal to datesend, the invoice will
                be due on that day of the following month.'''
    )
    brand_id = fields.Many2one(
        string='Brand ID',
        comodel_name='ubersmith.brand'
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )
    parent_account_id = fields.Many2one(
        string='Parent',
        comodel_name='ubersmith.client'
    )
    odoo_partner_id = fields.Many2one(
        string="Odoo Partner",
        comodel_name='res.partner'
    )
    invoice_ids = fields.One2many(
        string="Client Ubersmith invoices",
        comodel_name="ubersmith.invoice",
        inverse_name="client_id"
    )

    def create_or_sync_clients(self):
        api = self.env['ubersmith.api']
        clients_dict = api.get_clients()
        for client_id, client_dict in clients_dict.iteritems():
            self.sudo().create_or_sync_client(clients_dict, client_id)

    def create_or_sync_client(self, clients_dict, client_id):
        client = self.search([('client_id', '=', client_id)])
        if not client:
            client_dict = clients_dict[client_id]
            brand = self.brand_id.get_brand(client_dict['class_id'])
            vat_number = client_dict.get('metadata', {}).get('vat_number')
            parent_id = client_dict.get('metadata', {}).get(
                'parent_account_id')
            odoo_parent_id = self.get_odoo_parent_id(clients_dict, parent_id)
            disc = client_dict['discount_type']
            return self.create({
                'client_id': client_dict['clientid'],
                'full_name': client_dict['full_name'],
                'first': client_dict['first'],
                'last': client_dict['last'],
                'company': client_dict['company'],
                'phone': client_dict['phone'],
                'email': client_dict['email'],
                'fax': client_dict['fax'],
                'address': client_dict['address'],
                'city': client_dict['city'],
                'state': client_dict['state'],
                'zip': client_dict['zip'],
                'country': client_dict['country'],
                'brand_id': brand.id,
                'vat_number': vat_number,
                'grace_due': self._convert_to_bool(
                    client_dict['grace_due']),
                'datepay': client_dict['datepay'],
                'datedue': client_dict['datedue'],  #
                'datesend': client_dict['datesend'],  #
                'discount_type': self._get_discount_type(disc),
                'parent_account_id': odoo_parent_id
            })
        client.sync_client(clients_dict, client_id)
        return client

    def get_odoo_parent_id(self, clients_dict, parent_id):
        return self.create_or_sync_client(clients_dict,
                                          parent_id).id if parent_id else False

    def sync_client(self, clients_dict, client_id):
        client_values = {}
        client_dict = clients_dict[client_id]
        if self.full_name != client_dict.get('full_name'):
            client_values['full_name'] = client_dict.get('full_name')
        if self.first != client_dict.get('first'):
            client_values['first'] = client_dict.get('first')
        if self.last != client_dict.get('last'):
            client_values['last'] = client_dict.get('last')
        if self.company != client_dict.get('company'):
            client_values['company'] = client_dict.get('company')
        if self.phone != client_dict.get('phone'):
            client_values['phone'] = client_dict.get('phone')
        if self.email != client_dict.get('email'):
            client_values['email'] = client_dict.get('email')
        if self.fax != client_dict.get('fax'):
            client_values['fax'] = client_dict.get('fax')
        if self.address != client_dict.get('address'):
            client_values['address'] = client_dict.get('address')
        if self.city != client_dict.get('city'):
            client_values['city'] = client_dict.get('city')
        if self.state != client_dict.get('state'):
            client_values['state'] = client_dict.get('state')
        if self.zip != client_dict.get('zip'):
            client_values['zip'] = client_dict.get('zip')
        if self.country != client_dict.get('country'):
            client_values['country'] = client_dict.get('country')
        if self.brand_id.brand_id != client_dict['class_id']:
            brand = self.brand_id.get_brand(client_dict['class_id'])
            client_values['brand_id'] = brand.id
        vat_number = client_dict.get('metadata', {}).get('vat_number')
        if self.vat_number != vat_number:
            client_values['vat_number'] = vat_number
        grace_due = self._convert_to_bool(client_dict['grace_due'])
        if self.grace_due != grace_due:
            client_values['grace_due'] = grace_due
        if self.datepay != client_dict.get('datepay'):
            client_values['datepay'] = client_dict.get('datepay')
        if self.datedue != client_dict.get('datedue'):
            client_values['datedue'] = client_dict.get('datedue')
        if self.datesend != client_dict.get('datesend'):
            client_values['datesend'] = client_dict.get('datesend')
        disc = self._get_discount_type(client_dict['discount_type'])
        if self.discount_type != disc:
            client_values['discount_type'] = disc
        parent_id = client_dict.get('metadata', {}).get(
            'parent_account_id', False)
        if self.parent_account_id.client_id != parent_id:
            odoo_parent_id = self.get_odoo_parent_id(clients_dict, parent_id)
            client_values['parent_account_id'] = odoo_parent_id
            odoo_partner_id = self.browse(odoo_parent_id).odoo_partner_id.id
            client_values['odoo_partner_id'] = odoo_partner_id
        self.write(client_values)

    @api.multi
    def get_or_create_partner(self):
        for rec in self.sudo():
            if not rec.parent_account_id:
                odoo_partner_id = rec.create_partner()
            elif rec.parent_account_id.odoo_partner_id:
                odoo_partner_id = rec.parent_account_id.odoo_partner_id.id
            else:
                odoo_partner_id = rec.create_partner()
                rec.parent_account_id.write({
                    'odoo_partner_id': odoo_partner_id})
            rec.write({'odoo_partner_id': odoo_partner_id})

    def create_partner(self):
        odoo_country = self._get_odoo_country(self.country)
        return self.odoo_partner_id.create({
            'company_type': 'company',
            'name': self.company or self.full_name,
            'phone': self.phone,
            'email': self.email,
            'fax': self.fax,
            'city': self.city,
            'zip': self.zip,
            'street': self.address,
            'country_id': odoo_country.id,
            'state_id': self._get_odoo_state_id(self.state, odoo_country),
            'company_id': self.brand_id.company_id.id,
            'comment': self.vat_number,
        }).id

    def _get_odoo_country(self, country):
        return self.env['res.country'].search([
            '|',
            ('code', '=', country),
            ('name', '=', country),
        ], limit=1)

    @staticmethod
    def _get_odoo_state_id(state, odoo_country):
        states_ids = odoo_country.state_ids.filtered(
            lambda s: s.name == state).mapped('id')
        return next(iter(states_ids), False)

    @staticmethod
    def _convert_to_bool(value):
        return bool(int(value))

    @staticmethod
    def _get_discount_type(discount_type):
        if discount_type == '0':
            return 'percentage'
        elif discount_type == '1':
            return 'value'
        else:
            return 'other'

    @api.multi
    def write(self, values):
        res = super(UbersmithClient, self).write(values)
        for rec in self:
            if 'odoo_partner_id' in values:
                child = self.search([('parent_account_id', '=', rec.id)])
                child.write({'odoo_partner_id': values['odoo_partner_id']})
                continue
            if rec.odoo_partner_id:
                rec.sudo().sync_partner(values)
        return res

    def sync_partner(self, client_values):
        partner_values = {}
        if 'company' in client_values or 'full_name' in client_values:
            company = client_values.get('company')
            full_name = client_values.get('full_name')
            partner_values['name'] = company or full_name
        if 'phone' in client_values:
            partner_values['phone'] = client_values['phone']
        if 'email' in client_values:
            partner_values['email'] = client_values['email']
        if 'fax' in client_values:
            partner_values['fax'] = client_values['fax']
        if 'city' in client_values:
            partner_values['city'] = client_values['city']
        if 'zip' in client_values:
            partner_values['zip'] = client_values['zip']
        if 'address' in client_values:
            partner_values['street'] = client_values['address']
        if 'country' in client_values:
            odoo_country = self._get_odoo_country(client_values['country'])
            partner_values['country_id'] = odoo_country.id
        if 'state' in client_values:
            country = client_values.get('country', self.country)
            odoo_country = self._get_odoo_country(country)
            odoo_state_id = self._get_odoo_state_id(client_values['state'],
                                                    odoo_country)
            partner_values['state_id'] = odoo_state_id
        if 'brand_id' in client_values:
            new_brand = self.brand_id.get_brand(client_values['brand_id'])
            partner_values['company_id'] = new_brand.company_id.id
        if 'vat_number' in client_values:
            partner_values['comment'] = self.vat_number
        self.odoo_partner_id.write(partner_values)

    @api.multi
    def create_or_sync_client_ubersmith_invoices(self):
        api = self.env['ubersmith.api']
        invoice_keys = api.get_client_invoices(self.client_id).keys()
        for invoice_id in invoice_keys:
            self.invoice_ids.create_ubersmith_invoice(invoice_id, client=self)

    def create_or_sync_client_services(self):
        service_model = self.env['ubersmith.service']
        api = self.env['ubersmith.api']
        services_dict = api.get_client_services(self.client_id)
        for service_id, service_dict in services_dict.iteritems():
            service_model.create_or_sync_service(service_dict)
