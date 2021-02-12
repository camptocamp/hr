# -*- coding: utf-8 -*-
# import base64
# import hashlib
# import hmac
import logging

from odoo.addons.web.controllers.main import ensure_db
from odoo.http import request

from odoo import http
from ..models.docusign_signer import DocusignSigner as DS

_logger = logging.getLogger(__name__)


class WebhookController(http.Controller):

    @http.route('/bso_docusign/webhooks', type='json', auth='none',
                method=['POST'])
    def webhooks(self):
        ensure_db()
        document_model = request.env['docusign.document'].sudo()
        data = request.jsonrequest
        envelope_id = data.get('envelopeId')
        document = document_model.get_document(envelope_id)
        if not document:
            return
        docusign_states_keys = [s[0] for s in DS.DOCUSIGN_RECIPIENT_STATES]
        if data.get('status') == 'completed':
            self._update_signers_state(data, document, docusign_states_keys)
            document.download_attachments()
            document.write({'state': 'completed'})
            if not document.model or not document.res_id:
                return
            update_state = document.docusign_template_id.update_state
            rec = self._get_so(document)
            rec._update_so(update_state)
        if data.get('status') in ('sent', 'delivered'):
            self._update_signers_state(data, document, docusign_states_keys)

    @staticmethod
    def _update_signers_state(data, document, docusign_states_keys):
        recipients = data.get('recipients', {})
        signers = recipients.get('signers', [])
        # match docusign signers with document.signer_ids
        for docusign_signer in signers:
            odoo_signer = document.signer_ids.filtered(
                lambda x: x.routing_order == int(docusign_signer[
                                                     'routingOrder']))
            status = docusign_signer.get('status')
            if status in docusign_states_keys:
                odoo_signer.write({'status': status})
            else:
                _logger.warning("%s Unknown Docusign status" % status)

    @staticmethod
    def _get_so(document):
        return request.env[document.model].sudo().browse(
            document.res_id).exists()

    # @staticmethod
    # def compute_hash(secret, payload):
    #     hash_bytes = hmac.new(secret, msg=payload,
    #                           digestmod=hashlib.sha256).digest()
    #     base_64_hash = base64.b64encode(hash_bytes)
    #     return base_64_hash
    #
    # def is_valid_hash(self, secret, payload, signature):
    #     return signature == self.compute_hash(secret, payload)
