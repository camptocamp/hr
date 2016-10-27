# -*- coding: utf-8 -*-
# Author: Damien Crier
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class ResCompanyLDAP(models.Model):
    _inherit = 'res.company.ldap'

    @api.model
    def map_ldap_attributes(self, conf, login, ldap_entry):
        values = super(ResCompanyLDAP, self).map_ldap_attributes(
            conf, login, ldap_entry)
        mapping = [
            ('name', ['givenName', 'sn']),
        ]
        for value_key, conf_name in mapping:
            values[value_key] = ' '.join(
                [ldap_entry[1][c][0] for c in conf_name])
        return values
