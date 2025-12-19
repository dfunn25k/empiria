odoo.define('ruc_validation_pos_sunat.ruc_validation_pos_sunat', function (require) {
    "use strict";

    const PartnerListScreen = require('point_of_sale.PartnerListScreen');
    const PartnerDetailsEdit = require('point_of_sale.PartnerDetailsEdit');
    const Registries = require('point_of_sale.Registries');

    const PosPartnerListScreen = (PartnerListScreen) =>
        class extends PartnerListScreen {
            triggerValidationSunat() {
                let validation_rut_obj = $('#validation-ruc')
                if (validation_rut_obj.is(':checked')) {
                    validation_rut_obj.prop('checked', false)
                } else {
                    validation_rut_obj.prop('checked', true)
                }
                this.trigger('click-save')
                validation_rut_obj.prop('checked', false)
            }

            validationRucSunatFields(processedChanges) {
                if (!processedChanges.l10n_latam_identification_type_id || processedChanges.l10n_latam_identification_type_id === '') {
                    processedChanges.l10n_latam_identification_type_id = $('.partner-document-type').val()
                }
                if (!processedChanges.vat || processedChanges.vat === '') {
                    processedChanges.vat = $('.vat').val()
                }
            }

            async saveChanges(event) {
                let validation_rut_obj = $('#validation-ruc')
                if (validation_rut_obj.is(':checked')) {
                    this.validationRucSunatFields(event.detail.processedChanges)
                    await this.rucValidationSunat(event)
                }
                if(event.detail.processedChanges)
                    super.saveChanges(event);
                validation_rut_obj.prop('checked', false)
            }

            async rucValidationSunat(event) {
                try {
                    let partner_values = await this.rpc({
                        model: 'res.partner',
                        method: 'handle_data_sunat',
                        args: [event.detail.processedChanges],
                    });
                    if (!partner_values) {
                        await this.showPopup('OfflineErrorPopup', {
                            title: "UPPS!",
                            body: "No se puede realizar la consulta, porque el servicio de SUNAT está demorando en Responder, o su conexión a Internet es demasiado lenta. Pruebe haciendo la consulta manual directo en la página de consulta RUC de SUNAT, porque si el servicio de SUNAT presenta problemas de lentitud, Odoo no se conectará para evitar afectar el rendimiento del sistema.",
                        });
                    }
                    if (partner_values) {
                        partner_values.l10n_latam_identification_type_id = event.detail.processedChanges.l10n_latam_identification_type_id;
                        event.detail.processedChanges = partner_values;
                    }
                } catch (error) {
                    if (error.message.code < 0) {
                        await this.showPopup('OfflineErrorPopup', {
                            title: this.env._t('Offline'),
                            body: this.env._t('Unable to save changes.'),
                        });
                    } else {
                        throw error;
                    }
                }
            }
        };
    Registries.Component.extend(PartnerListScreen, PosPartnerListScreen);

    const PosPartnerDetailsEdit = (PartnerDetailsEdit) =>
        class extends PartnerDetailsEdit {
            validate_fields(processedChanges) {
                // Override this method to avoid to ask for empty field 'name' in new Clients
                let error_msj = super.validate_fields(processedChanges);
                if (error_msj === 'A Customer Name Is Required' && $('#validation-ruc').is(':checked')) {
                    error_msj = false
                }
                return error_msj
            }
        };

    Registries.Component.extend(PartnerDetailsEdit, PosPartnerDetailsEdit);
});
