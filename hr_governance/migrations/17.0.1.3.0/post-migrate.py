# Copyright 2025 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    reorganization_proposal = env.ref(
        "hr_governance.reorganization_proposal", raise_if_not_found=False
    )
    assigned_user_ids_field = env.ref(
        "hr_governance.field_governance_circle__assigned_user_ids",
        raise_if_not_found=False,
    )
    reorganization_proposal.write({"default_user_field_id": assigned_user_ids_field.id})
    _logger.info("Assigned assigned_user_ids_field for reorganization_proposal")
