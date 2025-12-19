odoo.define('autocreate_pos_invoice.PaymentScreen', function (require) {
    "use strict";

    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');

    const PosPaymentScreen = PaymentScreen =>
        class PosPaymentScreen extends PaymentScreen {

            async _finalizeValidation() {

                if (!this.currentOrder.is_to_invoice() && this.env.pos.config.always_move_account) {
                    if (!this.currentOrder.get_partner()) {
                        const { confirmed } = await this.showPopup('ConfirmPopup', {
                            title: this.env._t('Please select the Customer'),
                            body: this.env._t('You need to select the customer before you can invoice an order.')
                        });
                        if (confirmed) {
                            this.selectPartner();
                        }
                        return false;
                    }
                    this.currentOrder.to_invoice = true;
                    this.currentOrder.fake_invoice = true;
                }
                await super._finalizeValidation();
            }
        }

    Registries.Component.extend(PaymentScreen, PosPaymentScreen);
    return PaymentScreen;
});
