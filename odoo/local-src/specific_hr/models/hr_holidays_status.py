# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import fields, models, api


class HolidaysType(models.Model):
    _inherit = "hr.holidays.status"

    annual_leaves = fields.Float(
        'Annual leaves',
    )

    def update_leaves_allocation(self):
        ## ---> Set BreakPoint
        import pdb;
        pdb.set_trace()
        toto = "toto"
        return True
