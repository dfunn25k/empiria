odoo.define('select_invoice_format_pos.ReceiptScreen', function (require) {
    "use strict";

    const { useAsyncLockedMethod } = require('point_of_sale.custom_hooks');
    const { useListener } = require("@web/core/utils/hooks");
    const Registries = require('point_of_sale.Registries');
    const ReceiptScreen = require('point_of_sale.ReceiptScreen');

    const SelectInvoiceFormatReceiptScreen = ReceiptScreen => class extends ReceiptScreen {
        setup() {
            super.setup();
            useListener('print-electronic-receipt', () => this._printDynamicReceipt());
            this.report_value = false;
            this._printDynamicReceipt = useAsyncLockedMethod(this._printDynamicReceipt);
        }
        async _printDynamicReceipt() {
            const currentOrder = this.currentOrder;
            const reportValue = await this.env.pos.getDynamicReport(false, currentOrder.name);
            try {
                printJS({
                    printable: reportValue,
                    type: 'pdf',
                    base64: true,
                    showModal: false
                });
            } catch (e) {
                console.error(e);
            }
        }
    };
    Registries.Component.extend(ReceiptScreen, SelectInvoiceFormatReceiptScreen);
    return ReceiptScreen;
});
