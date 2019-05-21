# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ForecastLineManual(models.Model):
    _name = "forecast.line.manual"
    _description = "Forecast Line Manual"

    description = fields.Char(
        string='Description',
    )
    line_id = fields.Many2one(
        string='Forecast Line',
        comodel_name='forecast.line',
        delegate=True,
        ondelete='cascade',
        required=True,
    )
    form_id = fields.Many2one(
        string='Open',
        comodel_name='forecast.line.manual',
        readonly=True,
    )

    @api.model
    def create(self, values):
        if not values.get('type'):
            values['type'] = self.env.context.get('type')
        rec = super(ForecastLineManual, self).create(values)
        rec.form_id = rec.id
        return rec
