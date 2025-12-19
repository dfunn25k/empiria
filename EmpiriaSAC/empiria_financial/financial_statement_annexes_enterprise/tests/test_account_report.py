from odoo.addons.account.tests.common import AccountTestInvoicingCommon

from odoo import fields, Command
from odoo.tests import tagged
from odoo.tools import frozendict

@tagged('post_install', '-at_install')
class TestWizardReportFinancial(AccountTestInvoicingCommon):

    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        
        cls.reports = cls.env['account.report'].search([('country_id', 'in', available_country_ids)]).with_context(allowed_company_ids=cls.company_data['company'].ids)

    def test_open_wizard_financial():
        if cls.reports:
            dict = cls.reports[0].open_wizard_financial()
            cls.assertTrue(dict)
            cls.assertTrue(dict['view_id'])
            print(dict['view_id'])
            print('------------Test Wizard Financial View------------')
