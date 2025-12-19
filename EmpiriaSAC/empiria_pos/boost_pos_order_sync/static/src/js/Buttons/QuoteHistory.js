odoo.define('boost_pos_order_sync.QuoteHistory', function (require) {
    "use strict";

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    const { useListener } = require("@web/core/utils/hooks");

    class QuoteHistory extends PosComponent {

        setup() {
            super.setup();
            useListener('click', this._onClick);
        }

        _onClick() {
            var self = this;
            self.rpc({
                model: 'pos.quote',
                method: 'load_quote_history',
                args: [{
                    'session_id': self.env.pos.pos_session.id,
                }],
            }).then(function (result) {
                self.env.pos.history = result.quote_list
                $('#quote_history').css('color', '#5EB937');
                self.showPopup('QuoteHistoryPopup', {
                    quotes: self.env.pos.history
                })
            }).catch(function (error) {
                console.error(error)
                $("#quote_history").css('color', '#FF0000');
                self.showPopup('ErrorPopup', {
                    title: self.env._t('Error Network'),
                    body: self.env._t('Please make sure you are connected to the network'),
                });
            });
        }
    }

    QuoteHistory.template = 'QuoteHistory';
    Registries.Component.add(QuoteHistory);
    return QuoteHistory;
});