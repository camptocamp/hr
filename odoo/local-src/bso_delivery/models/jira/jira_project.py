from odoo import models, fields, exceptions, api


class JiraProject(models.Model):
    _name = 'jira.project'

    name = fields.Char(
        string='name'
    )
    key = fields.Char(
        string='JIRA key'
    )
    description = fields.Char(
        string='description'
    )

    def get(self):
        record = self._get()
        if not record:
            raise exceptions.ValidationError(
                "Project not found, please check settings menu")
        return record

    def _get(self):
        return self.search([], order='id DESC', limit=1)

    @api.constrains('key')
    def check_project_exist(self):
        jira = self.env['jira.api']
        try:
            jira.sudo().project(self.key)
        except Exception:
            raise exceptions.ValidationError(
                'No project could be found with key "%s"' % self.key
            )
