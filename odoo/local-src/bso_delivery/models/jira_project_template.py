from odoo import models, fields, api, exceptions
from odoo.exceptions import ValidationError


class JiraProjectTemplate(models.Model):
    _name = 'jira.product.template'
    _order = 'name ASC, id ASC'

    name = fields.Char(
        string='name'
    )
    default = fields.Boolean(
        string='Default',
        default=False
    )
    template_key = fields.Char(
        string='JIRA key'
    )
    description = fields.Char(
        string='description'
    )

    category_id = fields.Many2one(
        string='Product',
        comodel_name='product.category'
    )


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
        jira = self.env['jira.backend'].search([], limit=1).get_api_client()
        try:
            jira.project(self.key)
        except Exception:
            raise ValidationError(
                'No project could be found with key "%s"' % self.key
            )
