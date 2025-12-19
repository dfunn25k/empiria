import time
from freezegun import freeze_time

import odoo
from odoo.addons.point_of_sale.tests.common import TestPointOfSaleCommon


@odoo.tests.tagged('post_install', '-at_install')
class TestGenerateDynamicReport(TestPointOfSaleCommon):

    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

    def compute_tax(self, product, price, qty=1, taxes=None):

        if not taxes:
            taxes = product.taxes_id.filtered(lambda t: t.company_id.id == self.env.company.id)
        currency = self.pos_config.pricelist_id.currency_id
        res = taxes.compute_all(price, currency, qty, product=product)
        untax = res['total_excluded']
        return untax, sum(tax.get('amount', 0.0) for tax in res['taxes'])

    def test_generate_dynamic_report_from_pos_ui(self):

        # Creates an order from pos an ensures to create an account move from the order
        self.pos_config.open_ui()
        current_session = self.pos_config.current_session_id

        untax1, atax1 = self.compute_tax(self.product3, 450 * 0.95, 2)
        untax2, atax2 = self.compute_tax(self.product4, 300 * 0.95, 3)
        # I create a new PoS order with 2 units of PC1 at 450 EUR (Tax Incl) and 3 units of PCSC349 at 300 EUR. (Tax Excl)
        self.pos_order_pos1 = self.PosOrder.create({
            'company_id': self.env.company.id,
            'session_id': current_session.id,
            'partner_id': self.partner1.id,
            'pricelist_id': self.partner1.property_product_pricelist.id,
            'lines': [(0, 0, {
                'name': "OL/0001",
                'product_id': self.product3.id,
                'price_unit': 450,
                'discount': 5.0,
                'qty': 2.0,
                'tax_ids': [
                    (6, 0, self.product3.taxes_id.filtered(lambda t: t.company_id.id == self.env.company.id).ids)],
                'price_subtotal': untax1,
                'price_subtotal_incl': untax1 + atax1,
            }), (0, 0, {
                'name': "OL/0002",
                'product_id': self.product4.id,
                'price_unit': 300,
                'discount': 5.0,
                'qty': 3.0,
                'tax_ids': [
                    (6, 0, self.product4.taxes_id.filtered(lambda t: t.company_id.id == self.env.company.id).ids)],
                'price_subtotal': untax2,
                'price_subtotal_incl': untax2 + atax2,
            })],
            'amount_tax': atax1 + atax2,
            'amount_total': untax1 + untax2 + atax1 + atax2,
            'amount_paid': 0.0,
            'amount_return': 0.0,
        })

        # I click on the "Make Payment" wizard to pay the PoS order
        context_make_payment = {"active_ids": [self.pos_order_pos1.id], "active_id": self.pos_order_pos1.id}
        self.pos_make_payment = self.PosMakePayment.with_context(context_make_payment).create({
            'amount': untax1 + untax2 + atax1 + atax2,
        })
        # I click on the validate button to register the payment.
        context_payment = {'active_id': self.pos_order_pos1.id}
        self.pos_make_payment.with_context(context_payment).check()

        # I check that the order is marked as paid and there is no invoice
        # attached to it
        self.assertEqual(self.pos_order_pos1.state, 'paid', "Order should be in paid state.")
        self.assertFalse(self.pos_order_pos1.account_move, 'Invoice should not be attached to order.')

        # I generate an invoice from the order
        res = self.pos_order_pos1.action_pos_order_invoice()
        self.assertIn('res_id', res, "Invoice should be created")

        # I test that the total of the attached invoice is correct
        invoice = self.env['account.move'].browse(res['res_id'])
        if invoice.state != 'posted':
            invoice.action_post()
        self.assertAlmostEqual(
            invoice.amount_total, self.pos_order_pos1.amount_total, places=2, msg="Invoice not correct")

        # I close the session to generate the journal entries
        current_session.action_pos_session_closing_control()

        # After generate the invoice, check the function to generate a report from the order
        ir_report_id = 213  # id template
        values = self.PosOrder.generate_dynamic_report_from_pos_ui(self.pos_order_pos1.pos_reference, ir_report_id)
        self.assertFalse(values['error'])
