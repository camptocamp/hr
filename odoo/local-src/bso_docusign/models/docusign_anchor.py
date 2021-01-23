# -*- coding: utf-8 -*-

from odoo import models, fields


class DocusignAnchor(models.Model):
    _name = 'docusign.anchor'
    _rec_name = 'signature_type'

    xoff = fields.Float(
        string='Anchor X Offset'
    )
    yoff = fields.Float(
        string='Anchor Y Offset'
    )
    anchor_str = fields.Char(
        string='Anchor String'
    )
    signature_type = fields.Selection(
        selection=[
            ('sign', 'Sign'),
            ('countersign', 'Countersign'),
        ],
        string='Signature Type',
        default='sign')
    field_type = fields.Selection(
        selection=[
            ('signature', 'Signature'),
            ('date', 'Date'),
            ('name', 'Name'),
            ('title', 'Title')
        ],
        string='Field Type',
    )
    template_id = fields.Many2one(
        comodel_name='docusign.template',
        string='Docusign Template'
    )
    ignore_if_not_present = fields.Boolean(
        string='Ignore If Not Present'
    )
    units = fields.Selection(
        selection=[
            ('inches', 'Inches'),
            ('pixels', 'Pixels'),
            ('millimeters', 'Millimeters'),
            ('centimeters', 'Centimeters')
        ],
        string='Units',
        default='inches'
    )
