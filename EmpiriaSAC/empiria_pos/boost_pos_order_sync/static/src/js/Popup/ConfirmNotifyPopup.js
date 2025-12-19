odoo.define('boost_pos_order_sync.ConfirmNotifyPopup', function (require) {
    'use strict';

    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    const { _lt } = require('@web/core/l10n/translation');
    const { onMounted } = owl;


    class ConfirmNotifyPopup extends AbstractAwaitablePopup {

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
            if (!(self.props && self.props.title)) {
                setTimeout(function () {
                    self.cancel();
                    self.env.pos.removeOrder(self.env.pos.get_order());
                    if(self.env.pos.config.module_pos_restaurant && self.env.pos.config.floor_ids && self.env.pos.config.is_table_management){
                        self.showScreen('FloorScreen');

                    }else {
                        self.showScreen('TicketScreen');
                    }
                }, 1500);
            } else {
                setTimeout(function () {
                    self.cancel();
                }, 1500);
            }
        }
    }

    ConfirmNotifyPopup.template = 'ConfirmNotifyPopup';
    ConfirmNotifyPopup.defaultProps = {
        body: '',
    };
    Registries.Component.add(ConfirmNotifyPopup);
    return ConfirmNotifyPopup;
});