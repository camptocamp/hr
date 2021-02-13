from odoo import models, fields, api


class DeliveryDoc(models.Model):
    _name = 'delivery.doc'

    so_product_category = fields.Selection(
        [('hosting', 'Hosting Service'),
         ('iptransit', 'IP Transit Service'),
         ('l2l', 'L2L / RF Service'),
         ('m2m', 'M2M / VPLS Service'),
         ('other', 'Other Service')],
        string='Category',
        default=False
    )
    po_product_category = fields.Selection(
        [('hosting', 'Hosting Service'),
         ('iptransit', 'IP Transit Service'),
         ('l2l', 'L2L / RF Service'),
         ('other', 'Other Service')],
        string='Category',
        default=False
    )
    service_id = fields.Char(
        string='Service ID'
    )
    hosting_site_address = fields.Char(
        string='Hosting Site address'
    )
    rack_location = fields.Char(
        string='Rack location(s)'
    )
    extra_note = fields.Char(
        string='Extra notes'
    )
    site_address = fields.Char(
        string='Site address'
    )
    demarcation = fields.Char(
        string='Demarcation'
    )
    ip_details = fields.Char(
        string='IP details'
    )
    service_details = fields.Char(
        string='Service details'
    )
    service_point = fields.One2many(
        string='Service Points',
        comodel_name='service.point',
        inverse_name='document_id'
    )
    enough_service_point = fields.Boolean(
        compute='compute_enough_service_point'
    )
    pop_name = fields.Char(
        string='Pop Name'
    )
    bandwidth = fields.Char(
        string='Bandwidth'
    )
    latency = fields.Char(
        string='Latency'
    )
    service_point_name_ref = fields.Integer(default=0)

    @api.depends('service_point', 'so_product_category', 'po_product_category')
    def compute_enough_service_point(self):
        for rec in self:
            if any([
                rec.so_product_category == 'l2l',
                rec.po_product_category == 'l2l']
            ):
                if len(rec.serivce_point) == 2:
                    rec.enough_service_point = True
