odoo.define('boost_pos_order_sync.SendOrderPopup', function (require) {
    "use strict";

    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');
    var core = require('web.core');
    var QWeb = core.qweb;

    class SendOrderPopup extends AbstractAwaitablePopup {

        setup() {
            super.setup();
            this.selected_session_id = null;
        }

        click_select_session(session_id) {
            this.selected_session_id = session_id;
            $('.select_session').css('background', '#FFFFFF');
            $("span.select_session[id=" + session_id + " ]").css('background', 'rgb(84 222 100)');
        }

        pre_validation_send_order_quote() {
            return true
        }

        send_and_print_order_quote() {
            var self = this;
            self.send_order_quote(true);

            if(!self.pre_validation_send_order_quote()) {
                return
            }

            if (self.selected_session_id) {
                if (self.env.pos.config.quotation_print_type == 'pdf') {
                    setTimeout(function () {
                        self.env.legacyActionManager.do_action('boost_pos_order_sync.report_quote', {
                            additional_context: {
                                active_ids: [self.env.pos.get_order().created_quote_id],
                            }
                        });
                    }, 1000)
                }
                // Review this functionality later priority 2 //
                /*
                else if (self.env.pos.config.quotation_print_type == 'posbox') {
                    var order = self.env.pos.get_order();
                    var to_session = _.filter(self.env.pos.other_active_session, function (session) {
                        return (session.id == self.to_session_id)
                    });
                    var quote = {
                        'quote_id': $("#quote_id").text(),
                        'from_session': self.env.pos.pos_session.config_id[1],
                    }
                    if (to_session)
                        quote['to_session'] = to_session[0].config_id[1];
                    var result = {
                        widget: self.env,
                        pos: self.env.pos,
                        order: order,
                        receipt: order.export_for_printing(),
                        orderlines: order.get_orderlines(),
                        paymentlines: order.get_paymentlines(),
                        quote: quote,
                    }
                    var receipt = QWeb.render('OrderSyncOrderReceipt', result);
                    self.env.pos.proxy.printer.print_receipt(receipt);
                }
                */
            }
        }

        send_order_quote(print_order_quote) {
            var self = this;
            var session_id = self.selected_session_id;

            if (session_id) {

                if(!self.pre_validation_send_order_quote()) {
                    return
                }

                if ($("#quote_id").text() == '') {
                    self.showPopup('ErrorPopup', {
                        title: self.env._t('Error ID'),
                        body: self.env._t('No quote ID found'),
                    });
                } else {
                    self.rpc({
                        model: 'pos.quote',
                        method: 'search_quote',
                        args: [{ 'quotation_id': $("#quote_id").text() }],
                    }).then(function (result) {
                        if (result) {
                            self.showPopup('ErrorPopup', {
                                title: self.env._t('Error Quote'),
                                body: self.env._t('This quote ID has already been used'),
                            });
                        } else {
                            self.rpc({
                                model: 'pos.quote',
                                method: 'create',
                                args: [self.fill_order_quote(session_id)],
                            }).then(function (new_quote_id) {
                                if (print_order_quote === true)
                                    self.env.pos.get_order().created_quote_id = new_quote_id;
                                self.showPopup('ConfirmNotifyPopup');
                                self.cancel();
                            }).catch(function (error) {
                                console.error(error)
                                self.showPopup('ErrorPopup', {
                                    title: self.env._t('Error Network'),
                                    body: self.env._t('Please make sure you are connected to the network')
                                });
                            })
                        }
                    }).catch(function (error) {
                        console.error(error)
                        self.showPopup('ErrorPopup', {
                            title: self.env._t('Error Network'),
                            body: self.env._t('Please make sure you are connected to the network')
                        });
                    })
                }
            } else {
                $(".select_session").css("background-color", "#F18787");
                setTimeout(function () {
                    $(".select_session").css("background-color", "");
                }, 100);
                setTimeout(function () {
                    $(".select_session").css("background-color", "#F18787");
                }, 200);
                setTimeout(function () {
                    $(".select_session").css("background-color", "");
                }, 300);
                setTimeout(function () {
                    $(".select_session").css("background-color", "#F18787");
                }, 400);
                setTimeout(function () {
                    $(".select_session").css("background-color", "");
                }, 500);
            }
        }

        get_quote_data(session_id) {
            let currentOrder = this.env.pos.get_order();
            let orderVals = {
                to_session_id: session_id,
                date_order: moment(currentOrder.creation_date).format("YYYY-MM-DD HH:mm:ss"),
                user_id: this.env.pos.user.id || 2,
                partner_id: currentOrder.get_partner()?.id || undefined,
                session_id: this.env.pos.pos_session.id,
                pricelist_id: currentOrder.pricelist.id,
                note: $("#quote_note").val(),
                quote_id: $("#quote_id").text(),
                amount_total: currentOrder.get_total_with_tax(),
                amount_tax: currentOrder.get_total_tax(),
                lines: []
            };

            return orderVals
        }

        get_quote_line_data(orderLine) {
            const orderLineVals = {
                product_id: orderLine.product.id,
                price_unit: orderLine.price,
                qty: orderLine.quantity,
                discount: orderLine.discount,
                price_subtotal: orderLine.get_price_without_tax(),
                price_subtotal_incl: orderLine.get_price_with_tax(),
                product_uom: orderLine.get_unit()?.id,
                quote_tax_ids: orderLine.product.taxes_id.slice(),
                // pos loyalty fields
                is_reward_line: orderLine.is_reward_line,
                reward_id: orderLine.reward_id,
                coupon_id: orderLine.coupon_id > 0 ? orderLine.coupon_id: false ,
                reward_identifier_code: orderLine.reward_identifier_code,
                points_cost: orderLine.points_cost
            };
            return orderLineVals
        }

        fill_order_quote(session_id) {
            let orderVals = this.get_quote_data(session_id)
            this.to_session_id = session_id;
            let orderLines = this.env.pos.get_order().get_orderlines();
            let self = this;
            orderLines.forEach(function (orderLine) {
                orderVals.lines.push([0, 0, self.get_quote_line_data(orderLine)]);
            });
            return orderVals;
        }
    }

    SendOrderPopup.template = 'SendOrderPopup';
    Registries.Component.add(SendOrderPopup);
    return SendOrderPopup;
});