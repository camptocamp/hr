# -*- coding: utf-8 -*-
# Author: Damien Crier
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api


class ResCompanyLDAP(models.Model):
    _inherit = 'res.company.ldap'

    @api.model
    def map_ldap_attributes(self, conf, login, ldap_entry):
        values = super(ResCompanyLDAP, self).map_ldap_attributes(
            conf, login, ldap_entry)

        for key in values:
            values[key] = values[key].decode('utf-8')

        mapping = [
            ('name', ['givenName', 'sn']),
        ]
        for value_key, conf_name in mapping:
            values[value_key] = u' '.join(
                [ldap_entry[1][c][0].decode('utf-8') for c in conf_name])

        return values

    @api.model
    def get_or_create_user(self, conf, login, ldap_entry):
        return super(ResCompanyLDAP, self.with_context(
            no_reset_password=True  # avoid to send mail on user creation
        )).get_or_create_user(conf, login, ldap_entry)
