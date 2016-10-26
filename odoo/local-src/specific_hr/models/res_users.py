# -*- coding: utf-8 -*-
# Author: Damien Crier
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, values):
        # when I create a user from ldap, I will look in hr.employee object if
        # there's one with the XML ID corresponding to the "login" and if so,
        # make the link else if not found, do nothing
        user = super(ResUsers, self).create(values)
        user._get_employee(user.name, user.login)
        return user

    def _get_employee(self, name, login):
        self.ensure_one()
        data_obj = self.env['ir.model.data']
        emp_obj = self.env['hr.employee']
        emp = emp_obj.search([('user_login', '=', login)])
        if not emp:
            # try searching on xml_id
            emps = data_obj.search(
                [('name', '=', login),
                 ('model', '=', 'hr.employee'),
                 ('module', '=', 'BSO_employee')]).mapped('res_id')
            if emps:
                # link the employee to the user
                emp = emp_obj.browse(emps[0])

        emp.user_id = self.id
        if emp.company_id != self.company_id:
            # set the user company to the value of employee's one
            self.write({'company_id': emp.company_id.id,
                        'company_ids': [(6, 0, [emp.company_id.id])]})

        return emp
