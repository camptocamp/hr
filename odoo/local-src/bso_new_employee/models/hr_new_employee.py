import requests
import urlparse
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, AccessError


class HrNewEmployee(models.Model):
    _name = 'hr.new.employee'

    user_id = fields.Many2one(
        comodel_name='res.users',
        string='User')
    employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Employee'
    )

    login = fields.Char(
        related='user_id.login',
        string='Login',
    )

    name = fields.Char(
        string='Name',
        required=True)

    manager_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Manager'
    )
    csd = fields.Date(string='Contract start date')

    nationality = fields.Many2one(
        'res.country',
        string='Nationality (Country)')

    passport = fields.Char(string='Passport No')

    gender = fields.Selection(
        [('male', 'Male'),
         ('female', 'Female'),
         ('other', 'Other')],
        string='Gender')

    marital = fields.Selection(
        [('single', 'Single'),
         ('maried', 'Maried'),
         ('widower', 'Widower'),
         ('divorced', 'Divorced'),
         ('pacs', 'PACS'),
         ('cohabiting', 'Cohabiting')
         ],
        string='Martial')

    children = fields.Integer(
        string='Children',
        default=0)

    dob = fields.Date(string='Date of birth')

    pob = fields.Char(string='Place of birth')

    email = fields.Char(
        related='user_id.email',
        string='Email')

    phone = fields.Char(string='Phone')

    department_id = fields.Many2one(
        comodel_name='hr.department',
        string='Department',
    )
    title = fields.Many2one(comodel_name='hr.job', string='Job title')

    company_ids = fields.Many2many(
        comodel_name='res.company',
        string='Allowed companies',
        required=True
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        required=True
    )
    location = fields.Char(
        related='company_id.city',
        string='Location',
    )
    is_manager = fields.Boolean(string='Is Manager')

    status = fields.Selection(
        [('requested', 'Requested'),
         ('treated', 'Treated'),
         ('archived', 'Archived')],
        string='Status',
        default='requested')

    @api.model
    def create(self, vals):
        employee = super(HrNewEmployee, self).create(vals)
        if self.env['res.users'].search([
            ('login', '=ilike', employee.login),
            ('active', 'in', (True, False))
        ]):
            raise ValidationError(_(
                'A user with the same credentials already exists, '
                'please activate it instead of creating a new one'
            ))
        if self.env['hr.employee'].search([
            ('login', '=ilike', employee.login),
            ('active', '=', False)
        ]):
            raise ValidationError(_(
                'An employee with the same credentials already exists, '
                'please activate it instead of creating a new one'
            ))

        endpoint_url = self.env['res.api'].search([('api_id', '=',
                                                    'flawless')]).endpoint
        data = {
            employee.id: {
                'name': vals['name'].split(' ')[0],
                'surname': vals['name'].split(' ')[-1]
            }
        }
        r = requests.post(urlparse.urljoin(endpoint_url, 'user'), data=data)

        if r.status_code != 200:
            raise AccessError(_(
                'Something went wrong, please try again later'
            ))

        data = data[employee.id]
        data['login'] = str.lower(
            'temp_{}_{}{}'.format(
                str(employee.id),
                vals['name'][0],
                vals['name'].split(' ')[-1]
            )
        )
        data['name'] = '{} {}'.format(data.pop('name'), data.pop('surname'))
        user = self.env['res.users'].sudo().create(data)

        employee.user_id = user

        user.write({
            'name': employee.name,
            'company_ids': [(6, 0, [employee.company_ids.ids])],
            'company_id': employee.company_id.id,
        })

        data = {
            'name': employee.name,
            'parent_id': employee.manager_id.id,
            'user_id': user.id,
            'crt_date_start': employee.csd,
            'gender': employee.gender,
            'work_location': employee.location,
            'department_id': employee.department_id.id,
            'title': employee.title,
            'company_id': employee.company_id.id,
            'address_id': employee.company_id.partner_id.id,
            'address_home_id': user.partner_id.id,
            'work_phone': employee.phone,
        }
        employee.employee_id = self.env['hr.employee'].create(data)
        return employee

    @api.model
    def update_credentials_when_treated(self):
        endpoint_url = self.env['res.api'].search([('api_id', '=',
                                                    'flawless')]).endpoint
        hr_new_employees = self.env['hr.new.employee'].search([
            ('status', '=', 'requested')
        ])

        for employee in hr_new_employees:
            url = urlparse.urljoin(
                urlparse.urljoin(endpoint_url, 'user'), str(employee.id)
            )
            r = requests.get(url)
            if r.status_code == 200:
                data = r.json()
                if data['status'] == 'treated':
                    employee.update(data['data'])
                    employee.user_id.update(data['data'])
                    employee.employee_id.update(
                        {'login': data['data']['login']})
                    employee.status = 'archived'

    @api.multi
    @api.constrains('company_id', 'company_ids')
    def _check_company(self):
        if any(user.company_ids and user.company_id not in
               user.company_ids for user in self):
            raise ValidationError(_(
                'The chosen company is not in the allowed companies for this '
                'user'
            ))
