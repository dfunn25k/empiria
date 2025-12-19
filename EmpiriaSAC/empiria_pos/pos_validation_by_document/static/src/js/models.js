odoo.define('pos_validation_by_document.models', function (require) {
    'use strict';

    var { PosGlobalState } = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');

    const PosModelGlobalState = (PosGlobalState) =>
        class PosModelGlobalState extends PosGlobalState {
            async _processData(loadedData) {
                await super._processData(loadedData);
                this.documents_identification_ids = loadedData['l10n_latam.identification.type'];
            }
        }

    Registries.Model.extend(PosGlobalState, PosModelGlobalState);
});