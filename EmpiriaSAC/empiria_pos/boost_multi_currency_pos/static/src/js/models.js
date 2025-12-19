odoo.define('boost_multi_currency_pos.models', function (require) {
    "use strict";

    var { PosGlobalState, Order, Orderline } = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');

    // Helper function to calculate the number of decimals
    function calculateDecimals(rounding) {
        return rounding > 0 ? Math.ceil(Math.log10(1.0 / rounding)) : 0;
    }

    function loadMultiCurrency(currencyList) {
        for (const [key, currency] of Object.entries(currencyList)) {
            currency.decimals = calculateDecimals(currency.rounding);
        }
    }

    const PosModelGlobalState = PosGlobalState =>
        class PosModelGlobalState extends PosGlobalState {

			async _processData(loadedData) {
                this.currency_list = loadedData["currency_list"];
                this.dict_curr_list = loadedData["dict_curr_list"];
                loadMultiCurrency(this.currency_list);
                loadMultiCurrency(this.dict_curr_list);
                await super._processData(loadedData);
			}
        }

    Registries.Model.extend(PosGlobalState, PosModelGlobalState);

    const PosOrder = Order =>
        class PosOrder extends Order {

            set_currency_mode(mode) {
                this.currency_mode = mode;
            }

            get_currency_mode() {
                return this.currency_mode;
            }

            set_currency_id(currency) {
                this.order_currency_id = currency;
            }

            get_currency_id() {
                return this.order_currency_id;
            }

            set_amount_currency(amount) {
                this.amount_currency = amount;
            }

            get_amount_currency() {
                return this.amount_currency;
            }

            set_currency_receipt_mode(curr_receipt_mode) {
                this.curr_receipt_mode = curr_receipt_mode;
            }

            get_currency_receipt_mode() {
                return this.curr_receipt_mode;
            }

            export_as_JSON() {
                const json = super.export_as_JSON();
                json.order_currency_id = this.get_currency_id() || false;
                json.amount_currency = this.get_amount_currency() || false;
                return json;
            }

            export_for_printing() {
                const receipt = super.export_for_printing();
                receipt.order_currency_id = this.get_currency_id() || false;
                receipt.amount_currency = this.get_amount_currency() || false;
                receipt.curr_receipt_mode = this.get_currency_receipt_mode() || false;
                return receipt;
            }
        }

    Registries.Model.extend(Order, PosOrder);

    const PosOrderline = Orderline =>
        class PosOrderline extends Orderline {

            set_line_amount_currency(line_amount_currency) {
                this.line_amount_currency = line_amount_currency;
            }

            get_line_amount_currency() {
                return this.line_amount_currency;
            }

            export_as_JSON() {
                const json = super.export_as_JSON();
                json.line_amount_currency = this.get_line_amount_currency() || false;
                return json;
            }

            export_for_printing() {
                const receipt = super.export_for_printing();
                receipt.line_amount_currency = this.get_line_amount_currency() || false;
                return receipt;
            }
        }
    
    Registries.Model.extend(Orderline, PosOrderline);
});
