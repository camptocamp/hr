# Copyright 2025 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from openupgradelib import openupgrade

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    openupgrade.set_defaults(cr, env, {"governance.role.type": [("color", 1)]})
    openupgrade.load_data(env, "hr_governance", "security/governance_security.xml")
