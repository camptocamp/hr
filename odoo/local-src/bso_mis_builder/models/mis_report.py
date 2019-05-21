# -*- coding: utf-8 -*-


from odoo import models, fields


class MisReportQuery(models.Model):
    _inherit = 'mis.report.query'

    row_model_id = fields.Many2one(
        string='Row Model',
        comodel_name='ir.model',
        required=True,
    )
