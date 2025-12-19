odoo.define('boost_multi_currency_pos.OrderReceipt', function (require) {
    "use strict";

    const OrderReceipt = require('point_of_sale.OrderReceipt');
    const Registries = require('point_of_sale.Registries');
    var utils = require('web.utils');
    var round_di = utils.round_decimals;

    const PosOrderReceipt = OrderReceipt =>
        class PosOrderReceipt extends OrderReceipt {

            convert_currency(currency_id, amount) {
                if (!currency_id && !amount) {
                    return
                }
                let currency = this.env.pos.dict_curr_list[currency_id];
                if (currency) {
                    let decimals = currency.decimals;
                    let currency_total = round_di(amount * currency.rate, decimals).toFixed(decimals);
                    return currency_total;
                } else {
                    return false
                }
            }

            format_foreign(amount, currency, precision) {
                if (!amount && !currency) {
                    return
                }
                var decimals = currency.decimals;
                if (precision && (typeof this.pos.dp[precision]) !== undefined) {
                    decimals = this.pos.dp[precision];
                }
                if (typeof amount === 'number') {
                    amount = round_di(amount, decimals).toFixed(decimals);
                }
                if (currency.position === 'after') {
                    return amount + ' ' + (currency.symbol || '');
                } else {
                    return (currency.symbol || '') + ' ' + amount;
                }
            }
        }

    Registries.Component.extend(OrderReceipt, PosOrderReceipt);
    return PosOrderReceipt;
});