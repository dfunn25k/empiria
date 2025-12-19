odoo.define('pos_home_driver_delivery.models', function (require) {
	"use strict";

	var { Order, PosGlobalState } = require('point_of_sale.models');
	const Registries = require('point_of_sale.Registries');

    const PosModelPosGlobalState = PosGlobalState => 
		class PosModelPosGlobalState extends PosGlobalState {
    
			async _processData(loadedData) {
				this.users_total_by_id = loadedData['users_total_by_id'];
				await super._processData(loadedData);
			}
    	}

    Registries.Model.extend(PosGlobalState, PosModelPosGlobalState);

    const PosOrder = Order =>
		class PosOrder extends Order {

        init_from_JSON(json) {
            super.init_from_JSON(json);
			this.d_name = json.d_name || "";
			this.mobile = json.mobile || "";
			this.email = json.email || "";
			this.address = json.address || "";
			this.street = json.street || "";
			this.city = json.city || "";
			this.zip = json.zip || "";
			this.delivery_date = json.delivery_date || "";
			this.person_id = json.person_id || "";
			this.order_note = json.order_note || "";
			this.set_delivery_data(json);
			this.delivery = json.delivery || false;
        }

		set_delivery_data(fields){
			this.d_name = fields.d_name;
			this.mobile = fields.mobile;
			this.email = fields.email;
			this.address = fields.address;
			this.street = fields.street;
			this.city = fields.city;
			this.zip = fields.zip || "";
			this.delivery_date = fields.delivery_date;
			this.person_id = fields.person_id;
			this.order_note = fields.order_note;
			//this.trigger('change',this);
		}

		set_delivery_status(delivery) {
			this.delivery = delivery;
			//this.trigger('change',this);
		}

		get_delivery_status(delivery) {
			return this.delivery;
		}

		get_div_name(d_name) {
			return this.d_name;
		}

		get_div_email(email) {
			return this.email;
		}

		get_div_mobile(mobile) {
			return this.mobile;
		}

		get_div_location(address) {
			return this.address;
		}

		get_div_street(street) {
			return this.street;
		}

		get_div_city(city) {
			return this.city;
		}

		get_div_zip(zip) {
			return this.zip;
		}

		get_delivery_date(delivery_date) {
			return this.delivery_date;
		}

		get_div_person(person_id) {
			return this.person_id;
		}

		get_div_note(order_note) {
			return this.order_note;
		}
    
        export_as_JSON() {
            const json = super.export_as_JSON();
			json.d_name = this.get_div_name();
			json.email = this.get_div_email();
			json.mobile = this.get_div_mobile();
			json.address = this.get_div_location();
			json.street = this.get_div_street();
			json.city = this.get_div_city();
			json.zip = this.get_div_zip();
			json.delivery_date = this.get_delivery_date();
			json.person_id = this.get_div_person();
			json.order_note = this.get_div_note();
			json.delivery = this.get_delivery_status();
			return json;
        }

        export_for_printing(){
            const receipt = super.export_for_printing();
            receipt.reference_rectified = this.reference_rectified ? this.reference_rectified : false;
            receipt.date_rectified = this.date_rectified ? this.date_rectified : false;
            receipt.invoice_reference_type_l10n_latam_document_type_ids = this.invoice_reference_type_l10n_latam_document_type_ids ? this.invoice_reference_type_l10n_latam_document_type_ids : false;
            receipt.ticket_reference_type_l10n_latam_document_type_ids = this.ticket_reference_type_l10n_latam_document_type_ids ? this.ticket_reference_type_l10n_latam_document_type_ids : false;
            return receipt;
        }

    }

    Registries.Model.extend(Order, PosOrder);
});
