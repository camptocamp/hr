# -*- coding: utf-8 -*-


from odoo import models, fields, exceptions, api, _

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from os import urandom


class JiraSettings(models.Model):
    _name = 'jira.settings'

    RSA_BITS = 4096
    RSA_PUBLIC_EXPONENT = 65537
    KEY_LEN = 255  # 255 == max Atlassian db col len

    _sql_constraints = [
        ('unique_name', 'UNIQUE (name)', "Settings already exists")
    ]

    name = fields.Char(
        default='Settings',
        readonly=True
    )
    jira_url = fields.Char(
        string='Jira URL',
        required=True,
    )

    def get(self):
        record = self._get()
        if not record:
            raise exceptions.ValidationError(
                "Settings not found, please check settings menu")
        return record

    def _get(self):
        return self.search([], order='id DESC', limit=1)

    def action_settings(self):
        return {
            "name": "Settings",
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "target": "inline",
            "res_model": self._name,
            "res_id": self._get().id,
        }

    def do_auth(self):
        # jira = self.env['jira.api']
        # jira.issue('PP-2')
        # jira.user('mohammed.janatiidrissi@bsonetwork.com')
        # jira.project('PP')
        # jira.project_issue_type('PP')
        self.create_rsa_key_vals()
        auth = self.env['jira.auth'].create({'settings_id': self.id})
        return auth.auth_action()

    private_key = fields.Text(
        readonly=True,
    )
    public_key = fields.Text(readonly=True)
    consumer_key = fields.Char(
        default=lambda self: self._default_consumer_key(),
        readonly=True,
    )

    access_token = fields.Char(
        readonly=True,
    )
    access_secret = fields.Char(
        readonly=True,
    )
    verify_ssl = fields.Boolean(default=True, string="Verify SSL?")

    @api.multi
    def create_rsa_key_vals(self):
        """ Create public/private RSA keypair """
        for setting in self:
            private_key = rsa.generate_private_key(
                public_exponent=self.RSA_PUBLIC_EXPONENT,
                key_size=self.RSA_BITS,
                backend=default_backend()
            )
            pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            )
            public_pem = private_key.public_key().public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            setting.write({
                'private_key': pem,
                'public_key': public_pem,
            })

    @api.multi
    def state_setup(self):
        for backend in self:
            if backend.state == 'authentify':
                backend.state = 'setup'

    def _default_consumer_key(self):
        ''' Generate a rnd consumer key of length self.KEY_LEN '''
        return urandom(self.KEY_LEN).encode('hex')[:self.KEY_LEN]

    state = fields.Selection(
        selection=[
            ('authentify', 'Authentify'),
            ('setup', 'Setup'),
            ('running', 'Running')],
        default='authentify',
        required=True,
        readonly=True,
    )

    @api.multi
    def test_auth(self):
        res = self.env['jira.api']._get_oauth_session().get(
            '%s%s' % (self.jira_url, '/rest/api/3/serverInfo'))
        if res.status_code == 200:
            return self.env['jira.auth'].create(
                {'settings_id': self.id, 'state': 'done'}
            ).auth_action()
        raise exceptions.AccessError(_('Auth Broken'))
