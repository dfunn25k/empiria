from odoo import _, fields, models
import requests
import json
from json.decoder import JSONDecodeError
from datetime import datetime


class StockPicking(models.Model):
    _inherit = "stock.picking"

    sync_status_picking = fields.Selection(
        selection=[
            ('normal', 'No Informar'),
            ('done', 'Sincronizado a Intralot'),
            ('blocked', 'No Sincronizado'),
        ],
        string='Sync status',
        default='blocked',
        tracking=True,
        copy=False
    )
    message_api_intra = fields.Char()
    message_api_intra_exactivo = fields.Char()
    test_environment = fields.Boolean()

    def no_report_stock_picking(self):
        for rec in self:
            if rec.sync_status_picking == 'blocked':
                rec.sync_status_picking = 'normal'

    def action_sync_tinka_stock_picking(self):
        """Save Movement with api and change the status sync"""
        company = self.env.company
        test_environment = company.test_environment
        config_settings = self.env['res.config.settings'].create({})
        config_settings.test_environment = test_environment
        token = config_settings.action_api_intralot()
        if test_environment:
            if self.env.company.url_provider_test_intralot:
                url = company.url_provider_test_intralot + '/asset/savemovementv2'
        else:
            if self.env.company.url_provider_prod_intralot:
                url = company.url_provider_prod_intralot + '/asset/savemovementv2'
        for rec in self:
            if rec.sync_status_picking not in ['normal', 'done'] and rec.state == 'done':
                actives = {}
                index=0
                for line in rec.move_line_ids_without_package:
                    if line and line.product_id.intralot and line.location_id.intralot and line.location_dest_id.intralot:
                        if line.lot_id:
                            code_active = line.lot_id.name.split('/')[0] if '/' in line.lot_id.name else ''
                            code_active = code_active.replace(" ", "")
                            code_active = code_active.replace('\t', '')
                            code_origin = rec.find_between(line.location_id.name, '[', ']')
                            code_destiny = rec.find_between(line.location_dest_id.name, '[', ']')
                            actives[index] = {
                                "codigoorigen": code_origin,
                                "codigodestino": code_destiny,
                                "codigoactivo": code_active,
                                "estadoactivo": line.status.code,
                            }
                            index += 1 
                if actives:
                    data = {
                        "token": token,
                        "numerotransaccion":rec.name,
                        "fechaenvio": rec.scheduled_date.strftime("%Y-%m-%d %H:%M:%S"),
                        "activos": actives
                    }
                    response = requests.post(url, data=json.dumps(data))
                    response = response.content

                    msg2=''
                    try:
                        response = json.loads(response)
                        msg = response.get('mensaje')
                        msg2 = response.get('mensajexactivo')
                        err = False
                    except JSONDecodeError:
                        msg = str(response)
                        err = True

                    message = _(f'Guardar Movimiento - Mensaje: {msg}, MensajexActivo: {msg2}')

                    self.env['mail.message'].sudo().create({
                        'model': self._name,
                        'res_id': rec.id,
                        'body': message,
                        'message_type': 'notification',
                        'author_id': self.env.ref('base.partner_root').id,
                    })
                    rec.message_api_intra= msg
                    rec.message_api_intra_exactivo=msg2
                    
                    if not err and response.get('mensaje') == "OK":
                        self.sync_status_picking = 'done'
                    else:
                        template_id = self.env.ref('intra_inventory_api_pe.mail_template_intralot_sync_stock_picking').id
                        rec.env['mail.template'].browse(template_id).send_mail(rec.id, force_send=True)

    def button_validate(self):
        res = super(StockPicking, self).button_validate()
        company = self.env.company
        if company.intralot:
            self.action_sync_tinka_stock_picking()
            return res
        else:
            return res
    
    def get_emails(self, follower_ids):
        email_ids = ''
        for user in follower_ids:
            if email_ids:
                email_ids = email_ids + ',' + str(user.sudo().partner_id.email)
            else:
                email_ids = str(user.sudo().partner_id.email)
        return email_ids

    @staticmethod
    def find_between(string, first, last):
        """Find a string between a two characters"""
        try:
            start = string.index(first) + len(first)
            end = string.index(last, start)
            return string[start:end]
        except ValueError:
            return ""
