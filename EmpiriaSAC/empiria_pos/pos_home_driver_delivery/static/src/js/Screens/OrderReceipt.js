odoo.define('pos_home_driver_delivery.BiOrderReceipt', function(require) {
	"use strict";

	const OrderReceipt = require('point_of_sale.OrderReceipt');
	const Registries = require('point_of_sale.Registries');

	const PosOrderReceipt = OrderReceipt => 
		class PosOrderReceipt extends OrderReceipt {

			get deliveryPerson(){
				let order = this.env.pos.get_order();
				let deliveryPerson = '';
				for (let i = 0; i < this.env.pos.users_total_by_id.length; i++) {
					if(this.env.pos.users_total_by_id[i].id == order.person_id){
						deliveryPerson =  this.env.pos.users_total_by_id[i].name;
						break;
					}
				}
				return deliveryPerson;
			}
			
			get hddate(){
				let order = this.env.pos.get_order();
				let dt = new Date(order.delivery_date).toLocaleString();
				return dt;
			}
		}

	Registries.Component.extend(OrderReceipt, PosOrderReceipt);
	return OrderReceipt;
});