odoo.define('autocreate_pos_invoice.models', function (require) {
    "use strict";

    var { PosGlobalState, Order } = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');

    const PosModelGlobalState = PosGlobalState =>
        class PosModelGlobalState extends PosGlobalState {

            push_single_order(order, opts) {
                if (order.fake_invoice) {
                    order.to_invoice = false;
                }
                return super.push_single_order(order, opts);
            }
        }

    Registries.Model.extend(PosGlobalState, PosModelGlobalState);

    const PosOrder = Order =>
        class PosOrder extends Order {
            constructor(obj, options) {
                super(obj, options);
                if (this.pos.config.ticket_user_id) {
                    const partner = this.pos.db.get_partner_by_id(this.pos.config.ticket_user_id[0])
                    if (options.json) {
                        if(!options.json.partner_id) {
                            this.set_partner(partner);
                        }
                    } else {
                        this.set_partner(partner);
                    }
                }
            }
        }
    Registries.Model.extend(Order, PosOrder);
});
