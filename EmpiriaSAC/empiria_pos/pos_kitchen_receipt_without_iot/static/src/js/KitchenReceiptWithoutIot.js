odoo.define('pos_kitchen_receipt_without_iot.WVPosKitchenReceiptButton', function (require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const Registries = require('point_of_sale.Registries');    
    const { useListener } = require("@web/core/utils/hooks");

    class WVPosKitchenReceiptButton extends PosComponent {

        setup() {
            super.setup();
            this.clicked = false; //mutex, we don't want to be able to spam the printers
            useListener('click', this._onClick);
        }

        async _onClick() {
            if (!this.clicked) {
                try {
                    this.clicked = true;
                    const order = this.env.pos.get_order();
                    if (order.hasChangesToPrint()) {
                        await order.printChanges2();
                        order.updatePrintedResume();
                        await this.showTempScreen('KitchenReceiptScreen', {"report": order.receipt_val});
                    }
                } finally {
                    this.clicked = false;
                }
            }
        }

        get currentOrder() {
            return this.env.pos.get_order();
        }

        get addedClasses() {
            if (!this.currentOrder) return {};
            const changes = this.currentOrder.hasChangesToPrint();
            const skipped = changes ? false : this.currentOrder.hasSkippedChanges();
            return {
                highlight: changes,
                altlight: skipped,
            }
        }
    }

    WVPosKitchenReceiptButton.template = 'WVPosKitchenReceiptButton';
    ProductScreen.addControlButton({
        component: WVPosKitchenReceiptButton,
        condition: function () {
            return this.env.pos.config.module_pos_restaurant && this.env.pos.unwatched.printers.length && this.env.pos.config.allow_kitchens_receipt;
        },
    });
    
    Registries.Component.add(WVPosKitchenReceiptButton);
    return WVPosKitchenReceiptButton
});
