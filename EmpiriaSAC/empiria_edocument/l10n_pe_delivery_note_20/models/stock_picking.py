import base64
import hashlib
import json
import urllib.parse
from json.decoder import JSONDecodeError

import requests
from markupsafe import Markup
from lxml import etree
from lxml import objectify

from odoo import _, _lt, fields, models, api
from odoo.exceptions import UserError


DEFAULT_PE_DATE_FORMAT = '%Y-%m-%d'
PE_TRANSFER_REASONS = [
    ('01', 'Sale'),
    ('02', 'Compra'),
    ('03', 'Sale with delivery to third parties'),
    ('04', 'Transfer between establishments of the same company'),
    ('05', 'Consignment'),
    ('06', 'Devolución'),
    ('07', 'Recojo de bienes transformados'),
    ('08', 'Importación'),
    ('09', 'Exportación'),
    ('13', 'Others'),
    ('14', "Sale subject to buyer's confirmation"),
    ('17', 'Transfer of goods for transformation'),
    ('18', 'Itinerant issuer transfer CP'),
    ('19', 'Transfer to primary zone (deprecated)'),  # TODO master: remove
]

ERROR_MESSAGES = {
    "request": _lt("There was an error communicating with the SUNAT service.") + " " + _lt("Details:"),
    "json_decode": _lt("Could not decode the response received from SUNAT.") + " " + _lt("Details:"),
    "unzip": _lt("Could not decompress the ZIP file received from SUNAT."),
    "processing": _lt("The delivery guide is being processed by SUNAT. Click on 'Retry' to refresh the state."),
    "duplicate": _lt("A delivery guide with this number is already registered with SUNAT. Click on 'Retry' to try sending with a new number."),
    "response_code": _lt("SUNAT returned an error code.") + " " + _lt("Details:"),
    "response_unknown": _lt("Could not identify content in the response retrieved from SUNAT.") + " " + _lt("Details:"),
}


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    sunat_sequence = fields.Selection(
        selection='get_prefix', 
        string='Guia Electronica'
    )

    sunat_sequence_id = fields.Many2one(
        'ir.sequence', 
        string='Guia Electronica',
        domain=lambda self: [('code', '=', 'l10n_pe_edi_stock.stock_picking_sunat_sequence'),
                            ('company_id', '=', self.env.company.id)],
        check_company=True,
    )

    l10n_pe_edi_reason_for_transfer = fields.Selection(
        selection_add=[
            ('02', 'Compra'),
            ('06', 'Devolución'),
            ('07', 'Recojo de bienes transformados'),
            ('08', 'Importación'),
            ('09', 'Exportación')
        ]
    )
    l10n_pe_edi_handling_instructions = fields.Char(
        string='Descripción del motivo de traslado por otros'
    )
    l10n_pe_edi_scheduled_transfer = fields.Boolean(
        string='Indicador de transbordo programado'
    )
    
    @api.onchange('l10n_pe_edi_reason_for_transfer')
    def _onchange_l10n_pe_edi_reason_for_transfer(self):
        if not self.l10n_pe_edi_reason_for_transfer == '13':
            self.l10n_pe_edi_handling_instructions = False

    def get_prefix(self):
        return [(key, key) for key in self.env['ir.sequence'].search([('code', '=', 'l10n_pe_edi_stock.stock_picking_sunat_sequence'),
                                                                      ('company_id.id', '=', self.env.company.id)]).mapped('prefix')]
    @api.model
    def _migrate_sunat_sequence_to_sunat_sequence_id(self):
        pickings_with_sunat_sequence = self.search([('sunat_sequence', '!=', False)])
        for picking in pickings_with_sunat_sequence:
            picking.sunat_sequence_id = self.env['ir.sequence'].search([
                ('prefix', '=', picking.sunat_sequence),
                ('company_id', '=', picking.company_id.id)
            ], limit=1).id
    
    def action_send_delivery_guide(self):
        """Make the validations required to generate the EDI document, generates the XML, and sent to sign in the
        SUNAT"""
        self._check_company()
        self._l10n_pe_edi_check_required_data()
        for record in self:
            if not record.sunat_sequence_id:
                raise UserError(
                    _('Debe asignar una serie a su guía electrónica. '))

            if record.picking_type_id.code in ['internal', 'incoming']:
                if not record.location_dest_id.direction_id:
                    raise UserError(
                        _('No se enviará la GRE hasta que no se configure el campo “dirección” dentro de la ubicación de stock. Debe colocar la dirección del almacén para que pueda enviar la GRE.'))
            if record.picking_type_id.code in ['internal', 'outgoing']:
                if not record.location_id.direction_id:
                    raise UserError(
                        _('No se enviará la GRE hasta que no se configure el campo “dirección” dentro de la ubicación de stock. Debe colocar la dirección del almacén para que pueda enviar la GRE.'))

            if not record.l10n_latam_document_number:
                sunat_sequence = self.env['ir.sequence'].search([
                    ('code', '=', 'l10n_pe_edi_stock.stock_picking_sunat_sequence'),
                    ('prefix', '=', record.sunat_sequence_id.prefix),
                    ('company_id', '=', record.company_id.id)], limit=1)
                if not sunat_sequence:
                    sunat_sequence = self.env['ir.sequence'].sudo().create({
                        'name': 'Stock Picking Sunat Sequence %s' % record.company_id.name,
                        'code': 'l10n_pe_edi_stock.stock_picking_sunat_sequence',
                        'padding': 8,
                        'company_id': record.company_id.id,
                        'prefix': 'T001-',
                        'number_next': 1,
                    })
                record.l10n_latam_document_number = sunat_sequence.next_by_id()
            edi_filename = '%s-09-%s' % (
                record.company_id.vat,
                (record.l10n_latam_document_number or '').replace(' ', ''),
            )
            edi_str = self._l10n_pe_edi_create_delivery_guide()
            
            # Digital signature
            edi_tree = objectify.fromstring(edi_str)
            edi_tree = record.company_id.l10n_pe_edi_certificate_id.sudo()._sign(edi_tree)
            edi_str = etree.tostring(edi_tree, xml_declaration=True, encoding='ISO-8859-1')
            
            res = record._l10n_pe_edi_sign(edi_filename, edi_str)

            # == Create the attachments with error ==
            if 'error' in res:
                if res.get("error_reason") != "processing":
                    zip_edi_str = self.env['account.edi.format']._l10n_pe_edi_zip_edi_document([('%s.xml' % edi_filename, edi_str)])
                    attachment_id = self.env['ir.attachment'].create({
                        'res_model': record._name,
                        'res_id': record.id,
                        'type': 'binary',
                        'name': '%s.zip' % edi_filename,
                        'datas': base64.encodebytes(zip_edi_str),
                        'mimetype': 'application/zip'
                    })
                    message = _("El documento EDI tiene un formato incorrecto, revisar el ZIP")
                    record.with_context(no_new_invoice=True).message_post(
                        body=message,
                        attachment_ids=[attachment_id.id],
                    )
                record.l10n_pe_edi_error = res['error']
                continue

            # == Create the attachments ==
            if res.get('xml_document'):
                record._l10n_pe_edi_decode_cdr(edi_filename, res['xml_document'])
            if res.get('cdr'):
                res_attachment = self.env['ir.attachment'].create({
                    'res_model': record._name,
                    'res_id': record.id,
                    'type': 'binary',
                    'name': 'cdr-%s.xml' % edi_filename,
                    'raw': res['cdr'],
                    'mimetype': 'application/xml',
                })
            else:
                continue
            message = _("El documento EDI fue creado y firmado correctamente por la SUNAT.")
            record._message_log(body=message, attachment_ids=res_attachment.ids)
            record.write({'l10n_pe_edi_error': False, 'l10n_pe_edi_status': 'sent'})

    def _l10n_pe_edi_get_delivery_guide_values(self):
        # OVERRIDE
        result = super()._l10n_pe_edi_get_delivery_guide_values()
        result.update({
            'reason_for_transfer': dict(PE_TRANSFER_REASONS)[self.l10n_pe_edi_reason_for_transfer] if not self.l10n_pe_edi_handling_instructions else self.l10n_pe_edi_handling_instructions,
        })
        return result

    def _l10n_pe_edi_get_sunat_guia_credentials(self):
        company = self.company_id.sudo()
        if company.l10n_pe_edi_delivery_test_env:
            return {
                "access_id": "test-85e5b0ae-255c-4891-a595-0b98c65c9854",
                "access_key": "test-Hty/M6QshYvPgItX2P0+Kw==",
                "client_id": "{}MODDATOS".format(company.vat),
                "password": "MODDATOS",
                "login_url": "https://gre-test.nubefact.com/v1/clientessol/%s/oauth2/token/",
            }
        else:
            return super()._l10n_pe_edi_get_sunat_guia_credentials()

    def _l10n_pe_edi_request_token(self, credentials):
        """ Request an authentication token from the SUNAT authentication service.
            The token can then be used in requests to the endpoints for sending the
            delivery guide and for requesting the CDR. """
        headers = {
            "Accept": "application/json",
        }
        data = {
            "grant_type": "password",
            # Change scope if the test environment is active
            "scope": "https://api-cpe.sunat.gob.pe/" if not self.company_id.l10n_pe_edi_delivery_test_env else "https://api-cpe.sunat.gob.pe",
            "client_id": credentials["access_id"],
            "client_secret": credentials["access_key"],
            "username": credentials["client_id"],
            "password": credentials["password"],
        }
        try:
            response = requests.post(credentials["login_url"] % urllib.parse.quote(credentials["access_id"], safe=''), data=data, headers=headers, timeout=20)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            return {"error": str(Markup("%s<br/>%s") % (ERROR_MESSAGES["request"], e))}

        try:
            response_json = response.json()
        except JSONDecodeError as e:
            return {"error": str(Markup("%s<br/>%s") % (ERROR_MESSAGES["json_decode"], e))}

        if "error" in response_json or "error_description" in response_json:
            error_msg = str(Markup("%s<br/>%s: %s") % (ERROR_MESSAGES["response_code "], response_json.get("error", ""), response_json.get("error_description", "")))
            return {"error": error_msg}
        if not response_json.get("access_token"):
            return {"error": str(Markup("%s<br/>%s") % (ERROR_MESSAGES["response_unknown"], response_json))}

        token = response_json["access_token"]
        return {"token": token}

    def _l10n_pe_edi_send_delivery_guide(self, edi_filename, edi_str, token):
        """ Send a delivery guide to SUNAT via the REST API.

            SUNAT provides a ticket number in its response, which can be used to
            retrieve the CDR once the SUNAT service has finished processing the
            delivery guide.

            :param edi_filename: the name of the XML file containing the delivery guide
            :param edi_str: the content of the XML file containing the delivery guide
            :param token: the SUNAT authentication token """
        self.ensure_one()
        headers = {
            'Authorization': "Bearer " + token,
            'Content-Type': "Application/json",
        }
        ruc = self.company_id.vat
        serie_folio = self._l10n_pe_edi_get_serie_folio()
        serie = serie_folio["serie"]
        folio = serie_folio["folio"]
        url = "https://api-cpe.sunat.gob.pe/v1/contribuyente/gem/comprobantes/%s-09-%s-%s" % (
            urllib.parse.quote(ruc, safe=''), urllib.parse.quote(serie, safe=''), urllib.parse.quote(folio, safe=''))
        # Change the url if the test environment is active
        if self.company_id.l10n_pe_edi_delivery_test_env:
            url = "https://gre-test.nubefact.com/v1/contribuyente/gem/comprobantes/%s-09-%s-%s" % (
                urllib.parse.quote(ruc, safe=''), urllib.parse.quote(serie, safe=''), urllib.parse.quote(folio, safe=''))
        zip_file = self._l10n_pe_edi_zip(edi_str, edi_filename)
        data = {
            "archivo": {
                "nomArchivo": "%s-09-%s-%s.zip" % (ruc, serie, folio),
                "arcGreZip": base64.b64encode(zip_file).decode(),
                "hashZip": hashlib.sha256(zip_file).hexdigest(),
            }
        }
        payload = json.dumps(data)
        try:
            response = requests.post(url, data=payload, headers=headers, verify=True, timeout=20)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            to_return = {"error": str(Markup("%s<br/>%s") % (ERROR_MESSAGES["request"], e))}
            if isinstance(e, requests.exceptions.HTTPError) and e.response.status_code == 401:
                to_return.update({"error_reason": "unauthorized"})
            return to_return
        try:
            response_json = response.json()
        except JSONDecodeError as e:
            return {"error": str(Markup("%s<br/>%s") % (ERROR_MESSAGES["json_decode"], e))}

        if isinstance(response_json.get("errors"), list) and len(response_json["errors"]) > 0 and isinstance(response_json["errors"][0], dict):
            code = response_json["errors"][0].get("cod", "")
            msg = response_json["errors"][0].get("msg", "")
            return {"error": str(Markup("%s<br/>%s: %s") % (ERROR_MESSAGES["response_code"], code, msg))}
        if not response_json.get("numTicket"):
            return {"error": str(Markup("%s<br/>%s") % (ERROR_MESSAGES["response_unknown"], response_json))}

        return {"ticket_number": response_json["numTicket"]}
    
    def _l10n_pe_edi_get_cdr(self, ticket_number, token):
        """ Retrieve the CDR (confirmation of receipt) for a delivery guide that was sent.

            :param ticket_number: the ticket number obtained when sending the delivery guide
            :param token: the SUNAT authentication token """
        headers = {
            'Authorization': "Bearer " + token,
            'Content-Type': "Application/json",
        }
        url = 'https://api-cpe.sunat.gob.pe/v1/contribuyente/gem/comprobantes/envios/%s' % urllib.parse.quote(ticket_number, safe='')
        # Change the url if the test environment is active
        if self.company_id.l10n_pe_edi_delivery_test_env:
            url = 'https://gre-test.nubefact.com/v1/contribuyente/gem/comprobantes/envios/%s' % urllib.parse.quote(ticket_number, safe='')
        try:
            response = requests.get(url, params={'numTicket': ticket_number}, headers=headers, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            to_return = {"error": str(Markup("%s<br/>%s") % (ERROR_MESSAGES["request"], e))}
            if isinstance(e, requests.exceptions.HTTPError) and e.response.status_code == 401:
                to_return.update({"error_reason": "unauthorized"})
            return to_return
        try:
            response_json = response.json()
        except JSONDecodeError as e:
            return {"error": str(Markup("%s<br/>%s") % (ERROR_MESSAGES["json_decode"], e))}

        if response_json.get("codRespuesta") == "98":
            error_msg = ERROR_MESSAGES["processing"]
            return {"error": error_msg, "error_reason": "processing"}
        if response_json.get("error"):
            code = response_json["error"].get("numError", "")
            msg = response_json["error"].get("desError", "")
            if code == "1033":
                error_msg = ERROR_MESSAGES["duplicate"]
                return {"error": error_msg, "error_reason": "duplicate"}
            else:
                return {"error": str(Markup("%s %s: %s") % (ERROR_MESSAGES["response_code"], code, msg)), "error_reason": "rejected"}
        if not response_json.get("arcCdr") or response_json.get("codRespuesta") != "0":
            if "codRespuesta" in response_json:
                return {"error": str(Markup("%s %s") % (ERROR_MESSAGES["request"], response_json["codRespuesta"])), "error_reason": "rejected"}
            else:
                return {"error": str(Markup("%s<br/>%s") % (ERROR_MESSAGES["response_unknown"], response_json))}

        cdr_zip = response_json["arcCdr"]

        try:
            cdr = self.env["account.edi.format"]._l10n_pe_edi_unzip_edi_document(base64.b64decode(cdr_zip))
        except Exception as e:
            return {"error": str(Markup("%s<br/>%s") % (ERROR_MESSAGES["unzip"], e))}

        return {"cdr": cdr}


class StockLocation(models.Model):
    _inherit = 'stock.location'

    direction_id = fields.Many2one(
        comodel_name='res.partner',
        string='Dirección'
    )
