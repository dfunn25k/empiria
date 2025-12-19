odoo.define('document_type_on_pos.PosModelGlobalState', function (require) {
    "use strict";

    var { PosGlobalState } = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');

    const DocumentTypeOnPosModelGlobalState = PosGlobalState =>
        class DocumentTypeOnPosModelGlobalState extends PosGlobalState {

            async _processData(loadedData) {
                await super._processData(loadedData);
                this.documents_by_id = loadedData['documents_by_id'];
            }
        }
    
    Registries.Model.extend(PosGlobalState, DocumentTypeOnPosModelGlobalState);
});
