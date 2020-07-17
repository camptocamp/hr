# -*- coding: utf-8 -*-

from odoo import fields, models


class HubspotContactProperty(models.TransientModel):
    _name = 'hubspot.contact.property'

    property_name = fields.Char(
        string='Property Name',
    )
    property_value = fields.Char(
        string='Property Value',
    )
    lead_field_name = fields.Char(
        string='Lead field name',
    )
    contact_id = fields.Many2one(
        comodel_name='hubspot.contact',
        ondelete='cascade',
    )

    def get_value(self):
        value = {}
        if self.property_name == 'hubspot_owner_id':
            user_id = self.env['res.users'].search([
                ('hubspot_owner_id', '=', self.property_value)
            ])
            value.update({'user_id': user_id.id})
            employee_id = self.contact_id.lead_id._get_employee_by_user(
                user_id.id)
            value.update({'company_id': employee_id.company_id.id})
        elif self.property_name == 'original_company_bso_ixreach_':
            company = self.env['res.company'].search([
                ('hubspot_original_company_id', '=', self.property_value)
            ], limit=1)
            value.update({'company_id': company.id})
        elif self.property_name == 'associatedcompanyid' \
                or self.property_name == 'company':
            if self.property_name == 'associatedcompanyid':
                associatedcompanyid = self.property_value
                partner_name = \
                    self.contact_id.lead_id.get_associatedcompany_name(
                        associatedcompanyid)
            else:
                partner_name = self.property_value
            value.update({'partner_name': partner_name})
            if not self.contact_id.lead_id.partner_id:
                partner_id = self.contact_id.lead_id.get_partner_id(
                    partner_name)
                value.update({'partner_id': partner_id})
        else:
            mapping = {
                'email': 'email_from',
                'job_function': 'function',
                # firstname, lastname, name, phone are the same in Odoo
            }
            key = mapping.get(self.property_name, self.property_name)
            value[key] = self.property_value
        return value
