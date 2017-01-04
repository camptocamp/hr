# -*- coding: utf-8 -*-
# Author: Damien Crier
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    planned_revenue_nrc = fields.Float('Expected NRC Revenue',
                                       track_visibility='always')
    planned_revenue_mrc = fields.Float('Expected MRC Revenue',
                                       track_visibility='always')
    planned_duration = fields.Integer('Duration',
                                      track_visibility='always')
    planned_revenue = fields.Float('Expected Revenue',
                                   compute='_get_planned_revenue')

    @api.depends('planned_duration',
                 'planned_revenue_mrc',
                 'planned_revenue_nrc')
    def _get_planned_revenue(self):
        for rec in self:
            rec.planned_revenue = (rec.planned_revenue_nrc +
                                   (rec.planned_revenue_mrc *
                                    rec.planned_duration)
                                   )
