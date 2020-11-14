from odoo import models, api


class SaleSubscription(models.Model):
    _inherit = 'sale.subscription'

    @api.multi
    def upsell_action(self):
        wizard = self.env['sale.subscription.wizard'].create(
            {'subscription_id': self.id,
             'account_id': self.analytic_account_id.id
             })
        view = wizard.with_context(active_id=self.id).create_sale_order()
        self.env['sale.order'].browse(view['res_id']).write(
            {'order_type': 'upsell'}
        )
        return view

    @api.multi
    def prepare_renewal_order(self):
        so_view = super(SaleSubscription, self).prepare_renewal_order()
        to_delete_line_ids = []
        for line in self.recurring_invoice_line_ids:
            to_delete_line_ids.append(
                self.env['sale.order.sub_line_remove'].create(
                    {'subscription_line_id': line.id}).id)
        self.env['sale.order'].browse(so_view['res_id']).sudo().write(
            {'order_type': 'renew',
             'to_delete_line_ids': [
                 (6, 0, to_delete_line_ids)],
             }
        )
        return so_view

    @api.multi
    def action_replace_lines(self):
        self.ensure_one()
        wizard = self.env['replace.subscription.lines.wizard'].create(
            {'subscription_id': self.id})
        return {
            'name': 'Replace Options',
            'type': 'ir.actions.act_window',
            'res_model': wizard._name,
            'res_id': wizard.id,
            'view_id': self.env.ref(
                'bso_sales_process.replace_subscription_lines_wizard'
            ).id,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
        }
