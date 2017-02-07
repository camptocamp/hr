# -*- coding: utf-8 -*-
# Author: Damien Crier
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

coa_dict = {
    'base.main_company': 'l10n_fr.l10n_fr_pcg_chart_template',
    '__setup__.roctool_inc': 'l10n_generic_coa.configurable_chart_template',
    '__setup__.roctool_gmbh': 'l10n_de_skr03.l10n_de_chart_template',
    # '__setup__.roctool_taiwan': l10n_cn,
    # '__setup__.roctool_japan': 'l10n_jp.l10n_jp1',
    # cannot import Japan now because of this bug:
    # https://github.com/odoo/odoo/issues/15384
    # OPW reported on 2017-02-07
}
