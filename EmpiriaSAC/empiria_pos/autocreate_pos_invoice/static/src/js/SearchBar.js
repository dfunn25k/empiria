odoo.define('autocreate_pos_invoice.SearchBar', function (require) {
    'use strict';

    const SearchBar = require('point_of_sale.SearchBar');
    const Registries = require('point_of_sale.Registries');
    const { onMounted } = owl;

    const PosSearchBar = SearchBar =>
        class PosSearchBar extends SearchBar {
            setup() {
                super.setup();
                onMounted(this.onMounted);
            }
            onMounted() {
                this.state.searchInput = ''
            }
        }

    Registries.Component.extend(SearchBar, PosSearchBar);
    return SearchBar;
});