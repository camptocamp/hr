# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api


class HolidaysType(models.Model):
    _inherit = "hr.holidays.status"

    annual_leaves = fields.Float(
        'Annual leaves',
        digits=(16, 3),
    )

    is_rtt = fields.Boolean('Is RTT')

    exclude_rest_days = fields.Boolean('Exclude week-end')

    @api.multi
    def update_leaves_allocation(self):
        for rec in self:
            emps = self.env['hr.employee'].search(
                [('company_id', '=', rec.company_id.id),
                 ('active', '=', True),
                 ('crt_date_start', '!=', False),
                 ])
            self.env['hr.holidays'].create_allocation(emps, rec)

    @api.model
    def update_leaves_cron(self):
        leaves = self.env['res.company'].search([]).mapped(
            'legal_holidays_status_id')
        leaves.update_leaves_allocation()
        self.search([('is_rtt', '=', True)]).update_leaves_allocation()
