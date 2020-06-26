# -*- coding: utf-8 -*-
from odoo import models, fields


class UbersmithContractTerm(models.Model):
    _name = 'ubersmith.contract.term'
    _rec_name = 'name'

    contract_term_id = fields.Char(
        string="Contract Term ID"
    )
    name = fields.Char(
        string="Name"
    )
    status = fields.Boolean(
        string="Status"
    )
    term = fields.Integer(
        string="Term"
    )

    def create_or_sync_terms(self):
        api = self.env['ubersmith.api']
        terms = api.get_terms_list()
        for term_id, term_dict in terms.iteritems():
            self.create_or_sync_term(term_dict)

    def create_or_sync_term(self, term_dict):
        term = self.search([
            ('contract_term_id', '=', term_dict['contract_term_id'])
        ])
        if not term:
            term = self.create({
                'contract_term_id': term_dict['contract_term_id'],
                'name': term_dict['name'],
                'status': bool(int(term_dict['status'])),
                'term': int(term_dict['term'])
            })
        if term.name != term_dict['name']:
            term.write({'name': term_dict['name']})
        if term.status != bool(int(term_dict['status'])):
            term.write({'status': bool(int(term_dict['status']))})
        if term.term != int(term_dict['term']):
            term.write({'term': int(term_dict['term'])})
        return term
