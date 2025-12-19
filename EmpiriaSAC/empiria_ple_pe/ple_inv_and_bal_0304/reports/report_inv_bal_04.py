from io import BytesIO
from odoo.tools.misc import xlsxwriter


class ReportInvBalFourExcel(object):

    def __init__(self, obj, data_1):
        self.obj = obj
        self.data_1 = data_1

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

        ws = workbook.add_worksheet('Report CXC Empresa')
        ws.set_column('A:H', 15)

        ws.set_row(0, 50)

        headers = [
            'Periodo', 'Cuenta contable', 'Denominación', 'Código Operación',
            'Número Correlativo', 'Tipo de documento de identidad del cliente',
            'Número de documento de identidad del cliente',
            'Apellido y Nombres, Den. o Raz. Social cliente',
            'Fecha de emisión o referencia', 'Monto de cuenta por cobrar',
            'Indica el estado de la operación'
        ]
        for col, header in enumerate(headers):
            ws.write(0, col, header, style1)

        data = []

        for i in range(len(self.data_1)):
            join = {**self.data_1[i]}
            data.append(join)

        for row, value in enumerate(data, start=1):
            ws.write(row, 0, value['period'])
            ws.write(row, 1, value['account'])
            ws.write(row, 2, value['desc_account'])
            ws.write(row, 3, value['code_uo'])
            ws.write(row, 4, value['correlative'])
            ws.write(row, 5, value['doc_type'])
            ws.write(row, 6, value['doc_num'])
            ws.write(row, 7, value['name_client'])
            ws.write(row, 8, value['date_ref'])
            ws.write(row, 9, value['mont'], style_number)
            ws.write(row, 10, value['status'])

        workbook.close()
        output.seek(0)
        return output.read()

    def get_filename(self):
        year_month = self.obj.date_end.strftime('%Y%m')
        return 'Libro_Ctas. por cobrar: Trab. Soc. Direc. Ger. Acc._{}.xlsx'.format(year_month)


class ReportInvBalFourTxt(object):

    def __init__(self, obj, data_1):
        self.obj = obj
        self.data_1 = data_1

    def get_content(self):
        raw = ''
        template = '{period}|{code_uo}|{correlative}|{doc_type}|{doc_num}|{name_client}|{date_ref}|{mont}|{status}|\r\n'

        data = []
        for i in range(len(self.data_1)):
            join = {**self.data_1[i]}
            data.append(join)

        for value in data:
            raw += template.format(
                period=value['period'],
                code_uo=value['code_uo'],
                correlative=value['correlative'],
                doc_type=value['doc_type'],
                doc_num=value['doc_num'],
                name_client=value['name_client'],
                date_ref=value['date_ref'],
                mont="{:.2f}".format(value['mont']),
                status=value['status']
            )
        return raw

    def get_filename(self):
        year, month, day = self.obj.date_end.strftime('%Y/%m/%d').split('/')
        return 'LE{vat}{period_year}{period_month}{period_day}030400{eeff_oportunity}{state_send}{has_info}11.txt'.format(
            vat=self.obj.company_id.vat,
            period_year=year,
            period_month=month,
            period_day=day,
            eeff_oportunity=self.obj.eeff_presentation_opportunity,
            state_send=self.obj.state_send or '',
            has_info=int(bool(self.data_1))
        )
