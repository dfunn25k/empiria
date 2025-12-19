odoo.define('pos_employee_access_premium.Chrome', function (require) {
    'use strict';

    const Chrome = require('point_of_sale.Chrome');
    const Registries = require('point_of_sale.Registries');

    const PosChrome = Chrome =>
        class PosChrome extends Chrome {
            // overriding get method
            get headerButtonIsShown() {
                return true;
            }
        };
    Registries.Component.extend(Chrome, PosChrome);
    return Chrome;
});
