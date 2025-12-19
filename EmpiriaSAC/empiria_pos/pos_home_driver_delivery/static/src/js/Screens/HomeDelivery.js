odoo.define('pos_home_driver_delivery.HomeDelivery', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const Registries = require('point_of_sale.Registries');
    const { useListener } = require("@web/core/utils/hooks");

	
    class HomeDelivery extends PosComponent {
        
		setup() {
            super.setup();
            useListener('click', this.onClick);
        }
		
        async onClick() {
            var self = this;
			var order = this.env.pos.get_order();

			var partner_id = false
			if (order.get_partner() != null)
				partner_id = order.get_partner();

			if (!partner_id) {
				self.showPopup('ErrorPopup', {
					'title': this.env._t('Unknown customer'),
					'body': this.env._t('You cannot use Home Delivery. Select customer first.'),
				});
				return;
			}       

			var orderlines = order.orderlines;
			if(orderlines.length < 1){
				self.showPopup('ErrorPopup',{
					'title': this.env._t('Empty Order !'),
					'body': this.env._t('Please select some products'),
				});
				return false;
			}
			
			self.showPopup('DeliveryOrderWidget', {
				'title': this.env._t('Home Delivery Order'),
				'name' : order.get_div_name(),
				'email' : order.get_div_email(),
				'mobile' : order.get_div_mobile(),
				'address' : order.get_div_location(),
				'street' : order.get_div_street(),
				'city' : order.get_div_city(),
				'zip' : order.get_div_zip(),
				'delivery_date' : order.get_delivery_date(),
				'person_id' : order.get_div_person(),
				'order_note' : order.get_div_note(),
			})
        }
    }

    HomeDelivery.template = 'HomeDelivery';
    ProductScreen.addControlButton({
        component: HomeDelivery,
        condition: function() {
            return this.env.pos.config.verify_delivery;
        },
    });

    Registries.Component.add(HomeDelivery);
    return HomeDelivery;
});
