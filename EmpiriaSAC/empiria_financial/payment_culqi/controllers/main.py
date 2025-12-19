from culqi.client import Culqi
from culqi.resources import Charge, Token

from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import request


class CulqiController(http.Controller):

    @http.route('/payment/culqi/poll', type='http', auth="public", website=True, csrf=False)
    def culqi_form_feedback(self, **post):
        if '__website_sale_last_tx_id' not in request.session:
            raise ValidationError('¡ERROR!\n Intente de nuevo o avise a su administrador de sistemas.')
        transaction_id = request.session['__website_sale_last_tx_id']
        transaction_sudo = request.env['payment.transaction'].sudo().browse(int(transaction_id))
        amount_value = 'Pagar {}{} {}'.format(
            transaction_sudo.currency_id.symbol,
            transaction_sudo.amount,
            transaction_sudo.currency_id.name or post.get('currency')
        )
        if 'base_url' in request.session:
            base_url = request.session['base_url']
        else:
            base_url = '/shop/confirm_order'

        values = {
            'data_transaction': transaction_id,
            'amount_value': amount_value,
            'data_url': '/payment/culqi/return',
            'base_url': base_url,
            'default_partner_mail': transaction_sudo.partner_id.email,
            'default_partner_name': transaction_sudo.partner_id.name
        }
        return request.render("payment_culqi.token_culqi_form", values)

    @http.route('/payment/culqi/return', type='json', auth="public", methods=['POST'], csrf=False, save_session=False)
    def culqi_return_from_redirect(self, **post):
        """ Process the data returned by Culqi after redirection.

        The route is flagged with `save_session=False` to prevent Odoo from assigning a new session
        to the user if they are redirected to this route with a POST request. Indeed, as the session
        cookie is created without a `SameSite` attribute, some browsers that don't implement the
        recommended default `SameSite=Lax` behavior will not include the cookie in the redirection
        request from the payment provider to Odoo. As the redirection to the '/payment/status' page
        will satisfy any specification of the `SameSite` attribute, the session of the user will be
        retrieved and with it the transaction which will be immediately post-processed.

        :param dict data: The feedback data to process
        """

        try:
            transaction = post.get('transaction')
            card_number = post.get('cardNumber')
            cvv = post.get('cvv')
            email = post.get('email')
            expiration_month = post.get('expirationMonth')
            expiration_year = post.get('expirationYear')

            PaymentTransaction = request.env['payment.transaction']
            transaction_sudo = PaymentTransaction.sudo().browse(transaction)

            provider_id = transaction_sudo.provider_id
            currency_code = transaction_sudo.currency_id.name
            reference = transaction_sudo.reference
            amount = transaction_sudo.amount

            culqi_obj = Culqi(
                public_key=provider_id.culqi_public_key,
                private_key=provider_id.culqi_private_key
            )

            token_data = {
                'card_number': card_number,
                'cvv': cvv,
                'email': email,
                'expiration_month': expiration_month,
                'expiration_year': expiration_year
            }
            token = self._generate_culqi_token(culqi_obj, token_data)

            if token['data'].get('object') == 'error':
                return {'Error': token['data'].get('merchant_message')}

            charge_data = {
                'amount': int(amount * 100),
                'capture': True,
                'currency_code': currency_code,
                'description': reference,
                'email': email,
                'installments': 0,
                'metadata': {'order_id': reference},
                'source_id': token['data']['id']
            }
            charge = self._generate_culqi_charge(culqi_obj, charge_data)
            
            if charge['data'].get('object') != 'charge':
                return {'Error': charge['data'].get('merchant_message')}

            notification_data = {
                'amount': amount,
                'currency': currency_code,
                'reference': reference,
                'status': 'done'
            }
            PaymentTransaction.sudo()._handle_notification_data('culqi', notification_data)

            return {'Redirect': '/payment/status'}

        except ValidationError:
            return {'Error': 'No se pudo procesar la compra'}
        except Exception as excep_val:
            return {'Error': f'No se pudo procesar la compra:\n{excep_val}'}

    @staticmethod
    def _generate_culqi_token(culqi_obj, token_data):
        token_obj = Token(client=culqi_obj)
        token = token_obj.create(data=token_data)

        return token

    @staticmethod
    def _generate_culqi_charge(culqi_obj, charge_data):
        charge_obj = Charge(client=culqi_obj)
        charge = charge_obj.create(data=charge_data)

        return charge
