from odoo import models, fields, api, exceptions, _


class ReplaceSubsriptionLinesWizard(models.TransientModel):
    _name = 'replace.subscription.lines.wizard'

    subscription_id = fields.Many2one(
        string='Subscription',
        comodel_name='sale.subscription',
        required=True,
        readonly=True
    )

    subscription_line_ids = fields.Many2many(
        string='Lines To Replace',
        comodel_name='sale.subscription.line',
        domain="[('analytic_account_id', '=', subscription_id)]"
    )

    @api.multi
    def replace_action(self):
        wizard = self.env['sale.subscription.wizard'].create(
            {'subscription_id': self.subscription_id.id,
             'account_id': self.subscription_id.analytic_account_id.id
             })
        view = wizard.create_sale_order()
        res = self.env['sale.order'].browse(view['res_id'])
        if not self.subscription_line_ids:
            raise exceptions.ValidationError(_(
                'Please Select at least one line to be %s, '
                'or you might need to use the Upsell option!' % self.order_type
            ))
        res.sudo().write({
            'to_delete_line_ids': [
                (6, 0, self.subscription_line_ids.ids)],
            'order_type': 'replace'
        })
        return view

    @api.multi
    def write(self, vals):
        return super(ReplaceSubsriptionLinesWizard, self.sudo()).write(vals)
