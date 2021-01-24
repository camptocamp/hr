# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

import json
import tempfile

import httplib2
from odoo.exceptions import Warning


def docusign_login(username, password, api_key, url, context={}):
    authenticateStr = "<DocuSignCredentials>" \
                      "<Username>%s</Username>" \
                      "<Password>%s</Password>" \
                      "<IntegratorKey>%s</IntegratorKey>" \
                      "</DocuSignCredentials>" % (username, password, api_key)
    headers = {'X-DocuSign-Authentication': authenticateStr,
               'Accept': 'application/json'}
    http = httplib2.Http()
    try:
        response, content = http.request(url, 'GET', headers=headers)
    except Exception, e:
        raise Warning("%s." % e)
    return response, content, authenticateStr


def create_envelope(self, login, recipient, body, subject,
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
    rec_email = recipient.email
    rec_name = recipient.name
    if datesigned:
        count = 1
        envelopeDef = "{\"emailBlurb\":\"" + str(body) + "\"," + \
                      "\"emailSubject\":\"" + str(subject) + "\"," + \
                      "\"documents\":["
        my_boundary_lst = []
        doc_envelop = ""
        for file_con in file_lst:
            doc_envelop += \
                "{ \"documentId\":\"" + str(count) + "\"," + \
                "\"name\":\"" + str(file_con['fname']) + "\"},"

            fileContents = open(str(file_con['fname']), "rb").read()
            my_boundary = "\r\n\r\n--MYBOUNDARY\r\n" + \
                          "Content-Type:" + str(file_con['ftype']) + "\r\n" + \
                          "Content-Disposition: file; filename=\"" + \
                          str(file_con['fname']) + \
                          "\"; documentId=" + str(count) + "\r\n" + \
                          "\r\n" + \
                          fileContents + "\r\n"
            #                my_boundary = my_boundary.decode('ascii','ignore')
            my_boundary_lst.append(my_boundary)
            count += 1
        envelopeDef += doc_envelop
        envelopeDef += "]," + \
                       "\"recipients\":{" + \
                       "\"signers\":[{" + \
                       "\"email\":\"" + str(rec_email) + "\"," + \
                       "\"name\":\"" + str(rec_name) + " \"," + \
                       "\"recipientId\":\"1\"," + \
                       "}]}," + \
                       "\"status\":\"sent\"}"
        #            "\"tabs\":{" + \
        #            "\"dateSignedTabs\": [{" + \
        #            "\"anchorString\": \"" + str(datesigned) + "\", " + \
        #            "\"anchorXOffset\": \"" + str(xoff_date) + "\", " + \
        #            "\"anchorYOffset\": \"" + str(yoff_date) + "\"," + \
        #            "\"anchorIgnoreIfNotPresent\": \"false\"," + \
        #            "\"anchorUnits\": \"inches\"" + "}]," + \
        #            "\"signHereTabs\":[{" + \
        #            "\"anchorString\": \"" + str(signature) + "\", " + \
        #            "\"anchorXOffset\": \"" + str(xoff) + "\", " + \
        #            "\"anchorYOffset\": \"" + str(yoff) + "\"," + \
        #            "\"anchorIgnoreIfNotPresent\": \"false\"," + \
        #            "\"anchorUnits\": \"inches\"" + "

        requestBody = "\r\n\r\n--MYBOUNDARY\r\n" + \
                      "Content-Type: application/json\r\n" + \
                      "Content-Disposition: form-data\r\n" + \
                      "\r\n"
        if my_boundary_lst:
            for my_bound in my_boundary_lst:
                requestBody += envelopeDef + my_bound
        requestBody += "--MYBOUNDARY--\r\n\r\n"

    else:
        envelopeDef = "{\"emailBlurb\":\"" + str(body) + "\"," + \
                      "\"emailSubject\":\"" + str(subject) + "\"," + \
                      "\"documents\":["

        count = 1
        doc_envelop = ""
        my_boundary_lst = []

        for file_con in file_lst:
            doc_envelop += \
                "{ \"documentId\":\"" + str(count) + "\"," + \
                "\"name\":\"" + str(file_con['fname']) + "\"},"

            fileContents = open(str(file_con['fname']), "rb").read()
            my_boundary = \
                "\r\n\r\n--MYBOUNDARY\r\n" + \
                "Content-Type: " + str(file_con['ftype']) + "\r\n" + \
                "Content-Disposition: file; filename=\"" + \
                str(file_con['fname']) + \
                "\"; documentId=" + str(count) + "\r\n" + \
                "\r\n" + \
                fileContents + "\r\n"
            my_boundary_lst.append(my_boundary)
            count += 1
        envelopeDef += doc_envelop
        envelopeDef += " ], \"recipients\":{" + \
                       "\"signers\":[{" + \
                       "\"email\":\"" + str(rec_email) + "\"," + \
                       "\"name\":\"" + str(rec_name) + " \"," + \
                       "\"recipientId\":\"1\"," + \
                       "}]}," + \
                       "\"status\":\"sent\"}"
        # "\"tabs\":{" + \
        # "\"signHereTabs\":[{" + \
        # "\"anchorString\": \"" + str(signature) + "\", " + \
        # "\"anchorXOffset\": \"" + str(xoff) + "\", " + \
        # "\"anchorYOffset\": \"" + str(yoff) + "\"," + \
        # "\"anchorIgnoreIfNotPresent\": \"false\"," + \
        # "\"anchorUnits\": \"inches\"" + \
        requestBody = "\r\n\r\n--MYBOUNDARY\r\n" + \
                      "Content-Type: application/json\r\n" + \
                      "Content-Disposition: form-data\r\n" + \
                      "\r\n"
        if my_boundary_lst:
            for bound in my_boundary_lst:
                requestBody += envelopeDef + bound
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


def req_env_status_url(self, login, envid):
    '''
    This method will be fetch the login user id and environment id.
    @param self: The object pointer.
    @param login : The login user id
    @param envid: The environment id.
    '''
    url = login['baseurl'] + '/envelopes?envelopeId=' + envid
    headers = {'X-DocuSign-Authentication': login['auth_str'],
               'Accept': 'application/json'}
    http = httplib2.Http()
    try:
        response, content = http.request(url, 'GET', headers=headers)
    except Exception, e:
        raise Warning("%s." % e)
    return response, content


def req_decline_env_status(self, login, envid):
    '''
    This method will be fetch the login user id and environment id.
    @param self: The object pointer.
    @param login : The login user id
    @param envid: The environment id.
    '''
    url = login['baseurl'] + '/envelopes/' + envid + '/recipients'
    headers = {'X-DocuSign-Authentication': login['auth_str'],
               'Accept': 'application/json'}
    http = httplib2.Http()
    try:
        response, content = http.request(url, 'GET', headers=headers)
    except Exception, e:
        raise Warning("%s." % e)
    return response, content


def download_documents(self, login, req_info):
    '''
    This method will be download the document from the docusign.
    @param self: The object pointer.
    @param login : The login user id
    @param req_info: This will fetch the request information.
    '''
    url = login['baseurl'] + req_info + "/documents"
    headers = {'X-DocuSign-Authentication': login['auth_str'],
               'Accept': 'application/json'}
    http = httplib2.Http()
    try:
        response, content = http.request(url, 'GET', headers=headers)
    except Exception, e:
        raise Warning("%s." % e)
    if response.get('status') != '200':
        return response, content
    data = json.loads(content)
    envelopeDocs = data.get('envelopeDocuments')
    uriList = []
    file_lst = []
    for docs in envelopeDocs:
        if docs['documentId'] != 'certificate':
            uriList.append(docs.get("uri"))
            url = login['baseurl'] + uriList[len(uriList) - 1]
            headers = {'X-DocuSign-Authentication': login['auth_str']}
            http = httplib2.Http()
            try:
                response_doc, content_doc = http.request(url, 'GET',
                                                         headers=headers)
            except Exception, e:
                raise Warning("%s." % e)
            if response_doc.get('status') == '200':
                file_name = docs.get("name").split('/')
                directory_name = tempfile.mkdtemp()
                filename = directory_name + "/%s" % (file_name and
                                                     file_name[-1] or
                                                     'doc.pdf')
                file_temp = open(filename, 'w')
                file_temp.write(content_doc)
                file_temp.close()
                file_lst.append(filename)
    return response_doc, file_lst, content_doc
