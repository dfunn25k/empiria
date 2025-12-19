from odoo.tests import TransactionCase
from lxml import etree


class TestAccountJournal(TransactionCase):

    def test_onchange_assign_to_domain(self):
        vals = {
            'name': 'Test Journal',
            'type': 'bank',
            'create_asset': False,
        }
        account_journal = self.env['account.journal'].create(vals)
        print('------------JOURNAL CREATED --------------')

        user_a = self.env['res.users'].create({
            'name': 'User A',
            'login': 'user_a',
            'groups_id': [(4, self.env.ref('add_user_by_journal.res_groups_admin_journal_access').id)],
        })

        account_journal.assign_to = [(4, user_a.id)]

        account_journal._onchange_assing_to_domain()
        self.assertIn((4, user_a.id), account_journal.assign_to_domain)
        print('-------------TEST USER-----------------')
        self.assertEqual(account_journal.assign_to_domain, [(4, user_a.id)])
        print('----------------TEST OK ---------------------')

    def test_account_payment_fields_view_get(self):
        user_b = self.env['res.users'].create({
            'name': 'User B',
            'login': 'user_b',
            'groups_id': [(4, self.env.ref('add_user_by_journal.res_groups_admin_journal_access').id)],
        })
        account_payment = self.env['account.payment'].create({
            'name': 'Test Payment',
            'amount': 100.0,
            'journal_id': self.env.ref('account.bank_journal').id,
        })
        view_id = self.env['ir.ui.view'].search([('model', '=', 'account.payment'), ('type', '=', 'form')]).id
        res_view = account_payment.fields_view_get(view_id=view_id, view_type='form')

        self.assertIn('arch', res_view)
        doc = etree.XML(res_view['arch'])
        value = "//field[@name='journal_id']"
        for node in doc.xpath(value):
            domain = node.attrib.get('domain', '')
            if user_b.has_group('add_user_by_journal.res_groups_admin_journal_access'):
                self.assertNotIn('assign_to', domain)
            else:
                self.assertIn('assign_to', domain)
                self.assertIn(str(user_b.id), domain)
        print('----------------TEST OK -----------------')

    def test_account_move_fields_view_get(self):
        user_c = self.env['res.users'].create({
            'name': 'User C',
            'login': 'user_c',
            'groups_id': [(4, self.env.ref('add_user_by_journal.res_groups_admin_journal_access').id)],
        })

        account_move = self.env['account.move'].create({
            'name': 'Test Move',
            'journal_id': self.env.ref('account.bank_journal').id,  # Replace with the appropriate journal ID
        })
        self.env = self.env(user=user_c)

        view_id = self.env['ir.ui.view'].search([('model', '=', 'account.move'), ('type', '=', 'form')]).id
        res_view = account_move.fields_view_get(view_id=view_id, view_type='form')

        self.assertIn('arch', res_view)
        doc = etree.XML(res_view['arch'])
        value = "//field[@name='journal_id']"
        for node in doc.xpath(value):
            if user_c:
                self.assertEqual(node.attrib['domain'],
                                 "['&', ('id', 'in', suitable_journal_ids), ('type', 'in', ('purchase','general','situation','sale','bank','cash'))]")
            else:
                self.assertEqual(
                    node.attrib['domain'],
                    "['&', '&', ('id', 'in', suitable_journal_ids), ('assign_to', 'in', [user.id]), ('type', 'in', ('purchase','general','situation','sale','bank','cash'))]"
                )
        print('--------------------------TEST OK ------------------------')
