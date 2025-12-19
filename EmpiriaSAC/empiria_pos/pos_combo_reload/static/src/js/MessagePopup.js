odoo.define('pos_combo_reload.MessagePopup', function(require) {
    'use strict';

    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    const { _lt } = require('@web/core/l10n/translation');

    class MessagePopup extends AbstractAwaitablePopup {}
    MessagePopup.template = 'MessagePopup';
    MessagePopup.defaultProps = {
        title: _lt('Message'),
        confirmText: _lt('Ok'),
        body: '',
    };

    Registries.Component.add(MessagePopup);

    return MessagePopup;
});
