odoo.define('pos_kitchen_receipt_combo.models', function (require) {
    "use strict";

    var { Order } = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');

    const PosOrder = Order =>
        class PosOrder extends Order {

            /*
                La funcionalidad de este codigo funciona comparando una orden actual y una orden pasada
            */


            _computePrintChanges() {
            /*
                Funcion que se ejecuta cada vez que sucede alguna accion en una order , agregar una order line, eliminar
                una order line, cambio de cantidad de order line

                Returns:
                    cambios de la orden actual
            */

                const changes = {};
                // If there's a new orderline, we add it otherwise we add the change if there's one
                // ADD
                this.orderlines.forEach(line => {
                    if (!line.mp_skip) {
                        const productId = line.get_product().id;
                        const note = line.get_note();
                        const productKey = `${productId} - ${line.get_full_product_name()} - ${note} - ${line.uuid}`;
                        const lineKey = `${line.uuid} - ${note}`;
                        const quantityDiff = line.get_quantity() - (this.printedResume[lineKey] ? this.printedResume[lineKey]['quantity'] : 0);
                        if (quantityDiff) {
                            if (!changes[productKey]) {
                                changes[productKey] = {
                                    product_id: productId,
                                    name: line.get_full_product_name(),
                                    note: note,
                                    quantity: quantityDiff,
                                    // add order menu
                                    order_menu: line.order_menu,
                                    own_data: line.own_data
                                }
                            } else {
                                changes[productKey]['quantity'] += quantityDiff;
                            }
                            line.set_dirty(true);
                        } else {
                            line.set_dirty(false);
                        }
                    }
                })

                // If there's an orderline that's not present anymore, we consider it as removed (even if note changed)
                // REM
                for (const [lineKey, lineResume] of Object.entries(this.printedResume)) {
                    if (!this._getPrintedLine(lineKey)) {
                        const productKey = `${lineResume['product_id']} - ${lineResume['name']} - ${lineResume['note']} - ${lineResume['line_uuid']}`;
                        if (!changes[productKey]) {
                            changes[productKey] = {
                                product_id: lineResume['product_id'],
                                name: lineResume['name'],
                                note: lineResume['note'],
                                quantity: -lineResume['quantity'],
                                // add$
                                order_menu: lineResume.order_menu,
                                own_data: lineResume.own_data
                            }
                        } else {
                            changes[productKey]['quantity'] -= lineResume['quantity'];
                        }
                    }
                }
                return changes;
            }

            updateChangesToPrint() {
                const changes = this._computePrintChanges(); // it's possible to have a change's quantity of 0
                // we thoroughly parse the changes we just computed to properly separate them into two
                const toAdd = [];
                const toRemove = [];

                for (const lineChange of Object.values(changes)) {
                    if (lineChange['quantity'] > 0) {
                        toAdd.push(lineChange);
                    } else if (lineChange['quantity'] < 0) {
                        lineChange['quantity'] *= -1; // we change the sign because that's how it is
                        toRemove.push(lineChange);
                    }
                }
                let { toAddNew, toRemoveNew } = this.unboxPrintingChanges(toAdd, toRemove)
                this.printingChanges = { new: toAddNew, cancelled: toRemoveNew };
            }

            unboxPrintingChanges(toAdd,toRemove) {
                let toadd_combo = [];
                let toadd_filter = toAdd.filter(element => element.order_menu && element.order_menu.length > 0 && element.descompres === undefined)
                let toadd_filter_normal = toAdd.filter(element => element.order_menu === undefined)

                let categories_printers_all_arrays = this.pos.unwatched.printers.map(objeto => objeto.config.product_categories_ids);
                let categories_printers_all_array = [].concat(...categories_printers_all_arrays);

                if (toadd_filter.length > 0) {
                    for (let i = 0; i < toadd_filter.length; i++) {
//                    filtrar por ordenes combo
                        let quantity_receipt_kitchen = toadd_filter[i].quantity;
                        if (toadd_filter) {
                            let order_descompres = [];
                            for (let j = 0; j < toadd_filter[i].order_menu.length; j++) {
////                                EN ORDER MENU PUEDO AGRUPAR LOS QUE SON DE MISMO CATEGORIA ****
//                                this.pos.db.is_product_in_category(categories, change['product_id'])
                                let products_prints = toadd_filter[i].order_menu[j].products.filter(element => this.pos.db.is_product_in_category(categories_printers_all_array, element.product_id));
                                let products_prints_change = [];

                                for (let rec in products_prints) {
                                    products_prints_change.push({
                                        'price': products_prints[rec]['price'],
                                        'product_id': products_prints[rec]['product_id'],
                                        'product_name': products_prints[rec]['product_name'],
                                        'qty': toadd_filter[i].own_data.filter(ele => ele.product_id.id == products_prints[rec].product_id)[0].qty * quantity_receipt_kitchen
                                    })
                                }

                                if (products_prints.length > 0) {
                                    let new_desem_combo = {
                                        'descompres': true,
                                        'name': toadd_filter[i].name,
                                        'note': toadd_filter[i].note,
                                        'order_menu':[{
                                            'toppingId': toadd_filter[i].order_menu[j].toppingId,
                                            'categoryName': toadd_filter[i].order_menu[j].categoryName,
                                            'include_price': toadd_filter[i].order_menu[j].include_price,
                                            'products': products_prints_change
                                        }],
                                        'product_id': products_prints_change[0].product_id,
                                        'quantity': toadd_filter[i].quantity
                                    }
                                    order_descompres.push(new_desem_combo)
                                }


                            }

                            for (let categ_print of categories_printers_all_arrays) {
                                let a = order_descompres.filter(element => this.pos.db.is_product_in_category(categ_print, element.product_id))
                                if (a.length > 0) {
                                    let order_menu_unificado = a.reduce((acumulador, objeto) => {
                                      return {
                                        descompres: true,
                                        name: objeto.name,
                                        note: objeto.note,
                                        order_menu: acumulador.order_menu.concat(objeto.order_menu),
                                        product_id: objeto.product_id,
                                        quantity: objeto.quantity
                                      };
                                    }, {
                                        descompres: true,
                                        name: "",
                                        note: "",
                                        order_menu: [],
                                        product_id: "",
                                        quantity: ""
                                    });
                                    toadd_combo.push(order_menu_unificado)
                                }
                            }
                        }
                    }
                }

                let toremove_combo = [];
                let toremove_filter = toRemove.filter(element => element.order_menu && element.order_menu.length > 0 && element.descompres === undefined)
                let toremove_filter_normal = toRemove.filter(element => element.order_menu === undefined)

                if (toremove_filter.length > 0) {
                    for (let i = 0; i < toremove_filter.length; i++) {
                        if (toremove_filter) {
                            let order_descompres = [];
                            for (let j = 0; j < toremove_filter[i].order_menu.length; j++) {
                                let products_prints = toremove_filter[i].order_menu[j].products.filter(element => this.pos.db.is_product_in_category(categories_printers_all_array, element.product_id))
                                let products_prints_change = [];

                                for (let rec in products_prints) {
                                    products_prints_change.push({
                                        'price': products_prints[rec]['price'],
                                        'product_id': products_prints[rec]['product_id'],
                                        'product_name': products_prints[rec]['product_name'],
                                        'qty': toremove_filter[i].own_data.filter(ele => ele.product_id.id == products_prints[rec].product_id)[0].qty * toremove_filter[i].quantity
                                    })
                                }

                                if (products_prints_change.length > 0) {
                                    let remove_desem_combo = {
                                        'descompres': true,
                                        'name': toremove_filter[i].name,
                                        'note': toremove_filter[i].note,
                                        'order_menu':[{
                                            'toppingId': toremove_filter[i].order_menu[j].toppingId,
                                            'categoryName': toremove_filter[i].order_menu[j].categoryName,
                                            'include_price': toremove_filter[i].order_menu[j].include_price,
                                            'products': products_prints_change
                                        }],
                                        'product_id': products_prints_change[0].product_id,
                                        'quantity': toremove_filter[i].quantity
                                    }
                                    order_descompres.push(remove_desem_combo)
                                }
                            }

                            for (let categ_print of categories_printers_all_arrays) {
                                let a = order_descompres.filter(element => this.pos.db.is_product_in_category(categ_print, element.product_id))
                                if (a.length > 0) {
                                    let order_menu_unificado = a.reduce((acumulador, objeto) => {
                                      return {
                                        descompres: true,
                                        name: objeto.name,
                                        note: objeto.note,
                                        order_menu: acumulador.order_menu.concat(objeto.order_menu),
                                        product_id: objeto.product_id,
                                        quantity: objeto.quantity
                                      };
                                    }, {
                                        descompres: true,
                                        name: "",
                                        note: "",
                                        order_menu: [],
                                        product_id: "",
                                        quantity: ""
                                    });
                                    toremove_combo.push(order_menu_unificado)
                                }
                            }
                        }
                    }
                }


                return{
                    toAddNew: [...toadd_filter_normal,...toadd_combo],
                    toRemoveNew: [...toremove_filter_normal,...toremove_combo]
                }
            }

            updatePrintedResume(){
            /*
                Funcion que se ejecuta cada vez que sucede alguna accion en una order , agregar una order line, eliminar
                una order line, cambio de cantidad de order line

                Returns:
                    cambios de la orden pasada
            */
                // we first remove the removed orderlines
                for (const lineKey in this.printedResume) {
                    if (!this._getPrintedLine(lineKey)) {
                        delete this.printedResume[lineKey];
                    }
                }
                // we then update the added orderline or product quantity change
                this.orderlines.forEach(line => {
                    if (!line.mp_skip) {
                        const note = line.get_note();
                        const lineKey = `${line.uuid} - ${note}`;
                        if (this.printedResume[lineKey]) {
                            this.printedResume[lineKey]['quantity'] = line.get_quantity();
                        } else {
                            this.printedResume[lineKey] = {
                                line_uuid: line.uuid,
                                product_id: line.get_product().id,
                                name: line.get_full_product_name(),
                                note: note,
                                quantity: line.get_quantity(),
                                // add order menu
                                own_data: line.own_data,
                                order_menu: line.order_menu,
                            }
                        }
                        line.set_dirty(false);
                    }
                });
                this._resetPrintingChanges();
            }
        }

    Registries.Model.extend(Order, PosOrder);
});