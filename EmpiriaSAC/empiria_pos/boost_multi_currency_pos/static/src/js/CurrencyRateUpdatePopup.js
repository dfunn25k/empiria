odoo.define('boost_multi_currency_pos.CurrencyRateUpdatePopup', function (require) {
    "use strict";

    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    const { _lt } = require('@web/core/l10n/translation');
    var utils = require('web.utils');
    var round_di = utils.round_decimals;

    class CurrencyRateUpdatePopup extends AbstractAwaitablePopup {

        setup() {
            super.setup();
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

        async _update_rate(event) {
            var self2 = this;
            let currentOrder = this.env.pos.get_order();
            let currency_id = parseInt(self.$("#currency_selection").val());
            let new_rate = parseFloat(self.$('#new_rate').val());
            if (new_rate && new_rate > 0) {
                await this.rpc({
                    model: 'res.currency.rate',
                    method: 'currency_rate_update',
                    args: [currency_id, new_rate],
                }).then(function (new_currency) {
                    if (new_currency) {
                        let all_currencies = self2.env.pos.dict_curr_list;
                        _.each(all_currencies, function (key, currency) {
                            if (new_currency.currency_id[0] === parseInt(currency)) {
                                key.rate = new_currency.rate;
                                let update_currency = self2.env.pos.dict_curr_list[key.id];
                                let currency_total = currentOrder.get_total_with_tax() * update_currency.rate;
                                let total_in = self2.env._t("Total in");
                                self.$('#conversion_rate').html('1 ' + update_currency.name + ' = ' + update_currency.rate + ' ' + update_currency.name);
                                self.$('#currency_value_label').html(total_in + ' ' + update_currency.name + ':');
                                self.$('#currency_value').html(update_currency.symbol + ' ' + currency_total);
                            }
                        });
                    }
                }).catch(function (error) {
                    console.error(error)
                });
                this.cancel();
            } else {
                this.showPopup("ErrorPopup", {
                    title: this.env._t('Error'),
                    body: this.env._t('Please enter new rate of currency in proper format'),
                });
                self.$('#new_rate').focus();
            }
        }
    }
    
    CurrencyRateUpdatePopup.defaultProps = {
        cancelText: _lt('Cancel'),
        title: _lt('Update Rate'),
        body: '',
    };
    CurrencyRateUpdatePopup.template = 'CurrencyRateUpdatePopup';
    Registries.Component.add(CurrencyRateUpdatePopup);
    return CurrencyRateUpdatePopup;
});