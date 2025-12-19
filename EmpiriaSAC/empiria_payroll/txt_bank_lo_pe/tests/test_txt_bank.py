from odoo.tests import common, tagged
from datetime import date
import base64
import logging

_logger = logging.getLogger(__name__)

@tagged('-at_install', 'post_install')
class TestMassivePayment(common.TransactionCase):
    
    def setUp(self):
        super().setUp()
        self._create_test_data()
        
    def _create_test_data(self):
        self.partner = self.env['res.partner'].create({'name': 'Test Partner'})
        
        self.bank_account = self.env['res.partner.bank'].create({
            'acc_number': '1234567890',
            'acc_type': 'wage',
            'partner_id': self.partner.id,
            'bank_id': False, 
            'type_bank_code': 'CC-TEST-100',
            'currency_id': self.env['res.currency'].search([('name', '=', 'PEN')], limit=1).id
        })
        
        self.test_employee = self.env['hr.employee'].create({
            'name': 'Test User - employee',
            'user_id': self.env['res.users'].search([], limit=1).id,
            'company_id': self.env['res.company'].search([], limit=1).id,
            'bank_account_id': self.bank_account.id,
        })
        
        self.payslip = self.env['hr.payslip'].create({
            'name': 'Test Payslip',
            'employee_id': self.test_employee.id,
            'date_from': date.today(),
            'date_to': date.today(),
        })

        self.binary_content = base64.b64encode(b'Test content')
        self.binary_content2 = base64.b64encode(b'Test content 2')
        
        self.massive_payment = self.env['hr.massive.payment'].create({
            'payment_date': date.today(),
            'acc_type': 'wage',
            'exchange_type': 1.0,
            'partner_id': self.partner.id,
            'payment_type_id': self.bank_account.id,
            'is_validate_account': True,
            'payslip_ids': [(6, 0, [self.payslip.id])],
            'type_process': 'A',
            'future_date': date.today(),
            'run_time': 'B',
            'txt_filename': 'test_file.txt',
            'txt_binary': self.binary_content,
            'txt_filename2': 'test_file2.txt',
            'txt_binary2': self.binary_content2
        })
    
    def test_module_installed(self):
        module = self.env['ir.module.module'].search([('name', '=', 'txt_bank_lo_pe')])
        self.assertTrue(module.state == 'installed', 'Module not installed')
        _logger.info("Module installed successfully")
    
    def test_massive(self):
        self.assertEqual(self.massive_payment.payment_date, date.today())
        self.assertEqual(self.massive_payment.acc_type, 'wage')
        self.assertEqual(self.massive_payment.exchange_type, 1.0)
        self.assertEqual(self.massive_payment.partner_id.id, self.partner.id)
        self.assertEqual(self.massive_payment.payment_type_id.id, self.bank_account.id)
        self.assertTrue(self.massive_payment.is_validate_account)
        self.assertEqual(self.massive_payment.payslip_ids.ids, [self.payslip.id])
        self.assertEqual(self.massive_payment.type_process, 'A')
        self.assertEqual(self.massive_payment.future_date, date.today())
        self.assertEqual(self.massive_payment.run_time, 'B')
        self.assertEqual(self.massive_payment.txt_filename, 'test_file.txt')
        self.assertEqual(self.massive_payment.txt_binary, self.binary_content)
        self.assertEqual(self.massive_payment.txt_filename2, 'test_file2.txt')
        self.assertEqual(self.massive_payment.txt_binary2, self.binary_content2)
        
        bank_bbva = self.massive_payment.get_bank_id_bbva(self.test_employee, self.massive_payment.acc_type)
        if not bank_bbva:
            self.assertFalse(bank_bbva) 
        else:
            self.assertEqual(self.bank_account, bank_bbva)

    def _set_bank_account(self, sunat_bank_code):
        bank = self.env['res.bank'].search([('sunat_bank_code', '=', sunat_bank_code)], limit=1)
        if not bank:
            bank = self.env['res.bank'].create({'name': f'Test Bank {sunat_bank_code}', 'sunat_bank_code': sunat_bank_code})
        self.bank_account.bank_id = bank
        return self.bank_account

    def test_get_partner_bank_by_code_scotiabank(self):
        bank_scotiabank = self._set_bank_account('09')
        bank_by_code = self.massive_payment.get_partner_bank_by_code(self.test_employee, '09', '=', self.massive_payment.acc_type)
        if not bank_by_code:
            self.assertFalse(bank_by_code)
        else:
            self.assertEqual(bank_by_code, bank_scotiabank)
        if not bank_scotiabank:
            self.assertNotEqual(self.bank_account.bank_id, bank_scotiabank)

    def test_get_partner_bank_by_code_bcp(self):
        bank_bcp = self._set_bank_account('02')
        bank_by_code = self.massive_payment.get_partner_bank_by_code(self.test_employee, '02', '=', self.massive_payment.acc_type)
        if not bank_by_code:
            self.assertFalse(bank_by_code)
        else:
            self.assertEqual(bank_by_code, bank_bcp)
        if not bank_bcp:
            self.assertNotEqual(self.bank_account.bank_id, bank_bcp)

    def test_get_partner_bank_by_code_interbank(self):
        bank_interbank = self._set_bank_account('03')
        bank_by_code = self.massive_payment.get_partner_bank_by_code(self.test_employee, '03', '=', self.massive_payment.acc_type)
        if not bank_by_code:
            self.assertFalse(bank_by_code)
        else:
            self.assertEqual(bank_by_code, bank_interbank)
        if not bank_interbank:
            self.assertNotEqual(self.bank_account.bank_id, bank_interbank)

