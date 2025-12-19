odoo.define('document_type_on_pos.PartnerDetailsEdit', function (require) {
    "use strict";

    const PartnerDetailsEdit = require('point_of_sale.PartnerDetailsEdit');
    const Registries = require('point_of_sale.Registries');

    const DocumentTypeOnPosPartnerDetailsEdit = PartnerDetailsEdit =>
        class DocumentTypeOnPosPartnerDetailsEdit extends PartnerDetailsEdit {
            setup() {
                super.setup();
                const partner = this.props.partner;
                this.changes['l10n_latam_identification_type_id'] = partner.l10n_latam_identification_type_id && partner.l10n_latam_identification_type_id[0]
            }
            saveChanges() {
                let processedChanges = {};
                for (let [key, value] of Object.entries(this.changes)) {
                    if (this.intFields.includes(key)) {
                        processedChanges[key] = parseInt(value) || false;
                    } else {
                        processedChanges[key] = value;
                    }
                }
                let error_msj = this.validate_fields(processedChanges);
                if (error_msj) {
                    return this.showPopup('ErrorPopup', {
                        title: this.env._t('Error Save Changes'),
                        body: error_msj,
                    })
                }
                processedChanges.id = this.props.partner.id || false;
                this.trigger('save-changes', { processedChanges });
            }

            validate_fields(processedChanges) {
                let error_msj = false
                if ((!this.props.partner.name && !processedChanges.name) || processedChanges.name === '') {
                    error_msj = this.env._t('A Customer Name Is Required')
                }
                if (processedChanges.l10n_latam_identification_type_id === '') {
                    error_msj = this.env._t('The "Document Type" field is empty')
                }
                if (processedChanges.vat === '') {
                    error_msj = this.env._t('The "Document N°" field is empty')
                }
                return error_msj
            }

        };

    Registries.Component.extend(PartnerDetailsEdit, DocumentTypeOnPosPartnerDetailsEdit);
    return PartnerDetailsEdit;
});
