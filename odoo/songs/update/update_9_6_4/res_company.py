# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem
from . import bso_vars


@anthem.log
def configure_subcontracting_service_proc_rule(ctx):
    """ Configuring procurement subcontracted service """

    for company_xml_id in bso_vars.coa_dict:
        company = ctx.env.ref(company_xml_id)
        with ctx.log("Configuring procurement subcontracted service for %s:" %
                     company.name):
            company._set_subcontracting_service_proc_rule()


@anthem.log
def main(ctx):
    configure_subcontracting_service_proc_rule(ctx)
