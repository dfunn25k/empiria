odoo.define('serie_and_correlative_pos.PaymentScreen', function (require) {
    "use strict";

    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');

    const PosPaymentScreen = PaymentScreen =>
        class PosPaymentScreen extends PaymentScreen {

            onChange_l10n_latam_document_type_id(ev) {
                // change "l10n_latam_document_type_id"
                let value = ev.target && $(ev.target).val() ? parseInt($(ev.target).val()) : false;
                this.currentOrder.set_l10n_latam_document_type_id(value);
            }

            toggleIsToInvoice() {
                // click_invoice
                this.currentOrder.set_l10n_latam_document_type_id(false);
                super.toggleIsToInvoice();
            }
        }

    Registries.Component.extend(PaymentScreen, PosPaymentScreen);
    return PaymentScreen;
});
