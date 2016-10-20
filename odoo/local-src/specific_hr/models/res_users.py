# -*- coding: utf-8 -*-
# Author: Damien Crier
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def create(self, values):
        # when I create a user from ldap, I will look in hr.employee object if
        # there's one with the XML ID corresponding to the "login" and if so,
        # make the link else if not found, create an employee related to the
        # user created and add the xml id
        user = super(ResUsers, self).create(values)
        user._get_employee(user.name, user.login)
        return user

    def _get_employee(self, name, login):
        self.ensure_one()
        data_obj = self.env['ir.model.data']
        emp_obj = self.env['hr.employee']
        emp = emp_obj.search([('user_login', '=', login)])
        create_emp = False
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
            else:
                create_emp = True

        if create_emp:
            emp = self.env['hr.employee'].create({
                'name': name,
                'user_login': login,
                'user_id': self.id,
                })
            data_obj.sudo().create({'name': login,
                                    'model': 'hr.employee',
                                    'module': 'BSO_employee',
                                    'res_id': emp.id
                                    })

        return emp
