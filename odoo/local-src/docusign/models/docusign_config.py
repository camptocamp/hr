# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

import docusign
import json

from odoo import api, fields, models
from odoo.exceptions import Warning


class DocusignConfig(models.Model):
    _name = 'docusign.config'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Docusign Configuration"
    
    
    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state == 'confirm':
                raise Warning("Not Allowed to delete confirmed Docusign")
            return super(DocusignConfig, self).unlink()

    name = fields.Char('Description', readonly=True,
                        states={'draft': [('readonly', False)]})
    docusign_user = fields.Char('Username',readonly=True,
                                states={'draft': [('readonly', False)]},
                                help="username for Docusign authentication")
    docusign_pass = fields.Char('Password',readonly=True,
                                 states={'draft': [('readonly', False)]},
                                help="password for Docusign authentication")
    docusign_key = fields.Char('API Key',readonly=True,
                                states={'draft': [('readonly', False)]},
                               help="Key for Docusign authentication")
    docusign_baseurl = fields.Char('BaseUrl',readonly=True,
                                    states={'draft': [('readonly', False)]},
                                   help="This is the baseUrl for docusign")
    docusign_acc_no = fields.Integer('Account Id',readonly=True,
                                      states={'draft': [('readonly', False)]})
    docusign_authstr = fields.Char('Docusign Authstr',readonly=True,
                                    states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirmed')],
                             'State',default="draft",
                             readonly=True, states={'draft': [('readonly', False)]})
    url = fields.Char('URL', help="url for docusign server",readonly=True,
                       states={'draft': [('readonly', False)]})
    

    @api.multi
    def test_docusign_connection(self):
        '''
            This method will be check the connection to docusign..
            @param self: The object pointer.
        '''
        
        for self_obj in self:
            response, content, auth = docusign.docusign_login(self_obj.docusign_user,
                self_obj.docusign_pass, self_obj.docusign_key,
                self_obj.url)
            content = content and json.loads(content) or False
            msg = ("<b>Test Connection Successful with Docusign.</b>")
            if response.get('status') != '200':
                raise Warning("Test Failed !   "+response.get('status'))
                msg = ("<b>%s</b> : %s If you are not an Administrator then"\
                       " Please contact your Administrator on <b>%s</b>") % \
                       (content and content.get('errorCode') or False,
                        content and content.get('message') or False,
                        self.env.user and self.env.user.email or False)
            else:
                login_info = content.get('loginAccounts')
                info = login_info and login_info[0] or False
                if info:
                    self.write({'docusign_baseurl': info['baseUrl'],
                                'docusign_acc_no': info['accountId'],
                                'state': 'confirm', 'docusign_authstr': auth})
            self_obj.message_post(body=msg)
        return True

