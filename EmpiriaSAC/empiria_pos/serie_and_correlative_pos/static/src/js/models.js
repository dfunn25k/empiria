odoo.define('serie_and_correlative_pos.models', function (require) {
    "use strict";

    var { Order, PosGlobalState } = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');

    const PosModelGlobalState = (PosGlobalState) =>
        class PosModelGlobalState extends PosGlobalState {

            async _processData(loadedData) {
                await super._processData(loadedData);
                this.document_type_ids = loadedData['l10n_latam.document.type'];
            }

            push_single_order(order, opts) {
                order.check_l10n_latam_document_type_id();
                return super.push_single_order(order, opts);
            }

            filter_document_type_by_move(records, document_type_ids) {
                let filter_ids = [];
                for (let rec in records) {
                    for (let doc in document_type_ids) {
                        if (records[rec] === document_type_ids[doc]['id']) {
                            filter_ids.push({
                                'id': document_type_ids[doc]['id'],
                                'internal_type': document_type_ids[doc]['internal_type'],
                                'name': document_type_ids[doc]['name']
                            })
                        }
                    }
                }
                return filter_ids;
            }

            get_invoice_type_document_ids() {
                const invoice_l10n_latam_document_type_ids = this.filter_document_type_by_move(this.config.invoice_l10n_latam_document_type_ids, this.document_type_ids);
                return invoice_l10n_latam_document_type_ids;
            }

            get_ticket_type_document_ids() {
                const ticket_l10n_latam_document_type_ids = this.filter_document_type_by_move(this.config.ticket_l10n_latam_document_type_ids, this.document_type_ids);
                return ticket_l10n_latam_document_type_ids;
            }
        }

    Registries.Model.extend(PosGlobalState, PosModelGlobalState);

    const PosOrder = Order =>
        class PosOrder extends Order {

            init_from_JSON(json) {
                super.init_from_JSON(json);
                this.l10n_latam_document_type_id = json.l10n_latam_document_type_id || false;
                this.l10n_latam_journal_id = json.l10n_latam_journal_id || false;
            }

            export_as_JSON() {
                const json = super.export_as_JSON();
                json.l10n_latam_document_type_id = this.l10n_latam_document_type_id ? this.l10n_latam_document_type_id : false;
                json.l10n_latam_journal_id = this.l10n_latam_journal_id ? this.l10n_latam_journal_id : false;
                return json;
            }

            export_for_printing() {
                const receipt = super.export_for_printing();
                receipt.l10n_latam_document_type_id = this.l10n_latam_document_type_id ? this.l10n_latam_document_type_id : false;
                receipt.l10n_latam_journal_id = this.l10n_latam_journal_id ? this.l10n_latam_journal_id : false;
                return receipt;
            }

            set_l10n_latam_document_type_id(l10n_latam_document_type_id) {
                this.l10n_latam_document_type_id = l10n_latam_document_type_id;
            }

            get_l10n_latam_document_type_id() {
                return this.l10n_latam_document_type_id;
            }

            set_l10n_latam_journal_id() {
                if (this.is_to_invoice() && !this.fake_invoice) {
                    this.l10n_latam_journal_id = this.pos.config.invoice_journal_id[0];
                } else {
                    this.l10n_latam_journal_id = this.pos.config.ticket_journal_id[0];
                }
            }

            check_l10n_latam_document_type_id() {
                if (this.is_to_invoice() && !this.fake_invoice) {
                    if (this.pos.get_invoice_type_document_ids().length > 0 && !this.l10n_latam_document_type_id) {
                        this.l10n_latam_document_type_id = parseInt($('#invoice_l10n_latam_document_type_ids').val());
                    }
                } else {
                    if (this.pos.get_ticket_type_document_ids().length > 0 && !this.l10n_latam_document_type_id) {
                        this.l10n_latam_document_type_id = parseInt($('#ticket_l10n_latam_document_type_ids').val());
                    }
                }
                this.set_l10n_latam_journal_id()
            }
        }

    Registries.Model.extend(Order, PosOrder);
});
