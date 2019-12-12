# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase


class TestTrackField(TransactionCase):
    def setUp(self):
        super(TestTrackField, self).setUp()
        self.Subtype = self.env['mail.message.subtype']
        self.salesman = self.env.ref('bso_track_subtype.salesman')
        self.partner = self.env.ref('bso_track_subtype.customer')
        self.manager = self.env.ref('bso_track_subtype.manager')
        self.emp_manager = self.env.ref('bso_track_subtype.emp_manager')
        self.emp_salesman = self.env.ref('bso_track_subtype.emp_salesman')

    def test_notify_so_sub_when_delasheet_validated(self):
        # we can't use dealsheet_state field in sale.order because related
        # doesn't trigger write => we won't be able to use write override
        ms_ds_validated = self.Subtype.create({
            'name': 'dealsheet_validated',
            'description': 'Dealsheet is validated',
            'res_model': 'sale.dealsheet',
            'default': True,
            'field_id': self._get_field_id('state', 'sale.dealsheet'),
            'trigger_value': 'validated',
        })
        self.Subtype.create({
            'name': 'dealsheet_validated',
            'description': 'Dealsheet is validated',
            'res_model': 'sale.order',
            'relation_field': 'sale_order_id',
            'parent_id': ms_ds_validated.id,
            'default': True,
        })
        # self.Data.create({
        #     'name': 'mt_ds_validated',
        #     'model': 'mail.message.subtype',
        #     'module': 'mail',
        #     'res_id': ms_ds_validated.id
        # })
        so = self._create_so()
        so.action_dealsheet()
        so.dealsheet_id.action_confirmed(self.salesman)
        so.dealsheet_id.action_validate()
        message = self._get_message(so.dealsheet_id, ms_ds_validated)
        self.assertTrue(message)
        self.assertIn(self.salesman.partner_id.id, message.partner_ids.ids)

    def test_track_dealsheet_confirmation(self):
        ms_ds_confirmed = self.Subtype.create({
            'name': 'dealsheet_confirmed',
            'description': 'Dealsheet is confirmed',
            'res_model': 'sale.dealsheet',
            'default': True,
            'field_id': self._get_field_id('state', 'sale.dealsheet'),
            'trigger_value': 'confirmed',
        })
        so = self._create_so()
        so.action_dealsheet()
        so.dealsheet_id.action_confirmed(self.salesman)
        message = self._get_message(so.dealsheet_id, ms_ds_confirmed)
        self.assertTrue(message)
        self.assertIn(self.salesman.partner_id.id, message.partner_ids.ids)

    def _get_field_id(self, field_name, model_name):
        return self.env['ir.model.fields'].search([
            ('name', '=', field_name),
            ('model_id.model', '=', model_name)
        ]).id

    def _create_so(self):
        return self.env['sale.order'].sudo(user=self.salesman).create({
            'partner_id': self.partner.id,
            'user_id': self.salesman.id,
            'currency_id': self.env.ref('base.EUR').id,
            'duration': 12,
        })

    @staticmethod
    def _get_message(mail_thread, message_subtype):
        return mail_thread.message_ids.filtered(
            lambda x: x.description == message_subtype.description)

    def test_track_leave_state(self):
        holiday_status_id = self.env['hr.holidays.status'].create({
            'name': 'Test Holiday',
            'exclude_rest_days': True,
            'limit': True
        }).id
        leave = self.env['hr.holidays'].create({
            'employee_id': self.emp_salesman.id,
            'holiday_status_id': holiday_status_id,
            'type': 'remove',
            'holiday_type': 'employee',
            'date_from': '2019-10-05',
            'date_to': '2019-10-10'
        })
        confirmation_message = leave.message_ids
        self.assertEqual(confirmation_message.subtype_id.name, 'Confirmed')
        self.assertEqual([self.manager.partner_id.id,
                          self.salesman.partner_id.id],
                         confirmation_message.needaction_partner_ids.ids)
        leave.sudo(user=self.manager).action_approve()
        approbation_message = leave.message_ids - confirmation_message
        self.assertEqual(approbation_message.subtype_id.name, 'Approved')
        self.assertEqual([self.manager.partner_id.id,
                          self.salesman.partner_id.id],
                         confirmation_message.needaction_partner_ids.ids)
