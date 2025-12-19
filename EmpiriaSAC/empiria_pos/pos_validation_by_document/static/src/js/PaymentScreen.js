odoo.define('pos_validation_by_document.PosPaymentScreen', function (require) {
    'use strict';

    const PaymentScreen = require('point_of_sale.PaymentScreen')
    const Registries = require('point_of_sale.Registries');
    var rpc = require('web.rpc');

    const PosPaymentScreen = PaymentScreen =>
        class PosPaymentScreen extends PaymentScreen {

            async validateOrder(isForceValidate) {

                const selectedOrder = this.env.pos.get_order();
                const partner = selectedOrder.get_partner()
                const div_invoice = $("#div_invoice_l10n_latam_document_type_ids");
                const document_type_invoice = _.isEmpty(div_invoice);
                const div_ticket = $("#div_ticket_l10n_latam_document_type_ids");
                const document_type_ticket = _.isEmpty(div_ticket);

                if (selectedOrder.get_total_with_tax() > this.env.pos.config.identify_client && (!document_type_invoice || !document_type_ticket)) {
                    if (partner !== null) {
                        const is_vat = this.get_element(partner.l10n_latam_identification_type_id[0]).is_vat;
                        if (partner.id === this.env.pos.config.ticket_user_id[0]) {
                            await this.showPopup('ErrorPopup', {
                                'title': this.env._t('Wrong value'),
                                'body': this.env._t('The amount of the sale is greater than ' + this.env.pos.config.identify_client + ' so you must identify a client'),
                            });
                            return;
                        }
                        if (!is_vat) {
                            await this.showPopup('ErrorPopup', {
                                'title': this.env._t('Wrong value'),
                                'body': this.env._t('Choose a client who has an identity document that is fiscal'),
                            });
                            return;
                        }
                    } else {
                        const { confirmed } = await this.showPopup('ConfirmPopup', {
                            'title': this.env._t('Wrong value'),
                            'body': this.env._t('You must select a client'),
                        });
                        if (confirmed) {
                            this.selectPartner();
                        }
                        return false;
                    }
                }

                if (!document_type_invoice || !document_type_ticket) {
                    if (partner !== null) {
                        const document_id = !document_type_invoice ? parseInt(div_invoice[0].children[1].value) : parseInt(div_ticket[0].children[1].value);
                        const array_documents_ids = this.get_element(partner.l10n_latam_identification_type_id[0]).invoice_validation_document;
                        if (!array_documents_ids?.includes(document_id) && selectedOrder.get_orderlines().length !== 0) {
                            await this.showPopup('ErrorPopup', {
                                'title': this.env._t('Wrong value'),
                                'body': this.env._t('The type of identification document of the Client, requires that another "Type of Document" of sale be used. I know ' +
                                    'suggests that you use another sales document, or change the type of customer identification'),
                            });
                            return;
                        }
                    } else {
                        const { confirmed } = await this.showPopup('ConfirmPopup', {
                            'title': this.env._t('Wrong value'),
                            'body': this.env._t('You must select a client'),
                        });
                        if (confirmed) {
                            this.selectPartner();
                        }
                        return false;
                    }
                }

                if (partner !== null) {
                    const partner_identification_type_id = partner.l10n_latam_identification_type_id[0];
                    const partner_identification_type_id_data = this.get_element(partner_identification_type_id);
                    if (partner.vat) {
                        const numberDocument = this.env._t('Document number');
                        this.validate_long(
                            partner.vat,
                            partner_identification_type_id_data.doc_length,
                            partner_identification_type_id_data.exact_length,
                            numberDocument
                        )
                    } else {
                        await this.showPopup('ErrorPopup', {
                            'title': this.env._t('Wrong value'),
                            'body': this.env._t('The customer must have a document number to make the purchase'),
                        });
                        return;
                    }
                }
                
                super.validateOrder(isForceValidate);
            }

            get_element(partner_identification_type_id) {
                let records = this.env.pos.documents_identification_ids;
                for (let rec in records) {
                    let doc = records[rec];
                    if (doc.id === partner_identification_type_id) {
                        return doc;
                    }
                }
                return '';
            }

            validate_long(word, length, validation_type, field_name) {
                if (word && validation_type) {
                    if (validation_type === 'exact') {
                        if (word.length !== length) {
                            this.showPopup('ErrorPopup', {
                                'title': this.env._t('Wrong value'),
                                'body': this.env._t('The number of characters for the field ' + field_name + ' must be ' + length),
                            });
                        }
                    } else if (validation_type === 'maximum') {
                        if (word.length > length) {
                            this.showPopup('ErrorPopup', {
                                'title': this.env._t('Wrong value'),
                                'body': this.env._t('The number of characters for the field ' + field_name + ' must be at most ' + length),
                            });
                        }
                    }
                }
            }
        };

    Registries.Component.extend(PaymentScreen, PosPaymentScreen);
    return PaymentScreen;
});
