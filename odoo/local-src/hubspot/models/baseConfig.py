import datetime
import time

from odoo import api, fields, models


class BaseConfigSettings(models.TransientModel):
    _inherit = "base.config.settings"

    hubspot_app_key = fields.Char(
        string='Hubspot App ID'
    )
    hubspot_app_name = fields.Char(
        string='Hubspot App Name'
    )
    modifiedDateForOdoo = fields.Char(
        string='Date',
        default=str(datetime.datetime.now())[:19]
    )
    modifiedDateForContact = fields.Char(
        string='Modified Date for Contact',
        default=time.time() * 1e3
    )
    createdDateForOwner = fields.Char(
        string='Create Date for Owner'
    )
    modifiedDateForOriginalCompany = fields.Char(
        string='Modified Date for Original Company',
    )
    hubspot_tcv_name = fields.Char(
        string='Hubspot TCV(USD) Name',
        default='planned_revenue_usd'
    )
    hubspot_mrc_name = fields.Char(
        string='Hubspot MRC(USD) Name',
        default='planned_revenue_mrc_usd'
    )
    hubspot_nrc_name = fields.Char(
        string='Hubspot NRC(USD) Name',
        default='planned_revenue_nrc_usd'
    )
    hubspot_duration_name = fields.Char(
        string='Hubspot Term Name',
        default='planned_duration'
    )
    hubspot_new_tcv_name = fields.Char(
        string='Hubspot New TCV(USD) Name',
        default='planned_new_revenue_usd'
    )
    hubspot_new_mrc_name = fields.Char(
        string='Hubspot New MRC(USD) Name',
        default='planned_revenue_new_mrc_usd'
    )
    hubspot_renew_mrc_name = fields.Char(
        string='Hubspot Renewal MRC(USD) Name',
        default='planned_revenue_renew_mrc_usd'
    )

    @api.multi
    def set_hubspot_app_key(self):
        config_value = self.hubspot_app_key
        self.env['ir.values'].set_default('base.config.settings',
                                          'hubspot_app_key', config_value)

    @api.multi
    def set_hubspot_app_name(self):
        config_value = self.hubspot_app_name
        self.env['ir.values'].set_default('base.config.settings',
                                          'hubspot_app_name', config_value)

    @api.multi
    def set_modifiedDateForOdoo(self):
        config_value = self.modifiedDateForOdoo
        self.env['ir.values'].set_default('base.config.settings',
                                          'modifiedDateForOdoo', config_value)

    @api.multi
    def set_modifiedDateForContact(self):
        config_value = self.modifiedDateForContact
        self.env['ir.values'].set_default('base.config.settings',
                                          'modifiedDateForContact',
                                          config_value)

    @api.multi
    def set_createdDateForOwner(self):
        config_value = self.createdDateForOwner
        self.env['ir.values'].set_default('base.config.settings',
                                          'createdDateForOwner',
                                          config_value)

    @api.multi
    def set_hubspot_tcv_name(self):
        config_value = self.hubspot_tcv_name
        self.env['ir.values'].set_default('base.config.settings',
                                          'hubspot_tcv_name',
                                          config_value)

    @api.multi
    def set_hubspot_new_tcv_name(self):
        config_value = self.hubspot_new_tcv_name
        self.env['ir.values'].set_default('base.config.settings',
                                          'hubspot_new_tcv_name',
                                          config_value)

    @api.multi
    def set_hubspot_mrc_name(self):
        config_value = self.hubspot_mrc_name
        self.env['ir.values'].set_default('base.config.settings',
                                          'hubspot_mrc_name',
                                          config_value)

    @api.multi
    def set_hubspot_new_mrc_name(self):
        config_value = self.hubspot_new_mrc_name
        self.env['ir.values'].set_default('base.config.settings',
                                          'hubspot_new_mrc_name',
                                          config_value)

    @api.multi
    def set_hubspot_renew_mrc_name(self):
        config_value = self.hubspot_renew_mrc_name
        self.env['ir.values'].set_default('base.config.settings',
                                          'hubspot_renew_mrc_name',
                                          config_value)

    @api.multi
    def set_hubspot_nrc_name(self):
        config_value = self.hubspot_nrc_name
        self.env['ir.values'].set_default('base.config.settings',
                                          'hubspot_nrc_name',
                                          config_value)

    @api.multi
    def set_hubspot_duration_name(self):
        config_value = self.hubspot_duration_name
        self.env['ir.values'].set_default('base.config.settings',
                                          'hubspot_duration_name',
                                          config_value)
