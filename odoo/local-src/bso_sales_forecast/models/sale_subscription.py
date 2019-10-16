# -*- coding: utf-8 -*-

from odoo import models, api


class SaleSubscriptionLine(models.Model):
    _inherit = "sale.subscription.line"

    @api.multi
    def write(self, values):
        res = super(SaleSubscriptionLine, self).write(values)
        if not any(item in values for item in (
                'price_unit', 'quantity', 'discount',
                'analytic_account_id.pricelist_id')):
            return res
        diff = self.env['forecast.line.diff']
        for rec in self:
            if rec.analytic_account_id.state == 'open':
                fields = rec.get_fields_to_log()
                diff.log(rec._name, rec.id, 'update', fields)
        return res

    @api.model
    def create(self, values):
        rec = super(SaleSubscriptionLine, self).create(values)
        diff = self.env['forecast.line.diff']
        if rec.analytic_account_id.state == 'open':
            fields = rec.get_fields_to_log()
            diff.log(rec._name, rec.id, 'create', fields)
        return rec

    @api.multi
    def unlink(self):
        diff = self.env['forecast.line.diff']
        for rec in self:
            if rec.analytic_account_id.state == 'open':
                fields = rec.get_fields_to_log()
                diff.log(rec._name, rec.id, 'delete', fields)
        return super(SaleSubscriptionLine, self).unlink()

    def get_fields_to_log(self, **kwargs):
        subscription = self.analytic_account_id

        auto_renewal = kwargs.get('automatic_renewal',
                                  subscription.automatic_renewal)
        state = kwargs.get('state', subscription.state)

        return {
            'company_id': kwargs.get('company_id', subscription.company_id.id),
            'amount': kwargs.get('price_subtotal', self.price_subtotal),
            'auto_renewal': self._get_corresponding_renewal(auto_renewal),
            'start_date': kwargs.get('date_start', subscription.date_start),
            'end_date': kwargs.get('date', subscription.date),
            'state': self._get_corresponding_state(state),
            'template_id': kwargs.get('template_id',
                                      subscription.template_id.id),
        }

    @staticmethod
    def _get_corresponding_state(state):
        return 'open' if state == 'open' else 'close'

    @staticmethod
    def _get_corresponding_renewal(automatic_renewal):
        return False if automatic_renewal in [False, 'none'] else True


class SaleSubscription(models.Model):
    _inherit = "sale.subscription"

    @api.multi
    def write(self, values):
        # check if updated fields need to be logged
        to_check = ('automatic_renewal', 'date_start', 'date', 'state',
                    'template_id')
        if not any(value in values for value in to_check):
            return super(SaleSubscription, self).write(values)
        updated_fields = {field: values[field] for field in values if
                          field in to_check}
        diff = self.env['forecast.line.diff']
        for rec in self:
            action_to_log = rec.get_action(values)
            if not action_to_log:
                continue
            for line in rec.recurring_invoice_line_ids:
                fields_to_log = line.get_fields_to_log(**updated_fields)
                diff.log(line._name, line.id, action_to_log, fields_to_log)
        return super(SaleSubscription, self).write(values)

    def get_action(self, values):
        if self.state != 'open' and values.get('state') == 'open':
            return 'create'
        if self.state == 'open' and 'state' in values \
                and values['state'] != 'open':
            return 'delete'
        if self.state == 'open':
            return 'update'
        return False

    # def is_futur_subscription(self, **values):
    #     end_date = values.get('date', self.date)
    #     automatic_renewal = values.get('automatic_renewal',
    #                                    self.automatic_renewal)
    #     if automatic_renewal not in (False, 'none'):
    #         return True
    #     end_dt = fields.Datetime.from_string(end_date)
    #     today = datetime.today()
    #     if end_date and end_dt >= today:
    #         return True
    #     return False

    @api.multi
    def unlink(self):
        diff = self.env['forecast.line.diff']
        for rec in self:
            if rec.state != 'open':
                continue
            for line in rec.recurring_invoice_line_ids:
                fields = line.get_fields_to_log()
                diff.log(line._name, line.id, 'delete', fields)
        return super(SaleSubscription, self).unlink()
