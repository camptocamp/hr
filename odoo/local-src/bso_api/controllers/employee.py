# -*- coding: utf-8 -*-
import logging

from odoo.http import request

from odoo import http
from utils import _response

_logger = logging.getLogger(__name__)


class EmployeeController(http.Controller):

    @http.route('/api/employees', type='http', auth='none')
    def get_employees(self, offset=0, limit=None):
        fields = [
            'firstname',
            'lastname',
            # Public Information
            'address_id',
            'mobile_phone',
            'work_location',
            'work_email',
            'work_phone',
            'department_id',
            'job_id',
            'title',
            'partial_time',
            'parent_id',
            'coach_id',
            'manager',
            'family_id',
            'calendar_id',
            'notes',
            # HR Settings
            'company_id',
            'user_login',
            'crt_date_start',
            'user_id'
        ]
        employees = request.env['hr.employee'].sudo().search_read(
            [], fields=fields, offset=int(offset),
            limit=int(limit) if limit else None)
        for e in employees:
            user_id = e['user_id'][0] if e['user_id'] else False
            user = request.env['res.users'].sudo().browse(user_id)
            e['has_odoo_login'] = user.active
        return _response(employees)
