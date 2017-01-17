# -*- coding: utf-8 -*-
# Author: Damien Crier
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class HrDepartment(models.Model):
    _inherit = 'hr.department'

    company_id = fields.Many2one(default=False)
