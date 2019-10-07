from odoo.tests import common


@common.at_install(False)
@common.post_install(True)
class TestIrModelAccess(common.TransactionCase):

    def test_create_rule_without_perm_chat(self):
        def get_model_from_name(model_name):
            return self.env['ir.model'].search([('model', '=', model_name)])

        access = self.env['ir.model.access'].create({
            'model_id': get_model_from_name('res.partner').id,
            'name': 'res_partner_test_rule',
            'group_id': self.env.user.groups_id[-1].id,
            'perm_write': True
        })
        self.assertEqual(access.perm_chat, access.perm_write)
        access.write({'perm_chat': True})
        self.assertEqual(access.perm_chat, True)
