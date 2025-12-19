odoo.define('boost_pos_order_sync.QuoteHistoryPopup', function (require) {
    "use strict";

    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    const { _lt } = require('@web/core/l10n/translation');

    class QuoteHistoryPopup extends AbstractAwaitablePopup { }

    QuoteHistoryPopup.template = 'QuoteHistoryPopup';
    QuoteHistoryPopup.defaultProps = {
        cancelText: _lt('Ok'),
        title: _lt('Synchronized Quote History'),
        body: ''
    };
    Registries.Component.add(QuoteHistoryPopup);
    return QuoteHistoryPopup;
});