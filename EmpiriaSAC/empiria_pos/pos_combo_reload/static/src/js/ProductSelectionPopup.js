odoo.define('pos_combo_reload.ProductSelectionPopup', function (require) {
    'use strict';

    var { Orderline } = require('point_of_sale.models');
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    const { useListener } = require("@web/core/utils/hooks");
    const { useState } = owl;
    const { _lt } = require('@web/core/l10n/translation');

    class ProductSelectionPopup extends AbstractAwaitablePopup {

        setup() {
            super.setup();
            useListener('click-combo-product', this._clickProduct);
            useListener('remove-combo-product', this._removeProduct);
            useListener('switch-category', this._switchCategory);
            this.data = this.props.data;
            this.main_product = this.props.main_product;
            this.main_product_name = this.props.main_product_name;
            this.main_product_price = this.props.main_product_price;
            this.pricelist = this.currentOrder.pricelist;
            this.state = useState({ isRemoved: false });
            this.env.pos.order_menu = this.props.order_menu || [];
            this.is_editable = this.props.is_editable || false;
            this.selected_orderline = this.props.selected_orderline || false;
            if (this.is_editable) {
                this.selected_order_menu = JSON.parse(JSON.stringify(this.selected_orderline.order_menu));
            }
        }

        get selectionSelectedToppingId() {
            return this.env.pos.getSelectionSelectedToppingId();
        }

        get productsToDisplay() {
            const topping_data = this.env.pos.topping_item_by_id[this.selectionSelectedToppingId];
            const list = [];
            if (topping_data) {
                let product_ids = topping_data.product_ids;
                if (product_ids) {
                    for (let i = 0; i < product_ids.length; i++) {
                        for (let j = 0; j < product_ids[i].length; j++) {
                            list.push(this.env.pos.db.get_product_by_id(product_ids[i][j]));
                        }
                    }
                }
            }
            return list;
        }

        get orderMenuToDisplay() {
            return this.env.pos.order_menu;
        }

        get totalPriceToDisplay() {
            let total_price = 0.0;
            for (let i = 0; i < this.env.pos.order_menu.length; i++) {
                for (let j = 0; j < this.env.pos.order_menu[i].products.length; j++) {
                    total_price += this.env.pos.order_menu[i].products[j].price;
                }
            }
            return total_price.toFixed(2);
        }

        async _clickProduct(event) {
            if (this.state.isRemoved) {
                this.state.isRemoved = false;
                return
            }
            const topping_data = this.env.pos.topping_item_by_id[this.selectionSelectedToppingId];
            if (!topping_data) return;
            const product = event.detail.product;
            const description = topping_data.description;
            const multi_selection = topping_data.multi_selection;
            let allow = true;
            let order_menu = this.props.order_menu || [];

            if (!topping_data.no_of_items && multi_selection) {
                return
            }

            let item = _.where(order_menu, { 'toppingId': topping_data.id })
            if (item && item.length > 0) {
                item = item[0];
                let item_products = item.products;
                if (item_products.length > 0 && multi_selection == false) {
                    this.showPopup('MessagePopup', { 'body': this.env._t("You can select only one item") });
                    allow = false;
                    return
                } else {
                    let total_items = 0;
                    for (let i = 0; i < item_products.length; i++) {
                        total_items += item_products[i].qty;
                    }
                    if (item_products.length > 0 && total_items >= topping_data.no_of_items) {
                        let msg1 = this.env._t("You can only select") 
                        let msg2 = this.env._t("item from")
                        let msg = msg1 + " " + topping_data.no_of_items + " " + msg2 + " " + topping_data.description
                        this.showPopup('MessagePopup', { 'body': msg });
                        return
                    }
                }
            }

            for (let i = 0; i < order_menu.length; i++) {
                if (topping_data.id == order_menu[i].toppingId) {
                    let exist_product = _.find(order_menu[i].products, function (p) { return p.product_id === product.id });
                    if (exist_product) {
                        exist_product['qty'] = exist_product.qty + 1;
                        exist_product['price'] = exist_product.qty * product.get_price(this.pricelist, 1);
                        allow = false;
                    } else {
                        order_menu[i].products.push({
                            'product_id': product.id,
                            'product_name': product.display_name.replace('(<p><br></p>)', ''),
                            'price': product.get_price(this.pricelist, 1),
                            'qty': 1
                        });
                    }
                    allow = false;
                }
                if (order_menu[i].products.length <= 0) {
                    order_menu.splice(i, 1);
                }
            }
            if (allow) {
                order_menu.push({
                    'toppingId': topping_data.id,
                    'categoryName': description,
                    'include_price': this.props.include_price,
                    'products': [{
                        'product_id': product.id,
                        'product_name': product.display_name,
                        'price': product.get_price(this.pricelist, 1),
                        'qty': 1
                    }]
                });
            }
            this.env.pos.order_menu = order_menu;
            this.render();
        }

        async _removeProduct(event) {
            this.state.isRemoved = true;
            const topping_data = this.env.pos.topping_item_by_id[this.selectionSelectedToppingId];
            const product = event.detail.product;
            _.each(this.env.pos.order_menu, function (order_menu) {
                if (topping_data.id == order_menu.toppingId) {
                    order_menu['products'] = _.reject(order_menu.products, function (p) { return p.product_id === product.id });
                }
            });
            const order_menu = _.reject(this.env.pos.order_menu, function (order_menu) { return order_menu.products < 1 });
            this.env.pos.order_menu = order_menu;
        }

        get currentOrder() {
            return this.env.pos.get_order();
        }

        update_order_line(product, total_price) {
            if (this.is_editable) {
                this.selected_orderline.set_unit_price(product.get_price(this.pricelist, 1) + total_price);
                this.currentOrder.select_orderline(this.selected_orderline);
            } else {
                const orderline = Orderline.create({}, {
                    pos: this.env.pos,
                    order: this.currentOrder,
                    product: product,
                    price: product.get_price(this.pricelist, 1) + total_price
                });
                this.currentOrder.add_orderline(orderline);
                this.currentOrder.selected_orderline.price_manually_set = true;
            }
        }

        async confirm() {
            const topping_data = this.env.pos.topping_item_by_id[this.selectionSelectedToppingId];
            if (!topping_data) return;
            const own_data = [];
            let total_price = 0.0;
            let required_sub_item = false;

            for (let i = 0; i < this.data.length; i++) {
                if (this.data[i].no_of_min_items != 0) {
                    required_sub_item = true;
                    break;
                }
            }
            if (this.env.pos.order_menu.length == 0 && required_sub_item) {
                this.showPopup('MessagePopup', { 'body': this.env._t("You can not confirm without select any item of min qty") });
                return
            } else {
                for (let i = 0; i < this.data.length; i++) {
                    if (this.data[i].no_of_min_items != 0) {
                        let min_items = 0;
                        for (let j = 0; j < this.env.pos.order_menu.length; j++) {
                            for (let k = 0; k < this.env.pos.order_menu[j]['products'].length; k++) {
                                if (this.env.pos.order_menu[j]['toppingId'] == this.data[i]['id']) {
                                    min_items += this.env.pos.order_menu[j]['products'][k].qty;
                                }
                            }
                        }
                        if (this.data[i].no_of_min_items > min_items) {
                            let msg1 = this.env._t("You Must Have to Select") 
                            let msg2 = this.env._t("item from")
                            let msg = msg1 + " " + this.data[i].no_of_min_items +  " " + msg2 + " " + this.data[i].category
                            this.showPopup('MessagePopup', { 'body': msg });
                            return
                        }
                    }
                }
            }

            for (let i = 0; i < this.env.pos.order_menu.length; i++) {
                for (let j = 0; j < this.env.pos.order_menu[i].products.length; j++) {
                    let product_id = this.env.pos.order_menu[i].products[j].product_id;
                    let product = this.env.pos.db.get_product_by_id(parseInt(product_id))
                    own_data.push({
                        "product_id": {
                            'id': product.id,
                            'display_name': product.display_name,
                            'description': product.description,
                            'product_uom_id': product.uom_id[0]
                        },
                        'qty': this.env.pos.order_menu[i].products[j].qty,
                        'price': this.env.pos.order_menu[i].products[j].price,
                        'worthless_combo': true
                    });
                    if (this.env.pos.order_menu[i].include_price) {
                        total_price += this.env.pos.order_menu[i].products[j].price;
                    }
                }
            }

            const product = this.env.pos.db.get_product_by_id(this.main_product);
            this.update_order_line(product, total_price);
            this.currentOrder.selected_orderline.set_own_data(own_data);
            this.currentOrder.selected_orderline.set_order_menu(this.env.pos.order_menu);
            this.currentOrder.selected_orderline.set_selected(true);
            super.confirm();
        }

        _switchCategory(event) {
            this.env.pos.setSelectionSelectedToppingId(event.detail);
        }

        cancel() {
            if (this.is_editable) {
                this.selected_orderline.order_menu = this.selected_order_menu;
            }
            super.cancel();
        }
    }
    ProductSelectionPopup.template = 'ProductSelectionPopup';
    ProductSelectionPopup.defaultProps = {
        confirmText: _lt('Confirm'),
        cancelText: _lt('Cancel'),
    };
    Registries.Component.add(ProductSelectionPopup);
    return ProductSelectionPopup;
});
