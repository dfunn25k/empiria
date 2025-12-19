odoo.define('pos_multi_uom_product_right.pos_multi_uom_popup', function (require) {
    'use strict';
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');

    class UomOrderlinePopup extends AbstractAwaitablePopup {
        setup() {
            super.setup();
        }

        async _clickUom(event) {
            let order = this.env.pos.get_order();
            let orderline = order.get_selected_orderline();
            let uom_id = event.srcElement.parentElement.getAttribute("data-uom_id");
            let price = event.srcElement.parentElement.childNodes[1].innerText.split(" ")[1]
            let lines_all_units = this.env.pos.units;
            let select_uom = {};
            for (let line of lines_all_units) {
                if (parseInt(uom_id) === line.id) {
                    select_uom = line
                }
            }
            orderline.set_unit_price(price);
            orderline.set_product_uom(uom_id);
            event.stopPropagation();
            this.cancel();
        }
    }

    //Create products popup
    UomOrderlinePopup.template = 'UomOrderlinePopup';
    Registries.Component.add(UomOrderlinePopup);
    return UomOrderlinePopup;
});