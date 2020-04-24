# -*- coding: utf-8 -*-

import logging

from odoo.exceptions import UserError, ValidationError

from hubspotCon.connection import APIKey
from hubspotCon.connection import PortalConnection
from odoo import api, fields, models, _

logger = logging.getLogger(__name__)


class Stage(models.Model):
    _inherit = "crm.stage"

    hubspot_stage_id = fields.Char(
        string='Hubspot Stage ID',
        copy=False,
        index=True,
        required=True
    )


class ResCompany(models.Model):
    _inherit = "res.company"

    hubspot_original_company_id = fields.Char(
        string='Hubspot Original Company ID',
        copy=False,
        required=True
    )


class ResUsers(models.Model):
    _inherit = "res.users"

    hubspot_owner_id = fields.Char(
        string='Hubspot Owner ID',
        readonly=True,
        copy=False,
        index=True
    )


class CrmLead(models.Model):
    _inherit = "crm.lead"

    hubspot_contact_id = fields.Char(
        string='Hubspot Contact ID',
        readonly=True,
        copy=False,
        index=True
    )
    hubspot_deal_id = fields.Char(
        string='Hubspot Deal ID',
        readonly=True,
        copy=False,
        index=True
    )
    is_not_synced = fields.Boolean(
        string='Is not synced correctly'
    )

    @api.multi
    @api.constrains('stage_id')
    def _check_hubspot_stage(self):
        for record in self:
            if not record.stage_id.hubspot_stage_id:
                raise ValidationError(_(
                    'Hubspot Stage ID sould be filled in %s stage'
                    % record.stage_id.name,
                ))

    @api.model
    def create(self, vals):
        rec = super(CrmLead, self).create(vals)
        hubspot_app_key = self.env['ir.values'].get_default(
            'base.config.settings', 'hubspot_app_key')
        hubspot_app_name = self.env['ir.values'].get_default(
            'base.config.settings', 'hubspot_app_name')
        hubspot_app_key = APIKey(hubspot_app_key)
        if self.env.context.get('default_type') == 'opportunity':
            original_lead = self.with_context(default_type='lead').create({
                'name': vals['name']})
            rec.write({'original_lead_id': original_lead.id})
            return rec
        if not self.env.context.get('from_hubspot') and \
                not self.env.context.get('is_converted'):
            rec._create_contact(vals,
                                hubspot_app_key,
                                hubspot_app_name)
        return rec

    @api.multi
    def write(self, vals):
        res = super(CrmLead, self).write(vals)
        fields_to_sync = ['name', 'contact_name', 'user_id', 'stage_id',
                          'email_from', 'planned_revenue_mrc',
                          'planned_revenue_nrc', 'planned_revenue',
                          'planned_revenue_new_mrc',
                          'planned_revenue_renew_mrc',
                          'planned_duration', 'original_lead_id']
        if any(key in vals for key in fields_to_sync):
            hubspot_app_key = self.env['ir.values'].get_default(
                'base.config.settings', 'hubspot_app_key')
            hubspot_app_name = self.env['ir.values'].get_default(
                'base.config.settings', 'hubspot_app_name')
            hubspot_app_key = APIKey(hubspot_app_key)
            if not self.env.context.get('from_hubspot'):
                for rec in self:
                    if vals.get('original_lead_id'):
                        rec._create_deal(vals, hubspot_app_key,
                                         hubspot_app_name)
                        continue
                    if rec.hubspot_contact_id:
                        rec._update_contact(vals,
                                            hubspot_app_key,
                                            hubspot_app_name)
                    if rec.hubspot_deal_id:
                        rec._update_deal(vals,
                                         hubspot_app_key,
                                         hubspot_app_name)
        return res

    @api.multi
    def unlink(self):
        hubspot_app_key = self.env['ir.values'].get_default(
            'base.config.settings', 'hubspot_app_key')
        hubspot_app_name = self.env['ir.values'].get_default(
            'base.config.settings', 'hubspot_app_name')
        hubspot_app_key = APIKey(hubspot_app_key)
        for rec in self:
            if rec.hubspot_contact_id:
                rec._delete_contact(hubspot_app_key, hubspot_app_name)
            if rec.hubspot_deal_id:
                rec._delete_deal(hubspot_app_key, hubspot_app_name)
        return super(CrmLead, self).unlink()

    @api.multi
    def _create_contact(self, vals, key, app_name):
        logger.info('Creating new contacts in hubspot')
        # create hubspot dictionary
        properties = self.with_context(is_create=True)._get_contact_properties(
            vals)
        try:
            with PortalConnection(key, app_name) as connection:
                response = connection.send_post_request(
                    '/contacts/v1/contact',
                    ({'properties': properties}))
                self.hubspot_contact_id = response['canonical-vid']
        except Exception, e:
            logger.error("Cannot create contact in Hubspot: %s", e)
            try:
                existingContact = connection.send_get_request(
                    '/contacts/v1/contact/email/' + self.email_from +
                    '/profile')
                if existingContact:
                    self.hubspot_contact_id = existingContact['canonical-vid']
            except Exception, e:
                logger.error("Cannot update contact in Hubspot: %s", e)
                self.is_not_synced = True
        logger.info('Completed Creating new contacts in hubspot')

    def _get_contact_properties(self, vals):
        properties = []
        if 'name' in vals:
            properties.append({'property': 'name', 'value': vals['name']})
        if vals.get('email_from'):
            # do not include in properties if emptied or False in creation
            properties.append({'property': 'email',
                               'value': vals['email_from']})
        if 'contact_name' in vals:
            if vals['contact_name']:
                names_list = vals['contact_name'].split()
                properties.append({'property': 'firstname',
                                   'value': names_list[0]})
                if len(names_list) > 1:
                    properties.append({'property': 'lastname',
                                       'value': ' '.join(names_list[1:])})
                else:
                    properties.append({'property': 'lastname', 'value': ''})
            else:
                properties.append({'property': 'firstname', 'value': ''})
                properties.append({'property': 'lastname', 'value': ''})
        if 'partner_name' in vals:
            properties.append({'property': 'company',
                               'value': vals['partner_name'] or ''})
        if 'user_id' in vals or self.env.context.get('is_create'):
            owner_id = self.user_id.hubspot_owner_id or ''
            employee_id = self._get_employee_by_user()
            origin = employee_id.sudo().company_id.hubspot_original_company_id
            properties.extend([
                {'property': 'hubspot_owner_id',
                 'value': owner_id},
                {'property': 'original_company_bso_ixreach_',
                 'value': origin or ''}
            ])
        if self.env.context.get('is_create'):
            properties.extend([
                {'property': 'lifecyclestage', 'value': 'lead'},
                {'property': 'odoo_id', 'value': self.id},
            ])
        return properties

    def _get_employee_by_user(self):
        return self.env['hr.employee'].search([
            ('user_id', '=', self.user_id.id)
        ], limit=1)

    def _create_deal(self, vals, key, app_name):
        properties = self.with_context(is_create=True)._get_deal_properties(
            vals)
        associations = self._get_deal_associations()
        try:
            with PortalConnection(key, app_name) as connection:
                response = connection.send_post_request(
                    '/deals/v1/deal',
                    ({'associations': associations, 'properties': properties})
                )
                self.hubspot_deal_id = response['dealId']
        except Exception, e:
            logger.error("Cannot create deal in Hubspot: %s", e)
            self.is_not_synced = True

    def _get_deal_properties(self, vals):
        properties = []
        if 'name' in vals or self.env.context.get('is_create'):
            properties.append({'name': 'dealname', 'value': self.name})
        if 'stage_id' in vals or self.env.context.get('is_converted') or \
                self.env.context.get('is_create'):
            properties.append({'name': 'dealstage',
                               'value': self.stage_id.hubspot_stage_id})
        if 'planned_revenue_mrc' in vals:
            mrc_name = self.env['ir.values'].get_default(
                'base.config.settings', 'hubspot_mrc_name')
            properties.append({'name': mrc_name,
                               'value': self.planned_revenue_mrc_usd})
        if 'planned_revenue_renew_mrc' in vals \
                or 'planned_revenue_mrc' in vals:
            new_mrc_name = self.env['ir.values'].get_default(
                'base.config.settings', 'hubspot_new_mrc_name')
            properties.append({'name': new_mrc_name,
                               'value': self.planned_revenue_new_mrc_usd})
        if 'planned_revenue_renew_mrc' in vals:
            renew_mrc_name = self.env['ir.values'].get_default(
                'base.config.settings', 'hubspot_renew_mrc_name')
            properties.append({'name': renew_mrc_name,
                               'value': self.planned_revenue_renew_mrc_usd})
        if 'planned_revenue_nrc' in vals:
            nrc_name = self.env['ir.values'].get_default(
                'base.config.settings', 'hubspot_nrc_name')
            properties.append({'name': nrc_name,
                               'value': self.planned_revenue_nrc_usd})
        if 'planned_revenue_mrc' in vals or 'planned_revenue_nrc' in vals \
                or 'planned_duration' in vals:
            tcv_name = self.env['ir.values'].get_default(
                'base.config.settings', 'hubspot_tcv_name')
            properties.append({'name': tcv_name,
                               'value': self.planned_revenue_usd})
        if 'planned_revenue_nrc' in vals or 'planned_revenue_mrc' in vals \
                or 'planned_duration' in vals or 'planned_revenue_renew_mrc' \
                in vals:
            new_tcv_name = self.env['ir.values'].get_default(
                'base.config.settings', 'hubspot_new_tcv_name')
            properties.append({'name': new_tcv_name,
                               'value': self.planned_new_revenue_usd})
        if 'planned_duration' in vals:
            duration_name = self.env['ir.values'].get_default(
                'base.config.settings', 'hubspot_duration_name')
            properties.append({'name': duration_name,
                               'value': vals['planned_duration']})
        if 'user_id' in vals or self.env.context.get('is_create'):
            owner_id = self.user_id.hubspot_owner_id or ''
            properties.append({'name': 'hubspot_owner_id',
                               'value': owner_id})
        return properties

    def _get_owner_id(self, user_id):
        user_id = self.user_id.browse(user_id)
        return user_id.hubspot_owner_id

    def _update_vals(self, vals, user_id):
        if self.env.context.get('is_create'):
            return
        user_id = self.user_id.browse(user_id)
        vals['company_id'] = user_id.company_id.id
        vals['team_id'] = self.env['crm.team'].sudo()._get_default_team_id(
            user_id=user_id.id)
        return vals

    def _get_deal_associations(self):
        contacts_list = []
        if self.original_lead_id.hubspot_contact_id:
            contacts_list.append(self.original_lead_id.hubspot_contact_id)
        return {
            "associatedVids": contacts_list
        }

    @api.multi
    def _update_contact(self, vals, key, app_name):
        logger.info('Updating contacts in hubspot')
        try:
            with PortalConnection(key, app_name) as connection:
                properties = self._get_contact_properties(vals)
                connection.send_post_request(
                    '/contacts/v1/contact/vid/' +
                    self.hubspot_contact_id + '/profile',
                    ({'properties': properties}))
        except Exception, e:
            logger.error("Cannot update contact in Hubspot: %s", e)
            self.is_not_synced = True
        logger.info('Completed updating contacts in hubspot')

    @api.multi
    def _update_deal(self, vals, key, app_name):
        logger.info('Updating deals in hubspot')
        try:  # c3
            with PortalConnection(key, app_name) as connection:
                properties = self._get_deal_properties(vals)
                connection.send_put_request(
                    '/deals/v1/deal/' + self.hubspot_deal_id,
                    ({'properties': properties}))
        except Exception, e:
            logger.error("Cannot update contact in Hubspot: %s", e)
            self.is_not_synced = True
        logger.info('Completed updating contacts in hubspot')

    def _delete_contact(self, key, app_name):
        logger.info('Delete contact from Hubspot')
        try:
            with PortalConnection(key, app_name) as connection:
                connection.send_delete_request(
                    '/contacts/v1/contact/vid/' + self.hubspot_contact_id)
        except Exception, e:
            logger.error("Cannot delete from Hubspot: %s", e)
            self.is_not_synced = True
        logger.info('Completed Delete from hubspot')

    def _delete_deal(self, key, app_name):
        logger.info('Delete deal from Hubspot')
        try:
            with PortalConnection(key, app_name) as connection:
                connection.send_delete_request(
                    '/deals/v1/deal/' + self.hubspot_deal_id)
        except Exception, e:
            logger.error("Cannot delete from Hubspot: %s", e)
            self.is_not_synced = True
        logger.info('Completed Delete from hubspot')

    @api.model
    def syncHubspotData(self):
        logger.info('Synchronization with Hubspot Started')
        '''Synchronize the leads with the hubspot contacts'''
        # Hubspot Information
        hubspot_app_key = self.env['ir.values'].get_default(
            'base.config.settings', 'hubspot_app_key')
        hubspot_app_name = self.env['ir.values'].get_default(
            'base.config.settings', 'hubspot_app_name')
        if not hubspot_app_key or not hubspot_app_name:
            raise UserError(_(
                'Error in Synchronization!\nHubspot API Key and App Name need \
                to be specified for synchronization of data with Odoo.'))
        hubspot_app_key = APIKey(hubspot_app_key)
        modifiedDateForContact = float(
            self.env['ir.values'].get_default('base.config.settings',
                                              'modifiedDateForContact') or 0)
        createdDateForOwner = float(
            self.env['ir.values'].get_default('base.config.settings',
                                              'createdDateForOwner') or 0)
        modifiedDateForOriginalCompany = float(
            self.env['ir.values'].get_default(
                'base.config.settings',
                'modifiedDateForOriginalCompany') or 0)
        # Owners
        self.match_users_with_owners(
            hubspot_app_key,
            hubspot_app_name,
            createdDateForOwner
        )
        # Original companies
        self.match_original_companies(
            hubspot_app_key,
            hubspot_app_name,
            modifiedDateForOriginalCompany
        )
        # Contacts
        '''From Hubspot to Odoo'''
        contacts_to_sync = self._get_modified_contacts(
            hubspot_app_key,
            hubspot_app_name,
            modifiedDateForContact
        )
        self._create_or_update_leads(contacts_to_sync)
        logger.info('Synchronization with Hubspot Completed')

    @api.model
    def match_users_with_owners(self, key, app_name, createdDateForOwner):
        logger.info('Getting all owners from Hubspot')
        try:
            with PortalConnection(key, app_name) as connection:
                owners_list = connection.send_get_request('/owners/v2/owners')
                new_owners_list = [owner for owner in owners_list if
                                   owner['createdAt'] >= createdDateForOwner]
                new_create_date = 0
                for owner_dict in new_owners_list:
                    user_id = self._get_user_by_email(owner_dict)
                    if not user_id or user_id.hubspot_owner_id:
                        continue
                    user_id.write({'hubspot_owner_id': owner_dict['ownerId']})
                    if new_create_date < owner_dict['createdAt']:
                        new_create_date = owner_dict['createdAt']
                owners_ids = ['%s' % owner['ownerId'] for owner in owners_list]
                self._unmatch_users(owners_ids)
                if new_create_date:
                    self.env['ir.values'].set_default('base.config.settings',
                                                      'createdDateForOwner',
                                                      new_create_date)
        except Exception, e:
            logger.error("Cannot connect to  Hubspot: %s", e)

    def _get_user_by_email(self, owner_dict):
        partner_id = self.partner_id.search([
            ('email', 'ilike', owner_dict['email'])
        ], limit=1).id
        return self.user_id.search([
            ('partner_id', '=', partner_id)
        ])

    def _unmatch_users(self, owners_ids):
        unused_users = self.env['res.users'].search([
            ('hubspot_owner_id', '!=', False),
            ('hubspot_owner_id', 'not in', owners_ids)
        ])
        if not unused_users:
            return
        unused_users.write({'hubspot_owner_id': False})

    @api.model
    def _get_modified_contacts(self, key, app_name, modifiedDateForContact):
        contacts_to_sync = []
        has_more = True
        vid_offset = False
        time_offset = False
        # first contact returned is most recently updated
        is_most_recent = True
        params = {
            'count': 10,
            'property': ['firstname', 'lastname', 'email', 'hubspot_owner_id',
                         'associatedcompanyid', 'name', 'odoo_id']
        }
        with PortalConnection(key, app_name) as connection:
            while has_more:
                if vid_offset:
                    params['vidOffset'] = vid_offset
                if time_offset:
                    params['timeOffset'] = time_offset
                modified_contacts = connection.send_get_request(
                    '/contacts/v1/lists/recently_updated/contacts/recent',
                    params)
                for contact in modified_contacts['contacts']:
                    contact_updated_at = int(
                        contact['properties']['lastmodifieddate']['value'])
                    if is_most_recent:
                        new_contact_update_date = contact_updated_at
                        is_most_recent = False
                    if contact_updated_at <= modifiedDateForContact:
                        has_more = False
                        break
                    else:
                        properties = contact['properties']
                        properties['company'] = self._get_name_by_companyid(
                            connection, properties)
                        properties['canonical-vid'] = contact['canonical-vid']
                        contacts_to_sync.append(properties)
                else:
                    has_more = modified_contacts['has-more']
                    time_offset = modified_contacts['time-offset']
                    vid_offset = modified_contacts['vid-offset']
        self.env['ir.values'].set_default('base.config.settings',
                                          'modifiedDateForContact',
                                          new_contact_update_date)
        return contacts_to_sync

    def _get_name_by_companyid(self, connection, properties):
        company_id = properties.get('associatedcompanyid', {}).get('value')
        if not company_id:
            return False
        company_dict = connection.send_get_request(
            '/companies/v2/companies/' + company_id)
        return company_dict['properties'].get('name', {}).get('value')

    def _create_or_update_leads(self, contacts_to_sync):
        if not contacts_to_sync:
            return
        logger.info('Creating new leads in Odoo')
        for contact in contacts_to_sync:
            self._create_or_update_lead(contact)

    def _create_or_update_lead(self, contact):
        hubspot_contact_id = str(contact['canonical-vid'])
        odoo_id = contact.get('odoo_id', {}).get('value', False)
        if odoo_id:
            lead = self.search([
                ('id', '=', int(odoo_id))
            ])
            if lead and not lead.hubspot_contact_id:
                lead.with_context({'from_hubspot': True}).write({
                    'hubspot_contact_id': hubspot_contact_id
                })
                return
        firstname = contact.get('firstname', {}).get('value', False)
        lastname = contact.get('lastname', {}).get('value', False)
        hubspot_owner_id = contact.get('hubspot_owner_id', {}).get('value',
                                                                   False)
        name = contact.get('name', {}).get('value', False)
        company_name = contact['company']
        email = contact.get('email', {}).get('value', False)
        contact_name = self._get_contact_name(firstname, lastname)
        partner_id = self._get_partner_by_company(company_name)
        lead_values = {
            'contact_name': contact_name,
            'user_id': self._get_user_by_owner_id(hubspot_owner_id),
            'email_from': email,
            'partner_id': partner_id,
            'name': name
        }
        lead = self._get_lead_by_hubspot_id(hubspot_contact_id)
        if lead:
            lead._update_lead(lead_values)
            lead._call_onchange(lead_values)
            return lead
        lead_values['hubspot_contact_id'] = hubspot_contact_id
        lead = self._get_lead_by_email(email)
        if lead:
            lead._update_lead(lead_values)
        else:
            partner_name = self.partner_id.browse(partner_id).name
            name = partner_name or contact_name or email or 'Unknown'
            lead_values['name'] = name
            lead = self.with_context({'from_hubspot': True}).create(
                lead_values)
        lead._call_onchange(lead_values)
        return lead

    def _call_onchange(self, vals):
        for rec in self:
            if vals.get('user_id'):
                rec._onchange_user_id()
            if vals.get('partner_id'):
                rec._onchange_partner_id()

    @staticmethod
    def _get_contact_name(firstname, lastname):
        if firstname and lastname:
            return '%s %s' % (firstname, lastname)
        if firstname and not lastname:
            return firstname
        if not firstname and lastname:
            return lastname
        return False

    def _get_user_by_owner_id(self, owner_id):
        if not owner_id:
            return False
        return self.env['res.users'].search([
            ('hubspot_owner_id', '=', owner_id)
        ], limit=1).id

    def _get_partner_by_company(self, company_name):
        if not company_name:
            return False
        return self.env['res.partner'].search([
            ('is_company', '=', True),
            ('name', '=ilike', company_name)
        ], limit=1).id

    def _get_lead_by_hubspot_id(self, hubspot_id):
        return self.search([
            ('hubspot_contact_id', '=', hubspot_id)
        ])

    def _get_lead_by_email(self, email):
        if not email:
            return
        return self.search([
            ('email_from', 'ilike', email)
        ])

    @api.multi
    def _update_lead(self, vals_from_hubspot):
        vals = {}
        for rec in self:
            if vals_from_hubspot['name'] and \
                    rec.name != vals_from_hubspot['name']:
                vals['name'] = vals_from_hubspot['name']
            if rec.email_from != vals_from_hubspot['email_from']:
                vals['email_from'] = vals_from_hubspot['email_from']
            if rec.user_id.id != vals_from_hubspot['user_id']:
                vals['user_id'] = vals_from_hubspot['user_id']
            if rec.contact_name != vals_from_hubspot['contact_name']:
                vals['contact_name'] = vals_from_hubspot['contact_name']
            if not rec.partner_id and vals_from_hubspot['partner_id']:
                vals['partner_id'] = vals_from_hubspot['partner_id']
            if vals_from_hubspot.get('hubspot_contact_id'):
                hubspot_contact_id = vals_from_hubspot['hubspot_contact_id']
                vals['hubspot_contact_id'] = hubspot_contact_id
            if not vals:
                return False
            rec.with_context({'from_hubspot': True}).write(vals)

    @api.model
    def match_original_companies(self, key, app_name, modified_date_company):
        logger.info('Getting all original company values from Hubspot')
        try:
            with PortalConnection(key, app_name) as connection:
                o_company_values = connection.send_get_request(
                    '/properties/v1/contacts/properties/named/\
                    original_company_bso_ixreach_')
                if o_company_values['updatedAt'] > modified_date_company:
                    for original_company in o_company_values['options']:
                        odoo_company = self.env['res.company'].search([
                            ('name', '=', original_company['label'])
                        ])
                        if odoo_company:
                            odoo_company.write({
                                'hubspot_original_company_id':
                                    original_company['label']
                            })
                    self.env['ir.values'].set_default(
                        'base.config.settings',
                        'modifiedDateForOriginalCompany',
                        o_company_values['updatedAt'])
        except Exception, e:
            logger.error("Cannot connect to  Hubspot: %s", e)
