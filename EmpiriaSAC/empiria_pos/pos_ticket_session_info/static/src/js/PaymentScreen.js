odoo.define('pos_ticket_session_info.PaymentScreen', function (require) {
    "use strict";

    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');

    const SessionInfoPosPaymentScreen = PaymentScreen =>
        class PosPaymentScreen extends PaymentScreen {

            async _finalizeValidation() {
                this.currentOrder.order_change = this.currentOrder.get_change();
                await super._finalizeValidation();
            }
        }

    Registries.Component.extend(PaymentScreen, SessionInfoPosPaymentScreen);
    return PaymentScreen;
});
