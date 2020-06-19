from odoo import fields, models, api, exceptions


class DeliveryProjectLine(models.Model):
    _name = 'delivery.project.line'

    name = fields.Char(
        string='Name'
    )
    select = fields.Boolean(
        string='Select'
    )
    delivery_id = fields.Many2one(
        string='Service delivery',
        comodel_name='delivery.project'
    )
    order_line_id = fields.Many2one(
        string='Order Line',
        comodel_name='sale.order.line'
    )
    display_qty_delivered = fields.Char(
        string='Delivered Qty',
        compute='compute_display_qty_delivered',
        store=True
    )

    date_forecasted = fields.Date(
        string='Forecasted Date',
    )
    date_sla = fields.Date(
        string='SLA Date'
    )

    jira_product_template_ids = fields.Many2many(
        comodel_name='jira.product.template',
        string='Jira Templates',
    )
    product_id = fields.Many2one(
        related='order_line_id.product_id',
        readonly=1
    )

    # handover document fields
    product_category = fields.Selection(
        [('hosting', 'Hosting Service'),
         ('iptransit', 'IP Transit Service'),
         ('l2l', 'L2L / RF Service'),
         ('m2m', 'M2M / VPLS Service'),
         ('other', 'Other Service')],
        string='Category'
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
        inverse_name='delivery_line_id'
    )
    service_point_name_ref = fields.Integer(default=0)
    delivery_date = fields.Date(
        string='Delivery Date'
    )

    @api.onchange('service_point')
    def constrains_service_point(self):
        if self.product_category == 'l2l':
            if len(self.service_point) > 2:
                self.service_point = self.service_point[:2]
                raise exceptions.ValidationError(
                    "L2L service can not have more than 2 endpoints, "
                    "the extra elements won't be considered, "
                    "please delete them!")

    @api.multi
    def write(self, vals):
        for rec in self:
            if (rec.product_category == 'l2l' or
                vals.get('product_category') == 'l2l') and \
                    'service_point' in vals:
                if len(rec.service_point) == 2:
                    del vals['service_point']
                elif len(rec.service_point) == 1:
                    vals['service_point'] = vals['service_point'][0]
                elif len(vals['service_point']) > 2:
                    vals['service_point'] = vals['service_point'][:2]
            super(DeliveryProjectLine, rec).write(vals)

    @api.model
    def create(self, vals):
        rec = super(DeliveryProjectLine, self).create(vals)
        jira_template = self.env['jira.product.template']
        template_ids = jira_template.search([(
            'category_id', '=',
            rec.order_line_id.product_id.categ_id.id
        )], limit=1)
        if template_ids:
            rec.write({
                'jira_product_template_ids': [(6, 0, template_ids.ids)]
            })
        return rec
