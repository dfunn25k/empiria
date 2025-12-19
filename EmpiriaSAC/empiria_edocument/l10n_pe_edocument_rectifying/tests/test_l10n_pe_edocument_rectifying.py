from odoo.tests.common import TransactionCase

class TestAccountMove(TransactionCase):
    def test_refund_reason_13(self):
        # Get the model and search for the account.move
        account_move = self.env['account.move']
        move = account_move.search([], limit=1)

        self.assertIn(
            ('13', 'Corrección del monto neto pendiente de pago y/o la(s) de vencimiento del \n pago único o de las cuotas y/o los montos '
            'correspondientes a cada cuota , de ser el caso'),
            move._fields['l10n_pe_edi_refund_reason'].selection,
            "El nuevo campo no esta en el modelo"
        )
        print("--- TEST l10n_pe_edocument_rectifying OK ---")