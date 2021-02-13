# -*- coding: utf-8 -*-

from odoo import models, api, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # attachment_ids = fields.One2many(
    #     comodel_name='ir.attachment',
    #     inverse_name='res_id',
    #     domain=[('res_model', '=', 'sale.order')],
    #     string='Attachments')

    docusign_document_ids = fields.One2many(
        comodel_name='docusign.document',
        inverse_name='res_id',
        domain=[('model', '=', 'sale.order')],
        string='Docusin Documents')

    is_retrievable = fields.Boolean(
        string='Signed attachments to retrieve',
        compute='_compute_retrievable',
        store=True
    )
    is_signed = fields.Boolean(
        string='Is signed by docusign',
    )
    is_countersigned = fields.Boolean(
        string='Is countersigned by docusign',
    )

    @api.multi
    @api.depends('docusign_document_ids.state')
    def _compute_retrievable(self):
        for rec in self:
            rec.is_retrievable = any(doc.state in ('sent', 'delivered')
                                     for doc in rec.docusign_document_ids)

    @api.multi
    def action_open_docusign_wizard(self):
        '''
        This function opens a window to select
        an attachment to sign by Docusign
        '''
        self.ensure_one()
        ctx = dict(self.env.context or {})
        ctx.update({
            'model': self._name,
            'res_id': self.id
        })
        if ctx.get('sign_and_countersign', False):
            ctx['partner_id'] = self.partner_id.id
        res_id = self._create_docusign_wizard()
        view_id = self.env.ref('bso_docusign.docusign_wizard_form_view').id
        return {
            'name': 'Docusign',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'docusign.wizard',
            'res_id': res_id,
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'target': 'new',
            'context': ctx,
        }

    def _create_docusign_wizard(self):
        wizard_vals = self._get_wizard_values()
        return self.env['docusign.wizard'].create(wizard_vals).id

    def _get_wizard_values(self):
        wizard_values = {}
        attachment_id = self._get_attachment_id()
        if attachment_id:
            wizard_values['attachment_id'] = attachment_id
        template_id = self._get_docusign_template_id()
        if template_id:
            wizard_values['template_id'] = template_id
        return wizard_values

    def _get_attachment_id(self):
        attachment_ids = self.env['ir.attachment'].search([
            ('res_id', '=', self.id),
            ('res_model', '=', self._name)
        ])
        if not attachment_ids:
            return self._create_attachment()
        if len(attachment_ids) == 1:
            return attachment_ids.id
        return False

    def _create_attachment(self):
        self.env['report'].get_pdf([self.id], 'sale.report_saleorder')
        attachment = self.env['ir.attachment'].search([
            ('res_id', '=', self.id),
            ('res_model', '=', self._name)
        ], limit=1)
        if not attachment:
            return False
        return attachment.id

    def _get_docusign_template_id(self):
        template_ids = self.env['docusign.template'].search([
            ('model', '=', self._name)
        ])
        if len(template_ids) == 1:
            return template_ids.id
        return False

    @api.model
    def retrieve_documents(self):
        orders = self.search([
            ('is_retrievable', '=', True)
        ])
        orders.action_retrieve_document()

    @api.multi
    def action_retrieve_document(self):
        ctx = dict(self.env.context or {})
        for rec in self:
            documents = rec.docusign_document_ids.filtered(
                lambda d: d.state in ('sent', 'delivered'))
            ctx['from_docusign'] = True
            documents.with_context(ctx).download_document_cron()
            completed_docs = documents.filtered(
                lambda d: d.state == 'completed')
            if not completed_docs:
                continue
            template_id = self._get_template(completed_docs)
            rec._update_so(template_id.update_state)

    def _update_so(self, update_state):
        if self.state not in ('sale', 'sent', 'done'):
            return
        if self.state == 'sent':
            self.write({
                'is_signed': True,
                'is_countersigned': True
            })
            if update_state:
                self._confirm_so_and_log_exceptions()
        else:
            self.write({
                'is_countersigned': True
            })
        return

    def _confirm_so_and_log_exceptions(self):
        try:
            self.action_confirm()
        except Exception, e:
            msg = "%s can't be confirmed: %s" % (self.name, e)
            self.message_post(body=msg)

    @staticmethod
    def _get_template(docs):
        if len(docs) == 1:
            return docs.docusign_template_id
        return docs[0].docusign_template_id
