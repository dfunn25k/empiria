from io import BytesIO

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter


class RetentionReportExcel(object):
    def __init__(self, obj, data):
        self.obj = obj
        self.data = data

    def get_content(self):
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {"in_memory": True})

        # ---------------------------------------------------------------------------- #
        #                         TODO - COLORES PERSONALIZADOS                        #
        # ---------------------------------------------------------------------------- #
        bg_odoo = "#684C60"
        bg_white = "#FFFFFF"
        font_white = "#FFFFFF"
        font_black = "#000000"

        # ---------------------------------------------------------------------------- #
        #                                TODO - ESTILOS                                #
        # ---------------------------------------------------------------------------- #
        header_style = workbook.add_format(
            {
                "bold": True,
                "font_color": font_white,
                "bg_color": bg_odoo,
                "align": "center",
                "valign": "vcenter",
                "font_size": 11,
                "font_name": "Arial Narrow",
                "border": 1,
                "border_color": "black",
            }
        )

        text_style = workbook.add_format(
            {
                "bold": False,
                "font_color": font_black,
                "bg_color": bg_white,
                "align": "left",
                "valign": "vcenter",
                "font_size": 11,
                "font_name": "Arial Narrow",
                "border": 1,
                "border_color": "black",
            }
        )

        currency_style = workbook.add_format(
            {
                "num_format": "#,##0.00",
                "bold": False,
                "font_color": font_black,
                "bg_color": bg_white,
                "align": "right",
                "valign": "vcenter",
                "font_size": 11,
                "font_name": "Arial Narrow",
                "border": 1,
                "border_color": "black",
            }
        )

        date_style = workbook.add_format(
            {
                "num_format": "dd/mm/yyyy",
                "bold": False,
                "font_color": font_black,
                "bg_color": bg_white,
                "align": "center",
                "valign": "vcenter",
                "font_size": 11,
                "font_name": "Arial Narrow",
                "border": 1,
                "border_color": "black",
            }
        )

        worksheet = workbook.add_worksheet("Reporte de Retenciones")

        # Encabezados
        headers = [
            "Fila",
            "RUC del proveedor",
            "Razón social",
            "Apellido paterno",
            "Apellido materno",
            "Nombres",
            "Serie del comprobante de retención",
            "Número de comprobante de retención",
            "Fecha de emisión del comprobante de emisión",
            "Valor total del comprobante de pago",
            "Tipo del comprobante de pago",
            "Serie del comprobante de pago",
            "Número del comprobante de pago",
            "Fecha de emisión del comprobante de pago",
            "Monto de pago del comprobante de retención",
        ]

        for col_num, header in enumerate(headers):
            worksheet.write(0, col_num, header, header_style)
            worksheet.set_column(col_num, col_num, len(header) + 2)

        # Contenido de la tabla
        for i, value in enumerate(self.data, start=1):
            worksheet.write(i, 0, i, text_style)  # Fila
            worksheet.write(i, 1, value["ruc_proveedor"], text_style)
            worksheet.write(i, 2, value["razon_social"], text_style)
            worksheet.write(i, 3, value["apellido_paterno"], text_style)
            worksheet.write(i, 4, value["apellido_materno"], text_style)
            worksheet.write(i, 5, value["nombres"], text_style)
            worksheet.write(i, 6, value["serie_retencion"], text_style)
            worksheet.write(i, 7, value["numero_retencion"], text_style)
            worksheet.write(i, 8, value["fecha_emision_retencion"], date_style)
            worksheet.write(i, 9, value["valor_total_pago"], currency_style)
            worksheet.write(i, 10, value["tipo_pago"], text_style)
            worksheet.write(i, 11, value["serie_pago"], text_style)
            worksheet.write(i, 12, value["numero_pago"], text_style)
            worksheet.write(i, 13, value["fecha_emision_pago"], date_style)
            worksheet.write(i, 14, value["monto_pago_retencion"], currency_style)

        workbook.close()
        output.seek(0)
        return output.read()

    def get_filename(self):
        # Define el formato base
        format_code = "0626"

        # Obtiene los valores necesarios para construir el nombre del archivo
        company_vat = self.obj.company_id.vat or ""
        year = str(self.obj.year) or ""
        period = str(self.obj.period).zfill(2) or ""

        # Construye el nombre del archivo con el formato requerido
        filename = f"{format_code}{company_vat}{year}{period}.xlsx"

        return filename
