odoo.define('pos_ticket_session_info.models', function (require) {
    "use strict";

    var { Order } = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');

    const PosOrder = Order =>
        class PosOrder extends Order {

            init_from_JSON(json) {
                super.init_from_JSON(json);
                this.order_change = json.order_change || 0.00;
            }

            export_as_JSON() {
                const json = super.export_as_JSON();
                json.order_change = this.order_change;
                return json;
            }

            export_for_printing() {
                const receipt = super.export_for_printing();
                receipt.order_change = this.order_change || 0.00
                return receipt;
            }
        }

    Registries.Model.extend(Order, PosOrder);
});


