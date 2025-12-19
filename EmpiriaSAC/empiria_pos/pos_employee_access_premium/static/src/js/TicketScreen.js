odoo.define('pos_employee_access_premium.TicketScreen', function (require) {
    'use strict';

    const TicketScreen = require('point_of_sale.TicketScreen');
    const Registries = require('point_of_sale.Registries');

    const PosTicketScreen = TicketScreen =>
        class PosTicketScreen extends TicketScreen {

            async _onDeleteOrder({ detail: order }) {
                const user = this.env.pos.get_cashier();
                if (this.env.pos.config.module_pos_hr && !user.pos_access_delete_order) {
                    await this.showPopup("ErrorPopup", {
                        title: this.env._t('Access Denied'),
                        body: this.env._t('You do not have access to delete orders!'),
                    });
                } else {
                    return await super._onDeleteOrder({ detail: order });
                }
            }
        }

    Registries.Component.extend(TicketScreen, PosTicketScreen);
    return TicketScreen;
});