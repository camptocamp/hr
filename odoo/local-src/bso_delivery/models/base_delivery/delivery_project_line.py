from odoo import fields, models, api, exceptions


class DeliveryProjectLine(models.AbstractModel):
    _name = 'delivery.project.line'

    name = fields.Char(
        string='Name'
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

    # handover/factsheet document related fields
    document_id = fields.Many2one(
        comodel_name='delivery.doc'
    )
    so_product_category = fields.Selection(
        related='document_id.so_product_category'
    )
    po_product_category = fields.Selection(
        related='document_id.po_product_category'
    )

    service_id = fields.Char(
        related='document_id.service_id'
    )
    hosting_site_address = fields.Char(
        related='document_id.hosting_site_address'
    )
    rack_location = fields.Char(
        related='document_id.rack_location'
    )
    extra_note = fields.Char(
        related='document_id.extra_note'
    )
    site_address = fields.Char(
        related='document_id.site_address'
    )
    demarcation = fields.Char(
        related='document_id.demarcation'
    )
    ip_details = fields.Char(
        related='document_id.ip_details'
    )
    service_details = fields.Char(
        related='document_id.service_details'
    )
    service_point = fields.One2many(
        related='document_id.service_point'
    )
    pop_name = fields.Char(
        related='document_id.pop_name'
    )
    bandwidth = fields.Char(
        related='document_id.bandwidth'
    )
    # latency = fields.Char(
    #     related='document_id.latency'
    # )
    enough_service_point = fields.Boolean(
        related='document_id.enough_service_point')

    delivery_date = fields.Date(
        string='Delivery Date'
    )
    report_line = fields.Boolean()

    @api.onchange('service_point')
    def constrains_service_point(self):
        if self.document_id.so_product_category == 'l2l':
            if len(self.service_point) > 2:
                self.service_point = self.service_point[:2]
            raise exceptions.ValidationError(
                "L2L service can not have more than 2 endpoints, "
                "the extra elements won't be considered, "
                "please delete them!")

    @api.multi
    def write(self, vals):
        for rec in self:
            if not rec.document_id:
                vals['document_id'] = rec.document_id.create({}).id
            return super(DeliveryProjectLine, self).write(vals)
