from io import BytesIO
from odoo.tools.misc import xlsxwriter



class ReportInvBalOneExcel(object):

    def __init__(self, obj, data):
        self.obj = obj
        self.data = data

    def get_content(self):
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        style1 = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'size': 10,
            'bold': True,
            'font_name': 'Arial'
        })
        style_number = workbook.add_format({
            'size': 11,
            'num_format': '#,##0.00',
        })

        ws = workbook.add_worksheet('Report Cash')
        ws.set_column('A:H', 15)

        ws.set_row(0, 50)

        headers = ['Periodo', 'Código de la Cuenta', 'Denominación','Codigo de la Entidad Financiera', 'Número de la cuenta de la Entidad Financiera',
        'Tipo de moneda', 'Saldo deudor de la cuenta', 'Saldo acreedor de la cuenta','Indica el estado de la operación']

        for col, header in enumerate(headers):
            ws.write(0, col, header, style1)

        for row, data_row in enumerate(self.data, start=1):
            ws.write(row, 0, data_row['period'])
            ws.write(row, 1, data_row['accounting_account'])
            ws.write(row, 2, data_row['bank_account_name'])
            ws.write(row, 3, data_row['bic'])
            ws.write(row, 4, data_row['account_bank_code'])
            ws.write(row, 5, data_row['type_currency'])
            ws.write(row, 6, data_row['debit_balance'], style_number)
            ws.write(row, 7, data_row['credit_balance'], style_number)
            ws.write(row, 8, data_row['status'])

        workbook.close()
        output.seek(0)
        return output.read()

    def get_filename(self):
        year_month = self.obj.date_end.strftime('%Y%m')
        return 'Libro_Efectivo y Equivalente de efectivo_{}.xlsx'.format(year_month)


class ReportInvBalOneTxt(object):

    def __init__(self, obj, data):
        self.obj = obj
        self.data = data

    def get_content(self):
        raw = ''
        template = '{period}|{accounting_account}|{bic}|{account_bank_code}|{type_currency}|{debit_balance}|{credit_balance}|{status}|\r\n'

        for value in self.data:
            raw += template.format(
                period=value['period'],
                accounting_account=value['accounting_account'],
                bic=value['bic'],
                account_bank_code=value['account_bank_code'],
                type_currency=value['type_currency'],
                credit_balance="{:.2f}".format(float(value['credit_balance'] or 0.0)),
                debit_balance="{:.2f}".format(float(value['debit_balance'] or 0.0)),
                status=value['status']
            )
        return raw

    def get_filename(self):
        year, month, day = self.obj.date_end.strftime('%Y/%m/%d').split('/')
        return 'LE{vat}{period_year}{period_month}{period_day}030200{eeff_oportunity}{state_send}{has_info}11.txt'.format(
            vat=self.obj.company_id.vat,
            period_year=year,
            period_month=month,
            period_day=day,
            eeff_oportunity=self.obj.eeff_presentation_opportunity,
            state_send=self.obj.state_send or '',
            has_info=int(bool(self.data))
        )
