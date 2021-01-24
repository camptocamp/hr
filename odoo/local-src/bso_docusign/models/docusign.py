import json

import httplib2
import odoo.addons.docusign.models.docusign as docusign


def new_create_envelope(self, login, recipient, body, subject,
                        file_lst, signature, xoff, yoff, datesigned,
                        xoff_date, yoff_date):
    '''
    This method will be fetch the model id..
    @param self: The object pointer.
    @param login: Login user name
    @param recipient: Recipient name
    @param body: Email body
    @param subject : Email Subject name
    @param file_lst : List file will atteched
    @param signature: A signature position.
    @param xoff: A signature pointer.
    '''

    count = 1
    my_boundary_lst = []
    documents = []
    for file_con in file_lst:
        doc_envelop = {
            "documentId": str(count),
            "name": file_con['fname']
        }
        documents.append(doc_envelop)
        fileContents = open(file_con['fname'], "rb").read()
        my_boundary = "\r\n\r\n--MYBOUNDARY\r\n" + \
                      "Content-Type:" + str(file_con['ftype']) + "\r\n" + \
                      "Content-Disposition: file; filename=\"" + \
                      str(file_con['fname']) + \
                      "\"; documentId=" + str(count) + "\r\n" + \
                      "\r\n" + \
                      fileContents + "\r\n"
        my_boundary_lst.append(my_boundary)
        count += 1
    envelope = {
        "emailBlurb": body,
        "emailSubject": subject,
        "documents": documents,
        "recipients": {
            "signers": _get_signers(self, recipient, self.signer_ids)
        },
        "status": "sent"
    }
    requestBody = "\r\n\r\n--MYBOUNDARY\r\n" + \
                  "Content-Type: application/json\r\n" + \
                  "Content-Disposition: form-data\r\n" + \
                  "\r\n"
    if my_boundary_lst:
        for my_bound in my_boundary_lst:
            requestBody += json.dumps(envelope) + my_bound
    requestBody += "--MYBOUNDARY--\r\n\r\n"
    url = ''
    if login['baseurl']:
        url = str(login['baseurl'] + "/envelopes")
    headers = {'X-DocuSign-Authentication': login['auth_str'],
               'Content-Type': 'multipart/form-data; boundary=MYBOUNDARY',
               'Accept': 'application/json'}
    http = httplib2.Http()
    try:
        response, content = http.request(url,
                                         'POST',
                                         headers=headers,
                                         body=requestBody)
    except Exception, e:
        raise Warning("%s." % e)
    return response, content


def _get_signers(self, recipient, signer_ids):
    if not signer_ids and recipient:
        return [{
            "email": recipient.email,
            "name": recipient.name,
            "recipientId": 1,
        }]
    signers = []
    for count, signer in enumerate(signer_ids, 1):
        anchor_id = signer.anchor_id
        signer = {
            "email": signer.partner_id.email,
            "name": signer.partner_id.name,
            "recipientId": count,
            "tabs": {
                "dateSignedTabs": _get_date_tabs(self,
                                                 anchor_id.signature_type),
                "fullNameTabs": _get_name_tabs(self,
                                               anchor_id.signature_type),
                "signHereTabs": _get_sign_tabs(anchor_id),
                "titleTabs": _get_title_tabs(self,
                                             anchor_id.signature_type),
                # "textTabs": _get_name_tabs(self,
                #                            anchor_id.signature_type)

            },
            "routingOrder": signer.routing_order
        }
        signers.append(signer)
    return signers


def _get_date_tabs(self, signature_type):
    date_anchor_id = self.docusign_template_id.get_anchor(signature_type,
                                                          'date')
    if not date_anchor_id:
        return []
    return [
        {
            "anchorString": date_anchor_id.anchor_str,
            "anchorXOffset": date_anchor_id.xoff,
            "anchorYOffset": date_anchor_id.yoff,
            "anchorIgnoreIfNotPresent":
                date_anchor_id.ignore_if_not_present,
            "anchorUnits": date_anchor_id.units
        }
    ]


def _get_name_tabs(self, signature_type):
    name_anchor_id = self.docusign_template_id.get_anchor(signature_type,
                                                          'name')
    if not name_anchor_id:
        return []
    return [
        {
            "anchorString": name_anchor_id.anchor_str,
            # "name": name,
            "anchorXOffset": name_anchor_id.xoff,
            "anchorYOffset": name_anchor_id.yoff,
            "anchorIgnoreIfNotPresent":
                name_anchor_id.ignore_if_not_present,
            "anchorUnits": name_anchor_id.units,
            # "lock": True
        }
    ]


def _get_sign_tabs(anchor_id):
    if not anchor_id:
        return []
    return [
        {
            "anchorString": anchor_id.anchor_str,
            "anchorXOffset": anchor_id.xoff,
            "anchorYOffset": anchor_id.yoff,
            "anchorIgnoreIfNotPresent": anchor_id.ignore_if_not_present,
            "anchorUnits": anchor_id.units
        }
    ]


def _get_title_tabs(self, signature_type):
    title_anchor_id = self.docusign_template_id.get_anchor(signature_type,
                                                           'title')
    if not title_anchor_id:
        return []
    return [
        {
            "anchorString": title_anchor_id.anchor_str,
            "anchorXOffset": title_anchor_id.xoff,
            "anchorYOffset": title_anchor_id.yoff,
            "anchorIgnoreIfNotPresent": title_anchor_id.ignore_if_not_present,
            "anchorUnits": title_anchor_id.units
        }
    ]


docusign.create_envelope = new_create_envelope
