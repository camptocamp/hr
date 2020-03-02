from odoo import models, api


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
