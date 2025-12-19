odoo.define('pos_product_return.TicketScreen', function (require) {
    'use strict';

    const TicketScreen = require('point_of_sale.TicketScreen');
    const Registries = require('point_of_sale.Registries');

    const PosTicketScreen = TicketScreen =>
        class PosTicketScreen extends TicketScreen {

            async _onDoRefund() {
                await super._onDoRefund();
                const selectedSyncedOrder = this.getSelectedSyncedOrder();
                const order = this.env.pos.get_order();
                //set info to rectified invoice
                if (selectedSyncedOrder && order) {
                    order['account_move_rel_name'] = selectedSyncedOrder['account_move_rel_name'];
                    order['account_move_rel_document_type'] = selectedSyncedOrder['account_move_rel_document_type'];
                    order['account_move_rel_invoice_date'] = selectedSyncedOrder['account_move_rel_invoice_date'];
                }
            }

            _getSearchFields() {
                const fields = super._getSearchFields();

                fields['ACCOUNT_MOVE_DOCUMENT_TYPE'] = {
                    repr: (order) => order.account_move_rel_document_type,
                    displayName: this.env._t('Document type'),
                    modelField: 'account_move_rel_document_type',
                },
                    fields['ACCOUNT_MOVE_NAME'] = {
                        repr: (order) => order.account_move_rel_name,
                        displayName: this.env._t('Invoice number'),
                        modelField: 'account_move_rel_name',
                    }

                return fields;
            }
        }

    Registries.Component.extend(TicketScreen, PosTicketScreen);
    return TicketScreen;
});