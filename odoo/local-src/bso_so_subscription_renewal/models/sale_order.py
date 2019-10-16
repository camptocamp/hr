from odoo import models, api, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    pickings_done = fields.Boolean(
        string='pickings done',
        compute='compute_pickings_done',
        default=False,
        store=True
    )
    non_computable_pickings_done = fields.Boolean(
        default=False
    )

    @api.multi
    def _compute_subscription(self):
        for order in self:
            if not self.env.context.get('no_update_subscription'):
                order.subscription_id = self.env['sale.subscription'].search(
                    [('analytic_account_id', '=', order.project_id.id)],
                    limit=1)

    @api.depends('picking_ids.state')
    def compute_pickings_done(self):
        for so in self:
            so.pickings_done = all(
                pick.state == 'done' for pick in so.picking_ids
            ) if so.picking_ids else False

    @api.multi
    def action_confirm(self):
        for order in self:
            if not order.pickings_done:
                super(SaleOrder, order.with_context(
                    no_update_subscription=True)).action_confirm()
            else:
                super(SaleOrder, order).action_confirm()
        return True

    @api.multi
    def update_subscription(self):
        self.ensure_one()
        if not self.non_computable_pickings_done and self.pickings_done:
            self.non_computable_pickings_done = True
            self.action_confirm()

    @api.multi
    def action_invoice_create(self, grouped=False, final=False):
        res = super(SaleOrder, self).action_invoice_create(grouped, final)
        self.action_done()
        return res
