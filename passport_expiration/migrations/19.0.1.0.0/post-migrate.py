# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not version:
        return
    if not _column_exists(cr, "hr_employee", "passport_expiration_date"):
        return

    _logger.info("Migrating passport expiration dates to hr.version")
    cr.execute(
        """
        UPDATE hr_version hv
           SET passport_expiration_date = he.passport_expiration_date
          FROM hr_employee he
         WHERE hv.id = COALESCE(he.current_version_id, he.version_id)
           AND he.passport_expiration_date IS NOT NULL
           AND hv.passport_expiration_date IS NULL
        """
    )


def _column_exists(cr, table, column):
    cr.execute(
        """
        SELECT 1
          FROM information_schema.columns
         WHERE table_name = %s
           AND column_name = %s
        """,
        (table, column),
    )
    return bool(cr.fetchone())
