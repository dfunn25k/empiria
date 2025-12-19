odoo.define('boost_pos_order_sync.SendButton', function (require) {
    "use strict";

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const { useListener } = require("@web/core/utils/hooks");

    class SendButton extends PosComponent {

        setup() {
            super.setup();
            useListener('click', this._onClick);
        }

        _onClick() {
            var self = this;
            var current_order = self.env.pos.get_order();
            if (current_order && current_order.orderlines) {
                if (current_order.orderlines.length == 0) {
                    self.showPopup('ErrorPopup', {
                        title: self.env._t('Empty quotation'),
                        body: self.env._t("You can't send an empty quotation, please add some products in cart")
                    });
                }
                else {
                    self.rpc({
                        model: 'ir.sequence',
                        method: 'next_by_code',
                        args: ['pos.quote'],
                        context: self.env.session.user_context,
                    }).then(function (quote_sequence_id) {
                        if (quote_sequence_id) {
                            self.showPopup('SendOrderPopup', {
                                title: self.env._t('Send Quotation'),
                                confirmText: self.env._t('Cancel'),
                            });
                            setTimeout(function () {
                                $('#quote_note').focus();
                                $('#quote_id').text(quote_sequence_id);
                            }, 150);
                        } else {
                            self.showPopup('ErrorPopup', {
                                title: self.env._t('Error Sequence'),
                                confirmText: self.env._t('Missing to configure the sequence for the company'),
                            });
                        }
                    }).catch(function (error) {
                        console.error(error)
                        self.showPopup('ErrorPopup', {
                            title: self.env._t('Error Network'),
                            body: self.env._t('Please make sure you are connected to the network'),
                        });
                    });
                }
            }
        }
    }

    SendButton.template = 'SendButton';
    Registries.Component.add(SendButton);
    return SendButton;
});