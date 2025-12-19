import logging
import requests
from requests.exceptions import ConnectionError, HTTPError, Timeout, TooManyRedirects, RequestException
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ResCurrency(models.Model):
    _inherit = 'res.currency'

    @api.model
    def _action_sbs_currency_update(self):
        tokens = self._get_api_token()

        today = fields.Date.today().strftime('%Y-%m-%d')
        url = f'https://api.ganemo.co/api/v1/tipo-cambio/list/{today}'

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
        
        self._process_and_update_rates(response_data, today)
            

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
            response = session.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except ConnectionError as e:
            _logger.info(f"Error de conexión: {e}")
        except HTTPError as e:
            _logger.info(f"Error HTTP: {e}")
        except Timeout as e:
            _logger.info(f"Error de tiempo de espera: {e}")
        except TooManyRedirects as e:
            _logger.info("Demasiadas redirecciones: %s", e)
        except ValueError as e: 
            _logger.info("Error de valor (posiblemente durante la decodificación JSON): %s", e)
        except KeyError as e:
            _logger.info("Key error: %s", e)
        except RequestException as e:
            _logger.info(f"Error en la solicitud: {e}")
        except Exception as e:
            _logger.info("Ocurrió un error inesperado: %s", e)
        return None

    def _process_and_update_rates(self, data, today):
        try:
            venta = float(data['data'][0]['venta'])
        except (KeyError, IndexError, ValueError) as e:
            _logger.info(f"Error al procesar la respuesta de la API: {e}")
            raise

        if venta <= 0:
            _logger.info(f"La API devolvió una tasa de venta de {venta}. Usando tasa predeterminada...")
            venta = 1.0

        companies = self.env['res.company'].sudo().search([
            ('currency_id.name', '=', 'PEN')
        ])

        if not companies:
            _logger.info("No se encontraron compañías con moneda principal PEN")
            return
        
        usd_currency = self.env.ref('base.USD', raise_if_not_found=False)
        if not usd_currency:
            _logger.info("No se encontró la moneda USD")
            return

        for company in companies:
            active_currency = self.env['res.currency'].search([
                ('active', '=', True),
                '|',
                ('name', '=', 'PEN'),
                ('name', '=', 'USD')
            ])

            if len(active_currency) != 2:
                _logger.info(f"La compañía {company.name} no tiene exactamente PEN y USD activas")
                continue

            currency_rate = self.env['res.currency.rate']
            existing_rate = currency_rate.search([
                ('currency_id', '=', usd_currency.id),
                ('name', '=', today),
                ('company_id', '=', company.id)
            ], limit=1)

            rate_value = (1 / venta) or currency_rate._get_latest_rate().rate or 1.0
            try:
                if existing_rate:
                    existing_rate.write({'rate': rate_value})
                else:
                    currency_rate.create({
                        'currency_id': usd_currency.id,
                        'rate': rate_value,
                        'name': today,
                        'company_id': company.id
                    })
                _logger.info(f"Tasa de cambio actualizada para USD en {company.name}: {rate_value}")
            except Exception as e:
                _logger.info(f"Error al actualizar/crear tasa para {company.name}: {e}")
