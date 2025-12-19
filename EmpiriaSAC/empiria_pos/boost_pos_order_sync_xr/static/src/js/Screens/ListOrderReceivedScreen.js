odoo.define('boost_pos_order_sync_xr.ListOrderReceivedScreen', function (require) {
    "use strict";

    const ListOrderReceivedScreen = require('boost_pos_order_sync.ListOrderReceivedScreen');
    const Registries = require('point_of_sale.Registries');

    const PosListOrderReceivedScreen = ListOrderReceivedScreen =>
        class PosListOrderReceivedScreen extends ListOrderReceivedScreen {

            load_order_from_quote(quote_data) {
                let on_restaurant = false;
                if (this.env.pos.config.module_pos_restaurant && this.env.pos.config.floor_ids && this.env.pos.config.is_table_management) {
                    on_restaurant = true;
                    if (quote_data.table_json) {
                        let table_data = JSON.parse(quote_data.table_json);
                        if (table_data) {
                            var table_id = table_data.table_json[0].table_id;
                            var floor_id = table_data.table_json[1].floor_id;
                            if (floor_id && table_id) {
                                if (this.env.pos.floors_by_id[floor_id]) {
                                    _.each(this.env.pos.floors_by_id[floor_id].table_ids, function (id) {
                                        if (id === parseInt(table_id)) {
                                            let quote_table = this.env.pos.tables_by_id[id];
                                            this.env.pos.table = quote_table;
                                            this.set_order(quote_data, quote_table);
                                        }
                                    });
                                }
                            }
                        }
                    }
                }
                if (!on_restaurant) {
                    this.set_order(quote_data);
                }
                setTimeout(function () {
                    $(".button.back").click();
                }, 200);
            }

        }
    Registries.Component.extend(ListOrderReceivedScreen, PosListOrderReceivedScreen);
    return PosListOrderReceivedScreen;
})