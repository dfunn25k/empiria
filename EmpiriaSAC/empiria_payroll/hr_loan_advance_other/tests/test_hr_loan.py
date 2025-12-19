import logging

from odoo.tests import tagged
from odoo.addons.hr_contract.tests.common import TestContractCommon
from datetime import datetime

_logger = logging.getLogger(__name__)


@tagged('-at_install', 'post_install')
class TestHrLoan(TestContractCommon):

    def setUp(self):
        super().setUp()
        self.company = self.env.ref('base.main_company')
        self.journal = self.env['account.journal'].search([
            ('company_id', '=', self.company.id),
            ('type', '=', 'sale')
        ], limit=1)
        self.default_acccount = self.env['account.account'].search([
            ('company_id', '=', self.company.id),
            ('account_type', '=', 'income'),
        ], limit=1)
    
    def create_contract(self, state, kanban_state, start, end=None):
        
        return self.env['hr.contract'].create({
            'name': 'Contract',
            'employee_id': self.employee.id,
            'state': state,
            'kanban_state': kanban_state,
            'wage': 1,
            'date_start': start,
            'date_end': end,
        })
    
    def create_loan(self):
        start = datetime.strptime('2022-06-01', '%Y-%m-%d').date()
        contract = self.create_contract('open', 'normal', start)
        loan = self.env['hr.loan'].create({
            'employee_id': self.employee.id,
            'loan_amount': 300,
            'contract_id': contract.id,
            'journal_id': self.journal.id,
            'emp_account_id': self.default_acccount.id,
            'treasury_account_id': self.default_acccount.id,
        })
        return loan
    
    def test_approve_loan(self):
        loan = self.create_loan()
        loan.compute_installment()
        res = loan.action_approve()
        self.assertEqual(
            res, True,
            'The loan should be approve it.',
        )
        _logger.info('Test approve loan hr passed')