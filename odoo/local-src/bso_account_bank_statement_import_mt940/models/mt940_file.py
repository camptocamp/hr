# -*- coding: utf-8 -*-
import logging
import os

from odoo import models, fields

_logger = logging.getLogger(__name__)


class Mt940File(models.Model):
    _name = "mt940.file"

    name = fields.Char(
        string='File Name',
        required=True,
        readonly=True,
    )
    content = fields.Text(
        string='File Content',
        readonly=True,
    )
    status = fields.Char(
        string='Status',
        readonly=True,
    )
    statement_id = fields.Many2one(
        string='Statement',
        comodel_name='account.bank.statement'
    )

    def delete_file(self, file_path):
        os.remove(file_path)
