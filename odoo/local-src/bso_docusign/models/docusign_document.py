import base64
import json
import logging
import shutil
import tempfile

import odoo.addons.docusign.models.docusign as docusign
from odoo.exceptions import Warning

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
                if not email_id.state in ['draft', 'fail']:
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
