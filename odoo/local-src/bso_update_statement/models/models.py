# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import psycopg2


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


class AccountBankStmtImportCSV(models.TransientModel):
    _inherit = 'base_import.import'

    @api.multi
    def do(self, fields, options, dryrun=False):
        if self.env.context.get('active_model') == 'account.bank.statement':
            options['bank_stmt_import'] = False
            statement = self.env[self.env.context['active_model']].browse(
                self.env.context['active_id'])
            return super(
                AccountBankStmtImportCSV,
                self.with_context(bank_statement_id=statement.id)
            ).do(
                fields, options, dryrun=dryrun
            )
        return super(AccountBankStmtImportCSV, self).do(
            fields,
            options,
            dryrun=dryrun
        )
