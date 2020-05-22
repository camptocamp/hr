# -*- coding: utf-8 -*-

import StringIO
import logging
import os

import mt940

from odoo import models

_logger = logging.getLogger(__name__)


class AccountBankStatementImport(models.TransientModel):
    _inherit = "account.bank.statement.import"

    def import_mt940_files(self):
        dir_path = self._get_mt940_files_path()
        if not dir_path:
            _logger.info("""mt940 files Path not found,
            please check your settings """)
            return
        files_list = os.listdir(dir_path)
        to_delete = self._get_delete_option()
        for f in files_list:
            file_path = os.path.join(dir_path, f)
            with open(file_path, 'rb') as mt940_file:
                mt940_file = mt940_file.read()
                name = str(f)
                mt940_rec = self._get_or_create_mt940_rec(name, mt940_file)
                if mt940_rec.status == 'Imported':
                    if to_delete:
                        mt940_rec.delete_file(os.path.join(dir_path, f))
                    continue
                journal_id = self._get_journal(mt940_file)
                ctx = {'journal_id': journal_id.id}
                mt940_file_encoded = mt940_file.encode('base64')
                import_wizard = self.with_context(ctx).create({
                    'data_file': mt940_file_encoded
                })
                try:
                    # à modifier
                    self.env.user.company_id = journal_id.company_id.id
                    res = import_wizard.import_file()
                    statement_ids = res.get('context', {}).get('statement_ids')
                    if statement_ids:
                        mt940_rec.write({
                            'status': 'Imported',
                            'statement_id': statement_ids[0]
                        })
                        if to_delete:
                            mt940_rec.delete_file(os.path.join(dir_path, f))
                    if res.get('name') == 'Journal Creation':
                        mt940_rec.write({'status': 'Missing Journal'})
                except ValueError, e:
                    mt940_rec.write({'status': '%s' % e})
                except Exception, e:
                    mt940_rec.write({'status': '%s %s' % (e.name, e.message)})

    def _get_or_create_mt940_rec(self, name, content):
        mt940_rec = self.env['mt940.file'].search([
            ('name', '=', name),
            ('content', '=', content),
        ])
        if not mt940_rec:
            mt940_rec = self.env['mt940.file'].create({
                'name': name,
                'content': content
            })
        return mt940_rec

    def _get_journal(self, mt940_file_content):
        journal_obj = self.env['account.journal']
        try:
            account = mt940.parse(StringIO.StringIO(mt940_file_content)).data[
                'account_identification']
            journal = journal_obj.search([
                ('bank_account_id.sanitized_acc_number', '=', account),
                ('type', '=', 'bank')
            ])
            if len(journal) == 1:
                return journal
        except Exception, e:
            _logger.info(e)
        return journal_obj

    def _get_mt940_files_path(self):
        conf = self.env['ir.config_parameter']
        dir_path = conf.get_param('mt940.mt940_files_path', '')
        if not os.path.exists(dir_path):
            return False
        return dir_path

    def _get_delete_option(self):
        conf = self.env['ir.config_parameter']
        return conf.get_param('mt940.delete_imported_files')
