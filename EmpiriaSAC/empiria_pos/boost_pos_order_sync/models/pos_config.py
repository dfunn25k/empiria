from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PosConfig(models.Model):
    _inherit = 'pos.config'

    quotation_print_type = fields.Selection(
        selection=[('pdf', 'Browser based (PDF Report)'),
                   ('posbox', 'POSBOX (XML Report)')],
        default='pdf',
        required=True,
        string='Quotation print type'
    )
    send_orders_ids = fields.Many2many(
        comodel_name='pos.config',
        relation='send_orders_ids_rel_pos_config',
        column1='picking_type_id',
        column2='id',
        string='Send orders to',
    )

    @api.constrains('quotation_print_type', 'iface_print_via_proxy')
    def _check_hardware_connection(self):
        for config in self:
            if config.quotation_print_type == 'posbox' and not config.iface_print_via_proxy:
                raise UserError(
                    _("You can not print XML receipt. Please check receipt printer in Hardware Proxy/PosBox"))
