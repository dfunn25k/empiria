from odoo import Command
from odoo.tests import TransactionCase, tagged
from odoo.exceptions import UserError
from freezegun import freeze_time

@tagged('post_install', '-at_install')
class TestAccountOperations(TransactionCase):

    def setUp(self):
        super(TestAccountOperations, self).setUp()

        self.company = self.env['res.company'].create({
            'name': 'Test Company',
        })
        self.env.company = self.company
        self.env.user.company_ids |= self.company
        self.env.user.company_id = self.company

        self.currency = self.env['res.currency'].search([], limit=1)
        
        self.journal = self.env['account.journal'].create({
            'name': 'Test Journal',
            'code': 'TST',
            'type': 'general',
            'company_id': self.company.id,
        })

        self.account_revenue = self.env['account.account'].create({
            'name': 'Test Revenue Account',
            'code': 'X123',
            'account_type': 'income',
            'company_id': self.company.id,
        })
        self.account_expense = self.env['account.account'].create({
            'name': 'Test Expense Account',
            'code': 'X124',
            'account_type': 'expense',
            'company_id': self.company.id,
        })

    def test_prevent_changing_account_company_with_journal_entries(self):
        self.env['account.move'].create({
            'move_type': 'entry',
            'date': '2019-01-01',
            'journal_id': self.journal.id,
            'company_id': self.company.id,
            'line_ids': [
                (0, 0, {
                    'name': 'line_debit',
                    'account_id': self.account_revenue.id,
                    'debit': 100,
                }),
                (0, 0, {
                    'name': 'line_credit',
                    'account_id': self.account_revenue.id,
                    'credit': 100,
                }),
            ],
        })

        with self.assertRaises(UserError):
            self.account_revenue.company_id = self.env['res.company'].create({'name': 'Another Company'})

    def test_toggle_reconcile_status_on_account_with_entries(self):
        ''' Verify the behavior when toggling the reconcile status on an account with existing journal entries. '''
        move = self.env['account.move'].create({
            'move_type': 'entry',
            'date': '2019-01-01',
            'journal_id': self.journal.id,
            'company_id': self.company.id,
            'line_ids': [
                (0, 0, {
                    'account_id': self.account_revenue.id,
                    'currency_id': self.currency.id,
                    'debit': 100.0,
                    'credit': 0.0,
                    'amount_currency': 200.0,
                }),
                (0, 0, {
                    'account_id': self.account_revenue.id,
                    'currency_id': self.currency.id,
                    'debit': 0.0,
                    'credit': 100.0,
                    'amount_currency': -200.0,
                }),
            ],
        })
        move.action_post()
        self.env['account.move.line'].flush_model()
        self.assertRecordValues(move.line_ids, [
            {'reconciled': False, 'amount_residual': 0.0, 'amount_residual_currency': 0.0},
            {'reconciled': False, 'amount_residual': 0.0, 'amount_residual_currency': 0.0},
        ])

        self.account_revenue.reconcile = True
        self.env.invalidate_all()

        self.assertRecordValues(move.line_ids, [
            {'reconciled': False, 'amount_residual': 100.0, 'amount_residual_currency': 200.0},
            {'reconciled': False, 'amount_residual': -100.0, 'amount_residual_currency': -200.0},
        ])

        move.line_ids.reconcile()
        self.assertRecordValues(move.line_ids, [
            {'reconciled': True, 'amount_residual': 0.0, 'amount_residual_currency': 0.0},
            {'reconciled': True, 'amount_residual': 0.0, 'amount_residual_currency': 0.0},
        ])

        move.line_ids.remove_move_reconcile()
        self.account_revenue.reconcile = False
        self.env.invalidate_all()

        self.assertRecordValues(move.line_ids, [
            {'reconciled': False, 'amount_residual': 0.0, 'amount_residual_currency': 0.0},
            {'reconciled': False, 'amount_residual': 0.0, 'amount_residual_currency': 0.0},
        ])

    def test_toggle_reconcile_status_with_partial_reconciliation(self):
        move = self.env['account.move'].create({
            'move_type': 'entry',
            'date': '2019-01-01',
            'journal_id': self.journal.id,
            'company_id': self.company.id,
            'line_ids': [
                (0, 0, {
                    'account_id': self.account_revenue.id,
                    'currency_id': self.currency.id,
                    'debit': 100.0,
                    'credit': 0.0,
                    'amount_currency': 200.0,
                }),
                (0, 0, {
                    'account_id': self.account_revenue.id,
                    'currency_id': self.currency.id,
                    'debit': 0.0,
                    'credit': 50.0,
                    'amount_currency': -100.0,
                }),
                (0, 0, {
                    'account_id': self.account_expense.id,
                    'currency_id': self.currency.id,
                    'debit': 0.0,
                    'credit': 50.0,
                    'amount_currency': -100.0,
                }),
            ],
        })
        move.action_post()

        self.account_revenue.reconcile = True
        self.env.invalidate_all()

        move.line_ids.filtered(lambda line: line.account_id == self.account_revenue).reconcile()

        with self.assertRaises(UserError), self.cr.savepoint():
            self.account_revenue.reconcile = False
