# -*- coding: utf-8 -*-

import json
from odoo import http
from odoo.addons.website.controllers.main import Website
from odoo.http import request

FIELDS = ['id', 'pid', 'name', 'title', 'work_location', 'company_id']


class Main(Website):

    @http.route(['/hr_employee/get_org_chart/<int:employee_id>'],
                type='http', auth="public", website=True)
    def get_org_chart(self, employee_id=0):
        Model = request.env['hr.employee'].sudo()
        employee_ids = Model.browse(employee_id)
        manager = employee_ids.parent_id
        employee_ids |= manager
        employee_ids |= Model.search([('parent_id', 'child_of', employee_id)])
        data_source = self.get_chart_data_source(employee_ids)

        data = {'dataSource': data_source,
                'customize': {manager.id: {"color": "darkred"},
                              employee_id: {"color": "teal"}},
                'expandToLevel': manager and 3 or 2
                }
        return json.dumps(data)

    @http.route(['/hr_employee/name/<string:name>'],
                type='http', auth="public", website=True)
    def get_employee_by_name(self, name=''):
        Model = request.env['hr.employee'].sudo()
        employee_ids = Model.search(
            ['|', ('name', 'ilike', name), '|', ('title', 'ilike', name),
             ('department_id.name', 'ilike', name)], limit=10)
        data_source = self.get_chart_data_source(employee_ids)
        for node in data_source:
            node['textInNode'] = '{}, {}'.format(
                node['name'].encode('utf-8'), node['title'].encode('utf-8')),
            node['textId'] = str(node['id'])
        data = {'dataSource': data_source}
        return json.dumps(data)

    def get_chart_data_source(self, employee_ids):
        res = []
        for employee in employee_ids:
            employee_dict = dict()
            for field in FIELDS:
                employee_dict['img'] = 'data:image/png;base64,' + request.env[
                    'hr.employee'].browse(employee.id).image.rstrip()
                field_value = None
                if field == "pid":
                    field_value = getattr(employee, 'parent_id', None)
                    field_value = field_value and field_value.id or None
                elif field.endswith("id") and field != 'id':
                    field_value = getattr(employee, field, None)
                    field_value = field_value and field_value.name or ''
                else:
                    field_value = getattr(employee, field, None)
                    field_value = field_value or ''
                employee_dict[field] = field_value
            res.append(employee_dict)
        return res
