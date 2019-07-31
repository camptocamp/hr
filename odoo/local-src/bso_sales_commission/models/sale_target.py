from odoo import models, fields, api


class SaleTarget(models.Model):
    _name = 'sale.target'
    _rec_name = 'user_id'

    user_id = fields.Many2one(
        string='Salesperson',
        comodel_name='res.users',
        required=True
    )
    year = fields.Integer(
        string='Year',
        default=fields.Date.from_string(fields.Date.today()).year,
        required=True,
    )
    currency_id = fields.Many2one(
        string='Currency',
        comodel_name='res.currency',
        required=True
    )
    annual_target_nrr = fields.Monetary(
        string='Annual target NRR',
        required=True
    )
    annual_target_mrr = fields.Monetary(
        string='Annual target MRR',
        required=True
    )
    quarter_target_nrr = fields.Monetary(
        string='Quarter target NRR',
        readonly=True,
        compute='compute_quarter_target_nrr',
        store=True
    )
    quarter_target_mrr = fields.Monetary(
        string='Quarter target MRR',
        readonly=True,
        compute='compute_quarter_target_mrr',
        store=True
    )
    _sql_constraints = [
        ('year_user_id_uniq', 'UNIQUE(year, user_id)',
         'A target already exists for this Salesperson, in this year'),
    ]

    @api.depends('annual_target_nrr')
    def compute_quarter_target_nrr(self):
        for rec in self:
            rec.update({
                'quarter_target_nrr': rec.annual_target_nrr / 4
            })

    @api.depends('annual_target_mrr')
    def compute_quarter_target_mrr(self):
        for rec in self:
            rec.update({
                'quarter_target_mrr': rec.annual_target_mrr / 4
            })

    @api.model
    def create(self, values):
        rec = super(SaleTarget, self).create(values)
        commission_quarters = self.get_commission_quarters(rec.user_id.id,
                                                           rec.year)
        if commission_quarters:
            commission_quarters.write({'target_id': rec.id})
        return rec

    @api.multi
    def write(self, values):
        for rec in self:
            if any(v in values for v in ['user_id', 'year']):
                # unlink target before update
                quarters_to_unlink = self.get_commission_quarters(
                    rec.user_id.id, rec.year)
                quarters_to_unlink.write({'target_id': False})

                # link target after update
                user_id = values.get('user_id', rec.user_id.id)
                year = values.get('year', rec.year)
                quarters_to_link = self.get_commission_quarters(
                    user_id, year)
                quarters_to_link.write({'target_id': rec.id})

        return super(SaleTarget, self).write(values)

    def get_commission_quarters(self, user_id, year):
        commission_quarter_o = self.env['salesperson.commission.quarter']
        commission_quarters = commission_quarter_o.search([
            ('user_id', '=', user_id),
            ('year', '=', year)
        ])
        return commission_quarters
