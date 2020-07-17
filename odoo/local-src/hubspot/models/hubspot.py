# -*- coding: utf-8 -*-

import logging

from odoo.addons.queue_job.job import job
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
        readonly=True,
        copy=False,
    )


class ResUsers(models.Model):
    _inherit = "res.users"

    hubspot_owner_id = fields.Char(
        string='Hubspot Owner ID',
        readonly=True,
        copy=False,
        index=True
    )


def log_hubspot_exceptions(func):
    def func_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            lead = args[0]
            log_sync_exceptions = lead.env['ir.values'].get_default(
                'base.config.settings', 'log_sync_exceptions')
            if log_sync_exceptions:
                lead.env['hubspot.log'].sudo().create({
                    'lead_id': lead.id,
                    'error_message': e,
                    'function_name': func.func_name,
                    'params': str(args[3:]) if len(args) > 3 else '',
                    'hubspot_contact_id': lead.hubspot_contact_id,
                    'hubspot_deal_id': lead.hubspot_deal_id

                })
            if func.func_name == '_create_contact':
                args = args[1:3]
                lead._match_contact_by_email(*args)

    return func_wrapper


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
    prevent_sync = fields.Boolean(
        string='Prevent syncing with Hubspot',
        default=False
    )
    firstname = fields.Char(
        string='Firstname'
    )
    lastname = fields.Char(
        string='Lastname'
    )

    @api.multi
    @api.constrains('stage_id')
    def _check_hubspot_stage(self):
        for record in self:
            key = self.env['ir.values'].get_default(
                'base.config.settings', 'hubspot_app_key')
            name = self.env['ir.values'].get_default(
                'base.config.settings', 'hubspot_app_name')
            if not record.stage_id.hubspot_stage_id and key and name:
                raise ValidationError(_(
                    'Hubspot Stage ID sould be filled in %s stage'
                    % record.stage_id.name,
                ))

    @api.model
    def create(self, vals):
        rec = super(CrmLead, self).create(vals)
        if self.env.context.get('dryrun'):
            return rec
        if vals.get('prevent_sync'):
            return rec
        hubspot_app_key = self.env['ir.values'].get_default(
            'base.config.settings', 'hubspot_app_key')
        hubspot_app_name = self.env['ir.values'].get_default(
            'base.config.settings', 'hubspot_app_name')
        hubspot_app_key = APIKey(hubspot_app_key)
        if self.env.context.get('default_type') == 'opportunity':
            original_lead = self.with_context(default_type='lead').create({
                'name': vals['name']})
            fields = ['planned_revenue_mrc', 'planned_revenue_nrc',
                      'planned_revenue', 'planned_revenue_new_mrc',
                      'planned_revenue_renew_mrc', 'planned_duration']
            deal_vals = {field: vals[field] for field in fields
                         if field in vals.keys()}
            deal_vals['original_lead_id'] = original_lead.id
            rec.write(deal_vals)
            return rec
        if not self.env.context.get('from_hubspot') and \
                not self.env.context.get('is_converted'):
            ctx = {'is_create': True}
            properties = rec.with_context(ctx)._get_contact_properties(vals)
            rec._create_contact(hubspot_app_key,
                                hubspot_app_name,
                                properties)
        if self.env.context.get('from_hubspot'):
            properties = [{'property': 'odoo_id', 'value': rec.id}]
            rec._update_contact(hubspot_app_key,
                                hubspot_app_name,
                                properties)
        return rec

    @api.multi
    def write(self, vals):
        res = super(CrmLead, self).write(vals)
        fields_to_sync = ['name', 'contact_name', 'user_id', 'stage_id',
                          'email_from', 'partner_name', 'planned_revenue_mrc',
                          'planned_revenue_nrc', 'planned_revenue',
                          'planned_revenue_new_mrc',
                          'planned_revenue_renew_mrc',
                          'planned_duration', 'original_lead_id',
                          'phone', 'function']
        if any(key in vals for key in fields_to_sync):
            hubspot_app_key = self.env['ir.values'].get_default(
                'base.config.settings', 'hubspot_app_key')
            hubspot_app_name = self.env['ir.values'].get_default(
                'base.config.settings', 'hubspot_app_name')
            hubspot_app_key = APIKey(hubspot_app_key)
            if not self.env.context.get('from_hubspot'):
                for rec in self:
                    if vals.get('original_lead_id'):
                        ctx = {'is_create': True}
                        properties = \
                            rec.with_context(ctx)._get_deal_properties(vals)
                        associations = rec._get_deal_associations()
                        rec._create_deal(hubspot_app_key,
                                         hubspot_app_name,
                                         properties,
                                         associations, )
                        continue
                    if rec.hubspot_contact_id:
                        properties = rec._get_contact_properties(vals)
                        rec._update_contact(hubspot_app_key,
                                            hubspot_app_name,
                                            properties)
                    if rec.hubspot_deal_id:
                        properties = rec._get_deal_properties(vals)
                        rec._update_deal(hubspot_app_key,
                                         hubspot_app_name,
                                         properties)
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

    @log_hubspot_exceptions
    def _create_contact(self, key, app_name, properties):
        with PortalConnection(key, app_name) as connection:
            response = connection.send_post_request(
                '/contacts/v1/contact',
                ({'properties': properties}))
            self.hubspot_contact_id = response['canonical-vid']

    @log_hubspot_exceptions
    def _match_contact_by_email(self, key, app_name):
        with PortalConnection(key, app_name) as connection:
            if self.email_from:
                existingContact = connection.send_get_request(
                    '/contacts/v1/contact/email/' + self.email_from +
                    '/profile')
                self.hubspot_contact_id = existingContact['canonical-vid']

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
            employee_id = self._get_employee_by_user(self.user_id.id)
            origin_company = employee_id.sudo().company_id or self.company_id
            origin = origin_company.hubspot_original_company_id
            properties.extend([
                {'property': 'hubspot_owner_id',
                 'value': owner_id},
                {'property': 'original_company_bso_ixreach_',
                 'value': origin or ''}
            ])
        if 'function' in vals:
            properties.append({'property': 'job_function',
                               'value': self.function or ''})
        if 'phone' in vals:
            properties.append({'property': 'phone',
                               'value': self.phone or ''})
        if self.env.context.get('is_create'):
            properties.append(
                {'property': 'lifecyclestage', 'value': 'lead'},
            )
        properties.append({'property': 'odoo_id', 'value': self.id})
        return properties

    def _get_employee_by_user(self, user_id):
        return self.env['hr.employee'].search([
            ('user_id', '=', user_id)
        ], limit=1)

    @log_hubspot_exceptions
    def _create_deal(self, key, app_name, properties, associations):
        with PortalConnection(key, app_name) as connection:
            response = connection.send_post_request(
                '/deals/v1/deal',
                ({'associations': associations, 'properties': properties})
            )
            self.hubspot_deal_id = response['dealId']

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

    def _get_deal_associations(self):
        contacts_list = []
        if self.original_lead_id.hubspot_contact_id:
            contacts_list.append(self.original_lead_id.hubspot_contact_id)
        return {
            "associatedVids": contacts_list
        }

    @log_hubspot_exceptions
    def _update_contact(self, key, app_name, properties):
        with PortalConnection(key, app_name) as connection:
            connection.send_post_request(
                '/contacts/v1/contact/vid/' +
                self.hubspot_contact_id + '/profile',
                ({'properties': properties}))

    @log_hubspot_exceptions
    def _update_deal(self, key, app_name, properties):
        with PortalConnection(key, app_name) as connection:
            connection.send_put_request(
                '/deals/v1/deal/' + self.hubspot_deal_id,
                ({'properties': properties}))

    @log_hubspot_exceptions
    def _delete_contact(self, key, app_name):
        with PortalConnection(key, app_name) as connection:
            connection.send_delete_request(
                '/contacts/v1/contact/vid/' + self.hubspot_contact_id)

    @log_hubspot_exceptions
    def _delete_deal(self, key, app_name):
        with PortalConnection(key, app_name) as connection:
            connection.send_delete_request(
                '/deals/v1/deal/' + self.hubspot_deal_id)

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
                                    original_company['value']
                            })
                    self.env['ir.values'].set_default(
                        'base.config.settings',
                        'modifiedDateForOriginalCompany',
                        o_company_values['updatedAt'])
        except Exception, e:
            logger.error("Cannot connect to  Hubspot: %s", e)

    # Webhooks

    @job(default_channel='root.hubspot.sync')
    @api.model
    def sync(self, post):
        contacts = self.env['hubspot.contact'].create_or_update_contacts(post)
        for contact in contacts:
            if contact.change_source == 'API' and 'odoo_id' in \
                    contact.properties.mapped('property_name'):
                # Action to discard: coming from Odoo
                contact.unlink()
            elif contact.change_source == 'IMPORT' and \
                    'odoo_id' in contact.properties.mapped('property_name'):
                contact.link_with_lead()
            elif contact.subscription_type == 'contact.creation':
                contact.create_lead()
            elif contact.subscription_type == 'contact.propertyChange':
                contact.update_lead()

    def get_associatedcompany_name(self, associatedcompanyid):
        # associatedcompany deleted
        if not associatedcompanyid:
            return False
        app_key = self.env['ir.values'].get_default(
            'base.config.settings', 'hubspot_app_key')
        app_name = self.env['ir.values'].get_default(
            'base.config.settings', 'hubspot_app_name')
        key = APIKey(app_key)
        with PortalConnection(key, app_name) as connection:
            company_dict = connection.send_get_request(
                '/companies/v2/companies/' + associatedcompanyid)
            return company_dict['properties'].get('name', {}).get('value')

    def get_partner_id(self, partner_name):
        return self.env['res.partner'].search([
            ('is_company', '=', True),
            ('name', '=', partner_name)
        ], limit=1).id

    def call_onchange(self, vals):
        self.ensure_one()
        if 'user_id' in vals:
            self._onchange_user_id()
