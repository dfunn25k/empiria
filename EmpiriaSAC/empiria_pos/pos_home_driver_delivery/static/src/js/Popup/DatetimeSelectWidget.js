odoo.define('pos_home_driver_delivery.DatetimeSelectWidget', function(require) {
    'use strict';

    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    const { _lt } = require('@web/core/l10n/translation');
    const { onMounted } = owl;

    class DatetimeSelectWidget extends AbstractAwaitablePopup {

        setup() {
            super.setup();
            onMounted(this.onMounted);
        }

        onMounted() {
            $('#del_date').datetimepicker({
                format: 'YYYY-MM-DD HH:mm:ss',
                inline: true,
                sideBySide: true
            })
        }
    }
    
    DatetimeSelectWidget.template = 'DatetimeSelectWidget';
    DatetimeSelectWidget.defaultProps = {
        confirmText: _lt('Select'),
        cancelText: _lt('Cancel'),
        title: _lt('Select Date'),
        body: '',
    };

    Registries.Component.add(DatetimeSelectWidget);
    return DatetimeSelectWidget;
});
