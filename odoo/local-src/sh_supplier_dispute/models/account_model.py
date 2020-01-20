# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import api, exceptions, fields, models, _

from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
    
class account_invoice(models.Model):
    _inherit = "account.invoice"
    
    dispute_line_ids = fields.One2many('account.invoice.dispute', 'invoice_id', string='Dispute Lines',
        readonly=True, states={'draft': [('readonly', False)],'open': [('readonly', False)]}, copy=True)    
    
    
    
class account_register_payments(models.TransientModel):
    _inherit = "account.register.payments"


    @api.model
    def default_get(self, fields):
        active_ids = self._context.get('active_ids')

        if not active_ids:
            raise UserError(_("Programming error: wizard action executed without active_ids in context."))
        
        if active_ids:
            search_dispute_bills = self.env['account.invoice.dispute'].search([('invoice_id','in',active_ids),('state','=','dispute')])
            if search_dispute_bills:
                list_inv = []
                for rec in search_dispute_bills:
                    if rec.invoice_id.number not in list_inv:
                        list_inv.append(rec.invoice_id.number)                    
                raise UserError(_("Some Bill %s has %s vendor dispute. Please solve this dispute in order to register payment.")
                                    % (str(list_inv).replace("[", "").replace("]", "").replace("'", ""),len(search_dispute_bills.ids)))
                        
        rec = super(account_register_payments, self).default_get(fields)
        
        return rec    
    
    
class account_payment(models.Model):
    _inherit = "account.payment"

    @api.model
    def default_get(self, fields):
        rec = super(account_payment, self).default_get(fields)
        invoice_defaults = self.resolve_2many_commands('invoice_ids', rec.get('invoice_ids'))
        if invoice_defaults and len(invoice_defaults) == 1:
            invoice = invoice_defaults[0]
            if invoice['type'] == 'in_invoice':
                search_dispute = self.env['account.invoice.dispute'].search([
                    ('invoice_id','=',invoice['id']),
                    ('state','=','dispute'),
                    ])
                if search_dispute:
                    raise UserError(_("This bill has %s vendor dispute. Please solve this dispute in order to register payment.")
                                    % len(search_dispute.ids))                    

        return rec