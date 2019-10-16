from jira import JIRAError
from odoo import models, api


class JiraBackend(models.Model):
    _inherit = 'jira.backend'

    @api.multi
    def jira_key_exist(self, key):
        self.ensure_one()
        try:
            return self.get_api_client().project(key).id
        except JIRAError:
            return False
