from odoo import models, fields, api, exceptions


class JiraProductTemplate(models.Model):
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

    @api.constrains('template_key')
    def check_template_exists(self):
        jira = self.env['jira.api']
        if not jira.sudo().issue(self.template_key):
            raise exceptions.ValidationError(
                'No issue could be found with key "%s"' % self.template_key
            )
