# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import anthem
from ..install.crm import create_leads_for_partners


@anthem.log
def main(ctx):
    create_leads_for_partners(ctx)
