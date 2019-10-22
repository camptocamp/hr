# -*- coding: utf-8 -*-
import logging
from datetime import datetime

from odoo import models, fields, api
from pytz import timezone

_logger = logging.getLogger(__name__)


class UbersmithInvoice(models.Model):
    _name = 'ubersmith.invoice'
    _rec_name = 'invoice_id'

    invoice_id = fields.Char(
        string="Invoice ID",
    )
    client_id = fields.Many2one(
        string="Ubersmith Client",
        comodel_name="ubersmith.client"
    )
    date = fields.Date(
        string="Date"
    )
    datepaid = fields.Date(
        string="Date Paid"
    )
    due = fields.Date(
        string="Due Date"
    )
    paid = fields.Selection(
        selection=[(0, 'Unpaid'),
                   (1, 'Paid'),
                   (2, 'Disregarded'),
                   (3, 'All')],
        string="Invoice State",
    )
    ubersmith_invoice_line_ids = fields.One2many(
        comodel_name="ubersmith.invoice.line",
        inverse_name="invoice_id",
        string="Ubersmith Invoice Lines"
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )
    odoo_invoice_id = fields.Many2one(
        string="Odoo Invoice",
        comodel_name="account.invoice"
    )
    non_creation_reason = fields.Selection(
        string='Reason why Odoo invoice is not created',
        selection=[
            ('odoo_partner_missing', 'Odoo partner missing'),
            ('service_plan_missing', 'Service plan not found'),
            ('odoo_product_missing', 'Service plan not linked to a product'),
            ('odoo_company_missing', 'Client Brand not linked to a company'),
            ('line_date_missing', 'Date is missing in invoice lines period'),
            ('line_tax_missing', 'Ubersmith tax not linked to an odoo tax'),
            ('invoice_without_lines', 'Invoice without lines'),
            ('none', 'None')

        ],
        readonly=True
    )
    total_current_charges = fields.Float(
        string='Total current charges'
    )
    current_charges = fields.Float(
        string='Current charges'
    )
    is_correctly_imported = fields.Boolean(
        string='Correctly imported without Taxes',
        compute='_is_correctly_imported',
        store='True'
    )

    @api.depends('odoo_invoice_id.amount_untaxed', 'current_charges')
    def _is_correctly_imported(self):
        for rec in self:
            if not rec.odoo_invoice_id:
                continue
            amount_untaxed = int(rec.odoo_invoice_id.amount_untaxed)
            current_charges = int(rec.current_charges)
            if amount_untaxed == current_charges:
                rec.is_correctly_imported = True

    def create_ubersmith_invoice(self, invoice_id, client):
        invoice = self.search([
            ('invoice_id', '=', invoice_id)
        ])
        if not invoice:
            api = self.env['ubersmith.api']
            invoice_dict = api.get_invoice(invoice_id)
            paid = int(invoice_dict['paid'])
            self.create({
                'invoice_id': invoice_id,
                'client_id': client.id,
                'date': self.convert_timestamp_to_date(
                    invoice_dict['date']),
                'datepaid': self.convert_timestamp_to_date(
                    invoice_dict['datepaid']),
                'due': self.convert_timestamp_to_date(invoice_dict['due']),
                'ubersmith_invoice_line_ids':
                    self._get_ubsersmith_invoice_lines(invoice_dict),
                'total_current_charges': float(invoice_dict['summary'][
                                                   'total_current_charges']),
                'current_charges': float(invoice_dict['summary'][
                                             'current_charges']),
                'paid': 3 if paid == 'all' else paid
            })

    def _get_ubsersmith_invoice_lines(self, invoice_dict):
        packs = {}
        packs.update(invoice_dict['pre_billed_packs'])
        packs.update(invoice_dict['current_packs'])
        taxes_list = invoice_dict['taxes'].values() if isinstance(
            invoice_dict['taxes'], dict) else []
        if not packs:
            return False
        ubersmith_invoice_lines = []
        # u_plan_o = self.env['ubersmith.service.plan']
        u_tax_o = self.env['ubersmith.tax']
        for c, pack in packs.iteritems():
            line_id = pack['item_id']
            tax_ids = [t['tax_id'] for t in taxes_list if
                       t['inv_pack_id'] == line_id]
            q = float(pack['quantity'])
            p = int(pack['period'])
            service = self.env['ubersmith.service'].get_service(
                pack['packid'])
            ubersmith_invoice_lines.append((0, 0, {
                'line_id': line_id,
                # 'plan_id': u_plan_o.get_plan_by_code(pack['servtype']),
                'plan_id': service.plan_id.id,
                'quantity': q,
                'unit_price': service.price,
                'cost': pack['cost'],
                'value': pack['value'],
                'discount': pack['discount'],
                # ? desc should come from product
                'description': pack['desserv'],
                'date_start': self.convert_timestamp_to_date(
                    pack['date_range_start']),
                'date_end': self.convert_timestamp_to_date(
                    pack['date_range_end']),
                'period': p,
                'tax_ids': [(6, 0, u_tax_o.get_ubersmith_taxes(tax_ids))],
                'service_id': service.id
            }))
        return ubersmith_invoice_lines

    def convert_timestamp_to_date(self, ts):
        if not int(ts):
            return False
        dt = datetime.fromtimestamp(int(ts))
        dt_user_tz = self.convert_dt_to_user_tz(dt)
        return dt_user_tz.date()

    def convert_dt_to_user_tz(self, dt):
        from_tz = timezone('UTC')
        to_tz = timezone(self.env.user.tz)
        dt_utc = dt.replace(tzinfo=from_tz)
        return dt_utc.astimezone(to_tz)

    @api.multi
    def create_invoice(self):
        if not self.check_invoice_validity():
            return False
        if not self.odoo_invoice_id:
            company_id = self.client_id.brand_id.company_id.id
            # self.sudo().env.user.company_id = company_id
            context = self._get_invoice_context(company_id)
            vals = self._get_invoice_vals()
            inv = self.odoo_invoice_id.with_context(context).sudo().create(
                vals.copy())
            inv._onchange_partner_id()
            diff = self._get_onchange_diff(vals, inv)
            inv.write(diff)
            self.create_invoice_lines(inv)
            inv.compute_taxes()
            self.sudo().write({'odoo_invoice_id': inv.id,
                               'non_creation_reason': 'none'})
            return inv

    def check_invoice_validity(self):
        if not self.client_id.odoo_partner_id:
            self.write({'non_creation_reason': 'odoo_partner_missing'})
            return False
        settings = self.env['ubersmith.settings'].get()
        lines = self.ubersmith_invoice_line_ids
        if not settings.create_invoices_without_lines and not lines:
            self.write({'non_creation_reason': 'invoice_without_lines'})
            return False
        if not all(l.plan_id for l in lines):
            self.write({'non_creation_reason': 'service_plan_missing'})
            return False
        if not all(l.plan_id.odoo_product_id.id for l in lines):
            self.write({'non_creation_reason': 'odoo_product_missing'})
            return False
        if not all(t.odoo_tax_id for l in lines for t in l.tax_ids):
            self.write({'non_creation_reason': 'line_tax_missing'})
            return False
        if not self.client_id.brand_id.company_id:
            self.write({'non_creation_reason': 'odoo_company_missing'})
            return False
        if not all(l.date_start and l.date_end for l in lines):
            self.write({'non_creation_reason': 'line_date_missing'})
            return False
        return True

    @staticmethod
    def _get_invoice_context(company_id):
        return {
            'default_type': 'out_invoice',
            'journal_type': 'sale',
            'type': 'out_invoice',
            'force_company': company_id,
            'default_company_id': company_id,
            'company_id': company_id
        }

    def _get_invoice_vals(self):
        self.ensure_one()
        return {
            'partner_id': self.client_id.odoo_partner_id.id,
            'company_id': self.client_id.brand_id.company_id.id,
            'date_invoice': self.date,
            'date_due': self.due,
            'currency_id':
                self.client_id.brand_id.currency_id.odoo_currency_id.id
        }

    def create_invoice_lines(self, inv):
        lines = self.ubersmith_invoice_line_ids
        if not lines:
            return False
        for line in lines:
            # tax_ids = [t.odoo_tax_id.id for t in line.tax_ids]
            p = line.period or 1
            u_q = line.quantity
            q = u_q if line.bill_type == 'period' else u_q * p
            discount = line.get_discount_percentage()
            if line.cost != line.value and line.cost != 0:
                # and line.date_start and line.date_end:
                # start_dt = fields.Date.from_string(line.date_start)
                # end_dt = fields.Date.from_string(line.date_end)
                # number_of_days = (end_dt - start_dt).days + 1
                number_of_days = line.value / line.cost * 30 * p
                q = number_of_days * 1. / 30 * line.quantity
            vals = {
                'name': line.description,
                'invoice_id': inv.id,
                'product_id': line.plan_id.odoo_product_id.id,
                'uom_id': line.plan_id.odoo_product_id.uom_id.id,
                'quantity': q,
                'price_unit': line.service_id.price,
                'discount': discount,
                'start_date': line.date_start,
                'end_date': line.date_end,
                # 'invoice_line_tax_ids': [(6, 0, tax_ids)],
            }
            new_inv_line = self.env['account.invoice.line'].with_context(
                force_company=inv.company_id.id).sudo().new(vals)
            new_inv_line._onchange_product_id()
            diff = self._get_onchange_diff(vals, new_inv_line)
            inv_line_dict = new_inv_line._convert_to_write(new_inv_line._cache)
            inv_line_dict.update(diff)
            inv_line = self.env['account.invoice.line'].sudo().create(
                inv_line_dict)
            line.sudo().write({'odoo_invoice_line_id': inv_line.id})

    def _get_onchange_diff(self, data, record):
        diff = {}
        record_data = record.copy_data()[0]
        for key, value in data.iteritems():
            if key not in record_data or value != record_data[key]:
                diff[key] = value
        return diff

    def create_odoo_invoices(self):
        u_invoices = self.search([
            ('odoo_invoice_id', '=', False),
        ])
        for counter, u_invoice in enumerate(u_invoices):
            if not u_invoice.client_id.odoo_partner_id:
                u_invoice.client_id.sudo().get_or_create_partner()
            u_invoice.sudo().create_invoice()
            self.log_progress(counter + 1, len(u_invoices), 'invoice')

    @staticmethod
    def log_progress(counter, u_invoices_count, item_name):
        p = counter * 100 / u_invoices_count
        if not p % 10:
            _logger.info('%s%% odoo %s created' % (p, item_name))
