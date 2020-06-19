from odoo import models, fields, api


class ServicePoint(models.Model):
    _name = 'service.point'

    point_name = fields.Char(
        string='Point',
    )
    delivery_line_id = fields.Many2one(
        string='Delivery Line',
        comodel_name='delivery.project.line'
    )
    site_address = fields.Char(
        string='Site Address',
    )
    demarcation = fields.Char(
        string='Demarcation'
    )
    handoff = fields.Char(
        string='handoff'
    )
    ref = fields.Integer(
        related='delivery_line_id.service_point_name_ref'
    )

    @api.model
    def create(self, vals):
        rec = super(ServicePoint, self).create(vals)
        rec.point_name = chr(65 + rec.ref)
        rec.write({'ref': rec.ref + 1})
        return rec
