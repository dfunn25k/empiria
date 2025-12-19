from odoo.tests.common import TransactionCase


class TestAccountMove(TransactionCase):

    def setUp(self):
        super(TestAccountMove, self).setUp()
        self.AccountMove = self.env['account.move']

    def test_create_account_move_with_aditional_document_reference(self):
        move = self.AccountMove.create({
            'name': 'Test Move',
            'aditional_document_reference': '123-ABC',
        })

        self.assertTrue(move)
        self.assertEqual(move.aditional_document_reference, '123-ABC')

    def test_update_aditional_document_reference(self):
        move = self.AccountMove.create({
            'name': 'Test Move',
            'aditional_document_reference': '123-ABC',
        })

        move.aditional_document_reference = '456-DEF'
        self.assertEqual(move.aditional_document_reference, '456-DEF')

    def test_delete_account_move_with_aditional_document_reference(self):
        move = self.AccountMove.create({
            'name': 'Test Move',
            'aditional_document_reference': '123-ABC',
        })

        move_id = move.id
        move.unlink()
        move_deleted = self.AccountMove.search([('id', '=', move_id)])

        self.assertFalse(move_deleted)

    def test_create_account_move_without_aditional_document_reference(self):
        move = self.AccountMove.create({
            'name': 'Test Move',
        })

        self.assertTrue(move)
        self.assertFalse(move.aditional_document_reference)

    def test_search_by_aditional_document_reference(self):
        move = self.AccountMove.create({
            'name': 'Test Move',
            'aditional_document_reference': '123-ABC',
        })

        search_result = self.AccountMove.search([('aditional_document_reference', '=', '123-ABC')])

        self.assertIn(move, search_result)
