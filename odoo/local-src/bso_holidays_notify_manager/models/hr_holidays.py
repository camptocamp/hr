from odoo import api, models


class HrHolidays(models.Model):
    _inherit = 'hr.holidays'

    @api.model
    def create(self, vals):
        self._create_set_followers(vals)
        return super(HrHolidays, self).create(vals)

    @api.multi
    def write(self, vals):
        res = super(HrHolidays, self).write(vals)
        if vals.get('employee_id'):
            self._add_followers()
        return res

    def _get_users_to_subscribe(self, employee=False):
        users = self.env['res.users']
        employee = employee or self.employee_id
        if employee.user_id:
            users |= employee.user_id
        if employee.parent_id:
            users |= employee.parent_id.user_id
        if employee.department_id \
                and employee.department_id.manager_id \
                and employee.parent_id != employee.department_id.manager_id:
            users |= employee.department_id.manager_id.user_id
        return users

    def _add_followers(self):
        users = self._get_users_to_subscribe()
        self.message_subscribe_users(user_ids=users.ids)

    @api.model
    def _create_set_followers(self, values):
        # Add the followers at creation, so they can be notified
        employee_id = values.get('employee_id')
        if not employee_id:
            return

        employee = self.env['hr.employee'].browse(employee_id)
        users = self._get_users_to_subscribe(employee=employee) - self.env.user
        values['message_follower_ids'] = []
        MailFollowers = self.env['mail.followers']
        for partner in users.mapped('partner_id'):
            values['message_follower_ids'] += \
                MailFollowers._add_follower_command(self._name, [],
                                                    {partner.id: None}, {})[0]
