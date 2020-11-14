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
                'Please Select at lease one line to be replaced, '
                'or you might need to use the Upsell option!'
            ))
        to_delete_line_ids = []
        for line in self.subscription_line_ids:
            to_delete_line_ids.append(
                self.env['sale.order.sub_line_remove'].sudo().create(
                    {'subscription_line_id': line.id}).id)
        res.sudo().write({
            'to_delete_line_ids': [
                (6, 0, to_delete_line_ids)],
            'order_type': 'replace'
        })
        return view

    @api.multi
    def write(self, vals):
        return super(ReplaceSubsriptionLinesWizard, self.sudo()).write(vals)
