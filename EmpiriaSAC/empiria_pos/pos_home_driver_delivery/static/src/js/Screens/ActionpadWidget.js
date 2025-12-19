odoo.define('pos_home_driver_delivery.ActionpadWidget', function(require) {
	"use strict";

	const Registries = require('point_of_sale.Registries');
	const ProductScreen = require('point_of_sale.ProductScreen');

	const PosProductScreen = ProductScreen =>
		class PosProductScreen extends ProductScreen {

			async _clickProduct(event) { 
				var delivery = this.env.pos.get_order().delivery;
				if(delivery == false){
					super._clickProduct(event);
				}else{
					this.showPopup('ErrorPopup', {
						'title': this.env._t('Add New Product'),
						'body': this.env._t('This order already create home delivery , you can not add new product.'),
					});
				}
			}
	}

	// this was not called, check later
    //Registries.Component.extend(ProductScreen, PosProductScreen);
    //return ProductScreen;
});