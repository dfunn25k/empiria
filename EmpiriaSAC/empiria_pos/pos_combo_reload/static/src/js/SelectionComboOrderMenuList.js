odoo.define('pos_combo_reload.SelectionComboOrderMenuList', function (require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');

    class SelectionComboOrderMenuList extends PosComponent { }

    SelectionComboOrderMenuList.template = 'SelectionComboOrderMenuList';
    Registries.Component.add(SelectionComboOrderMenuList);
    return SelectionComboOrderMenuList;
});