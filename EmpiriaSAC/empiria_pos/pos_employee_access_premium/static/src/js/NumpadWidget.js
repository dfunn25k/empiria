odoo.define('pos_employee_access_premium.NumpadWidget', function (require) {
    "use strict";

    const NumpadWidget = require('point_of_sale.NumpadWidget');
    const Registries = require('point_of_sale.Registries');

    const PosNumpadWidget = NumpadWidget =>
        class PosNumpadWidget extends NumpadWidget {

            sendInput(key) {
                const user = this.env.pos.get_cashier();
                if (this.env.pos.config.module_pos_hr && !user.pos_access_decrease_quantity && key === 'Backspace') {
                    this.showPopup("ErrorPopup", {
                        title: this.env._t('Access Denied'),
                        body: this.env._t('You do not have access to decrease the quantity of the line items!'),
                    });
                } else {
                    super.sendInput(key);
                }
            }

            changeMode(mode) {
                const user = this.env.pos.get_cashier();
                if (this.env.pos.config.module_pos_hr && !user.pos_access_discount && mode === 'discount') {
                    this.showPopup("ErrorPopup", {
                        title: this.env._t('Access Denied'),
                        body: this.env._t('You do not have access to apply discounts!'),
                    });
                }
                else if (this.env.pos.config.module_pos_hr && !user.pos_access_price && mode === 'price') {
                    this.showPopup("ErrorPopup", {
                        title: this.env._t('Access Denied'),
                        body: this.env._t('You do not have access to change the price!'),
                    });
                }
                else {
                    super.changeMode(mode);
                }
            }
        }

    Registries.Component.extend(NumpadWidget, PosNumpadWidget);
    return NumpadWidget;
});
