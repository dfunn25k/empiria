odoo.define('pos_rectified_document_reference.models', function (require) {
    "use strict";

    var { Order, PosGlobalState } = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');

    const PosModelGlobalState = PosGlobalState =>
        class PosModelGlobalState extends PosGlobalState {

            push_single_order(order, opts) {
                order.set_refund_data();
                return super.push_single_order(order, opts);
            }
        }

    Registries.Model.extend(PosGlobalState, PosModelGlobalState);

    const PosOrder = Order =>
        class PosOrder extends Order {

            init_from_JSON(json) {
                super.init_from_JSON(json);
                this.reference_rectified = json.reference_rectified || false;
                this.date_rectified = json.date_rectified || false;
                this.invoice_reference_type_l10n_latam_document_type_ids = json.invoice_reference_type_l10n_latam_document_type_ids || false;
                this.ticket_reference_type_l10n_latam_document_type_ids = json.ticket_reference_type_l10n_latam_document_type_ids || false;
            }

            export_as_JSON() {
                const json = super.export_as_JSON();
                json.reference_rectified = this.reference_rectified ? this.reference_rectified : false;
                json.date_rectified = this.date_rectified ? this.date_rectified : false;
                json.invoice_reference_type_l10n_latam_document_type_ids = this.invoice_reference_type_l10n_latam_document_type_ids ? this.invoice_reference_type_l10n_latam_document_type_ids : false;
                json.ticket_reference_type_l10n_latam_document_type_ids = this.ticket_reference_type_l10n_latam_document_type_ids ? this.ticket_reference_type_l10n_latam_document_type_ids : false;
                return json;
            }

            export_for_printing() {
                const receipt = super.export_for_printing();
                receipt.reference_rectified = this.reference_rectified ? this.reference_rectified : false;
                receipt.date_rectified = this.date_rectified ? this.date_rectified : false;
                receipt.invoice_reference_type_l10n_latam_document_type_ids = this.invoice_reference_type_l10n_latam_document_type_ids ? this.invoice_reference_type_l10n_latam_document_type_ids : false;
                receipt.ticket_reference_type_l10n_latam_document_type_ids = this.ticket_reference_type_l10n_latam_document_type_ids ? this.ticket_reference_type_l10n_latam_document_type_ids : false;
                return receipt;
            }

            set_refund_data() {
                if ($('#reference_rectified').val() !== '-') {
                    if (this.is_to_invoice() && !this.fake_invoice) {
                        this.invoice_reference_type_l10n_latam_document_type_ids = parseInt($("#invoice_reference_type_l10n_latam_document_type_ids :selected").val());
                        this.reference_rectified = $('#reference_rectified').val();
                        this.date_rectified = $('#date_rectified').val();
                    }
                    else {
                        this.ticket_reference_type_l10n_latam_document_type_ids = parseInt($("#ticket_reference_type_l10n_latam_document_type_ids :selected").val());
                        this.reference_rectified = $('#reference_rectified').val();
                        this.date_rectified = $('#date_rectified').val();
                    }
                }
            }
        }

    Registries.Model.extend(Order, PosOrder);
});
