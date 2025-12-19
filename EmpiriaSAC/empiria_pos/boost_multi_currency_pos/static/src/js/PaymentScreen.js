odoo.define('boost_multi_currency_pos.PaymentScreen', function (require) {
    "use strict";

    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');
    var utils = require('web.utils');
    var round_di = utils.round_decimals;

    const PosPaymentScreen = PaymentScreen =>
        class PosPaymentScreen extends PaymentScreen {

            selectPaymentLine(event) {
                super.selectPaymentLine(event);
                self.$('#curr_input').val('');
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

            set_foreign_values(currency_id) {
                var currentOrder = this.env.pos.get_order();
                var currency = this.env.pos.dict_curr_list[currency_id];
                if (currency) {
                    let decimals = currency.decimals;
                    let currency_total = currentOrder.get_total_with_tax() * currency.rate;
                    let total_in = this.env._t('Total in')
                    let paid_in = this.env._t('Paid in')
                    let receipt_in = this.env._t('Receipt in')
                    if (this.env.pos.config.display_conversion)
                        self.$('#conversion_rate').html('1 ' + this.env.pos.currency.name + ' = ' + currency.rate + ' ' + currency.name);
                    self.$('#currency_value_label').html(total_in + ' ' + currency.name + ':');
                    self.$('#currency_value').html(currency.symbol + ' ' + currency_total);
                    self.$('#foreign_input_label').html(paid_in + ' ' + currency.name + ':');
                    self.$('#receipt_currency_label').html(receipt_in + ' ' + currency.name + ':');
                }
            }

            value_input(event) {
                // this event will call each one write values in curr_input , set payment
                let currentOrder = this.env.pos.get_order();
                let curr_input = self.$("#curr_input").val();
                let line = currentOrder.selected_paymentline;
                if (line == undefined) {
                    this.showPopup("ErrorPopup", {
                        title: this.env._t('Error'),
                        body: this.env._t('No Payment Line selected !'),
                    });
                    self.$('#curr_input').val('');
                    return false;
                }
                let curr_id = self.$("#currency_selection").val();
                var currency = this.env.pos.dict_curr_list[curr_id];
                if (currency) {
                    let converted_value = curr_input / currency.rate;
                    line.set_amount(converted_value);
                }
            }

            switch_change(event) {
                // add section for multi currency
                let currentOrder = this.env.pos.get_order();
                currentOrder.set_currency_mode(true);
                currentOrder.set_currency_receipt_mode(false);
                let toggle_multi_currency = self.$('#toggle_multi_currency').prop("checked");
                let line = currentOrder.selected_paymentline;
                if (toggle_multi_currency) {
                    if(self.$('.multi_currency_pos').hasClass('display-none')){
                        self.$('.multi_currency_pos').removeClass('display-none');
                    }
                    if(self.$('.div_currency_inputs').hasClass('display-none')){
                        self.$('.div_currency_inputs').removeClass('display-none');
                    }
                    self.$('.multi_currency_pos').show();
                    self.$('.div_currency_inputs').show();
                    let curr_id = parseInt(self.$("#currency_selection").val());
                    this.set_foreign_values(curr_id)
                    self.$('#curr_input').focus();
                    if (self.$('#curr_input').val() !== '')
                        self.$('#curr_input').select();
                } else {
                    self.$('.multi_currency_pos').hide();
                    self.$('.div_currency_inputs').hide();
                    if(!self.$('.multi_currency_pos').hasClass('display-none')){
                        self.$('.multi_currency_pos').addClass('display-none');
                    }
                    if(!self.$('.div_currency_inputs').hasClass('display-none')){
                        self.$('.div_currency_inputs').addClass('display-none');
                    }
                    currentOrder.set_currency_mode(false);
                    if (line === undefined || line === "") {
                        self.$('.paymentline input').val(0);
                        return false;
                    }
                    self.$('#curr_input').val('');
                    line.set_amount(0);
                }
            }

            receipt_change() {
                let currentOrder = this.env.pos.get_order();
                if (self.$('#curr_receipt').prop("checked") == true) {
                    currentOrder.set_currency_receipt_mode(true);
                } else {
                    currentOrder.set_currency_receipt_mode(false);
                }
            }

            currency_selection() {
                var self = this
                return self.env.pos.currency_list[0];
            }

            select_change(event) {
                // set values for selection currency
                let currentOrder = this.env.pos.get_order();
                let line = currentOrder.selected_paymentline;
                if (line) {
                    line.set_amount(0);
                }
                self.$('#curr_input').focus();
                let curr_id = parseInt(self.$("#currency_selection").val());
                this.set_foreign_values(curr_id)
                self.$('#curr_input').val('');
            }

            update_rate() {
                // update rate in screen with the helped popup
                let curr_id = self.$("#currency_selection").val();
                let currency = this.env.pos.dict_curr_list[curr_id];
                this.showPopup("CurrencyRateUpdatePopup", {
                    title: this.env._t('Update Rate'),
                    confirmText: this.env._t("Exit"),
                    currency: currency
                });
            }

            async validateOrder(isForceValidate) {
                let order = this.env.pos.get_order();
                let value = self.$('#curr_input').val();
                order.set_currency_id(false);
                if (order.get_currency_mode() && Number(value) > 0) {
                    let selected_currency = parseInt(self.$('#currency_selection').val());
                    let currency = this.env.pos.dict_curr_list[selected_currency];
                    order.set_currency_id(selected_currency);
                    order.set_amount_currency(value);
                    let orderlines = order.get_orderlines();
                    if (orderlines) {
                        _.each(orderlines, function (line) {
                            var line_amount_currency = round_di(line.get_price_with_tax() * currency.rate, currency.decimals).toFixed(currency.decimals);
                            line.set_line_amount_currency(line_amount_currency);
                        })
                    }
                }
                if(this.env.pos.config.cash_rounding) {
                    if(!this.env.pos.get_order().check_paymentlines_rounding()) {
                        this.showPopup('ErrorPopup', {
                            title: this.env._t('Rounding error in payment lines'),
                            body: this.env._t("The amount of your payment lines must be rounded to validate the transaction."),
                        });
                        return;
                    }
                }
                return super.validateOrder(...arguments);
            }
        }

    Registries.Component.extend(PaymentScreen, PosPaymentScreen);
    return PosPaymentScreen;
});