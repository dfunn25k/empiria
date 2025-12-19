odoo.define('pos_kitchen_receipt_without_iot.models', function (require) {
    "use strict";

    var { Order, Orderline } = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');
    let core = require('web.core');
    let QWeb = core.qweb;

    const PosOrder = Order => 
        class PosOrder extends Order {
    
//            build_line_resume() {
//                var resume = {};
//                const self = this;
//                this.orderlines.each(function (line) {
//                    if (line.mp_skip) {
//                        return;
//                    }
//                    resume = self._change_order_line(resume, line)
//                });
//                return resume;
//            }
//
//            _change_order_line(resume, line) {
//                let line_hash = line.get_line_diff_hash();
//                let qty = Number(line.get_quantity());
//                let note = line.get_note();
//                let product_id = line.get_product().id;
//
//                if (typeof resume[line_hash] === 'undefined') {
//                    resume[line_hash] = {
//                        printed_line_id: line.printed_line_id,
//                        qty: qty,
//                        note: note,
//                        product_id: product_id,
//                        product_name_wrapped: line.generate_wrapped_product_name(),
//                    };
//                } else {
//                    resume[line_hash].qty += qty;
//                }
//                return resume;
//            }
//
//            computeChanges(categories) {
//                // Fix print behaviour:
//                //  - Normal lines
//                //  - Lines with special price
//                //  - Lines with notes
//
//                let current_res = this.build_line_resume();
//                let old_res = this.saved_resume || {};
//                let json = this.export_as_JSON();
//                let add = [];
//                let rem = [];
//                let line_hash;
//
//                for (line_hash in current_res) {
//                    let curr = current_res[line_hash];
//                    let old = {};
//                    let found = false;
//                    for (let id in old_res) {
//                        if (old_res[id].printed_line_id === curr.printed_line_id) {
//                            found = true;
//                            old = old_res[id];
//                            break;
//                        }
//                    }
//                    let compute_current = this._compute_change_current(found, add, rem, curr, old);
//                    add = compute_current.add
//                    rem = compute_current.rem
//                }
//
//                for (line_hash in old_res) {
//                    let found_2nd = false;
//                    for (let id in current_res) {
//                        if (current_res[id].printed_line_id === old_res[line_hash].printed_line_id) {
//                            found_2nd = true;
//                        }
//                    }
//                    if (!found_2nd) {
//                        let old_2nd = old_res[line_hash];
//                        rem = this._compute_change_old(rem, old_2nd);
//                    }
//                }
//
//                if (categories && categories.length > 0) {
//                    // filter the added and removed orders to only contains
//                    // products that belong to one of the categories supplied as a parameter
//
//                    var self = this;
//
//                    var _add = [];
//                    var _rem = [];
//
//                    for (var i = 0; i < add.length; i++) {
//                        if (self.pos.db.is_product_in_category(categories, add[i].id)) {
//                            _add.push(add[i]);
//                        }
//                    }
//                    add = _add;
//
//                    for (var i = 0; i < rem.length; i++) {
//                        if (self.pos.db.is_product_in_category(categories, rem[i].id)) {
//                            _rem.push(rem[i]);
//                        }
//                    }
//                    rem = _rem;
//                }
//
//                let d = new Date();
//                let hours = '' + d.getHours();
//                hours = hours.length < 2 ? ('0' + hours) : hours;
//                let minutes = '' + d.getMinutes();
//                minutes = minutes.length < 2 ? ('0' + minutes) : minutes;
//
//                return {
//                    'new': add,
//                    'cancelled': rem,
//                    'table': json.table || false,
//                    'floor': json.floor || false,
//                    'name': json.name || 'unknown order',
//                    'time': {
//                        'hours': hours,
//                        'minutes': minutes,
//                    },
//                };
//            }
//
//            _compute_change_current(found, add, rem, curr, old) {
//
//                if (!found) {
//                    add.push({
//                        'id': curr.product_id,
//                        'name': this.pos.db.get_product_by_id(curr.product_id).display_name,
//                        'name_wrapped': curr.product_name_wrapped,
//                        'note': curr.note,
//                        'qty': curr.qty,
//                    });
//                } else if (old.qty < curr.qty) {
//                    add.push({
//                        'id': curr.product_id,
//                        'name': this.pos.db.get_product_by_id(curr.product_id).display_name,
//                        'name_wrapped': curr.product_name_wrapped,
//                        'note': curr.note,
//                        'qty': curr.qty - old.qty,
//                    });
//                } else if (old.qty > curr.qty) {
//                    rem.push({
//                        'id': curr.product_id,
//                        'name': this.pos.db.get_product_by_id(curr.product_id).display_name,
//                        'name_wrapped': curr.product_name_wrapped,
//                        'note': curr.note,
//                        'qty': old.qty - curr.qty,
//                    });
//                }
//
//                return {
//                    add: add,
//                    rem: rem,
//                };
//            }
//
//            _compute_change_old(rem, old_2nd) {
//
//                rem.push({
//                    'id': old_2nd.product_id,
//                    'name': this.pos.db.get_product_by_id(old_2nd.product_id).display_name,
//                    'name_wrapped': old_2nd.product_name_wrapped,
//                    'note': old_2nd.note,
//                    'qty': old_2nd.qty,
//                });
//
//                return rem;
//            }

            async printChanges2() {
                let receipt = "";
                let receiptList = [];
                const d = new Date();
                let hours = '' + d.getHours();
                hours = hours.length < 2 ? ('0' + hours) : hours;
                let minutes = '' + d.getMinutes();
                minutes = minutes.length < 2 ? ('0' + minutes) : minutes;

                for (const printer of this.pos.unwatched.printers) {
                    const changes = this._getPrintingCategoriesChanges(printer.config.product_categories_ids);
                    if (changes['new'].length > 0 || changes['cancelled'].length > 0) {
                        const printingChanges = {
                            new: changes['new'],
                            cancelled: changes['cancelled'],
                            table_name: this.pos.config.iface_floorplan ? this.getTable().name : false,
                            floor_name: this.pos.config.iface_floorplan ? this.getTable().floor.name : false,
                            name: this.name || 'unknown order',
                            time: {
                                hours,
                                minutes,
                            },
                        };
                        let KitchenOrderChangeReceipt = QWeb.render('KitchenOrderChangeReceipt', { changes: printingChanges });
                        receipt += KitchenOrderChangeReceipt;
                        receiptList.push(KitchenOrderChangeReceipt);
                    }
                }
                let order = this.pos.get_order();
                order.receipt_val = {'list': receiptList, 'normal': receipt};
            }
        }

    Registries.Model.extend(Order, PosOrder);

    const PosOrderLine = Orderline => 
        class PosOrderLine extends Orderline {
        
            init_from_JSON(json) {
                super.init_from_JSON(json);
                this.printed_line_id = json.printed_line_id || false;
                this.set_printed_line_id()
            }
        
            export_as_JSON() {
                const json = super.export_as_JSON();
                json.printed_line_id = this.printed_line_id || false;
                this.set_printed_line_id()
                return json;
            }

            set_printed_line_id() {
                if (this.id && !this.printed_line_id) {
                    this.printed_line_id = String(this.id) + '-' + String(this.product.id)
                }
            }

        }

    Registries.Model.extend(Orderline, PosOrderLine);
});