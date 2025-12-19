from odoo.tests import tagged

from datetime import timedelta
from .common import TestQueryCdrInvoice

@tagged('post_install', '-at_install')
class TestQueryCdrInvoiceSunat(TestQueryCdrInvoice):

    @classmethod
    def setUpClass(cls, chart_template_ref='l10n_pe.pe_chart_template', edi_format_ref='l10n_pe_edi.edi_pe_ubl_2_1'):
        super().setUpClass(chart_template_ref=chart_template_ref, edi_format_ref=edi_format_ref)

        cls.company_data['company'].l10n_pe_edi_provider = 'sunat'

    def test_get_query_cdr_invoice(self):
        yesterday = self.certificate._get_pe_current_datetime().date() - timedelta(1)
        move = self._create_invoice(invoice_date=yesterday, date=yesterday)
        move.action_post()

        # Send
        doc = move.edi_document_ids.filtered(lambda d: d.state in ('to_send', 'to_cancel'))
        # get cdr
        move.get_query_cdr_invoice()
        self.assertRecordValues(doc, [{'error': False}])
        self.assertRecordValues(move, [{'edi_state': 'sent'}])