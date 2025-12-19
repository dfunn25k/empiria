from odoo import api, fields, models,tools, _

class PosConfigInherit(models.Model):
    _inherit = 'pos.config'

    customer_name_custom_title = fields.Char('Customer Name')
    customer_address_custom_title = fields.Char('Customer Address')
    customer_mobile_custom_title = fields.Char('Customer Mobile')
    customer_phone_custom_title = fields.Char('Customer Phone')
    customer_email_custom_title = fields.Char('Customer Email')
    customer_vat_custom_title = fields.Char('Customer Vat')
    
    font_size = fields.Float(digits=(10, 2), default=12)
    bold_format = fields.Boolean()


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    customer_name_custom_title = fields.Char(related='pos_config_id.customer_name_custom_title',readonly=False)
    customer_address_custom_title = fields.Char(related='pos_config_id.customer_address_custom_title',readonly=False)
    customer_mobile_custom_title = fields.Char(related='pos_config_id.customer_mobile_custom_title',readonly=False)
    customer_phone_custom_title = fields.Char(related='pos_config_id.customer_phone_custom_title',readonly=False)
    customer_email_custom_title = fields.Char(related='pos_config_id.customer_email_custom_title',readonly=False)
    customer_vat_custom_title = fields.Char(related='pos_config_id.customer_vat_custom_title',readonly=False)
    
    font_size = fields.Float(related='pos_config_id.font_size', readonly=False)
    bold_format = fields.Boolean(related='pos_config_id.bold_format', readonly=False)