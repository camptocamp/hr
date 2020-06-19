import requests
from oauthlib.oauth1 import SIGNATURE_RSA
from requests_oauthlib import OAuth1
from urlparse import parse_qsl

from odoo import models, api, fields, exceptions, _


class JiraAuth(models.TransientModel):
    _name = 'jira.auth'

    OAUTH_BASE = 'plugins/servlet/oauth'

    settings_id = fields.Many2one('jira.settings')
    state = fields.Selection([
        ('leg_1', 'OAuth Remote Config'),
        ('leg_2', 'OAuth Remote Auth'),
        ('done', 'Complete')
    ], default='leg_1')

    consumer_key = fields.Char(
        related='settings_id.consumer_key',
        readonly=True,
    )
    public_key = fields.Text(
        related='settings_id.public_key',
        readonly=True,
    )

    # fields populated by leg_1
    request_token = fields.Char(readonly=True)
    request_secret = fields.Char(readonly=True)
    auth_uri = fields.Char(readonly=True)

    @api.model
    def _next_action(self):
        act = self.auth_action()
        act['res_id'] = self.id
        return act

    @api.multi
    def generate_new_key(self):
        self.settings_id.create_rsa_key_vals()
        jira_model = self.env['jira.settings']
        self.settings_id.consumer_key = jira_model._default_consumer_key()
        return self._next_action()

    @api.multi
    def do_oauth_leg_1(self):
        oauth_hook = OAuth1(
            client_key=self.consumer_key,
            client_secret='',
            signature_method=SIGNATURE_RSA,
            rsa_key=self.settings_id.private_key,
        )
        try:
            req = requests.post(
                '%s/%s/request-token' % (
                    self.settings_id.jira_url, self.OAUTH_BASE),
                verify=self.settings_id.verify_ssl, auth=oauth_hook
            )
        except requests.exceptions.SSLError as err:
            raise exceptions.UserError(
                _('SSL error during negociation: %s') % (err,)
            )
        resp = dict(parse_qsl(req.text))

        token = resp.get('oauth_token')
        secret = resp.get('oauth_token_secret')

        if None in [token, secret]:
            raise exceptions.UserError(
                _('Did not get token (%s) or secret (%s) from Jira. Resp %s') %
                (token, secret, resp)
            )

        self.write({
            'request_token': token,
            'request_secret': secret,
            'auth_uri': '%s/%s/authorize?oauth_token=%s' % (
                self.settings_id.jira_url, self.OAUTH_BASE, token
            ),
        })
        self.state = 'leg_2'
        return self._next_action()

    @api.multi
    def do_oauth_leg_3(self):
        """ Perform OAuth step 3 to get access_token and secret """
        oauth_hook = OAuth1(
            client_key=self.consumer_key,
            client_secret='',
            signature_method=SIGNATURE_RSA,
            rsa_key=self. settings_id.private_key,
            resource_owner_key=self.request_token,
            resource_owner_secret=self.request_secret,
        )
        try:
            req = requests.post(
                '%s/%s/access-token' % (
                    self.settings_id.jira_url, self.OAUTH_BASE),
                verify=self.settings_id.verify_ssl, auth=oauth_hook
            )
        except requests.exceptions.SSLError as err:
            raise exceptions.UserError(
                _('SSL error during negociation: %s') % (err,)
            )
        resp = dict(parse_qsl(req.text))

        token = resp.get('oauth_token')
        secret = resp.get('oauth_token_secret')

        if None in [token, secret]:
            raise exceptions.UserError(
                _('Did not get token (%s) or secret (%s) from Jira. Resp %s') %
                (token, secret, resp)
            )

        self.settings_id.write({
            'access_token': token,
            'access_secret': secret,
        })
        self.state = 'done'
        self.settings_id.state_setup()
        return self._next_action()

    @api.multi
    def auth_action(self):
        self.ensure_one()
        view_id = self.env.ref('bso_connector_jira.view_jira_auth_form').id
        return {
            'type': 'ir.actions.act_window',
            'name': 'My Action Name',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': self._name,
            'res_id': self.id,
            'views': [(view_id, 'form')],
            'target': 'new',
        }
