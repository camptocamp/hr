from odoo import models, fields


class ResApi(models.Model):
    _name = 'res.api'

    api_id = fields.Char('API ID', required=True, unique=True)
    endpoint = fields.Char('API URL', required=True)

    _sql_constraints = [
        ('uniq_api_id', 'unique(api_id)', 'API ID must be unique')]
