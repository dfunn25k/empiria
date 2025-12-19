odoo.define('pos_rectified_document_reference.PaymentScreen', function (require) {
    "use strict";

    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');
    const { onMounted } = owl;

    const PosPaymentScreen = PaymentScreen =>
        class PosPaymentScreen extends PaymentScreen {

            setup() {
                super.setup();
                onMounted(this.onMounted);
            }

            onMounted() {
                var documents_ids = (this.env.pos.get_invoice_type_document_ids()).length;
                for (var id_invoice = 0; id_invoice < documents_ids; id_invoice++) {
                    if (this.env.pos.get_invoice_type_document_ids()[id_invoice].name === this.currentOrder.account_move_rel_document_type) {
                        this.toggleIsToInvoice();
                    }
                }
                this.onChange_document_reference();
                this.set_values_reference_data();
            }

            async _finalizeValidation() {
                this.currentOrder.set_refund_data();
                await super._finalizeValidation();
            }

            onChange_document_reference() {
                let ticket_id = parseInt($('#ticket_l10n_latam_document_type_ids').val());
                let invoice_id = parseInt($('#invoice_l10n_latam_document_type_ids').val());
                let ticket_document = false;
                let invoice_document = false;

                var ticket_documents_ids = (this.env.pos.get_ticket_type_document_ids()).length
                for (var id_ticket = 0; id_ticket < ticket_documents_ids; id_ticket++) {
                    if (this.env.pos.get_ticket_type_document_ids()[id_ticket].id === ticket_id) {
                        ticket_document = this.env.pos.get_ticket_type_document_ids()[id_ticket];
                    }
                }

                var invoice_documents_ids = (this.env.pos.get_invoice_type_document_ids()).length
                for (var id_invoice = 0; id_invoice < invoice_documents_ids; id_invoice++) {
                    if (this.env.pos.get_invoice_type_document_ids()[id_invoice].id === invoice_id) {
                        invoice_document = this.env.pos.get_invoice_type_document_ids()[id_invoice];
                    }
                }

                if (!this.currentOrder.is_to_invoice()) {
                    $('#reference_data_id').hide();
                    if (ticket_document !== false) {
                        if (ticket_document.internal_type !== 'debit_note' && ticket_document.internal_type !== 'credit_note') {
                            $('#reference_data_id').hide();
                        }
                        else {
                            $('#reference_data_id').show();

                        }
                    }
                    if (ticket_document === false && (this.env.pos.get_ticket_type_document_ids()).length > 0) {
                        if (this.currentOrder.get_total_with_tax() + this.currentOrder.get_rounding_applied() >= 0 && this.env.pos.get_ticket_type_document_ids()[0].internal_type === 'invoice') {
                            $('#reference_data_id').hide();
                        }
                    }
                }
                if (this.currentOrder.is_to_invoice()) {
                    $('#reference_data_id').show();
                    if (invoice_document !== false) {
                        if (invoice_document.internal_type !== 'debit_note' && invoice_document.internal_type !== 'credit_note') {
                            $('#reference_data_id').hide();
                        }
                        else {
                            $('#reference_data_id').show();
                        }
                    }
                    if (invoice_document === false && (this.env.pos.get_invoice_type_document_ids()).length > 0) {
                        if (this.currentOrder.get_total_with_tax() + this.currentOrder.get_rounding_applied() >= 0 && this.env.pos.get_invoice_type_document_ids()[0].internal_type === 'invoice') {
                            $('#reference_data_id').hide();
                        }
                    }
                }
            }

            set_values_reference_data() {
                if (this.currentOrder.account_move_rel_name){
                    $('#reference_rectified').val((this.currentOrder.account_move_rel_name).replace(/ /g, ""));
                }
                $('#date_rectified').val(this.currentOrder.account_move_rel_invoice_date);
                if (this.currentOrder.get_total_with_tax() + this.currentOrder.get_rounding_applied() >= 0) {
                    $('#ticket_esc_max_id').val(this.currentOrder.account_move_rel_document_type);
                    $('#invoice_esc_max_id').val(this.currentOrder.account_move_rel_document_type);
                }
                else {
                    $('#ticket_esc_min_id').val(this.currentOrder.account_move_rel_document_type);
                    $('#invoice_esc_min_id').val(this.currentOrder.account_move_rel_document_type);
                }
            }

            toggleIsToInvoice() {
                // click_invoice
                this.set_values_reference_data();
                super.toggleIsToInvoice();
                this.onChange_document_reference();
            }

            get invoice_l10n_latam_document_type_ids_reference() {
                return this.env.pos.get_invoice_type_document_ids();
            }

            get ticket_l10n_latam_document_type_ids_reference() {
                return this.env.pos.get_ticket_type_document_ids();
            }

            onChange_l10n_latam_document_type_id(ev) {
                this.onChange_document_reference();
                super.onChange_l10n_latam_document_type_id(ev);
            }
        }

    Registries.Component.extend(PaymentScreen, PosPaymentScreen);
    return PaymentScreen;
});
