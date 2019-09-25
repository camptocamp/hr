# -*- coding: utf-8 -*-
import calendar
from datetime import date
from datetime import datetime

from lxml import etree
from odoo import models, api, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    salesperson_commission_line_ids = fields.One2many(
        string='Salespeople',
        comodel_name='salesperson.commission.line',
        inverse_name='order_id',
    )

    @api.model
    def fields_view_get(self, view_id=None,
                        view_type=False, toolbar=False,
                        submenu=False):
        result = super(SaleOrder, self).fields_view_get(
            view_id, view_type, toolbar, submenu)
        if view_type == 'search':
            doc = etree.XML(result['arch'])
            start_date, end_date = self.get_this_quarter_start_end_date()
            this_quarter_domain = self.get_this_quarter_domain(start_date,
                                                               end_date)
            for node in doc.xpath("//filter[@name='this_quarter']"):
                node.set('domain', this_quarter_domain)
            result['arch'] = etree.tostring(doc)
        return result

    @staticmethod
    def get_this_quarter_start_end_date():
        this_quarter = (date.today().month - 1) / 3 + 1

        start_month = 3 * this_quarter - 2
        start_dt = datetime(date.today().year, start_month, 1)

        end_month = start_month + 2
        number_of_days_in_month = calendar.monthrange(date.today().year,
                                                      end_month)[1]
        end_dt = datetime(date.today().year,
                          end_month,
                          number_of_days_in_month)

        start_date = fields.Datetime.to_string(start_dt)
        end_date = fields.Datetime.to_string(end_dt)

        return start_date, end_date

    @staticmethod
    def get_this_quarter_domain(start_date, end_date):
        return "[('date_order', '>=', '%s'), ('date_order', '<=', '%s')]" % \
               (start_date, end_date)

    @api.model
    def create(self, values):
        record = super(SaleOrder, self).create(values)
        record.add_main_salesperson()
        return record

    def add_main_salesperson(self):
        return self.salesperson_commission_line_ids.sudo().create({
            'order_id': self.id,
            'user_id': self.user_id.id,
            'percentage': 100,
            'is_main_salesperson': True,
        })

    @api.multi
    def write(self, values):
        if values.get('user_id'):
            self.update_main_salesperson(values['user_id'])
        return super(SaleOrder, self).write(values)

    def update_main_salesperson(self, user_id):
        to_delete = self.salesperson_commission_line_ids.sudo().search([
            ('order_id', 'in', self.ids),
            ('user_id', '=', user_id),
            ('is_main_salesperson', '=', False)
        ])
        to_delete.unlink()
        to_update = self.salesperson_commission_line_ids.sudo().search([
            ('order_id', 'in', self.ids),
            ('is_main_salesperson', '=', True),
        ])
        to_update.write({'user_id': user_id})
        return True

    def get_salesperson_commission(self, uid):
        return self.salesperson_commission_line_ids.filtered(
            lambda r: r.user_id.id == uid)
