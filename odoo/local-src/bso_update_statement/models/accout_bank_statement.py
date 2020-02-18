from odoo import models, api
from odoo.exceptions import ValidationError


class AccountBankStatement(models.Model):
    _inherit = 'account.bank.statement'

    @api.multi
    def append_to_statement_action(self):
        self.ensure_one()
        return self.env['account.journal'].import_statement()

    @api.multi
    def merge_statements_action(self):
        if len(self) < 2:
            raise ValidationError(
                'You must choose 2 or more statements to merge'
            )
        older_rec = self.search([('id', 'in', self.ids)])[-1]
        for statement in self - older_rec:
            for line in statement.line_ids:
                line.statement_id = older_rec.id
            statement.unlink()
