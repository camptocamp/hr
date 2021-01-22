# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class DocusignTemplate(models.Model):

    _name = 'docusign.template'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    name = fields.Char('Name')
    model_id = fields.Many2one('ir.model', 'Applies to',
        help="The kind of document with with this template can be used")
    model = fields.Char(related='model_id.model',
        string='Related Document Model',
        size=128, store=True)
    signhere_tab = fields.Char('Signhere Tab', size=128)
    signhere_tab_date = fields.Char('Signhere Date Tab', size=128)
    xoff = fields.Float('XOFF')
    yoff = fields.Float('YOFF')
    xoff_date = fields.Float('XOFF Date')
    yoff_date = fields.Float('YOFF Date')
    lang = fields.Char('Language',
        help="Optional translation language (ISO code) to select when sending"\
            " out an email. "
             "If not set, the english version will be used. "
             "This should usually be a placeholder expression "
             "that provides the appropriate language code, e.g. "
             "${object.partner_id.lang.code}.",
            placeholder="${object.partner_id.lang.code}")
    user_signature = fields.Boolean('Add Signature',
        help="If checked, the user's signature will be appended to the"\
            " text version of the message")
    subject = fields.Char('Subject', translate=True,
            help="Subject (placeholders may be used here)")
    email_from = fields.Char('From',
        help="Sender address (placeholders may be used here). If not set, "\
             "the default value will be the author's email alias if configured"\
             ", or email address.")
    email_to = fields.Char('To (Emails)',
        help="Comma-separated recipient addresses (placeholders may be "\
            "used here)")
    email_recipients = fields.Char('To (Partners)',
        help="Comma-separated ids of recipient partners (placeholders may be"\
            " used here)")
    email_cc = fields.Char('Cc',
        help="Carbon copy recipients (placeholders may be used here)")
    reply_to = fields.Char('Reply-To',
        help="Preferred response address (placeholders may be used here)")
    mail_server_id = fields.Many2one('docusign.config', 'Outgoing Mail Server',
        help="Optional preferred server for outgoing mails. If not set, "\
        "the highest priority one will be used.")
    body_html = fields.Text('Body', translate=True,
        help="Rich-text/HTML version of the message (placeholders may be used "\
            "here)")
    report_name = fields.Char('Report Filename', translate=True,
        help="Name to use for the generated report file (may contain "\
        "placeholders)\n The extension can be omitted and will then come "\
        "from the report type.")
    report_template = fields.Many2one('ir.actions.report.xml',
                                      'Optional report to print and attach')
    attachment_ids = fields.Many2many('ir.attachment',
                                      'docusign_template_attachment_rel',
                                      'docusign_template_id',
                                      'attachment_id', 'Attachments',
                                      help="You may attach files to this "\
                                        "template, to be added to all "\
                                        "emails created from this template")
    auto_delete = fields.Boolean('Auto Delete',
        help="Permanently delete this email after sending it, to save space",
        default=True)

    # Fake fields used to implement the placeholder assistant
    model_object_field = fields.Many2one('ir.model.fields', string="Field",
        help="Select target field from the related document model.\n"
           "If it is a relationship field you will be able to select "
           "a target field at the destination of the relationship.")
    sub_object = fields.Many2one('ir.model', 'Sub-model', readonly=True,
        help="When a relationship field is selected as first field, "
            "this field shows the document model the relationship goes to.")
    sub_model_object_field = fields.Many2one('ir.model.fields', 'Sub-field',
        help="When a relationship field is selected as first field, "
        "this field lets you select the target field within the "
        "destination document model (sub-model).")
    null_value = fields.Char('Default Value',
        help="Optional value to use if the target field is empty")
    copyvalue = fields.Char('Placeholder Expression',
        help="Final placeholder expression, to be copy-pasted in the desired"\
            " template field.")

    @api.onchange('model_id')
    def onchange_model_id(self):
        '''
            This method will be fetch the model id..
            
            @param self: The object pointer.
        '''
        for rec in self:
            if rec.model_id:
                rec.model = rec.model_id.model

