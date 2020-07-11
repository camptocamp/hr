from odoo import models, api, fields


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
        self.env['sale.order'].browse(so_view['res_id']).write(
            {'order_type': 'renew',
             'to_delete_line_ids': [
                 (6, 0, self.recurring_invoice_line_ids.ids)],
             }
        )
        return so_view

    @api.multi
    def action_replace_lines(self):
        self.ensure_one()
        wizard = self.env['replace.subscription.lines.wizard'].create(
            {'subscription_id': self.id})
        # wizard = self.env['replace.subscription.lines.wizard'].create(
        #     {'subscription_line_ids': [
        #         (6, 0, [self.recurring_invoice_line_ids.ids])]})
        context = dict(self.env.context)
        context['form_view_initial_mode'] = 'edit'

        return {
            'name': 'Replace Options',
            'type': 'ir.actions.act_window',
            'res_model': wizard._name,
            'res_id': wizard.id,
            'view_id': self.env.ref(
                'bso_sales_process.replace_subscription_lines_wizard'
            ).id,
            'view_type': 'tree',
            'view_mode': 'form',
            'target': 'new',
            'context': context,
        }
