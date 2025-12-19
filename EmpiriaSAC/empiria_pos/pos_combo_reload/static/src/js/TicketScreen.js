odoo.define('pos_combo_reload.TicketScreen', function (require) {
    'use strict';

    const TicketScreen = require('point_of_sale.TicketScreen');
    const Registries = require('point_of_sale.Registries');

    const PosTicketScreen = TicketScreen =>
        class PosTicketScreen extends TicketScreen {

            // overriding method to add order_menu, I don't think it's the best way but it works
           _getToRefundDetail(orderline) {
               if (orderline.id in this.env.pos.toRefundLines) {
                   return this.env.pos.toRefundLines[orderline.id];
               } else {
                   const partner = orderline.order.get_partner();
                   const orderPartnerId = partner ? partner.id : false;
                   const newToRefundDetail = {
                       qty: 0,
                       orderline: {
                           id: orderline.id,
                           productId: orderline.product.id,
                           price: orderline.price,
                           qty: orderline.quantity,
                           refundedQty: orderline.refunded_qty,
                           orderUid: orderline.order.uid,
                           orderBackendId: orderline.order.backendId,
                           orderPartnerId,
                           tax_ids: orderline.get_taxes().map(tax => tax.id),
                           discount: orderline.discount,
                           order_menu: orderline.order_menu,
                           own_data: orderline.own_data,
                           worthless_combo: orderline.worthless_combo
                       },
                       destinationOrderUid: false,
                   };
                   this.env.pos.toRefundLines[orderline.id] = newToRefundDetail;
                   return newToRefundDetail;
               }
           }

           _prepareRefundOrderlineOptions(toRefundDetail) {
               const { qty, orderline } = toRefundDetail;
               const refund = super._prepareRefundOrderlineOptions(toRefundDetail);
               refund['order_menu'] = orderline.order_menu || [];
               refund['own_data'] = orderline.own_data || [];
               refund['worthless_combo'] = orderline.worthless_combo || false;
               return refund
           }
        }

    Registries.Component.extend(TicketScreen, PosTicketScreen);
    return TicketScreen;
});