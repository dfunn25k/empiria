odoo.define('select_invoice_format_pos.PosGlobalState', function (require) {
    "use strict";

    var { PosGlobalState } = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');

    const SelectInvoiceFormatPosGlobalState = PosGlobalState => class extends PosGlobalState {
        is_report_printed() {
            if (this.env.pos.config.automatic_print_electronic_invoice) {
                return true;
            }
            return false;
        }
        get_report_action_name() {
            if (this.env.pos.config.invoice_report_id) {
                return this.env.pos.config.invoice_report_id[0];
            }
            return super.get_report_action_name();
        }
        async getDynamicReport(account_move, order_reference) {
            let report_value = false;
            let invoice_report_id = this.env.pos.config.invoice_report_id[0];
            let default_method = 'generate_dynamic_report_from_pos_ui';
            let reference_id = account_move ? account_move : order_reference;
            if (account_move) {
                default_method = 'generate_dynamic_report_from_account_move_pos_ui';
            }
            await this.env.services.rpc({
                model: 'pos.order',
                method: default_method,
                args: [reference_id, invoice_report_id],
            }).then(function (data) {
                if (data['error'] === false) {
                    report_value = data['report'];
                }
            }).catch(function (error) {
                console.error(error);
            });
            return report_value;
        }
        async report_action_backend(account_move) {
            if (this.is_report_printed() && this.env.pos.config.invoice_report_id) {
                const currentOrder = this.get_order();
                const reportValue = await this.getDynamicReport(account_move, currentOrder.name);
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
            } else {
                return super.report_action_backend(account_move);
            }
        }
    }
    Registries.Model.extend(PosGlobalState, SelectInvoiceFormatPosGlobalState);
});
