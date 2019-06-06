# -*- coding: utf-8 -*-

from odoo import models, api


class ResCurrencyRate(models.Model):
    _inherit = "res.currency.rate"

    @api.model
    def create(self, values):
        rec = super(ResCurrencyRate, self).create(values)
        recent_rate = self.search([
            ('currency_id', '=', rec.currency_id.id),
            ('company_id', '=', rec.company_id.id),
        ], limit=1, order='name DESC')
        if rec == recent_rate:
            months = self.env['forecast.month'].search([
                ('company_id', '=', rec.company_id.id),
                ('source_currency_id', '=', rec.currency_id.id),
                ('start_date', '>=', rec.name)
            ])
        else:
            months = self.env['forecast.month'].search([
                ('company_id', '=', rec.company_id.id),
                ('source_currency_id', '=', rec.currency_id.id),
                ('start_date', '=', rec.name)
            ])
        months.update({
            'exchange_rate_id': rec.id
        })
        return rec
