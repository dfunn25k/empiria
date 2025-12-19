odoo.define('pos_product_return.models', function (require) {
    "use strict";

    var { Order } = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');

    const PosOrder = Order =>
        class PosOrder extends Order {

            init_from_JSON(json) {
                super.init_from_JSON(json);
                this.account_move_rel_name = json.account_move_rel_name || '-';
                this.account_move_rel_document_type = json.account_move_rel_document_type || '-';
                this.account_move_rel_invoice_date = json.account_move_rel_invoice_date || false;
            }

            export_as_JSON() {
                const json = super.export_as_JSON();
                json.account_move_rel_name = this.account_move_rel_name;
                json.account_move_rel_document_type = this.account_move_rel_document_type;
                json.account_move_rel_invoice_date = this.account_move_rel_invoice_date;
                return json;
            }
        }

    Registries.Model.extend(Order, PosOrder);
});