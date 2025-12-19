from odoo import http
import logging
import odoo

_logger = logging.getLogger(__name__)


class AutoUpdateModules(http.Controller):

    @http.route('/update/modules', type='json', auth="public")
    def execute_auto_update_modules(self, db, master_pwd):
        response_body = {}
        try:
            # http.request.session.db = db
            _logger.info('Validando master password...')
            # odoo.service.db.check_super(master_pwd)
            http.request.env['ir.module.module'].sudo().upgrade_changed_checksum()
            response_body['status'] = 'ok'
        except Exception as error_description:
            # http.request.session.db = False
            response_body['status'] = f'Error en la actualización: {error_description}'
        _logger.info('Auto update module response: ', response_body)
        return response_body
