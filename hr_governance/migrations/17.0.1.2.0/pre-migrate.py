# Copyright 2025 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    openupgrade.drop_columns(cr, [("governance_circle", "is_circle")])
