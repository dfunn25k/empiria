# -*- coding: utf-8 -*
from odoo.tests import tagged
from odoo.addons.account_edi.tests.common import AccountEdiTestCommon
from unittest.mock import patch

from freezegun import freeze_time

@tagged('post_install', '-at_install')
class TestEdiFormat(AccountEdiTestCommon):

    def test_l10n_pe_edi_get_edi_values(self):
        invoice = self.init_invoice('out_invoice', products=self.product_a)
        values = self.edi_format._l10n_pe_edi_get_edi_values(invoice)
        self.assertTrue(values['invoice_line_vals_list'])
        print('---------TEST EDI GET VALUES PASSED---------')