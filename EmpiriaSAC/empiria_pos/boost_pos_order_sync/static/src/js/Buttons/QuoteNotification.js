odoo.define('boost_pos_order_sync.QuoteNotification', function (require) {
    "use strict";

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const { useListener } = require("@web/core/utils/hooks");

    class QuoteNotification extends PosComponent {

        setup() {
            super.setup();
            useListener('click', this._onClick);
        }

        _onClick() {
            var self = this;
            self.rpc({
                model: 'pos.quote',
                method: 'search_all_record',
                args: [{
                    "session_id": self.env.pos.pos_session.id
                }],
            }).then(function (result) {
                let quotes = result['quote_list'];
                self.env.pos.all_quotes = quotes;
                let all_quotes_length = self.env.pos.all_quotes.length;
                if (all_quotes_length >= 1) {
                    self.showTempScreen('ListOrderReceivedScreen', { quotes_received: quotes });
                } else {
                    self.showPopup('MessagePopup', {
                        title: self.env._t('Error Quotes'),
                        body: self.env._t('There are no quotes sent for this session'),
                    });
                }
            });
        }
    }

    QuoteNotification.template = 'QuoteNotification';
    Registries.Component.add(QuoteNotification);
    return QuoteNotification;
});