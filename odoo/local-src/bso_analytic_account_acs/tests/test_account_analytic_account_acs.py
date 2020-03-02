from odoo.tests import common
from odoo.exceptions import ValidationError


@common.at_install(False)
@common.post_install(True)
class TestAccountAnalyticAccountAcs(common.TransactionCase):

    def setUp(self):
        super(TestAccountAnalyticAccountAcs, self).setUp()
        company_id = self.env['res.company'].create({'name': 'test company'})
        self.ac1 = self.env['account.analytic.account'].create(
            {
                'name': 'ac1',
                'company_id': company_id.id,
            }
        )
        self.ac2 = self.env['account.analytic.account'].create({
            'name': 'ac2',
            'company_id': company_id.id,
        })
        self.ac3 = self.env['account.analytic.account'].create({
            'name': 'ac3',
            'company_id': company_id.id,
        })
        self.ac4 = self.env['account.analytic.account'].create({
            'name': 'ac4',
            'company_id': company_id.id,
        })

    def test_children_levels_ok(self):
        self.ac4.parent_ids = [self.ac3.id]
        self.ac3.parent_ids = [self.ac2.id]
        self.ac2.parent_ids = [self.ac1.id]
        self.assertEqual(self.ac1.immediate_child_ids, self.ac2)

        self.assertEqual(set(self.ac1.all_child_ids.ids),
                         {self.ac2.id, self.ac3.id, self.ac4.id})
        self.assertEqual(set(self.ac1.all_child_self_included_ids.ids),
                         {self.ac1.id, self.ac2.id, self.ac3.id, self.ac4.id})

    def test_constrains_nok(self):
        with self.assertRaises(ValidationError):
            self.ac1.parent_ids = [self.ac1.id]
        self.ac4.parent_ids = [self.ac3.id]
        with self.assertRaises(ValidationError):
            self.ac2.parent_ids = [self.ac4.id, self.ac3.id]
        with self.assertRaises(ValidationError):
            self.ac3.parent_ids = [self.ac4.id]
