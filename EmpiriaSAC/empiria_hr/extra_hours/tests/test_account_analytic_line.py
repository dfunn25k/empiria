from odoo.tests.common import TransactionCase

class TestAccountAnalyticLine(TransactionCase):
        
    def setUp(self):
        super(TestAccountAnalyticLine, self).setUp()
        
        self.account_account_analytic = self.env['account.analytic.account'].create({
           'name':'ExampleAccountAccount',
           'plan_id':1
           
        })
        self.account = self.env['account.analytic.line'].create({
            'name':'ExampleAccount',
            'account_id':self.account_account_analytic.id,
            'extra_hours':False,
            'hours_compensate':False,
            'extra_hours_morning':False,
            'extra_hour_25':0.00,
            'extra_hour_35':0.00,
            'r_extra_hour_25':0.00,
            'r_extra_hour_35':0.00,
            'hour_100':0.00,
            'night_hours':0.00,
            'pay_date':False
        })
              
    def test_fields_account_analytic_line(self):
        self.assertEqual(self.account.name, 'ExampleAccount')
        self.assertEqual(self.account.account_id.id, self.account_account_analytic.id)
        self.assertFalse(self.account.extra_hours, 0.0)
        self.assertFalse(self.account.hours_compensate, 0.0)
        self.assertFalse(self.account.extra_hours_morning, 0.0)
        self.assertEqual(self.account.extra_hour_25, 0.0)
        self.assertEqual(self.account.extra_hour_35, 0.0)
        self.assertEqual(self.account.r_extra_hour_25, 0.0)
        self.assertEqual(self.account.r_extra_hour_35, 0.0)
        self.assertEqual(self.account.hour_100, 0.0)
        self.assertEqual(self.account.night_hours, 0.0)
        self.assertFalse(self.account.pay_date)
        print("-----------TEST FILEDS ACCOUNT LINES OK----------")
    
    def test_function_account_analytic(self):
        self.assertIsNone(self.account._compute_error_dialog())
        self.assertIsNone(self.account._compute_fields())
        self.assertIsNone(self.account._onchange_hours_compensate())
        self.assertIsNone(self.account.action_validate_extra_hours())
        print("-----------TEST FUNCTIONS ACCOUNT LINES OK----------")