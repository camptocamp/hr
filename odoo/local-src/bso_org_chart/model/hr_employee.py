from odoo import models, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.multi
    def action_org_chart(self):
        self.ensure_one()
        view_id = self.env.ref('bso_org_chart.hr_employee_org_chart')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Org Chart',
            'view_id': view_id.id,
            'res_model': self._name,
            'res_id': self.id,
            'view_type': 'form',
            'view_mode': 'form',
            'views': [[view_id.id, 'form']],
            'target': 'current',
            'context': self._context,
        }
