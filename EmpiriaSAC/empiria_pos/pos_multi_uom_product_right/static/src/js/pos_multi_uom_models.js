odoo.define('pos_multi_uom_product_right.pos_multi_uom_order', function (require) {
    "use strict";

    const Registries = require('point_of_sale.Registries');
    var { Order, Orderline } = require('point_of_sale.models');

    const PosOrder = Order =>
        class PosOrder extends Order {

            set_pricelist(pricelist) {
                var self = this;
                this.pricelist = pricelist;

                var lines_to_recompute = _.filter(this.get_orderlines(), function (line) {
                    return !line.price_manually_set;
                });
                _.each(lines_to_recompute, function (line) {
                    if (line.product_uom === '') {
                        line.set_unit_price(line.product.get_price(self.pricelist, line.get_quantity()));
                        self.fix_tax_included_price(line);
                    }
                });
            }
        }

    Registries.Model.extend(Order, PosOrder);

    const PosOrderline = Orderline =>
        class PosOrderline extends Orderline {

            init_from_JSON(json) {
                super.init_from_JSON(...arguments);
                this.has_multi_uom = json.has_multi_uom;
                this.allow_uoms = json.allow_uoms;
                this.product_uom = json.product_uom;
            }
            export_as_JSON() {
                var self = this;
                const json = super.export_as_JSON();
                json.has_multi_uom = this.get_has_multi_uoms();
                json.allow_uoms = this.get_allow_uoms();
                json.product_uom = this.get_product_uom();
                return json;
            }
            export_for_printing() {
                const receipt = super.export_for_printing();
                receipt.has_multi_uom = this.get_product().has_multi_uom;
                receipt.allow_uoms = this.get_product().allow_uoms;
                return receipt;
            }

            export_own_data(data) {
                let own_data = [];
                if (this.own_data) {
                    for (let rec in data) {
                        own_data.push({
                            'product_uom': this.own_data[rec]['product_uom']
                        });
                    }
                }
                return own_data;
            }
            set_product_uom(uom_id) {
                this.product_uom = this.pos.units_by_id[uom_id];
            }

            get_has_multi_uoms() {
                if (this['has_multi_uom'] === undefined)
                    return this.product.has_multi_uom;
                else
                    return this.has_multi_uom;
            }

            get_allow_uoms() {
                if (this['allow_uoms'] === undefined)
                    return this.product.allow_uoms;
                else
                    return this.allow_uoms;
            }

            get_product_uom() {
                if (this['product_uom'] === undefined) {
                    var uom_id = this.product.uom_id[0];
                    return this.pos.units_by_id[uom_id];
                }
                else
                    return this.product_uom;
            }

            get_unit() {
                if (!this.product_uom) {
                    return this.product.get_unit();
                } else {
                    if (this.pos.units_by_id[this.product_uom['id']]) {
                        return this.pos.units_by_id[this.product_uom['id']];
                    } else {
                        return this.product.get_unit();
                    }
                }
            }
        }

    Registries.Model.extend(Orderline, PosOrderline);

});
