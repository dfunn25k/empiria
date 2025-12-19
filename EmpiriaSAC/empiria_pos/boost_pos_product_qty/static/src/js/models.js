odoo.define('boost_pos_product_qty.models', function (require) {
    "use strict";

    var { PosGlobalState, Orderline } = require('point_of_sale.models');
    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');

    const PosModelGlobalState = PosGlobalState =>
        class PosModelGlobalState extends PosGlobalState {

            refresh_qty_available(product) {
                var $elem = $("[data-product-id='" + product.id + "'] .qty-tag");
                $elem.html(product.qty_available);
                if (product.qty_available <= 0 && !$elem.hasClass('not-available')) {
                    $elem.addClass('not-available');
                }
            }

            set_product_qty_available(product, qty) {
                product.qty_available = qty;
                this.refresh_qty_available(product);
            }

            update_product_qty_from_order_lines(order) {
                var lines = order.orderlines;
                for (let i = 0; i < lines.length; i++) {
                    let product = lines[i].get_product();
                    product.qty_available -= lines[i].get_quantity();
                    this.refresh_qty_available(product);
                }
            }

            push_orders(order, opts) {
                if (order) {
                    this.update_product_qty_from_order_lines(order);
                }
                return super.push_orders(order, opts);
            }

            push_single_order(order, opts) {
                if (order || (order && order.get_partner() && order.orderlines)) {
                    this.update_product_qty_from_order_lines(order);
                }
                return super.push_single_order(order, opts);
            }
        }

    Registries.Model.extend(PosGlobalState, PosModelGlobalState);

    const PosOrderline = Orderline =>
        class PosOrderline extends Orderline {

            export_as_JSON() {
                var data = super.export_as_JSON();
                data.qty_available = this.product.qty_available;
                var product = this.pos.db.get_product_by_id(data.product_id);
                if (product.qty_available !== data.qty_available) {
                    this.pos.set_product_qty_available(product, data.qty_available);
                }
                return data;
            }
        }

    Registries.Model.extend(Orderline, PosOrderline);

    const PosPaymentScreen = PaymentScreen =>
        class PosPaymentScreen extends PaymentScreen {
            async _finalizeValidation() {
                await super._finalizeValidation();
                try {
                    const { product_by_id } = this.env.pos.db;
                    const { config } = this.env.pos;
                    const locationId = config.location_id[0];

                    const productIds = Object.keys(product_by_id).map(Number);
                    const productQtyAvailable = await this.env.services.rpc({
                        model: 'product.product',
                        method: 'search_read',
                        args: [],
                        fields: ['id', 'qty_available'],
                        domain: [
                            ['id', 'in', productIds],
                            ['sale_ok', '=', true],
                            ['available_in_pos', '=', true],
                        ],
                        context: { location: locationId },
                    });

                    const productQtyAvailableMap = new Map(
                        productQtyAvailable.map((p) => [p.id, p.qty_available])
                    );

                    for (const product of Object.values(product_by_id)) {
                        const qtyAvailable = productQtyAvailableMap.get(product.id);
                        if (qtyAvailable !== undefined && product.qty_available !== qtyAvailable) {
                            product.qty_available = qtyAvailable;
                        }
                    }
                } catch (error) {
                    console.error(error);
                }
            }
        }

    Registries.Component.extend(PaymentScreen, PosPaymentScreen);
    return PaymentScreen;
});
