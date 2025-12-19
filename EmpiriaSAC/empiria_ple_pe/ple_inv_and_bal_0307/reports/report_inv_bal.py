from io import BytesIO

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter


class ReportInvBalExcel(object):

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
            'num_format': '0.00',
        })

        ws = workbook.add_worksheet('Merca y Prod Term')
        ws.set_column('A:H', 15)

        ws.set_row(0, 50)

        headers = [
            'Periodo', 'Código del catálogo utilizado', 'Tipo de existencia',
            'Código propio de la existencia', 'Código del catálogo utilizado',
            'Código de Existencia', 'Descripción de la existencia',
            'Código de la Unidad de medida de la existencia',
            'Código del método de valuación utilizado', 'Cantidad de la existencia',
            'Costo unitario de la existencia', 'Costo Total', 'Estado de Operación/codeprefix'
        ]

        for col, header in enumerate(headers):
            ws.write(0, col, header, style1)

        for i, value in enumerate(self.data, start=1):
            ws.write(i, 0, value['period'])
            ws.write(i, 1, value['stock_catalog'])
            ws.write(i, 2, value['stock_type'])
            ws.write(i, 3, value['default_code'])
            ws.write(i, 4, value['code_catalog_used'])
            ws.write(i, 5, value['unspsc_code_id'])
            ws.write(i, 6, value['product_description'])
            ws.write(i, 7, value['product_udm'])
            ws.write(i, 8, value['property_cost_method'])
            ws.write(i, 9, value['quantity_product_hand'], style_number)
            ws.write(i, 10, value['standard_price'], style_number)
            ws.write(i, 11, value['total'], style_number)
            ws.write(i, 12, 1)

        workbook.close()
        output.seek(0)
        return output.read()

    def get_filename(self):
        year_month = self.obj.date_end.strftime('%Y%m')
        return 'Libro_Mercaderías y Productos Terminados_{}.xlsx'.format(year_month)


class ReportInvBalTxt(object):

    def __init__(self, obj, data):
        self.obj = obj
        self.data = data

    def get_content(self):
        raw = ''
        template = '{period}|{stock_catalog}|{stock_type}|{default_code}|{code_catalog_used}|{unspsc_code_id}|{product_description}|{product_udm}|{property_cost_method}|{quantity_product_hand}|{standard_price}|{total}|1|\r\n'

        for value in self.data:
            raw += template.format(
                period=value['period'],
                stock_catalog=value['stock_catalog'],
                stock_type=value['stock_type'],
                default_code=value['default_code'],
                code_catalog_used=value['code_catalog_used'],
                unspsc_code_id=value['unspsc_code_id'],
                product_description=value['product_description'],
                product_udm=value['product_udm'],
                property_cost_method=value['property_cost_method'],
                quantity_product_hand="{:.2f}".format(value['quantity_product_hand']),
                standard_price="{:.2f}".format(value['standard_price']),
                total="{:.2f}".format(value['total']),
            )
        return raw

    def get_filename(self):
        year, month, day = self.obj.date_end.strftime('%Y/%m/%d').split('/')
        return 'LE{vat}{period_year}{period_month}{period_day}030700{eeff_oportunity}{state_send}{has_info}11.txt'.format(
            vat=self.obj.company_id.vat,
            period_year=year,
            period_month=month,
            period_day=day,
            eeff_oportunity=self.obj.eeff_presentation_opportunity,
            state_send=self.obj.state_send or '',
            has_info=int(bool(self.data))
        )