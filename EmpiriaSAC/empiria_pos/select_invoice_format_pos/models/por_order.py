import base64

from odoo import api, models

import logging

_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    _inherit = 'pos.order'

    @api.model
    def generate_dynamic_report_from_account_move_pos_ui(self, account_move_id, ir_report_id):
        values = {
            'error': False,
            'report': False
        }
        try:
            ids_to_print = [account_move_id]
            report_id = self.env['ir.actions.report'].browse(ir_report_id)
            if not ids_to_print or not report_id:
                values['error'] = True
            else:
                report = report_id._render_qweb_pdf(report_id.get_external_id()[ir_report_id], ids_to_print)
                values['report'] = base64.b64encode(report[0])
        except Exception as error:
            values['error'] = True
            _logger.warning(error)
        return values

    @api.model
    def generate_dynamic_report_from_pos_ui(self, pos_reference, ir_report_id):
        order_id = self.search([('pos_reference', '=', pos_reference)], limit=1)
        values = self.generate_dynamic_report_from_account_move_pos_ui(order_id.account_move.id, ir_report_id)
        return values
