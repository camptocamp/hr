# Copyright 2025 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    group_user = env.ref("base.group_user")
    org_user = env.ref("hr_governance.governance_group_user", raise_if_not_found=False)
    if org_user in group_user.implied_ids:
        group_user._remove_group(org_user)
        _logger.info("Removed Governance User Group from internal User")
