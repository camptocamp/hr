from odoo.tests import common


class TestCrmLead(common.TransactionCase):

    def setUp(self):
        super(TestCrmLead, self).setUp()

    def test_renew_mrc_compute(self):
        lead = self.env['crm.lead'].create(
            {
                'name': 'test opp',
                'type': 'opportunity',
                'planned_revenue_mrc': 1000,
                'planned_revenue_renew_mrc': 0
            })
        self.assertEqual(lead.planned_revenue_new_mrc, 1000)
        lead.update({'planned_revenue_renew_mrc': 200})
        self.assertEqual(lead.planned_revenue_new_mrc, 800)
