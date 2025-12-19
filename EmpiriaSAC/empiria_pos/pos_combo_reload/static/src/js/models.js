odoo.define('pos_combo_reload.models', function (require) {
    "use strict";

    var { PosGlobalState, Order, Orderline } = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');

    const PosModelGlobalState = PosGlobalState =>
        class PosModelGlobalState extends PosGlobalState {

            constructor(obj) {
                super(obj);
                this.order_menu = [];
            }

            async _processData(loadedData) {
                await super._processData(loadedData);
                this.topping_item_by_id = loadedData['topping_item_by_id'];
            }
            
            setSelectionSelectedToppingId(toppingId) {
                this.selectionSelectedToppingId = toppingId;
            }

            getSelectionSelectedToppingId() {
                return this.selectionSelectedToppingId;
            }
        }
    Registries.Model.extend(PosGlobalState, PosModelGlobalState);

    const PosOrder = Order =>
        class PosOrder extends Order {
            set_orderline_options(orderline, options) {
                super.set_orderline_options(orderline, options);
                if (options.order_menu !== undefined) {
                    orderline.set_order_menu(options.order_menu);
                }
                if (options.own_data !== undefined) {
                    orderline.set_own_data(options.own_data);
                }
            }
        }
    Registries.Model.extend(Order, PosOrder);

    const PosOrderline = Orderline =>
        class PosOrderline extends Orderline {
            init_from_JSON(json) {
                super.init_from_JSON(...arguments);
                this.own_data = this.own_data || json.own_data || [];
                this.order_menu = this.order_menu || json.order_menu || [];
                this.worthless_combo = this.worthless_combo  || json.worthless_combo || false;
//                if (this.own_data && this.own_data.product_id == undefined) {
//                    let own_data = [];
//
//                    for (let i = 0, len = this.order_menu.length; i < len; i++) {
//                        for (let j = 0, len = this.order_menu[i].products.length; j < len; j++) {
//                            let product = this.pos.db.get_product_by_id(parseInt(this.order_menu[i].products[j].product_id))
//                            own_data.push({
//                                "product_id": {
//                                    'id': product.id,
//                                    'display_name': product.display_name,
//                                    'description': product.description,
//                                    'product_uom_id': product.uom_id[0]
//                                },
//                                'qty': this.order_menu[i].products[j].qty,
//                                'price': this.order_menu[i].products[j].price,
//                                'worthless_combo': true
//                            });
//                        }
//                    }
//                    this.own_data = own_data;
//                }
            }

            export_as_JSON() {
                const self = this;
                const json = super.export_as_JSON(...arguments);
                let own_line = [];
                let total_price = 0.0;
                if (this.product.is_selection_combo && this.own_data) {
//                  VERSION 14
                    _.each(self.own_data, function(item) {
                        let sub_total = 0.0;
                        if (item && item.product_id){
                            let uom_id = item.product_id.product_uom_id
                            let full_name = item.product_id.display_name;
                            if (item.product_id.description) {
                                full_name += ` (${item.product_id.description})`;
                                }
                                own_line.push([0, 0, {
                                    'product_id': item.product_id.id,
                                    'full_product_name': full_name,
                                    'qty': self.get_quantity() * item.qty,
                                    'price':item.price,
                                    'price_subtotal': sub_total,
                                    'price_subtotal_incl': sub_total,
                                    'product_uom': self.pos.units_by_id[uom_id],
                                    'worthless_combo': item.worthless_combo
                                }]);
                                total_price += item.price;
                        }

                    });
//                  VERSION 16
//                    for (let i = 0, len = this.own_data.length; i < len; i++) {
//                        let sub_total = 0.0;
//                        if (this.own_data[i] && this.own_data[i].product_id){
//                            console.log(this.own_data[i])
//                            let product_uom_id = this.own_data[i].product_id.product_uom_id;
//                            let full_name = this.own_data[i].product_id.display_name;
//                            if (this.own_data[i].product_id.description) {
//                                full_name += ` (${this.own_data[i].product_id.description})`;
//                            }
//
//                            own_line.push([0, 0, {
//                                'product_id': this.own_data[i].product_id.id,
//                                'full_product_name': full_name.replace('(<p><br></p>)', ''),
//                                'qty': this.get_quantity() * this.own_data[i].qty, 'price': this.own_data[i].price,
//                                'price_subtotal': sub_total,
//                                'price_subtotal_incl': sub_total,
//                                'product_uom_id': this.pos.units_by_id[product_uom_id],
//                                'worthless_combo': this.own_data[i].worthless_combo
//                            }]);
//                            total_price += this.own_data[i].price;
//                        }
//                    }


                }

                if (this.product.is_selection_combo) {
                    json.price_unit = total_price;
                }

                json.price_unit = this.price;
                json.worthless_combo = this.worthless_combo ? this.worthless_combo : false;
                json.is_selection_combo = this.product.is_selection_combo;
                json.own_line = this.product.is_selection_combo ? own_line : [];
//                json.own_data = this.export_own_data(this.own_data);
//                json.order_menu = this.order_menu;
                json.own_data = this.own_data;
                json.order_menu = this.export_order_menu(this.order_menu) ;
                return json;
            }

            export_for_printing() {
                const receipt = super.export_for_printing();
                receipt.order_menu = this.export_order_menu(this.order_menu);
                receipt.is_selection_combo_product = this.get_product().is_selection_combo;
                return receipt;
            }

            export_own_data(data) {
                let own_data = [];
                if (this.own_data) {
                    for (let rec in data) {
                        own_data.push({
                            'product_id': {
                                'id': this.own_data[rec]['product_id']['id'],
                                'display_name': this.own_data[rec]['product_id']['display_name'],
                                'description': this.own_data[rec]['product_id']['description'],
                                'product_uom_id': this.own_data[rec]['product_id']['product_uom_id']
                            },
                            'qty': this.own_data[rec]['qty'],
                            'price': this.own_data[rec]['price'],
                            'worthless_combo': this.own_data[rec]['worthless_combo']
                        });
                    }
                }
                return own_data;
            }

            export_order_menu(menu) {
                let order_menu = [];
                let quantity = this.quantity;
                if (this.order_menu) {
                    for (let rec in menu) {
                        let prods = this.order_menu[rec]['products']
                        if (prods) {
                            for (let pro in prods) {
                                prods[pro].qty = this.own_data.filter(ele => ele.product_id.id == prods[pro].product_id)[0].qty * quantity
                            }
                        }
                        order_menu.push({
                            'categoryName': this.order_menu[rec]['categoryName'],
                            'toppingId': this.order_menu[rec]['toppingId'],
                            'products': prods,
                            'include_price': this.order_menu[rec]['include_price']
                        });
                    }
                }
                return order_menu;
            }

            set_own_data(own_data) {
                this.own_data = own_data;
            }

            set_order_menu(order_menu) {
                this.order_menu = order_menu;
            }
        }

    Registries.Model.extend(Orderline, PosOrderline);
});
