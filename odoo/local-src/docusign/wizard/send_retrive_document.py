# -*- coding: utf-8 -*-
# © 2018 Serpent Consulting Services Pvt. Ltd. (support@serpentcs.com)

from odoo import api, models


class SendOrRetrieveDocument(models.TransientModel):
    _name = 'send.retrieve.document'

    @api.multi
    def send_or_retrieve_document(self):
        '''
            This method will be send and retrieve the document..
            
            @param self: The object pointer.
        '''
        context = dict(self.env.context)
        doc_obj = self.env['docusign.document']
        docsign_ids = doc_obj.browse(context['active_ids'])
        if 'active_ids' in context:
            if 'click_send' in context and context['click_send']:
                docsign_ids.send_document_cron()
            elif 'click_retrieve' in context and context['click_retrieve']:
                docsign_ids.download_document_cron()
        return {'type': 'ir.actions.act_window_close'}
