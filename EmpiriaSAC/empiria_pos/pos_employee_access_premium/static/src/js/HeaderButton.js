odoo.define('pos_employee_access_premium.HeaderButton', function (require) {
    "use strict";

    const HeaderButton = require('point_of_sale.HeaderButton');
    const Registries = require('point_of_sale.Registries');
    const { ConnectionLostError, ConnectionAbortedError } = require('@web/core/network/rpc_service')
    const { identifyError } = require('point_of_sale.utils');

    const PosHeaderButton = HeaderButton =>
        class PosHeaderButton extends HeaderButton {

            async onClick() {
                try {
                    const user = this.env.pos.get_cashier();
                    if (this.env.pos.config.module_pos_hr && !user.pos_access_close) {
                        this.showPopup("ErrorPopup", {
                            title: this.env._t('Access Denied'),
                            body: this.env._t('You do not have access to close the POS!'),
                        });
                    } else {
                        const info = await this.env.pos.getClosePosInfo();
                        this.showPopup('ClosePosPopup', { info: info, keepBehind: true });
                    }
                } catch (e) {
                    if (identifyError(e) instanceof ConnectionAbortedError || ConnectionLostError) {
                        this.showPopup('OfflineErrorPopup', {
                            title: this.env._t('Network Error'),
                            body: this.env._t('Please check your internet connection and try again.'),
                        });
                    } else {
                        this.showPopup('ErrorPopup', {
                            title: this.env._t('Unknown Error'),
                            body: this.env._t('An unknown error prevents us from getting closing information.'),
                        });
                    }
                }
            }
        }

    Registries.Component.extend(HeaderButton, PosHeaderButton);
    return HeaderButton;
});


