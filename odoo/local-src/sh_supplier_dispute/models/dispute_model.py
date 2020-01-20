# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import api, exceptions, fields, models, _

from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
    
class account_invoice_dispute(models.Model):
    _name = "account.invoice.dispute"
    _description = 'Account Invoice Dispute for dispute suppliers'    
    _order = 'id desc'    
    
    name = fields.Char(string='Dispute Reference', copy=False, readonly=True, default=lambda self: _('New'))
    state = fields.Selection([
        ('draft', 'Draft'),
        ('dispute', 'Dispute'),
        ('solved', 'Solved'),
        ], string='Status', readonly=True, copy=False, index=True, default='draft') 
    user_id = fields.Many2one('res.users', string='User', index=True,default=lambda self: self.env.user)
    date = fields.Date(string='Date', required=True, readonly=True, index=True, states={'draft': [('readonly', False)], 'dispute': [('readonly', False)]}, copy=False, default=fields.Date.context_today)    
    dispute_title = fields.Char(string="Title", required=True)
    dispute_description = fields.Text(string='Description')    
    
            
    invoice_id = fields.Many2one('account.invoice', string='Vendor Bill', required=True, ondelete='cascade', index=True)
    
    
    @api.model
    def create(self, vals):       
        
        dispute_name = self.env['ir.sequence'].next_by_code('sequence.supplier.dispute.code')
        vals.update({'name' : dispute_name})
        
        res =  super(account_invoice_dispute,self).create(vals)    
        return res
        
    @api.multi
    def action_solved(self):
        return self.write({'state': 'solved'})        
        
    @api.multi
    def action_draft(self):
        return self.write({'state': 'draft'})    
    
    @api.multi
    def action_dispute(self):
        return self.write({'state': 'dispute'})     
    
    
    
               