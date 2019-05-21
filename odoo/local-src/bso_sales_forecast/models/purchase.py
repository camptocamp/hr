# -*- coding: utf-8 -*-
from datetime import datetime

from odoo import models, api, fields


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.multi
    def write(self, values):
        res = super(PurchaseOrderLine, self).write(values)
        if not any(item in values for item in (
                'product_qty', 'price_unit', 'taxes_id')):
            return res
        diff = self.env['forecast.line.diff']
        for rec in self:
            if rec.to_log():
                fields = rec.get_fields_to_log()
                diff.log(rec._name, rec.id, 'update', fields)
        return res

    @api.model
    def create(self, values):
        rec = super(PurchaseOrderLine, self).create(values)
        diff = self.env['forecast.line.diff']
        if rec.to_log():
            fields = rec.get_fields_to_log()
            diff.log(self._name, rec.id, 'create', fields)
        return rec

    @api.multi
    def unlink(self):
        diff = self.env['forecast.line.diff']
        for rec in self:
            if rec.to_log():
                diff.log(rec._name, rec.id, 'delete', {})
        return super(PurchaseOrderLine, self).unlink()

    def to_log(self):
        if self.order_id.state not in ('purchase', 'done'):
            return False
        if not self.order_id.to_log():
            return False
        return True

    def get_fields_to_log(self, **kwargs):
        po = self.order_id
        state = kwargs.get('state', po.state)
        return {
            'amount': kwargs.get('price_subtotal', self.price_subtotal),
            'auto_renewal': kwargs.get('continue_after_end',
                                       po.continue_after_end),
            'start_date': kwargs.get('date_start', po.subscr_date_start),
            'end_date': kwargs.get('subscr_date_end', po.subscr_date_end),
            'state': self._get_corresponding_state(state),
        }

    @staticmethod
    def _get_corresponding_state(state):
        if state in ('purchase', 'done'):
            return 'open'
        return 'close'


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.multi
    def write(self, values):
        to_check = ('continue_after_end', 'subscr_date_start',
                    'subscr_date_end', 'state')
        if not any(value in values for value in to_check):
            return super(PurchaseOrder, self).write(values)
        updated_fields = {field: values[field] for field in values if
                          field in to_check}
        diff = self.env['forecast.line.diff']
        for rec in self:
            action = rec.get_action(values)
            if not action:
                continue
            if not rec.to_log():
                continue
            for line in rec.order_line:
                fields_to_log = line.get_fields_to_log(**updated_fields)
                diff.log(line._name, line.id, action, fields_to_log)
        return super(PurchaseOrder, self).write(values)

    def to_log(self):
        # check if updated sub company is related to a generated forecast
        # report
        generated_reports_companies = self._get_generated_reports_companies()
        if self.company_id not in generated_reports_companies:
            return False
        if not self.is_futur_purchase():
            return False
        return True

    def _get_generated_reports_companies(self):
        return self.env['forecast.report'].search([]).mapped('company_id')

    def is_futur_purchase(self):
        end_dt = fields.Datetime.from_string(self.subscr_date_end)
        today = datetime.today()
        if self.continue_after_end:
            return True
        if self.subscr_date_end and end_dt >= today:
            return True
        return False

    def get_action(self, values):
        if self.state != 'purchase' and values.get('state') == 'purchase':
            return 'create'
        if self.state == 'purchase' and 'state' in values \
                and values['state'] == 'cancel':
            return 'delete'
        if self.state in ('purchase', 'done'):
            return 'update'
        return False
