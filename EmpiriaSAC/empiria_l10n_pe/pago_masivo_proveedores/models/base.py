from odoo import api, fields, models
from datetime import date, timedelta
from odoo.exceptions import ValidationError
from ..reports.report_detractions import ReportInvBalTxt
from datetime import datetime
import base64
import pytz
import re


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    bank_id_related = fields.Selection(string='Bank relation code', related='bank_id.sunat_bank_code')
    company_code = fields.Char(string="Código de la empresa")
    service_code = fields.Char(string="Código del servicio")
    account_type = fields.Selection(string='Tipo de cuenta', selection=[
        ('001', 'Cuenta Corriente'),
        ('002', 'Cuenta de Ahorros'),
    ])


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    account_type = fields.Selection(string='Tipo de cuenta', selection=[
        ('001', 'Corriente'),
        ('002', 'Ahorro'),
        ('003', 'Detracción'),
    ])


class AccountBatchPayment(models.Model):
    _inherit = 'account.batch.payment'

    process_type = fields.Selection(string='Tipo de proceso', default='A', required=True, selection=[
        ('A', 'Inmediato'),
        ('F', 'Fecha futura'),
        ('H', 'Horario de ejecución'),
    ])
    future_date = fields.Date(string='Fecha futura', default=lambda self: self._get_default_future_date(),)
    executing_schedule = fields.Selection(string='Horario de ejecución', selection=[
        ('B', '11:00 horas'),
        ('C', '15:00 horas'),
        ('D', '19:00 horas'),
    ])
    validate_belonging = fields.Boolean(string='Validar pertenencia')
    journal_temporal_code = fields.Selection(related='journal_id.bank_id_related')
    process_type_itb = fields.Selection(string='Tipo de proceso', selection=[
        ('0', 'En línea'),
        ('1', 'En diferdo'),
    ])
    future_date_itb = fields.Date(string='Fecha futura')
    count_txt = fields.Integer(string='Contador', default=0)

    txt_filename_bank = fields.Char(string='Filaname_bank .txt')
    txt_binary_bank = fields.Binary(string='Reporte_bank .TXT')

    txt_filename_scotia = fields.Char(string='Pago')
    txt_binary_scotia = fields.Binary(string='Pago .txt')
    txt_filename_scotia_zip = fields.Char(string='Pago .zip')
    txt_binary_scotia_zip = fields.Binary(string='Pago .zip')

    @api.model
    def _get_default_future_date(self):
        today = date.today()
        return today + timedelta(days=1)

    @api.constrains('future_date')
    def _check_future_date(self):
        for record in self:
            today = date.today()
            six_months_future = today + timedelta(days=180)
            
            if not record.future_date:
                continue
            
            if record.future_date <= today:
                raise ValidationError("La fecha futura debe ser posterior al día de hoy.")
            
            if record.future_date > six_months_future:
                raise ValidationError("La fecha no debe ser mayor a 6 meses en el futuro.")
            
    def _format_number_account(self, number):
        """Esta función se creo para formatear el número de cuenta segun los requirimientos del BBVA"""
        number = number.replace('-', '')
        length = len(number)

        if length == 20:
            number = number[:8] + number[-2:] + number[8:18]
        elif length == 18:
            number = number[:8] + '00' + number[-10:]
        else:
            number = number.ljust(20, ' ')
        return number

    def generate_txt_suppliers(self):
        amount_total = 0
        lines = 0
        zeros = '00000000000000000000000000000000'
        type_bank = ' '
        line_data = []
        line_data_2 = []
        line_data_scot = []
        list_data = {}
        total_account = 0
        

        if self.journal_temporal_code == '11':
            type_bank = '11'
            for payment in self.payment_ids:
                amount_total = amount_total + payment.amount
                lines = lines + 1
                if payment.partner_id.l10n_latam_identification_type_id.name.strip() == 'DNI':
                    code_doc = 'L'
                elif payment.partner_id.l10n_latam_identification_type_id.name.strip() == 'RUC':
                    code_doc = 'R'
                elif payment.partner_id.l10n_latam_identification_type_id.name.strip() == 'Carnet Militar':
                    code_doc = 'M'
                elif payment.partner_id.l10n_latam_identification_type_id.name.strip() == 'Cédula Extranjera':
                    code_doc = 'E'
                elif payment.partner_id.l10n_latam_identification_type_id.name.strip() == 'Pasaporte':
                    code_doc = 'P'
                else:
                    code_doc = ' '

                if payment.partner_id.bank_ids:
                    for bank in payment.partner_id.bank_ids:
                        if bank.bank_id.sunat_bank_code == '11':
                            cod_bank = 'P'
                            account = self._format_number_account(bank.acc_number)
                            break
                        else:
                            if bank.account_type != '003':
                                cod_bank = 'I'
                                account = str(bank.cci).replace('-', '').ljust(20, ' ')
                else:
                    cod_bank = 'I'
                    account = ' '*20

                values = {
                    'doi_type': code_doc,
                    'doi_number': str(payment.partner_id.vat).ljust(12, ' ') if payment.partner_id.vat else ' '*12,
                    'type_deposit': cod_bank,
                    'account': account.ljust(20, ' '),
                    'name_client': str(payment.partner_id.name).ljust(40, ' ') if len(payment.partner_id.name) < 40 else str(payment.partner_id.name)[:40],
                    'amount': str(f"{payment.amount:.2f}").replace('.', '').rjust(15, '0'),
                    'type_document': payment.reconciled_bill_ids.l10n_latam_document_type_id.name[
                                :1] if payment.reconciled_bill_ids.l10n_latam_document_type_id.internal_type in ['invoice',
                                                                                                                 'credit_note'] else ' ',
                    'number_document': str(payment.ref)[-8:].ljust(12, ' '),
                    'grouped_credit': 'N',
                    'reference': str(payment.name).ljust(40, ' ') if payment.name else ' '*40,
                    'zeros': zeros.rjust(113, ' ') + ' ' * 18
                }
                line_data.append(values)
            list_data = {
                'bank_account_id': self._format_number_account(self.journal_id.bank_account_id.acc_number),
                'currency_id': self.journal_id.currency_id.name,
                'amount_total': str(f"{amount_total:.2f}").replace('.', '').rjust(15, '0'),
                'process_type': self.process_type,
                'date': str(self.future_date).replace('-', '') if self.process_type == 'F' else ' '*8,
                'executing_schedule': self.executing_schedule if self.process_type == 'H' else ' ',
                'reference': self.name.ljust(25, ' ') if self.name else ' '.ljust(25, ' '),
                'lines': str(lines).rjust(6, '0'),
                'validate_belonging': 'S' if self.validate_belonging else 'N',
                'zeros':'000000000000000000'.ljust(68, ' ')
            }
        elif self.journal_temporal_code == '02':
            type_bank = '02'
            amount_total = 0.0
            lines_total = 0

            # Estructuras donde almacenaremos la info agrupada
            partners_data = {}  # {partner_id: { 'bank_cod': ..., 'account': ..., 'doc_code': ..., 'partner_name': ..., 'total_amount': 0.0, 'line3_details': [] }}

            # 1) Recorremos todos los payments y agrupamos
            for payment in self.payment_ids:
                amount_total += payment.amount

                # Determinamos el código de documento
                if payment.partner_id.l10n_latam_identification_type_id:
                    doc_type_name = payment.partner_id.l10n_latam_identification_type_id.name.strip()
                else:
                    doc_type_name = ''
                if doc_type_name == 'DNI':
                    code_doc = '1'
                elif doc_type_name == 'RUC':
                    code_doc = '6'
                elif doc_type_name == 'FIC':
                    code_doc = '7'
                elif doc_type_name == 'Cédula Extranjera':
                    code_doc = '3'
                elif doc_type_name == 'Pasaporte':
                    code_doc = '4'
                else:
                    code_doc = ' '

                # Determinamos la cuenta y el "bank_cod"
                account = ' ' * 20
                bank_cod = 'B'
                partner_bank_ids = payment.partner_id.bank_ids
                if partner_bank_ids:
                    for bank in partner_bank_ids:
                        if bank.bank_id.sunat_bank_code == '02' and bank.account_type == '002':
                            bank_cod = 'A'
                            account = str(bank.acc_number).replace('-', '').ljust(20, ' ')
                            break
                        elif bank.bank_id.sunat_bank_code == '02' and bank.account_type == '001':
                            bank_cod = 'C'
                            account = str(bank.acc_number).replace('-', '').ljust(20, ' ')
                            break
                        else:
                            # Si no es cuenta de ahorros (002) o corriente (001), usamos CCI mientras no sea cuenta de detracción ('003')
                            if bank.account_type != '003':
                                bank_cod = 'B'
                                account = str(bank.cci).replace('-', '').ljust(20, ' ')

                # Acumulamos la parte "global" de cada partner (para la línea 2)
                partner_id = payment.partner_id.id
                if partner_id not in partners_data:
                    partners_data[partner_id] = {
                        'doc_code': code_doc,
                        'bank_cod': bank_cod,
                        'account': account,
                        'partner_vat': (payment.partner_id.vat or '').ljust(12, ' '),
                        'partner_name': (payment.partner_id.name or '').ljust(75, ' '),
                        'total_amount': 0.0,
                        'line3_details': []
                    }
                # Sumamos el amount a ese partner
                partners_data[partner_id]['total_amount'] += payment.amount

                # Preparamos la línea 3 asociada a este payment
                if payment.reconciled_bill_ids.l10n_latam_document_type_id.internal_type == 'invoice':
                    doc = 'F'
                elif payment.reconciled_bill_ids.l10n_latam_document_type_id.internal_type == 'credit_note':
                    doc = 'N'
                elif payment.reconciled_bill_ids.l10n_latam_document_type_id.internal_type == 'debit_note':
                    doc = 'C'
                else:
                    doc = 'D'

                # Valor del monto en texto, con decimales forzados
                payment_amount_str = f"{payment.amount:.2f}"  # siempre con 2 decimales
                # Armamos diccionario para línea 3
                line3_data = {
                    'doc': doc,
                    # Limpieza de ref si deseas:
                    'ref': re.sub(r'\W+', '', payment.ref or ''),
                    'amount': payment_amount_str,
                }
                partners_data[partner_id]['line3_details'].append(line3_data)

            # 2) Calculamos la suma de la "cuenta abono" (total_account) y la cantidad de líneas (line 2 + line 3)
            #    *La variable lines_total será la suma final de todas las líneas "2" + las líneas "3"*.
            total_account = 0
            # Sumar la cuenta base de la chequera
            main_acc = (self.journal_id.bank_account_id.acc_number or '').replace('-', '')
            if len(main_acc) >= 4:
                try:
                    total_account += int(main_acc[3:])
                except ValueError:
                    pass  # si no se puede, ignoramos

            for partner_id, info in partners_data.items():
                # -- Generamos la línea 2 para este partner una sola vez --
                # Revisa si la cuenta no es 20 espacios
                if info['account'] != ' ' * 20:
                    if info['bank_cod'] == 'B':
                        # Tomar los últimos 10
                        try:
                            total_account += int(info['account'][-10:])
                        except ValueError:
                            pass
                    else:
                        # Tomar desde el 3 en adelante
                        try:
                            total_account += int(info['account'][3:])
                        except ValueError:
                            pass

                # Preparamos el valor total en texto con padding
                total_partner_amount_str = f"{info['total_amount']:.2f}"
                if len(total_partner_amount_str.split('.')[1]) < 2:
                    total_partner_amount_str += '0'
                total_partner_amount_str = total_partner_amount_str.rjust(17, '0')

                # Línea 2 (una vez por partner)
                line2 = {
                    'id': '2',
                    'bank_cod': info['bank_cod'],
                    'account': info['account'],
                    'id_2': '1',
                    'doc': info['doc_code'],
                    'vat': info['partner_vat'],
                    'spaces': ' ' * 3,
                    'partner_name': info['partner_name'],
                    'reference': (self.name[:40] if self.name else '').ljust(40, ' '),
                    'payment_reference': (self.name[:20] if self.name else '').ljust(20, ' '),
                    'currency': '0001' if (not self.journal_id.currency_id or self.journal_id.currency_id.name == 'PEN') else '1001',
                    'amount': total_partner_amount_str,
                    'N': 'S',
                }
                line_data.append(line2)

                # Luego tantas líneas 3 como documentos haya
                for d in info['line3_details']:
                    # Ajustamos el amount con padding a la derecha
                    part_amount_str = d['amount']
                    if len(part_amount_str.split('.')[1]) < 2:
                        part_amount_str += '0'
                    part_amount_str = part_amount_str.rjust(17, '0')

                    line3 = {
                        'id': '3',
                        'document': d['doc'],
                        'ref': d['ref'][:15].rjust(15, '0') if d['ref'] else ' ' * 15,
                        'amount': part_amount_str,
                    }
                    line_data_2.append(line3)

            # Ahora, la cantidad total de líneas "2" + "3"
            lines_total = len(line_data) + len(line_data_2)

            # Montos totales globales para la línea 1
            amount_total_str = f"{amount_total:.2f}"
            if len(amount_total_str.split('.')[1]) < 2:
                amount_total_str += '0'
            amount_total_str = amount_total_str.rjust(17, '0')

            # Armamos el diccionario final para la línea 1
            list_data = {
                'id': '1',
                'lines_total': str(lines_total).rjust(6, '0'),
                'date': str(self.date).replace('-', '').replace(' ', '').replace(':', '') if self.date else ' ' * 8,
                'c': 'C',
                'currency': '0001' if (not self.journal_id.currency_id or self.journal_id.currency_id.name == 'PEN') else '1001',
                'acc_number': (self.journal_id.bank_account_id.acc_number or '').ljust(20, ' '),
                'amount_total': amount_total_str,
                'reference': (self.name or '').ljust(40, ' '),
                'N': 'N',
                'abono': str(total_account)[-15:].rjust(15, '0'),
            }

        elif self.journal_temporal_code == '03':
            self.count_txt = self.count_txt + 1
            type_bank = '03'
            for payment in self.payment_ids:
                amount_total = amount_total + payment.amount
                lines = lines + 1

                if payment.reconciled_bill_ids.l10n_latam_document_type_id.internal_type == 'invoice':
                    code_doc = 'F'
                elif payment.reconciled_bill_ids.l10n_latam_document_type_id.internal_type == 'credit_note':
                    code_doc = 'C'
                elif payment.reconciled_bill_ids.l10n_latam_document_type_id.internal_type == 'debit_note':
                    code_doc = 'D'
                else:
                    code_doc = ' '

                if payment.partner_id.l10n_latam_identification_type_id.name.strip() == 'DNI':
                    doc_tyoe = '01'
                elif payment.partner_id.l10n_latam_identification_type_id.name.strip() == 'RUC':
                    doc_tyoe = '02'
                elif payment.partner_id.l10n_latam_identification_type_id.name.strip() == 'Cédula Extranjera':
                    doc_tyoe = '03'
                elif payment.partner_id.l10n_latam_identification_type_id.name.strip() == 'Pasaporte':
                    doc_tyoe = '05'
                else:
                    doc_tyoe = ' '

                if payment.partner_id.bank_ids:
                    for bank in payment.partner_id.bank_ids:
                        if bank.bank_id.sunat_bank_code == '03':
                            sunat_code = '09'
                            account_type = bank.account_type
                            account = str(bank.acc_number).ljust(20, ' ')
                            break
                        else:
                            if bank.account_type != '003':
                                sunat_code = '99'
                                account_type = bank.account_type
                                account = str(bank.cci).ljust(20, ' ')
                else:
                    sunat_code = '99'
                    account_type = '   '
                    account = ' '.ljust(20, ' ')

                values = {
                    'ruc': str(payment.partner_id.vat).ljust(20, ' ') if payment.partner_id.vat else ' '.ljust(20, ' '),
                    'doc': code_doc,
                    'payment': str(payment.move_id.payment_reference).ljust(20, ' ') if payment.move_id.payment_reference else ' '.ljust(20, ' '),
                    'currency': '01' if payment.currency_id.name == 'PEN' else '10',
                    'amount': str(f"{payment.amount:.2f}").replace('.', '').rjust(15, '0') if payment.amount else ' '.rjust(15, '0'),
                    'space': ' ',
                    'sunat_bank_code': sunat_code,
                    'account_type': account_type,
                    'currency_id': '01' if payment.currency_id.name == 'PEN' else '10',
                    'acc_3': account[0:3],
                    'account': account[:20],
                    'type_document': 'C' if payment.partner_id.l10n_latam_identification_type_id.name == 'RUC' else 'P',
                    'doc_tyoe': doc_tyoe,
                    'document': str(payment.partner_id.vat).ljust(15, ' ') if payment.partner_id.vat else ' '.ljust(15, ' '),
                    'name': str(payment.partner_id.name).ljust(60, ' ') if payment.partner_id.name else ' '.ljust(60, ' '),
                    '203': ' ' * 203,
                }
                line_data.append(values)

            amount_total_str = str(amount_total)
            if len(amount_total_str.split('.')) < 2:
                amount_total_str += '.0'
            amount_total = amount_total_str + '0' if len(amount_total_str.split('.')[1]) < 2 else str(round(amount_total, 2))

            timezone = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')
            formatted_date_time = datetime.now()
            if timezone != 'UTC':
                formatted_date_time = datetime.now().astimezone(timezone)

            list_data = {
                'company_code': self.journal_id.company_code,
                'service_code': self.journal_id.service_code,
                'bank_account': self.journal_id.bank_account_id.acc_number.ljust(13, ' '),
                'account_type': self.journal_id.account_type,
                'currency_id': '01' if self.journal_id.currency_id.name == 'PEN' or not self.journal_id.currency_id else '10',
                'pay': 'Pagos a prov',
                'date_time': str(formatted_date_time).split('.')[0].replace('-', '').replace(' ', '').replace(':', ''),
                'process_type_itb': self.process_type_itb,
                'date': datetime.today().strftime('%Y%m%d') if self.process_type_itb == '0' else str(self.future_date_itb).replace('-', ''),
                'lines': str(lines).rjust(6, '0'),
                'amount_total_pen': str(amount_total).replace(',', '').replace('.', '').rjust(15,
                                                                                              '0') if (self.journal_id.currency_id and self.journal_id.currency_id.name == 'PEN') or not self.journal_id.currency_id else '000000000000000',
                'amount_total_usd': str(amount_total).replace(',', '').replace('.', '').rjust(15,
                                                                                              '0') if self.journal_id.currency_id and self.journal_id.currency_id.name == 'USD' else '000000000000000',
                'm': 'MC001',
            }
        elif self.journal_temporal_code == '09':
            type_bank = '09'
            for payment in self.payment_ids:
                type_acc = ' '
                acc_number = '            '
                cci_number = '            '
                cci_to_scot = False
                acc_to_scot = False
                for bank in payment.partner_id.bank_ids:
                    if not cci_to_scot:
                        cci_number = str(bank.cci) if bank.cci else ' ' * 20
                    if not acc_to_scot and bank.bank_id.sunat_bank_code == '09':
                        acc_to_scot = str(bank.acc_number).ljust(10, ' ')
                    if bank.bank_id.sunat_bank_code == '09' and bank.account_type == '002':
                        type_acc = '3'
                        acc_number = str(bank.acc_number).ljust(10, ' ')
                    elif bank.bank_id.sunat_bank_code == '09' and bank.account_type == '001':
                        type_acc = '2'
                        acc_number = str(bank.acc_number).ljust(10, ' ')
                    elif bank.bank_id.sunat_bank_code != '09' and bank.account_type != '003' and type_acc == ' ':
                        type_acc = '4'
                        cci_number = str(bank.cci) if bank.cci else ' ' * 20
                    else:
                        continue

                count_account = 0
                batch_partner = payment.partner_id
                for batch in self.payment_ids:
                    if batch.partner_id == batch_partner:
                        count_account = count_account + 1

                values = {
                    'ruc': str(payment.partner_id.vat).ljust(11, ' ') if payment.partner_id.vat else ' ' * 11,
                    'name': str(payment.partner_id.name[:60]).ljust(60, ' ') if payment.partner_id.name else ' '*60,
                    'ref': str(payment.ref[:14]).rjust(14, ' ') if payment.ref else ' '*14,
                    'invoice_date': payment.reconciled_bill_ids.invoice_date.strftime('%Y%m%d'),
                    'payment_amount': str(f"{payment.amount:.2f}").replace('.', '').rjust(11, '0') if payment.amount else ' ' * 11,
                    'type_acc': type_acc,
                    'office': acc_number[:3] if acc_number else ' ' * 3,
                    'acc_number': acc_number[3:].ljust(7) if acc_number else ' ' * 7,
                    'count_account': 'N' if count_account > 1 else 'S',
                    'email': str(payment.partner_id.email[:50]).ljust(50, ' ') if payment.partner_id.email else ' ' * 50,
                    'cci_number': cci_number.ljust(20) if cci_number else ' ' * 20,
                    'currency_id': '01' if payment.currency_id.name == 'USD' else '00',
                }
                line_data.append(values)

                if payment.currency_id.name == 'PEN':
                    amount_payment_line = payment.amount
                else:
                    currency_payment = self.env['res.currency'].search([('name', '=', 'USD'), ('active', '=', True)])
                    amount_payment_line = payment.amount / currency_payment.rate

                values_scot = {
                    'ruc': str(payment.partner_id.vat).ljust(11, ' ') if payment.partner_id.vat else ' ' * 11,
                    'name': str(payment.partner_id.name[:60]).ljust(60, ' ') if payment.partner_id.name else ' ' * 60,
                    'email': str(self.env.company.email[:60]).ljust(60, ' ') if self.env.company.email else ' ' * 60,
                    'ref': str(payment.ref).ljust(19, ' ') if len(str(payment.ref)) < 19 else str(payment.ref)[:19],
                    'currency_id': '0' if not self.journal_id.currency_id or self.journal_id.currency_id.name == 'PEN' else '1',
                    'amount': str(f"{payment.amount:.2f}").replace('.', '').rjust(15, '0') if payment.amount else ' '.rjust(15, '0'),
                    'spaces': ' '*15,
                    'bank': acc_to_scot if acc_to_scot else cci_to_scot,
                }
                line_data_scot.append(values_scot)
        else:
            return

        data_name = {
            'name': self.name
        }

        if self.journal_temporal_code == '03':
            timezone = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')
            formatted_date_time = datetime.now()
            if timezone != 'UTC':
                formatted_date_time = datetime.now().astimezone(timezone)

            data_name = {
                'company_code': self.journal_id.company_code,
                'service_code': self.journal_id.service_code,
                'count_txt': str(self.count_txt).zfill(30),
                'date_time': str(formatted_date_time).split('.')[0].replace('-', '').replace(' ', '').replace(':', ''),
            }

        if self.journal_temporal_code == '09':
            report_txt = ReportInvBalTxt(False, False, line_data_scot, False, '09_txt')
            values_content = report_txt.get_content()

            report_zip = ReportInvBalTxt(False, False, line_data_scot, False, '09_zip')
            txt_2 = report_zip.get_content()

            data = {
                'txt_binary_scotia': base64.b64encode(values_content.encode() or '\n'.encode()),
                'txt_filename_scotia': 'Pago.txt',
                'txt_binary_scotia_zip': txt_2 or base64.b64encode(b'\n'),
                'txt_filename_scotia_zip': 'Pago.zip',
            }
            self.write(data)

        report_txt = ReportInvBalTxt(data_name, list_data, line_data, line_data_2, type_bank)

        values_content = report_txt.get_content()
        data = {
            'txt_binary_bank': base64.b64encode(values_content.encode() or '\n'.encode()),
            'txt_filename_bank': report_txt.get_filename(),
        }
        self.write(data)
        return

