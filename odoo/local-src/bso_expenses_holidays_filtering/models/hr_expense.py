import logging

from lxml import etree
from odoo import models, api

_logger = logging.getLogger(__name__)


class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    @api.model
    def fields_view_get(self, view_id='view_hr_expense_sheet_filter_bso',
                        view_type=False, toolbar=False,
                        submenu=False):
        result = super(HrExpenseSheet, self).fields_view_get(
            view_id, view_type, toolbar, submenu)
        doc = etree.XML(result['arch'])
        employee_department_id = self.get_employee_department_id()
        domain = self.get_domain(employee_department_id)
        for node in doc.xpath("//filter[@name='my_perimeter']"):
            node.set('domain', domain)
        result['arch'] = etree.tostring(doc)
        return result

    def get_domain(self, department_id):
        return "[('department_id', 'child_of', %s)]" % department_id

    def get_employee_department_id(self):
        return self.env.user.employee_ids.department_id.id