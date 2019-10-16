import requests
from odoo.tests import common


class FakeResponse:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self.payload = payload

    def json(self):
        return self.payload


def post(url, data):
    payload = {
        "3403e87234ur238y234jhgv234": "requested",
        "iudfuhjdfihdf": "uuid already used, not created"
    }
    return FakeResponse(200, payload)


def get(url, params=None):
    payload = {
        "data": {
            "login": "testflname",
            "email": "fname.lname@bsonetwork.net"
        },
        "status": "treated"
    }
    response = FakeResponse(200, payload)
    return response


@common.at_install(False)
@common.post_install(True)
class TestHrNewEmployee(common.TransactionCase):
    def test_create(self):
        requests.post = post
        company = self.env['res.company'].create({'name': 'bso test'})
        vals = {
            'company_ids': [(6, 0, [company.id])],
            'company_id': company.id,
            'name': 'homer simpson'
        }
        hr_new_employees_pre = self.env['hr.new.employee'].search_count([])
        hr_employees_pre = self.env['hr.employee'].search_count([])
        res_users_pre = self.env['res.users'].search_count([])

        employee = self.env['hr.new.employee'].create(vals)

        hr_new_employees_post = self.env['hr.new.employee'].search_count([])
        res_users_post = self.env['res.users'].search_count([])
        hr_employees_post = self.env['hr.employee'].search_count([])

        self.assertEqual(hr_new_employees_post, hr_new_employees_pre + 1)
        self.assertEqual(hr_employees_post, hr_employees_pre + 1)
        self.assertEqual(res_users_post, res_users_pre + 1)

        self.assertEqual(vals['name'], employee.name)
        self.assertEqual(employee.status, 'requested')

    def test_update_credentials_when_treated(self):
        company = self.env['res.company'].create({'name': 'bso test'})
        vals = {
            'company_ids': [(6, 0, [company.id])],
            'company_id': company.id,
            'name': 'bart simpson',
        }
        requests.post = post
        employee = self.env['hr.new.employee'].create(vals)
        requests.get = get
        self.env['hr.new.employee'].update_credentials_when_treated()

        self.assertEqual(employee.status, 'archived')
        self.assertEqual(employee.login, 'testflname')
        self.assertEqual(employee.user_id.login, 'testflname')
        self.assertEqual(employee.email, 'fname.lname@bsonetwork.net')
        self.assertEqual(employee.user_id.email, 'fname.lname@bsonetwork.net')
