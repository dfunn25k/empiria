odoo.define('pos_combo_reload.SelectionComboProductList', function (require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');

    class SelectionComboProductList extends PosComponent { }

    SelectionComboProductList.template = 'SelectionComboProductList';
    Registries.Component.add(SelectionComboProductList);
    return SelectionComboProductList;
});