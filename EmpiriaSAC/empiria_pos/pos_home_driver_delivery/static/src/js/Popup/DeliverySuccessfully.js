odoo.define('pos_home_driver_delivery.DeliverySuccessfully', function(require) {
    'use strict';

    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    const { _lt } = require('@web/core/l10n/translation');
    const { onMounted } = owl;

    class DeliverySuccessfully extends AbstractAwaitablePopup {

        setup() {
            super.setup();
            onMounted(this.onMounted);
        }

        onMounted() {
            var self = this;
            $('.order_status').show();
            $('.order_status').removeClass('order_done');
            $('.show_tick').hide();
            setTimeout(function () {
                $('.order_status').addClass('order_done');
                $('.show_tick').show();
                $('.order_status').css({ 'border-color': '#5CB85C' });
            }, 800);
            setTimeout(function () {
                self.cancel();
            }, 1500);
        }
    }

    DeliverySuccessfully.template = 'DeliverySuccessfully';
    DeliverySuccessfully.defaultProps = {
        title: _lt('Delivery created successfully'),
        body: '',
    };

    Registries.Component.add(DeliverySuccessfully);
    return DeliverySuccessfully;
});