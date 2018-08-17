# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase


class TestCrmLead(TransactionCase):
    def setUp(self):
        super(TestCrmLead, self).setUp()
        Partner = self.env['res.partner'].with_context(tracking_disable=True)
        country_france = self.env['res.country'].search(
            [('name', '=', 'France')]
        )
        values = {'name': 'Test Customer',
                  'customer': True,
                  'supplier': False,
                  'street': 'street',
                  'street2': 'street2',
                  'zip': 'zipcode',
                  'country_id': country_france.id,
                  }
        self.partner1 = Partner.create(values)
        values.update({'name': 'Test Supplier',
                       'customer': False,
                       'supplier': True,
                       })
        self.partner2 = Partner.create(values)

    def test_customer_lead(self):
        lead = self.partner1.lead_id
        self.assertTrue(lead)
        self.assertEqual(lead.street, self.partner1.street)

    def test_suppplier_no_lead(self):
        lead = self.partner2.lead_id
        self.assertFalse(lead)

    def test_update_lead(self):
        lead = self.partner1.lead_id
        self.partner1.street = 'new street'
        self.assertEqual(self.partner1.lead_id, lead,
                         'Lead has changed')
        self.assertEqual(lead.street, self.partner1.street,
                         'Street was not updated')

    def _make_opportunity(self, lead):
        wizard = self.env['crm.lead2opportunity.partner'].with_context(
            active_id=lead.id,
            active_ids=lead.ids).create({'name': 'convert'})
        wizard.action_apply()
        opportunity = self.env['crm.lead'].search(
            [('partner_id', '=', self.partner1.id),
             ('type', '!=', 'lead'),
             ]
        )
        return opportunity

    def test_opportunity(self):
        lead = self.partner1.lead_id
        opportunity = self._make_opportunity(lead)
        self.assertEqual(len(opportunity), 1)
        self.assertEqual(opportunity.original_lead_id, lead)
        self.assertEqual(opportunity.street, self.partner1.street)

    def test_update_partner_nochange_opportunity(self):
        lead = self.partner1.lead_id
        opportunity = self._make_opportunity(lead)
        old_street = self.partner1.street
        self.partner1.street = 'new street'
        self.assertEqual(lead.street, self.partner1.street)
        self.assertEqual(opportunity.street, old_street,
                         'street was updated on opportunity')
