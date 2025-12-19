odoo.define('pos_employee_access_premium.ProductScreen', function (require) {
    "use strict";

    const ProductScreen = require('point_of_sale.ProductScreen');
    const NumberBuffer = require('point_of_sale.NumberBuffer');
    const Registries = require('point_of_sale.Registries');

    const PosProductScreen = ProductScreen =>
        class PosProductScreen extends ProductScreen {

            async _onClickPay() {
                const user = this.env.pos.get_cashier();
                if (this.env.pos.config.module_pos_hr && !user.pos_access_payment) {
                    this.showPopup("ErrorPopup", {
                        title: this.env._t('Access Denied'),
                        body: this.env._t('You do not have access to apply the payment!'),
                    });
                } else {
                    return await super._onClickPay();
                }
            }

            _setValue(val) {
                const user = this.env.pos.get_cashier();
                const keyboard = NumberBuffer.eventsBuffer[0]?.key || "";
                const mode = this.env.pos.numpadMode;
                const order = this.env.pos.get_order();
                const selectedLine = order.get_selected_orderline();

                if (this.env.pos.config.module_pos_hr && !user.pos_access_decrease_quantity) {
                    const keyboardDisallow = ['Backspace', 'Delete'];
                    if (keyboardDisallow.includes(keyboard)) {
                        this.showPopup("ErrorPopup", {
                            title: this.env._t('Access Denied'),
                            body: this.env._t('You do not have access to decrease the quantity of the line items!'),
                        });
                    } else if (selectedLine && mode === 'quantity' && parseFloat(selectedLine.quantity) > parseFloat(val)) {
                        this.showPopup("ErrorPopup", {
                            title: this.env._t('Access Denied'),
                            body: this.env._t('You do not have access to decrease the quantity of the line items!'),
                        });
                    } else {
                        super._setValue(val);
                    }
                } else if (this.env.pos.config.module_pos_hr && !user.pos_access_delete_orderline && val === 'remove' && mode === 'quantity') {
                    this.showPopup("ErrorPopup", {
                        title: this.env._t('Access Denied'),
                        body: this.env._t('You do not have access to delete the order lines!'),
                    });
                }
                else {
                    super._setValue(val);
                }
            }
        }

    Registries.Component.extend(ProductScreen, PosProductScreen);
    return ProductScreen;
});
