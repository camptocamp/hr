from datetime import date

from odoo import api, models


class CrmLead(models.Model):
    _inherit = "crm.lead"

    @api.model
    def retrieve_sales_dashboard(self):
        res = super(CrmLead, self).retrieve_sales_dashboard()
        if not self.env.user.has_group(
                'bso_sales_commission.group_sales_commission_user'):
            return res
        total_signed_so = self.get_number_of_signed_so_in_this_quarter()
        target = self.get_target_in_this_year()
        earnings = self.get_earnings_in_this_quarter()

        res['performance'] = {
            'this_quarter': {
                'total_signed_so': total_signed_so,
                'nrr': sum(earnings.mapped('earnings_nrr')),
                'mrr': sum(earnings.mapped('earnings_mrr')),
            }
        }

        res['target'] = {
            'this_quarter': {
                'nrr': target.quarter_target_nrr,
                'mrr': target.quarter_target_mrr,
            }
        }
        res['currency_id'] = target.currency_id.id
        return res

    def get_number_of_signed_so_in_this_quarter(self):
        sale_order = self.env['sale.order']
        start_date, end_date = sale_order.get_this_quarter_start_end_date()
        return self.env['sale.order'].search_count([
            ('state', '=', 'sale'),
            ('confirmation_date', '>=', start_date),
            ('confirmation_date', '<=', end_date),
            '|',
            ('user_id', '=', self.env.uid),
            ('salesperson_commission_line_ids.user_id', 'in', [self.env.uid]),
        ])

    def get_target_in_this_year(self):
        current_year = date.today().year
        return self.env['sale.target'].search([
            ('user_id', '=', self.env.uid),
            ('year', '=', current_year)
        ])

    def get_earnings_in_this_quarter(self):
        sale_order = self.env['sale.order']
        start_date, end_date = sale_order.get_this_quarter_start_end_date()
        return self.env['salesperson.commission.line'].search([
            ('order_id.state', '=', 'sale'),
            ('order_id.confirmation_date', '>=', start_date),
            ('order_id.confirmation_date', '<=', end_date),
            ('user_id', '=', self.env.uid),
        ])
