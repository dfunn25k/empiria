odoo.define('pos_combo_reload.ProductScreen', function (require) {
    "use strict";

    const ProductScreen = require('point_of_sale.ProductScreen');
    const Registries = require('point_of_sale.Registries');
    const NumberBuffer = require('point_of_sale.NumberBuffer');

    const PosProductScreen = ProductScreen =>
        class PosProductScreen extends ProductScreen {

            async _clickProduct(event) {
                const product = event.detail;
                let default_product_topping_id = false;
                if (product.is_selection_combo) {
                    const data = [];
                    for (let i = 0; i < product.product_topping_ids.length; i++) {
                        const products = [];
                        const selected_product = this.env.pos.topping_item_by_id[product.product_topping_ids[i]];
                        for (let j = 0; j < selected_product.product_ids.length; j++) {
                            for (let k = 0; k < selected_product.product_ids[j].length; k++) {
                                const item = this.env.pos.db.get_product_by_id(selected_product.product_ids[j][k]);
                                if (item) {
                                    products.push(item);
                                }
                            }
                        }
                        if (!default_product_topping_id) {
                            default_product_topping_id = selected_product.id
                        }
                        data.push({
                            'id': selected_product.id,
                            'category': selected_product.description,
                            'categ_id': selected_product.product_categ_id[0],
                            'products': products || [],
                            'multi_selection': selected_product.multi_selection,
                            'no_of_items': selected_product.no_of_items,
                            'no_of_min_items': selected_product.no_of_min_items,
                            'qty': selected_product.product_quantity,
                        });
                    }
                    this.env.pos.setSelectionSelectedToppingId(default_product_topping_id);
                    this.showPopup('ProductSelectionPopup', {
                        'data': data,
                        'main_product': product.id,
                        'main_product_name': product.display_name,
                        'main_product_price': product.lst_price,
                        'include_price': product.include_price,
                        'order_menu': []
                    });
                    NumberBuffer.reset();
                } else {
                    super._clickProduct(event);
                }
            }
        }

    Registries.Component.extend(ProductScreen, PosProductScreen);
    return PosProductScreen;
});
