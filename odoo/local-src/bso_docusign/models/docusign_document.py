import base64
import json
import logging
import mimetypes
import shutil
import tempfile
import time

import odoo.addons.docusign.models.docusign as docusign
from odoo.exceptions import Warning
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.tools.mimetypes import guess_mimetype

from odoo import api, models, fields

_logger = logging.getLogger(__name__)


class DocusignDocument(models.Model):
    _inherit = 'docusign.document'

    signer_ids = fields.One2many(
        string='Signers',
        comodel_name='docusign.signer',
        inverse_name='document_id',
    )

    @api.multi
    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'state' in init_values and self.state == 'completed':
            return 'bso_docusign.mt_docusign_document_completed'
        if 'state' in init_values and self.state == 'cancel':
            return 'bso_docusign.mt_docusign_document_canceled_parent'
        return super(DocusignDocument, self)._track_subtype(init_values)

    def get_document(self, env_id):
        return self.search([
            ('env_id', '=', env_id)
        ])

    def download_attachments(self):
        attachment_id = self._create_attachment()
        if attachment_id:
            self.write({
                'attachment_ids': [(6, 0, [attachment_id])],
            })

    def _create_attachment(self):
        login = {
            'baseurl': self.mail_server_id.docusign_baseurl,
            'auth_str': self.mail_server_id.docusign_authstr
        }
        req_info = "/envelopes/" + self.env_id
        response_doc, file_lst, content_doc = docusign.download_documents(
            self, login, req_info)
        if response_doc.get('status') != '200':
            msg = "<b>%s</b> : %s." % \
                  (content_doc.get('errorCode'),
                   content_doc.get('message'))
            self.message_post(body=msg)
            return
        for filename in file_lst:
            filecontents = open(filename, "rb").read()
            filecontents_en = base64.b64encode(filecontents)
            name = self._get_filename(filename, filecontents)
            data_attach = {
                'name': name,
                'datas': filecontents_en,
                'datas_fname': name,
                'res_model': self.model,
                'res_id': self.res_id,
                'type': 'binary',
            }
            return self.env['ir.attachment'].create(data_attach).id
        return

    # def download_attachments(self, data):
    #     envelope_documents = data.get('envelopeDocuments', [])
    #     attachment_ids = []
    #     for doc in envelope_documents:
    #         if doc.get('documentId') == 'certificate':
    #             continue
    #         attachment_id = self._create_attachment(doc)
    #         attachment_ids.append(attachment_id)
    #     if attachment_ids:
    #         self.write({
    #             'attachment_ids': [(6, 0, attachment_ids)],
    #         })

    # def _create_attachment(self, doc):
    #     name = doc.get('name')
    #     content = str(doc.get('PDFBytes'))
    #     filename = self._get_filename(name, content)
    #     attach_values = {
    #         'name': filename,
    #         'datas': content,
    #         'datas_fname': filename,
    #         'res_model': self.model,
    #         'res_id': self.res_id,
    #         'type': 'binary',
    #     }
    #     return self.env['ir.attachment'].create(attach_values).id

    @staticmethod
    def _get_filename(name, content):
        mimetype = guess_mimetype(content)
        extension = mimetypes.guess_extension(mimetype)
        name_without_extension = name.rstrip(extension)
        filename = name_without_extension.split('/')[-1]
        date_str = time.strftime(DEFAULT_SERVER_DATE_FORMAT)
        signature_suffix = 'Countersigned'
        return '%s_%s_%s%s' % (filename,
                               date_str,
                               signature_suffix,
                               extension)

    @api.multi
    def send_document_cron(self):
        '''
        This method will be send the mail and his document to users .
        @param self: The object pointer.
         '''
        docusign_email_ids = self.search([('state', 'in', ('draft', 'fail'))])
        if docusign_email_ids:
            for email_id in self:
                file_lst = []
                if email_id.state not in ['draft', 'fail']:
                    raise Warning(("You must select the email which is in "
                                   "Draft or Fail state."))
                login = {
                    'baseurl': email_id.mail_server_id.docusign_baseurl,
                    'auth_str': email_id.mail_server_id.docusign_authstr
                }
                files = [attach for attach in email_id.attachment_ids]
                for f in files:
                    content = base64.b64decode(f.datas)
                    directory_name = tempfile.mkdtemp()
                    filename = directory_name + "/%s" % f.name
                    file_lst.append({'fname': filename, 'ftype': f.mimetype})
                    file_content = open(filename, 'w')
                    file_content.write(content)
                    file_content.close()
                recipient = self.env['res.partner']
                if email_id.partner_ids:
                    recipient = [p for p in email_id.partner_ids][0]
                body = email_id.body_html
                subject = email_id.subject
                signature = \
                    email_id.docusign_template_id and \
                    email_id.docusign_template_id.signhere_tab
                xoff = \
                    email_id.docusign_template_id and \
                    email_id.docusign_template_id.xoff
                yoff = \
                    email_id.docusign_template_id and \
                    email_id.docusign_template_id.yoff
                datesigned = \
                    email_id.docusign_template_id and \
                    email_id.docusign_template_id.signhere_tab \
                    or False
                xoff_date = \
                    email_id.docusign_template_id and \
                    email_id.docusign_template_id.xoff_date or 0.00
                yoff_date = \
                    email_id.docusign_template_id and \
                    email_id.docusign_template_id.yoff_date or 0.00
                _logger.info("____docusign__mail_id____ %s" % email_id)
                response, content = docusign.create_envelope(self, login,
                                                             recipient,
                                                             body,
                                                             subject,
                                                             file_lst,
                                                             signature,
                                                             xoff, yoff,
                                                             datesigned,
                                                             xoff_date,
                                                             yoff_date)
                _logger.info("____docusign__response____________ %s"
                             % response)
                _logger.info("____docusign__content____________ %s"
                             % content)
                content = json.loads(content)
                msg = ("Envelope successfully sent to <b>%s</b> of this "
                       " <b>%s</b> email id.") % \
                      (recipient.name, recipient.email)
                if response.get('status') != '201':
                    msg = "<b>%s</b> : %s." % (content.get('errorCode'),
                                               content.get('message'))
                    email_id.write({'state': 'fail'})
                else:
                    email_id.write({'state': 'sent',
                                    'env_id': content.get('envelopeId')})
                email_id.message_post(body=msg)
                shutil.rmtree(directory_name)
            return True
