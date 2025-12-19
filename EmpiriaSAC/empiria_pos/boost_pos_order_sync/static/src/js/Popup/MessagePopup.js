odoo.define('boost_pos_order_sync.MessagePopup', function (require) {
    "use strict";

    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    const { _lt } = require('@web/core/l10n/translation');

    class MessagePopup extends AbstractAwaitablePopup { }

    MessagePopup.template = 'MessagePopup';
    MessagePopup.defaultProps = {
        cancelText: _lt('Ok'),
        title: _lt('Message'),
        body: ''
    };
    Registries.Component.add(MessagePopup);
    return MessagePopup;
});