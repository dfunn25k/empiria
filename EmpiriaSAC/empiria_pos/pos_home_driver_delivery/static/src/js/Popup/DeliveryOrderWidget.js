odoo.define('pos_home_driver_delivery.DeliveryOrderWidget', function(require) {
	'use strict';

	const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
	const Registries = require('point_of_sale.Registries');
    const { _lt } = require('@web/core/l10n/translation');
	const { onMounted } = owl;

	class DeliveryOrderWidget extends AbstractAwaitablePopup {

		setup() {
			super.setup();
			this.name = this.name;
			this.mobile = this.mobile;
			this.email = this.email;
			this.address = this.address;
			this.street = this.street;
			this.city = this.city;
			this.zip = this.zip;
			this.person_id = this.person_id;
			this.order_note = this.order_note;
			this.delivery_date = this.delivery_date;
			onMounted(this.onMounted);
		};

		onMounted() {
			$('#dell_date').datetimepicker({
				format: 'YYYY-MM-DD HH:mm:ss',
				inline: true,
				sideBySide: true
			});
			$('.delivery-detail').hide();
			$('#delivery_date').hide();
			$('#street').hide();
			$('#zip').hide();
			$('#mobile').hide();
			$('#d_name').hide();
			$('#city').hide();
			$('#address').hide();
			$('#delivery_person').hide();
			$('#dd_date').hide();
			$('#form1,#apply_shipping_address').click(function() {
				if ($('#apply_shipping_address').is(':checked')) {
					$('#apply_shipping_address').prop('checked', false);
				}
				else{
					$('#apply_shipping_address').prop('checked', true);
				}
				if ($('#apply_shipping_address').is(':checked')) {
					$('.delivery-detail').show();
					$('#default').hide()
				} else {
					$('.delivery-detail').hide();
					$('#default').show()
					$('#delivery_date').hide();
					$('#street').hide();
					$('#zip').hide();
					$('#mobile').hide();
					$('#d_name').hide();
					$('#city').hide();
					$('#address').hide();
					$('#delivery_person').hide();
					$('#dd_date').hide();
				}
			});
		};

        //@override
        async create() {
			let self = this;
			let order = this.env.pos.get_order();
			let order_lines = self.get_orderline_data()
			let rpc1 = false;
			if(order_lines.length > 0){
				let fields = {};
				$('.detail').each(function(idx, el){
					fields[el.name] = el.value || false;
				})
				if(!fields.delivery_date){
					$('#dd_date').show()
					setTimeout(function() {$('#dd_date').hide()},3000);
					$('#tab2').prop('checked', true);
					return
				}
				order.set_delivery_data(fields);
				let ddd = moment(fields.delivery_date,"YYYY-MM-DD HH:mm").toISOString();
				let d_date = new Date(ddd);
				fields.delivery_date = d_date.toISOString();
				let partner = order.get_partner();
				let order_date = new Date().toISOString();
				let order_data = {
					'order_no' : order.name || order.uid || false,
					'session_id': order.pos.pos_session.id || order.pos_session_id,
					'order_date': order_date || false,
					'cashier_id' : order.pos.user.id || false,
				}
				let orderlines = self.get_orderline_data();
				let notes = $('.order_note').val();
				let delivery_person = $('.person_id').val(); 
				let other_addrs = $("#apply_shipping_address").is(':checked') ? 1 : 0;
				let result = {
					'form_data': fields,
					'order_data': order_data,
					'line_data' : order_lines,
					'partner': partner,
					'other_addrs' : other_addrs,
				}
				let date_delivery = $('#my_date').val();
				let dd_date = new Date(date_delivery);
				date_delivery = dd_date.toISOString();
				if ($('#apply_shipping_address').is(':checked')) {
					if(fields.d_name == false){
						$('#apply_shipping_address').prop('checked', true);
						$('.delivery-detail').show();
						$('#default').hide()
						$('#d_name').show()
						setTimeout(function() {$('#d_name').hide()},3000);
						$('#tab1').prop('checked', true);
						return
					}
					else if(fields.mobile == false){
						$('.delivery-detail').show();
						$('#mobile').show()
						setTimeout(function() {$('#mobile').hide()},3000);
						$('#default').hide()
						$('#tab1').prop('checked', true);
						return
					}
					else if(fields.address == false){
						$('.delivery-detail').show();
						$('#address').show()
						setTimeout(function() {$('#address').hide()},3000);
						$('#default').hide()
						$('#tab1').prop('checked', true);
						return
					}
					else if(fields.street == false){
						$('.delivery-detail').show();
						$('#street').show()
						setTimeout(function() {$('#street').hide()},3000);
						$('#default').hide()
						$('#tab1').prop('checked', true);
						return
					}
					else if(fields.city == false){
						$('.delivery-detail').show();
						$('#city').show()
						setTimeout(function() {$('#city').hide()},3000);
						$('#default').hide()
						$('#tab1').prop('checked', true);
						return
					}
					else if(fields.zip == false){
						$('.delivery-detail').show();
						$('#zip').show()
						setTimeout(function() {$('#zip').hide()},3000);
						$('#default').hide()
						$('#tab1').prop('checked', true);
						return
					}
					else if(fields.delivery_date == false){
						$('.delivery-detail').show();
						$('#delivery_date').show()
						setTimeout(function() {$('#delivery_date').hide()},3000);
						$('#default').hide()
						$('#tab2').prop('checked', true);
						return
					}
					else if(fields.person_id == false){
						$('.delivery-detail').show();
						$('#delivery_person').show()
						$('#default').hide()
						setTimeout(function() {$('#delivery_person').hide()},3000);
						$('#tab2').prop('checked', true);
						return
					}
					else{
						rpc1 = this.rpc({
							model: 'pos.delivery.order',
							method: 'delivery_order_from_ui',
							args: [result],
						})
						.then(function(data){
							fields={};
							order.set_delivery_status(true);
							if (order.delivery){
								self.showPopup('DeliverySuccessfully',{});
							}
							return data;
						},function(err,event){
							event.preventDefault();
							self.showPopup('ErrorPopup',{
								'title': _lt('Delivery Order not Created'),
								'body': _lt('Please fill your details properly.'),
							});
							return false;
						});
					}
				} 
				else {
					if(fields.person_id == false){
						$('#delivery_person').show()
						setTimeout(function() {$('#delivery_person').hide()},3000);
						$('#tab2').prop('checked', true);
						return
					}
					else if(fields.delivery_date == false){
						$('#delivery_date').show()
						setTimeout(function() {$('#delivery_date').hide()},3000);
						$('#tab2').prop('checked', true);
						return
					}
					else{
						order.set_delivery_data({
							address: "",
							city: "",
							d_name: "",
							delivery_date: fields.delivery_date,
							email: "",
							mobile: "",
							order_note: fields.order_note,
							person_id: fields.person_id,
							street: "",
							zip: ""
						});
						rpc1 = this.rpc({
							model: 'pos.delivery.order',
							method: 'delivery_order_from_ui_with_partner',
							args: [ partner, order_data, orderlines, date_delivery, notes, delivery_person ],
						})
						.then(function(data){
							fields={};
							order.set_delivery_status(true);
							if (order.delivery){
								self.showPopup('DeliverySuccessfully',{});
							}
							return data;
						},function(err,event){
							event.preventDefault();
							self.showPopup('ErrorPopup',{
								'title': _lt('Delivery Order not Created'),
								'body': _lt('Please fill your details properly.'),
							});
							return false;
						});
					}   
				}
				if(!delivery_person){
					self.showPopup('DeliveryOrderWidget',{});
					$('#delivery_person').show()
					$('.delivery-detail').show();
					$('#default').hide()
					$('#tab2').prop('checked', true);
					return
				}
			}

			$.when(rpc1).done(function() {
				self.props.resolve({ confirmed: true, payload: null });
				self.cancel()
			})
        }

		get_orderline_data() {
			let order = this.env.pos.get_order();
			let orderlines = order.orderlines;
			let all_lines = [];
			for (let i = 0; i < orderlines.length; i++) {
				let line = orderlines[i]
				if (line && line.product && line.quantity !== undefined) {
					all_lines.push({
						'product_id': line.product.id,
						'qty': line.quantity,
						'price': line.get_display_price(),
						'note': line.get_note(),
					})
				}
			}
			return all_lines
		}

		clear() {
			$('.detail').val('');
			$('.d_name').focus();
		}
		
	}

	DeliveryOrderWidget.template = 'DeliveryOrderWidget';
	DeliveryOrderWidget.defaultProps = {
		confirmText: _lt('Create'),
		cancelText: _lt('Cancel'),
		clearText: _lt('Clear'),
		title: _lt('Home Delivery Order'),
		body: ''
	};

	Registries.Component.add(DeliveryOrderWidget);
	return DeliveryOrderWidget;
});
