odoo.define('boost_pos_order_sync_xr.SendOrderPopup', function (require) {
    "use strict";

    const SendOrderPopup = require('boost_pos_order_sync.SendOrderPopup');
    const Registries = require('point_of_sale.Registries');

    const PosSendOrderPopup = SendOrderPopup =>
        class PosSendOrderPopup extends SendOrderPopup {

            change_tables() {
                var related_tables = []
                var floor_id = $('#wk_change_floor').val();
                var floor = this.env.pos.db.floors_by_id[floor_id];
                $('#wk_change_table option').remove();
                $('.show_info').hide();
                if (floor) {
                    for (let i = 0, len = floor.table_ids.length; i < len; i++) {
                        related_tables.push(this.env.pos.db.tables_by_id[floor.table_ids[i]]);
                    }
                }
                if (related_tables.length) {
                    $('#wk_change_table').append("<option value=''> </option>")
                    _.each(related_tables, function (table) {
                        $('#wk_change_table').append("<option value=" + table.id + "> " + table.name + "</option>")
                    })
                }
            }

            click_table() {
                $('.show_info').hide();
            }

            click_select_session(session_id) {
                $('#wk_change_floor option').remove();
                $('#wk_change_table option').remove();
                $('.show_info').hide();
                $(".select_session").css('background', '#FFFFFF');

                this.selected_session_id = session_id;

                if (this.selected_session_id) {

                    let config_id = null;
                    let other_active_session = this.env.pos.other_active_session;

                    for (let i = 0, len = other_active_session.length; i < len; i++) {
                        if (other_active_session[i].id == this.selected_session_id) {
                            config_id = other_active_session[i].config_id[0];
                        }
                    }

                    let floors = [];
                    let tables = [];
                    let other_floors = this.env.pos.other_floors;
                    let other_tables = this.env.pos.other_tables;

                    for (let i = 0, len = other_floors.length; i < len; i++) {
                        if (other_floors[i].pos_config_id == config_id) {
                            floors.push(other_floors[i]);
                            for (let j = 0, len = other_tables.length; j < len; j++) {
                                for (let k = 0, len = other_floors[i].table_ids.length; k < len; k++) {
                                    if (other_tables[j].id == other_floors[i].table_ids[k]) {
                                        tables.push(other_tables[k]);
                                    }
                                }
                            }
                        }
                    }

                    if (floors.length > 0 && tables.length > 0) {
                        $('#wk_floor_table').show();
                        $('#wk_change_floor option').remove();
                        $('#wk_change_table option').remove();
                        if (floors.length) {
                            $('#wk_change_floor').append("<option value=''> </option>")
                            _.each(floors, function (floor) {
                                if (floor.table_ids.length) {
                                    $('#wk_change_floor').append("<option value=" + floor.id + "> " + floor.name + "</option>")
                                }
                            })
                        }
                    } else {
                        $('#wk_floor_table').hide();
                    }
                }
                $("span.select_session[id=" + session_id + " ]").css('background', 'rgb(84 222 100)');
            }

            pre_validation_send_order_quote() {
                let is_ok = true
                let wk_change_floor = $("#wk_change_floor").is(":visible");
                let wk_change_table = $("#wk_change_table").is(":visible");

                if (wk_change_floor && wk_change_table){
                    if (!$('#wk_change_floor').val() || !$('#wk_change_table').val()) {
                        if (!$('#wk_change_floor').val().length || !$('#wk_change_table').val().length) {
                            $('.show_info').show();
                            is_ok = false
                        }
                    }
                }
                return is_ok
            }

            get_quote_data(session_id) {
                let orderVals = super.get_quote_data(session_id);
                if (this.env.pos.get_order()) {
                    if ($('#wk_change_table').val() && $('#wk_change_floor').val()) {
                        orderVals.table_json = JSON.stringify({
                            'table_json': [{ 'table_id': $('#wk_change_table').val() },
                            { 'floor_id': $('#wk_change_floor').val() }]
                        })
                        let floor = self.env._t('Floor:')
                        let table = self.env._t(', Table:')
                        orderVals.pos_res_info = `${floor} ${self.env.pos.db.floors_by_id[$('#wk_change_floor').val()].name} ${table} ${self.env.pos.db.tables_by_id[$('#wk_change_table').val()].name}`
                    }
                }
                return orderVals
            }

        }

    Registries.Component.extend(SendOrderPopup, PosSendOrderPopup);
    return PosSendOrderPopup;
});