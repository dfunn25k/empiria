odoo.define('payment_culqi.culqi_form', function (require) {
    'use strict';

    var Ajax = require('web.ajax');
    var Widget = require('web.Widget');
    var Dialog = require('web.Dialog');

    const PaymentCulqiForm = Widget.extend({
        events: {
            'click #culqi_pay_button': '_onClick',
        },

        init(parent, options) {
            this._super.apply(this, arguments);
            this.options = _.extend(options || {}, {});
            this.initializeCard();
        },

        initializeCard() {
            new Card({
                form: document.querySelector('form'),
                container: '.card-wrapper',
            });
        },

        disableButton(button) {
            $(button).attr('disabled', true);
            $(button).children('.fa-lock').removeClass('fa-lock');
            $(button).prepend('<span class="o_loader"><i class="fa fa-refresh fa-spin"></i>&nbsp;</span>');
        },

        enableButton(button) {
            $(button).attr('disabled', false);
            $(button).children('.fa').addClass('fa-lock');
            $(button).find('span.o_loader').remove();
        },

        formatExpirationMonthYear(vals) {
            const splitList = vals.replace(/\s/g, '').split('/');
            return splitList;
        },

        _onClick(event) {
            event.preventDefault();
            const button = event.target;
            this.disableButton(button);

            const elForm = this.$el;
            elForm.find('input').each(function () {
                const myElement = $(this);
                if (!myElement[0].checkValidity()) {
                    myElement.addClass('is-invalid');
                } else {
                    myElement.removeClass('is-invalid');
                }
                if (myElement.attr('name') === 'expiry' && myElement.val().length !== 7) {
                    myElement.addClass('is-invalid');
                }
            });

            if (elForm.find('.is-invalid').length) {
                this.enableButton(button);
                event.stopPropagation();
                return false;
            }

            const actionUrl = elForm.attr('action');
            const cardNumber = elForm.find('input[name=number]').val().replace(/\s/g, '');
            const expiryList = this.formatExpirationMonthYear(elForm.find('input[name=expiry]').val());
            const formData = {
                'cardNumber': parseInt(cardNumber, 10),
                'email': elForm.find('input[name=email]').val(),
                'cvv': parseInt(elForm.find('input[name=cvc]').val(), 10),
                'expirationYear': parseInt(expiryList[1], 10),
                'expirationMonth': parseInt(expiryList[0], 10),
                'transaction': parseInt(elForm.find('input[name=transaction]').val(), 10),
            };

            Ajax.jsonRpc(actionUrl, 'call', formData).then(response => {
                if (_.has(response, 'Redirect')) {
                    window.location.href = response.Redirect;
                    return true;
                } else if (_.has(response, 'Error')) {
                    Dialog.alert(this, response.Error);
                    this.enableButton(button);
                    return false;
                }
            });
        },
    });

    $(function () {
        $('form[name=o_culqi_form]').each(function () {
            const $elem = $(this);
            const form = new PaymentCulqiForm(null, $elem.data());
            form.attachTo($elem);
        });
    });
});
