# -*- coding: utf-8 -*-

from odoo import models, fields


class DocusignSigner(models.Model):
    _name = 'docusign.signer'
    _rec_name = 'partner_id'
    _order = 'routing_order'

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Signer',
    )
    routing_order = fields.Integer(
        string='Routing Order'
    )
    anchor_id = fields.Many2one(
        comodel_name='docusign.anchor',
        string='Docusign Anchor'
    )
    document_id = fields.Many2one(
        comodel_name='docusign.document',
        string='Docusign Document'
    )
