from odoo import models, fields, api
from odoo.exceptions import ValidationError


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    parent_ids = fields.Many2many(
        string='Parents',
        comodel_name='account.analytic.account',
        relation='track_parents_rel',
        column1='parent_ids',
        column2='id',
    )

    immediate_child_ids = fields.Many2many(
        string='Immediate Children',
        comodel_name='account.analytic.account',
        compute='compute_immediate_child_ids'
    )

    all_child_ids = fields.Many2many(
        string='All Children',
        comodel_name='account.analytic.account',
        compute='compute_all_child_ids'
    )
    all_child_self_included_ids = fields.Many2many(
        string='Children ',
        comodel_name='account.analytic.account',
        compute='compute_all_child_ids'
    )
    immediate_child_subscription_count = fields.Integer(
        string='Children\'s subscriptions Count',
        compute='_compute_immediate_child_subscription_count'
    )

    def _compute_immediate_child_subscription_count(self):
        super(AccountAnalyticAccount, self)._compute_subscription_count()
        subscription_data = self.env['sale.subscription'].read_group(
            domain=[
                ('analytic_account_id', 'in', self.immediate_child_ids.ids)],
            fields=['analytic_account_id'],
            groupby=['analytic_account_id'])
        mapped_data = dict(
            [(m['analytic_account_id'][0], m['analytic_account_id_count']) for
             m in subscription_data])
        for account in self:
            for child in account.all_child_ids:
                account.immediate_child_subscription_count += int(
                    mapped_data.get(child.id, 0))

    @api.multi
    def action_immediate_child_subscription(self):
        self.ensure_one()
        children_subscription_ids = self.immediate_child_ids.mapped(
            'subscription_ids').ids
        result = super(AccountAnalyticAccount, self).subscriptions_action()
        result['domain'] = [["id", "in", children_subscription_ids]]
        if len(children_subscription_ids) > 1:
            result['views'] = [[False, "tree"], [False, "form"]]
        return result

    @api.multi
    def get_all_parents(self):
        parents_ids = self.env['account.analytic.account']
        for parent in self.parent_ids:
            parents_ids |= parent
            if parent.parent_ids:
                parent.get_all_parents()
        return parents_ids

    def compute_all_child_ids(self):
        for ac in self:
            ac.all_child_ids = ac.get_all_child_ids()
            ac.all_child_self_included_ids = ac.all_child_ids + self

    def compute_immediate_child_ids(self):
        for ac in self:
            ac.immediate_child_ids = ac.get_child_ids()

    def get_child_ids(self):
        return self.search([('parent_ids', 'in', self.ids)])

    def get_all_child_ids(self, accumulated_children=None):
        child_ids = self.get_child_ids()
        accumulated_children = self.env[
            'account.analytic.account'
        ] if not accumulated_children else accumulated_children
        if child_ids:
            if child_ids.__and__(accumulated_children):
                return child_ids
            else:
                child_ids |= child_ids.get_all_child_ids(
                    accumulated_children + child_ids)
        return child_ids

    def is_my_descendant(self, ac_id):
        return ac_id in self.all_child_ids.ids

    @api.constrains('parent_ids')
    def _check_parent_ids(self):
        for parent1 in self.parent_ids:
            if parent1.id == self.id:
                raise ValidationError('Can not be parent of yourself')
            if self.is_my_descendant(parent1.id):
                raise ValidationError('A descendant can not be a parent')
            for parent2 in self.parent_ids:
                if parent1.is_my_descendant(parent2.id):
                    raise ValidationError(
                        'There is a paternity relation between parents'
                    )
