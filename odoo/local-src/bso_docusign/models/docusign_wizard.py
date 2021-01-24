# -*- coding: utf-8 -*-

from datetime import datetime

from odoo.exceptions import UserError

from odoo import models, fields, api


class DocusignWizard(models.TransientModel):
    _name = 'docusign.wizard'

    attachment_id = fields.Many2one(
        comodel_name='ir.attachment',
        string='Attachment',
    )
    template_id = fields.Many2one(
        string='Docusign Template',
        comodel_name='docusign.template'
    )
    contact_id = fields.Many2one(
        comodel_name='res.partner',
        string='Customer Contact',
    )
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='BSO Countersigner',
    )

    @api.multi
    def sign(self):
        self.ensure_one()
        docusign_document = self.docusign()
        if docusign_document.state == 'sent':
            res_model = self.attachment_id.res_model
            res_id = self.attachment_id.res_id
            if res_model and res_id:
                order = self.env[res_model].browse(res_id).exists()
                if order.state == 'draft' and \
                        order.dealsheet_state == 'validated':
                    order.state = 'sent'

    @api.multi
    def docusign(self):
        self.ensure_one()
        docusign_server_id = self.get_docusign_server_id()
        if not docusign_server_id:
            raise UserError('No configuration found for Docusing integration')
        docusign_document = self.create_docusign_document()
        docusign_document.send_document_cron()
        return docusign_document

    def get_docusign_server_id(self):
        return self.env['docusign.config'].search([
            ('state', '=', 'confirm')
        ], limit=1).id

    @api.multi
    def create_docusign_document(self):
        self.ensure_one()
        signer_ids = self._get_signer_ids()
        return self.env['docusign.document'].create({
            'subject': '%s' % self.attachment_id.res_name,
            'email_from': self.template_id.email_from,
            'signer_ids': [(6, 0, signer_ids)],
            'docusign_template_id': self.template_id.id,
            'model': self.template_id.model,
            'res_id': self.attachment_id.res_id,
            'author_id': self.env.uid,
            'date': datetime.now(),
            'attachment_ids': [(6, 0, [self.attachment_id.id])],
            'body_html': self.template_id.body_html
        })

    def _get_signer_ids(self):
        signer_ids = []
        if not self.contact_id:
            anchor_id = self.template_id.get_anchor('countersign', 'signature')
            signer_id = self._create_signer(self.user_id.partner_id, anchor_id)
            signer_ids.append(signer_id)
            return signer_ids
        sign_anchor_id = self.template_id.get_anchor('sign', 'signature')
        signer_id = self._create_signer(self.contact_id, sign_anchor_id, 1)
        countersign_anchor_id = self.template_id.get_anchor('countersign',
                                                            'signature')
        countersigner_id = self._create_signer(self.user_id.partner_id,
                                               countersign_anchor_id,
                                               2)
        signer_ids.extend([signer_id, countersigner_id])
        return signer_ids

    def _create_signer(self, partner_id, anchor_id, routing_order=0):
        return self.env['docusign.signer'].create({
            'partner_id': partner_id.id,
            'anchor_id': anchor_id.id,
            'routing_order': routing_order
        }).id
