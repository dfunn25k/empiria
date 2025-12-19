odoo.define('boost_pos_order_sync.models', function (require) {
    "use strict";

    var { PosGlobalState, Order } = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');

    const PosModelGlobalState = PosGlobalState =>
        class PosModelGlobalState extends PosGlobalState {

            async after_load_server_data() {
                await super.after_load_server_data();
                await this._load_other_session();
            }

            async _load_other_session() {
                let session_state_opened = await this.env.services.rpc({
                    model: 'pos.session',
                    method: 'search_read',
                    fields: ['id', 'name', 'user_id', 'config_id', 'start_at', 'stop_at', 'sequence_number', 'payment_method_ids'],
                    domain: [['state', '=', 'opened']]
                });

                let other_config_ids = [];
                let other_active_session = [];

                for (let i = 0, len = session_state_opened.length; i < len; i++) {
                    if (session_state_opened[i].user_id[0] !== this.user.id) {
                        if (this.config.send_orders_ids.length > 0 && this.config.send_orders_ids.includes(session_state_opened[i].config_id[0])) {
                            other_config_ids.push(session_state_opened[i].config_id[0]);
                            other_active_session.push(session_state_opened[i]);
                        }
                    }
                }

                this.all_quotes = [];
                this.other_config_ids = other_config_ids;
                this.other_active_session = other_active_session;
            }
        }
    Registries.Model.extend(PosGlobalState, PosModelGlobalState);

    const PosOrder = Order =>
        class PosOrder extends Order {

            init_from_JSON(json) {
                super.init_from_JSON(json);
                this.quote_id = this.quote_id || false;
                this.quote_name = this.quote_name || false;
                this.created_quote_id = this.created_quote_id || false;
            }

            export_as_JSON() {
                const json = super.export_as_JSON();
                json.quote_id = this.quote_id ? this.quote_id : false;
                json.quote_name = this.quote_name ? this.quote_name : false;
                return json;
            }

            set_quote(quote_dict) {
                this.quote_id = quote_dict.quote_obj_id;
                this.quote_name = quote_dict.quote_id;
            }
        }
    Registries.Model.extend(Order, PosOrder);
});