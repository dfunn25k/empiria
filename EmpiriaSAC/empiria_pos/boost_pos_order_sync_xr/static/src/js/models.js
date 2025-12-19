odoo.define('boost_pos_order_sync_xr.models', function (require) {
    "use strict";

    var { PosGlobalState } = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');

    const PosModelGlobalState = PosGlobalState =>
        class PosModelGlobalState extends PosGlobalState {

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

                let get_floors = await this.env.services.rpc({
                    model: 'pos.config',
                    method: 'get_floors',
                    args: [{
                        'other_config': other_config_ids
                    }],
                });

                let other_floor_ids = [];
                let db_floors_by_id = [];

                if (get_floors) {
                    for (let i = 0, len = get_floors.length; i < len; i++) {
                        other_floor_ids.push(get_floors[i].id);
                        db_floors_by_id[get_floors[i].id] = get_floors[i];
                    }
                }

                let get_tables = await this.env.services.rpc({
                    model: 'pos.config',
                    method: 'get_tables',
                    args: [{
                        'other_config': other_config_ids
                    }],
                });

                let other_table_ids = [];
                let db_tables_by_id = [];

                if (get_tables) {
                    for (let i = 0, len = get_tables.length; i < len; i++) {
                        other_table_ids.push(get_tables[i].id);
                        db_tables_by_id[get_tables[i].id] = get_tables[i];
                    }
                }

                this.all_quotes = [];
                this.other_config_ids = other_config_ids;
                this.other_active_session = other_active_session;
                this.other_floors = get_floors;
                this.other_floor_ids = other_floor_ids;
                this.db.floors_by_id = db_floors_by_id;
                this.other_tables = get_tables;
                this.other_table_ids = other_table_ids;
                this.db.tables_by_id = db_tables_by_id;
            }
        }
    Registries.Model.extend(PosGlobalState, PosModelGlobalState);
});