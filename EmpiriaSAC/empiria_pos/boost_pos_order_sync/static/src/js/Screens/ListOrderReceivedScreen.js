odoo.define('boost_pos_order_sync.ListOrderReceivedScreen', function (require) {
    "use strict";

    var { Order, Orderline } = require('point_of_sale.models');
    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');

    class ListOrderReceivedScreen extends PosComponent {

        back() {
            this.trigger('close-temp-screen');
        }

        _clickOrderReceived(event) {
            const quotes = this.env.pos.all_quotes;
            const quote_id = event.srcElement.parentElement.getAttribute("data-quote_id");
            const quote_dict = quotes.find((e) => e.quote_id === quote_id);
            const all_pos_orders = this.env.pos.get_order_list() || [];
            const already_loaded = all_pos_orders.some((pos_order) => pos_order.quote_name === quote_id);

            if (already_loaded) {
                this.showPopup('MessagePopup', {
                    title: this.env._t('Quotation is already loaded & in progress'),
                    body: this.env._t('This quotation is already in progress. Please proceed with Order Reference')
                });
            } else {
                this.load_order_from_quote(quote_dict)
            }
        }

        load_order_from_quote(quote_data) {
            this.set_order(quote_data);
            setTimeout(function () {
                $(".button.back").click();
            }, 100);
        }

        set_order(quote_dict, table) {
            var self = this;

            let new_order = self.env.pos.add_new_order();

            if (table) {
                new_order.table = table;
            }

            let partner_id = quote_dict.partner_id[0];
            if (partner_id) {
                let new_client = self.env.pos.db.get_partner_by_id(quote_dict.partner_id[0]);
                if (new_client) {
                    new_order.set_partner(new_client);
                } else {
                    self.env.pos.load_new_partners().then(function () {
                        new_client = self.env.pos.db.get_partner_by_id(quote_dict.partner_id[0]);
                        new_order.set_partner(new_client);
                    });
                }
            }
            self.set_orderliness(new_order, quote_dict);
            return new_order
        }

        set_orderliness(new_order, quote_dict) {
            var self = this;

            quote_dict.line.forEach(function (line) {
                let orderline = Orderline.create({}, {
                    pos: self.env.pos,
                    order: new_order,
                    product: self.env.pos.db.get_product_by_id(line.product_id),
                });

                orderline.set_unit_price(line.price_unit);
                orderline.set_discount(line.discount);
                orderline.set_quantity(line.qty, 'set line price');
                orderline.tax_ids = line.tax_ids || []
                // pos loyalty fields
                orderline.is_reward_line = line.is_reward_line || false
                orderline.reward_id = line.reward_id || false
                orderline.coupon_id = line.coupon_id || false,
                orderline.reward_identifier_code = line.reward_identifier_code,
                orderline.points_cost = line.points_cost
                new_order.add_orderline(orderline);
            });

            new_order.set_quote(quote_dict);
            new_order.export_as_JSON();
            new_order.save_to_db();

            self.showPopup('ConfirmNotifyPopup', {
                'title': self.env._t('Quote Loaded')
            });

        }
    }

    ListOrderReceivedScreen.template = 'ListOrderReceivedScreen';
    Registries.Component.add(ListOrderReceivedScreen);
    return ListOrderReceivedScreen;
})