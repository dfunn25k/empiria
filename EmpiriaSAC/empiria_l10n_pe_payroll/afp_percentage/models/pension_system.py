from odoo import models, fields, api, _
import logging
import requests
from requests.exceptions import ConnectionError, HTTPError, Timeout, TooManyRedirects, RequestException
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError


_logger = logging.getLogger(__name__)
now = datetime.now()


class PensionSystem(models.Model):
    _inherit = 'pension.system'

    @api.model
    def button_afp_method(self, context=None):
        tokens = self._get_api_token()

        today = fields.Date.today().strftime('%Y-%m')
        url = f'https://api.ganemo.co/api/v1/prima-afp/list/{today}'

        response_data = None

        for token in tokens:
            response_data = self._get_api_data(url, token)
            _logger.info(f"Intentando obtener datos de la API con token {token}")
            if response_data is not None:
                break

        if response_data is not None:
            _logger.info(f"Datos de la API obtenidos con éxito, la data es {response_data}")
        else:
            _logger.info("No se pudo obtener datos de la API con ninguno de los tokens")
            raise UserError('No se pudo obtener datos de la API con ninguno de los tokens')
        
        self._process_afp_method(response_data, today)
            

    def _get_api_token(self):
        rcs = self.env['res.config.settings'].sudo().search([], limit=1)
        icp = self.env['ir.config_parameter'].sudo()

        tokens = [
            icp.get_param('api.access_token_first'),
            icp.get_param('api.access_token'),
            rcs.api_data_token
        ]

        valid_tokens = [token for token in tokens if token]

        if not valid_tokens:
            _logger.info('No se ha encontrado tokens de API válidos')
            raise UserError('No se han configurado tokens de API válidos. Por favor, configure al menos un token en la configuración del sistema.')

        return valid_tokens
    
    def create_session(retries=3, backoff_factor=0.3):
        session = requests.Session()
        retry = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=backoff_factor,
            status_forcelist=(500, 502, 504)
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    def _get_api_data(self, url, api_data_token):
        headers = {
            'Content-Type': 'application/json',
            'X-Token': api_data_token
        }

        session = self.create_session()

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        
        except ConnectionError as e:
            _logger.error(f"Error de conexión: {e}")
        except HTTPError as e:
            _logger.error(f"Error HTTP: {e}")
        except Timeout as e:
            _logger.error(f"Error de tiempo de espera: {e}")
        except TooManyRedirects as e:
            _logger.error("Demasiadas redirecciones: %s", e)
        except ValueError as e: 
            _logger.error("Error de valor (posiblemente durante la decodificación JSON): %s", e)
        except KeyError as e:
            _logger.error("Key error: %s", e)
        except RequestException as e:
            _logger.error(f"Error en la solicitud: {e}")
        except Exception as e:
            _logger.error("Ocurrió un error inesperado: %s", e)
        return None
    
    def _process_afp_method(self, data, today):

        try:
            afp_data = data['data'][0]
        except (KeyError, IndexError, ValueError) as e:
            _logger.info(f"Error al procesar la respuesta de la API: {e}")
            raise

        if afp_data:
            _logger.info(f'La data que llega es {data}') 
        
        habitat = self.env.ref('types_system_pension.pension_system_25', raise_if_not_found=False)
        integra = self.env.ref('types_system_pension.pension_system_21', raise_if_not_found=False)
        profuturo = self.env.ref('types_system_pension.pension_system_23', raise_if_not_found=False)
        prima = self.env.ref('types_system_pension.pension_system_24', raise_if_not_found=False)

        init_date = datetime(now.year, now.month, 1).date()
        last_day = datetime.now() + relativedelta(day=1, months=+1, days=-1)

        pension_line_habitat = {
            'date_from': init_date,
            'date_to': last_day,
            'fund': float(afp_data['habitat']['aporte_obligatorio']),
            'bonus': float(afp_data['habitat']['prima_seguro']),
            'mixed_flow': 0.0,
            'flow': float(afp_data['habitat']['comi_sobreflujo']),
            'balance': float(afp_data['habitat']['comi_sobresaldo']),
        }

        pension_line_integra = {
            'date_from': init_date,
            'date_to': last_day,
            'fund': float(afp_data['integra']['aporte_obligatorio']),
            'bonus': float(afp_data['integra']['prima_seguro']),
            'mixed_flow': 0.0,
            'flow': float(afp_data['integra']['comi_sobreflujo']),
            'balance': float(afp_data['integra']['comi_sobresaldo']),
        }

        pension_line_prima = {
            'date_from': init_date,
            'date_to': last_day,
            'fund': float(afp_data['prima']['aporte_obligatorio']),
            'bonus': float(afp_data['prima']['prima_seguro']),
            'mixed_flow': 0.0,
            'flow': float(afp_data['prima']['comi_sobreflujo']),
            'balance': float(afp_data['prima']['comi_sobresaldo']),
        }

        pension_line_profuturo = {
            'date_from': init_date,
            'date_to': last_day,
            'fund': float(afp_data['profuturo']['aporte_obligatorio']),
            'bonus': float(afp_data['profuturo']['prima_seguro']),
            'mixed_flow': 0.0,
            'flow': float(afp_data['profuturo']['comi_sobreflujo']),
            'balance': float(afp_data['profuturo']['comi_sobresaldo']),
        }

        if not self.env['tope.afp'].search([("date_from", "=", init_date)]):
            self.env['tope.afp'].create({
                'date_from': init_date,
                'date_to': last_day,
                'top': float(afp_data['habitat']['remu_asegurable']),
            })

        def update_or_create_lines(pension_system, pension_line):
            flag = False
            for line in pension_system.comis_pension_ids:
                if line.date_from == init_date:
                    flag = True
                    line.write(pension_line)
                    break
            if not flag:
                pension_system.comis_pension_ids = [(0, 0, pension_line)]

        update_or_create_lines(habitat, pension_line_habitat)
        update_or_create_lines(integra, pension_line_integra)
        update_or_create_lines(prima, pension_line_prima)
        update_or_create_lines(profuturo, pension_line_profuturo)