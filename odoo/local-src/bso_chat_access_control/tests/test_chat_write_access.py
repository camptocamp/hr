from odoo.exceptions import AccessError
from odoo.tests import common


@common.at_install(False)
@common.post_install(True)
class TestChatWriteAccess(common.TransactionCase):
    def setUp(self):
        super(TestChatWriteAccess, self).setUp()

        def get_model_from_name(model_name):
            """

            :param model_name: model name as string, eg: test.model
            :return: ir.model record
            """
            return self.env['ir.model'].search([('model', '=', model_name)])

        group = self.env['res.groups'].create({'name': 'test group'})

        self.user = self.env['res.users'].create(
            {'login': 'tuser81',
             'name': 'test user',
             'groups_id': [(6, 0, [group.id])]}
        )
        self.model_id = get_model_from_name('sale.subscription')

        self.access = self.env['ir.model.access'].create(
            {'model_id': self.model_id.id,
             'name': 'test_access_rule',
             'group_id': self.user.groups_id.id,
             'perm_read': True,
             'perm_chat': True
             }
        )
        self.env['ir.model.access'].create({
            'model_id': get_model_from_name('mail.tracking.value').id,
            'name': 'mail_tracking_test_rule',
            'group_id': self.user.groups_id.id,
            'perm_read': True
        })
        self.env['ir.model.access'].create({
            'model_id': get_model_from_name('mail.notification').id,
            'name': 'mail_notification_test_rule',
            'group_id': self.user.groups_id.id,
            'perm_read': True
        })
        self.env['ir.model.access'].create({
            'model_id': get_model_from_name('res.partner').id,
            'name': 'res_partner_test_rule',
            'group_id': self.user.groups_id.id,
            'perm_read': True
        })
        self.env['ir.model.access'].create({
            'model_id': get_model_from_name('res.groups').id,
            'name': 'res_partner_test_rule',
            'group_id': self.user.groups_id.id,
            'perm_read': True
        })
        self.env['ir.model.access'].create({
            'model_id': get_model_from_name('mail.message').id,
            'name': 'res_partner_test_rule',
            'group_id': self.user.groups_id.id,
            'perm_read': True,
        })
        self.subtype_id = self.env['mail.message.subtype'].create({
            'name': 'mt_mg_def',
            'default': True,
            'res_model': 'sale.subscription',
            'internal': False
        })

    def test_chat_access_nok(self):
        partner_id = self.user.partner_id.id
        access = self.env['ir.model.access'].search(
            [('id', '=', self.access.id)])
        access.update({'perm_chat': False})
        self.env.uid = self.user.id

        vals = {'attachment_ids': [],
                'email_from': 'test@bso.tst',
                'author_id': partner_id,
                'body': u'body',
                'message_type': u'comment',
                'model': self.model_id.model,
                'subject': False,
                }
        with self.assertRaises(AccessError):
            self.env['mail.message'].create(vals)

    def test_chat_acces_chat_perm_ok(self):
        access_obj = self.env['ir.model.access'].search(
            [('id', '=', self.access.id)])

        access_obj.update({'perm_read': True, 'perm_chat': True})
        partner_id = self.user.partner_id.id

        self.env.uid = self.user.id

        vals = {'attachment_ids': [],
                'author_id': partner_id,
                'email_from': 'test@bso.test',
                'body': 'body',
                'message_type': 'comment',
                'model': self.model_id.model,
                'subject': False,
                'subtype_id': self.subtype_id.id
                }
        chat_message = self.env['mail.message'].create(vals)
        self.assertEqual(chat_message.body, unicode('<p>body</p>'))
        self.assertEqual(chat_message.email_from, unicode(vals['email_from']))
        self.assertEqual(chat_message.author_id.id, self.user.partner_id.id)
