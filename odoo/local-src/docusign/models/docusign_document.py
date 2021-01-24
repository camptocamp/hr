# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

import base64
import json
import logging
import shutil
import tempfile
import time

from odoo.exceptions import Warning

import docusign
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class DocusignDocument(models.Model):
    _name = 'docusign.document'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Docusign Document"
    _rec_name = 'subject'

    @api.model
    def _default_docusign_server_id(self):
        '''
        This method will be check the docusign server details
        and fetch the ids.
        @param self: The object pointer.
        '''
        docusign_server_id = self.env['docusign.config'].search([
            ('state', '=', 'confirm')
        ], limit=1)
        return docusign_server_id.id or False

    mail_server_id = fields.Many2one('docusign.config', 'Outgoing mail server',
                                     default=_default_docusign_server_id)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('signed', 'Signed'),
        ('completed', 'Completed'),
        ('declined', 'Declined'),
        ('deleted', 'Deleted'),
        ('voided', 'Voided'),
        ('fail', 'Failed'),
        ('cancel', 'Cancelled')
    ], 'Status', track_visibility='onchange', default="draft")
    auto_delete = fields.Boolean(
        'Auto Delete',
        help="Permanently delete this email after sending it, to save space")
    references = fields.Text(
        'References',
        help='Message references, such as identifiers of previous messages')
    subject = fields.Char('Subject')
    email_from = fields.Char(
        'From',
        help='Message sender, taken from user preferences.')
    email_to = fields.Text('To', help='Message recipients')
    email_cc = fields.Char('Cc',
                           help='Carbon copy message recipients')
    reply_to = fields.Char('Reply-To',
                           help='Preferred response address for the message')
    body_html = fields.Text('Rich-text Contents',
                            help="Rich-text/HTML message")
    date = fields.Datetime('Date Created')
    signhere_tab = fields.Char('Signhere Tab')
    model = fields.Char('Related Document Model')
    message_id = fields.Char('Message-Id',
                             help='Message unique identifier')
    author_id = fields.Many2one(
        'res.users', 'Author',
        ondelete='set null',
        help="Author of the message. If not set, email_from may hold an email"
             " address that did not match any partner.")
    partner_ids = fields.Many2many('res.partner',
                                   'docusign_email_res_partner_rel',
                                   'document_id', 'partner_id',
                                   'Additional contacts')
    attachment_ids = fields.Many2many('ir.attachment',
                                      'docusign_email_ir_attachments_rel',
                                      'document_id', 'attachment_id',
                                      'Attachments')
    sign_attachment_ids = fields.Many2many(
        'ir.attachment',
        'docusign_email_ir_sign_attachments_rel',
        'sign_document_id',
        'sign_attachment_id', 'Attachments')
    res_id = fields.Integer('Related Document ID')
    docusign_template_id = fields.Many2one('docusign.template',
                                           'Docusign Template')
    env_id = fields.Char('Envelope Id')
    notification = fields.Boolean('Is Notification')

    @api.multi
    def cancel_document(self):
        '''
        This method will be used to cancel the document.
        @param self: The object pointer.
        '''
        self.write({'state': 'cancel'})
        return True

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
                recipient = [partner for partner in email_id.partner_ids][0]
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
                    email_id.docusign_template_id.signhere_tab or False
                xoff_date = \
                    email_id.docusign_template_id and \
                    email_id.docusign_template_id.xoff_date or 0.00
                yoff_date = \
                    email_id.docusign_template_id and \
                    email_id.docusign_template_id.yoff_date or 0.00
                _logger.info("_______docusign__mail_id_______ %s" % email_id)
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
                _logger.info("____docusign__response________ %s" % response)
                _logger.info("____docusign__content_______ %s" % content)
                content = json.loads(content)
                msg = ("Envelope successfully sent to <b>%s</b> of this "
                       " <b>%s</b> email id.") % (
                          recipient.name, recipient.email)
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

    @api.multi
    def download_document_cron(self):
        '''
        This method will be used to download the document from the
        docusign and set to the attechment.
        @param self: The object pointer.
        '''
        #        if docusign_sent_email_ids:
        for email_id in self:
            attach_ids = []
            if email_id.state not in ['sent', 'delivered'] and \
                    email_id.env_id != '':
                raise Warning("You must select the email which is in Sent"
                              " or Delivered state.")
            login = {
                'baseurl': email_id.mail_server_id.docusign_baseurl,
                'auth_str': email_id.mail_server_id.docusign_authstr
            }
            envid = email_id.env_id
            response_status, content_status = \
                docusign.req_env_status_url(self, login, envid)
            content_status = json.loads(content_status)
            if response_status.get('status') != '200':
                msg = "<b>%s</b> : %s." % \
                      (content_status.get('errorCode'),
                       content_status.get('message'))
                email_id.message_post(body=msg)
            if content_status.get('status') == 'completed':
                req_info = "/envelopes/" + email_id.env_id
                response_doc, file_lst, content_doc = docusign. \
                    download_documents(self, login, req_info)
                if response_doc.get('status') != '200':
                    msg = "<b>%s</b> : %s." % \
                          (content_doc.get('errorCode'),
                           content_doc.get('message'))
                    email_id.message_post(body=msg)
                else:
                    for filename in file_lst:
                        file_name = "doc.pdf"
                        f_name = filename.split('/')
                        if email_id.model == 'res.contract':
                            file_name = f_name and f_name[-1] or \
                                        str(email_id.res_id) + "_doc.pdf"
                        elif email_id.model == 'sale.order':
                            f_name = f_name[-1].split('.')
                            file_name = \
                                f_name and f_name[0] + ' - ' \
                                + time.strftime('%Y-%m-%d') + ".pdf" or \
                                str(email_id.res_id) + "_doc.pdf"
                        elif email_id.model == 'res.partner':
                            file_name = "Customer LOA - " + \
                                        time.strftime('%Y-%m-%d') + ".pdf"
                        filecontents = open(filename, "rb").read()
                        filecontents_en = base64.b64encode(filecontents)
                        data_attach = {
                            'name': file_name,
                            'datas': filecontents_en,
                            'datas_fname': file_name,
                            'res_model': email_id.model,
                            'res_id': email_id.res_id,
                            'type': 'binary',
                        }
                        res_id = self.env['ir.attachment']. \
                            create(data_attach)
                        attach_ids.append(res_id.id)
                    email_id.write({
                        'sign_attachment_ids': [(6, 0, attach_ids)]})
            email_id.write({'state': content_status.get('status')})
        return True
