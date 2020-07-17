# -*- coding: utf-8 -*-

from odoo import fields, models


class HubspotContact(models.TransientModel):
    _name = 'hubspot.contact'

    object_id = fields.Char(
        string='Object ID',
    )
    subscription_type = fields.Char(
        string='Subscription Type',
    )
    change_source = fields.Char(
        string='Change Source',
    )
    lead_id = fields.Many2one(
        comodel_name='crm.lead',
        string='Lead'
    )
    properties = fields.One2many(
        comodel_name='hubspot.contact.property',
        inverse_name='contact_id',
        string="Properties",
    )

    def create_or_update_contacts(self, post):
        events = post.get('params')
        contacts = self.env['hubspot.contact']
        for event in events:
            contact = self.create_or_update_contact(event)
            contacts |= contact
        return contacts

    def create_or_update_contact(self, event):
        contact = self.search([
            ('object_id', '=', event['objectId'])
        ])
        if contact:
            if event.get('subscriptionType') == 'contact.creation' and \
                    contact.subscription_type == 'contact.propertyChange':
                contact.write({'subscription_type': 'contact.creation'})
        else:
            lead = self.env['crm.lead'].search([
                ('hubspot_contact_id', '=', event['objectId'])
            ])
            contact = self.create({
                'object_id': event['objectId'],
                'subscription_type': event['subscriptionType'],
                'change_source': event['changeSource'],
                'lead_id': lead.id
            })
        if 'propertyName' in event:
            self.env['hubspot.contact.property'].create({
                'contact_id': contact.id,
                'property_name': event['propertyName'],
                'property_value': event['propertyValue']
            })
        return contact

    def create_lead(self):
        values = self.with_context(is_create=True).get_values_from_contact()
        if not values.get('name') or self.lead_id:
            return
        notify_users = self.env['ir.values'].get_default('base.config.settings'
                                                         , 'notify_users')
        ctx = {'from_hubspot': True}
        if not notify_users:
            ctx.update({'mail_auto_subscribe_no_notify': True})
        lead = self.with_context(ctx).lead_id.create(values)
        self.write({'lead_id': lead.id})
        self.lead_id.call_onchange(values)
        self.unlink()

    def update_lead(self):
        if not self.lead_id:
            return
        notify_users = self.env['ir.values'].get_default('base.config.settings'
                                                         , 'notify_users')
        ctx = {'from_hubspot': True}
        if not notify_users:
            ctx.update({'mail_auto_subscribe_no_notify': True})
        values = self.get_values_from_contact()
        self.with_context(ctx).lead_id.write(values)
        self.lead_id.call_onchange(values)
        self.unlink()

    def link_with_lead(self):
        odoo_id = self.properties.filtered(
            lambda p: p.property_name == 'odoo_id').property_value
        lead = self.env['crm.lead'].search([
            ('id', '=', odoo_id)
        ])
        lead.write({'hubspot_contact_id': self.object_id})
        self.unlink()

    def get_values_from_contact(self):
        values = dict()
        for contact_property in self.properties:
            value = contact_property.get_value()
            values.update(value)
        if 'firstname' in values or 'lastname' in values:
            values['contact_name'] = '%s %s' % (
                values.get('firstname', self.lead_id.firstname) or '',
                values.get('lastname', self.lead_id.lastname) or ''
            )
        if 'name' not in values and self.env.context.get('is_create'):
            values['name'] = values.get('partner_name') or \
                             values.get('contact_name') or \
                             values.get('email_from')
        if self.env.context.get('is_create'):
            values['hubspot_contact_id'] = self.object_id
        return values
