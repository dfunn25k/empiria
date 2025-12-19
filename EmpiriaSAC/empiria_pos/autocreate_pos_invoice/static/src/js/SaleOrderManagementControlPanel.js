odoo.define('autocreate_pos_invoice.SaleOrderManagementControlPanel', function (require) {
    'use strict';

    const SaleOrderManagementControlPanel = require('pos_sale.SaleOrderManagementControlPanel');
    const SaleOrderFetcher = require('pos_sale.SaleOrderFetcher');
    const Registries = require('point_of_sale.Registries');
    const { onMounted } = owl;

    const PosSaleOrderManagementControlPanel = SaleOrderManagementControlPanel =>
        class PosSaleOrderManagementControlPanel extends SaleOrderManagementControlPanel {
            setup() {
                super.setup();
                onMounted(this.onMounted);
            }
            onMounted() {
                this.orderManagementContext.searchString = '';
                SaleOrderFetcher.setSearchDomain(this._computeDomain());
            }
        }

    Registries.Component.extend(SaleOrderManagementControlPanel, PosSaleOrderManagementControlPanel);
    return SaleOrderManagementControlPanel;
});
