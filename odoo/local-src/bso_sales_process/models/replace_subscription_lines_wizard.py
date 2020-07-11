from odoo import models, fields, api


class ReplaceSubsriptionLinesWizard(models.TransientModel):
    _name = 'replace.subscription.lines.wizard'

    subscription_id = fields.Many2one(
        string='Subscription',
        comodel_name='sale.subscription',
        required=True,
        readonly=True
    )
    subscription_line_ids = fields.One2many(
        string='Subscription Lines',
        related='subscription_id.recurring_invoice_line_ids',
    )

    @api.multi
    def replace_action(self):
        wizard = self.env['sale.subscription.wizard'].create(
            {'subscription_id': self.subscription_id.id,
             'account_id': self.subscription_id.analytic_account_id.id
             })
        view = wizard.create_sale_order()
        res = self.env['sale.order'].browse(view['res_id'])
        selected_lines = self.subscription_line_ids.filtered(
            lambda x: x.to_be_deleted)
        res.to_delete_line_ids = selected_lines
        res.order_type = 'replace'
        return view
