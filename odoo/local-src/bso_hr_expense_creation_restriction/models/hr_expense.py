from odoo import models, api, _
from odoo.exceptions import AccessError


class HrExpense(models.Model):
    _inherit = 'hr.expense'

    @api.model
    def new(self, values={}):
        if (
                self.env.user.company_id.id !=
                self.env.user.employee_ids.company_id.id
        ):
            self.raise_change_company_error(
                self.env.user.employee_ids.company_id.name
            )
        return super(HrExpense, self).new(values)

    @api.constrains('name')
    def _check_current_company(self):
        if (
                self.env.user.company_id.id !=
                self.env.user.employee_ids.company_id.id
        ):
            self.raise_change_company_error(
                self.env.user.employee_ids.company_id.name
            )

    def raise_change_company_error(self, company):
        raise AccessError(
            _("Please change your current company (top right) to '{}'".format(
                company)
              )
        )
