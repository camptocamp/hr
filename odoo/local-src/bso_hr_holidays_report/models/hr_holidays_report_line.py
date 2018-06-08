# -*- coding: utf-8 -*-
import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class HrHolidaysReportLine(models.Model):
    _name = "hr.holidays.report.line"
    _description = "Leave Report Line"
    _rec_name = "holiday_id"
    _order = 'employee_id ASC'

    holiday_report_id = fields.Many2one(
        string='Holidays Report',
        comodel_name='hr.holidays.report',
        ondelete='cascade',
        readonly=True
    )
    holiday_id = fields.Many2one(
        string='Leave',
        comodel_name='hr.holidays',
        readonly=True,
        required=True
    )
    employee_id = fields.Many2one(
        string='Employee',
        comodel_name='hr.employee',
        readonly=True,
        required=True
    )
    company_id = fields.Many2one(
        string='Company',
        comodel_name='res.company',
        readonly=True,
        required=True
    )
    country_code = fields.Char(
        string='Country Code',
        related='company_id.country_id.code',
        readonly=True,
        store=True
    )
    holiday_status_id = fields.Many2one(
        string='Leave Type',
        comodel_name='hr.holidays.status',
        readonly=True,
        required=True
    )
    holiday_state = fields.Selection(
        string='Leave State',
        selection=[
            ('validate', 'Approved'),
            ('refuse', 'Refused')
        ],
        readonly=True,
        required=True
    )
    start_date = fields.Datetime(
        string='Start Date',
        readonly=True,
        required=True
    )
    end_date = fields.Datetime(
        string='End Date',
        readonly=True,
        required=True
    )
    days = fields.Float(
        string='Days in Period',
        readonly=True,
        required=True
    )
