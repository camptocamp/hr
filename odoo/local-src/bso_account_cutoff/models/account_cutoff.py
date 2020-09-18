# -*- coding: utf-8 -*-

from odoo import models


class AccountCutoff(models.Model):
    _inherit = 'account.cutoff'

    def _get_merge_keys(self):
        """ Return merge criteria for provision lines

        The returned list must contain valid field names
        for account.move.line. Provision lines with the
        same values for these fields will be merged.
        The list must at least contain account_id.
        """
        return ['account_id', 'analytic_account_id', 'partner_id']

    def _prepare_move(self, to_provision):
        self.ensure_one()
        movelines_to_create = []
        move_label = self.move_label
        merge_keys = self._get_merge_keys()
        for merge_values, amount in to_provision.items():
            vals = {
                'name': move_label,
                'debit': amount < 0 and amount * -1 or 0,
                'credit': amount >= 0 and amount or 0,
            }
            for k, v in zip(merge_keys, merge_values):
                vals[k] = v
            movelines_to_create.append((0, 0, vals))
            # add counter-part
            vals_counterpart = vals.copy()
            vals_counterpart['account_id'] = self.cutoff_account_id.id
            vals_counterpart['analytic_account_id'] = False
            vals_counterpart['debit'] = vals['credit']
            vals_counterpart['credit'] = vals['debit']
            movelines_to_create.append((0, 0, vals_counterpart))

        res = {
            'journal_id': self.cutoff_journal_id.id,
            'date': self.cutoff_date,
            'ref': move_label,
            'line_ids': movelines_to_create,
        }
        return res

    def _prepare_provision_line(self, cutoff_line):
        """ Convert a cutoff line to elements of a move line

        The returned dictionary must at least contain 'account_id'
        and 'amount' (< 0 means debit).

        If you override this, the added fields must also be
        added in an override of _get_merge_keys.
        """
        return {
            'account_id': cutoff_line.cutoff_account_id.id,
            'analytic_account_id': cutoff_line.analytic_account_id.id,
            'amount': cutoff_line.cutoff_amount,
            'partner_id': cutoff_line.partner_id.id,
        }

    def _prepare_provision_tax_line(self, cutoff_tax_line):
        """ Convert a cutoff tax line to elements of a move line

        See _prepare_provision_line for more info.
        """
        return {
            'account_id': cutoff_tax_line.cutoff_account_id.id,
            'analytic_account_id': cutoff_tax_line.analytic_account_id.id,
            'amount': cutoff_tax_line.cutoff_amount,
            'partner_id': cutoff_tax_line.partner_id.id,
        }
