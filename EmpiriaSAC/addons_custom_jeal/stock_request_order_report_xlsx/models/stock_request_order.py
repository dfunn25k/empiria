from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime

import json
import io
from odoo.tools import date_utils

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter

header = [
    "Fila",
    "Compañía",
    "Solicitud de existencias",
    "Pedido",
    "Producto",
    "Categoría",
    "Fecha prevista",
    "Política de Entrega",
    "Almacén",
    "Ubicación",
    "Ruta",
    "Área",  # STUDIO
    "Estado",  # STUDIO
    "Cant.",
    "Cant. a mano",  # STUDIO
    "Cant. en progreso",
    "Cant. finalizada",
    "Cant. cancelada",
    "Comentario",
    "Estado",
    "Observaciones",  # STUDIO
]


class StockRequestOrder(models.Model):
    _inherit = "stock.request.order"

    # ---------------------------------------------------------------------------- #
    #                                TODO - METODOS                                #
    # ---------------------------------------------------------------------------- #
    def _get_data_stock_request(self):
        domain_stock_request = [
            ("order_id", "=", self.id),
        ]
        return self.env["stock.request"].search(domain_stock_request)

    def __get_request_order_state(self):
        return self.env["stock.request"].fields_get(allfields=["state"])["state"][
            "selection"
        ]

    def __get_request_order_picking_policy(self):
        return self.env["stock.request"].fields_get(allfields=["picking_policy"])[
            "picking_policy"
        ]["selection"]

    def _get_selection_display_name(self, data_selection, state_value):
        return next(
            (label for value, label in data_selection if value == state_value), ""
        )

    # Método para validar y retornar un valor nulo o vacío si no existe
    def _validate_field(self, value, empty_value=""):
        return value if value else empty_value

    def _get_filename(self):
        now = datetime.now()
        date = now.strftime("%d-%m-%Y")
        name = self.name
        return f"Reporte_pedido_{name}_{date}"

    def _get_data(self):
        form_header = []
        form_data = []
        data_stock_request = self._get_data_stock_request()
        data_picking_policy_selection = self.__get_request_order_picking_policy()
        data_state_selection = self.__get_request_order_state()

        # --------------------------------- CABECERA --------------------------------- #
        for record in self:
            state_header = self._get_selection_display_name(
                data_state_selection, record.state
            )

            data_header = {
                "estado": self._validate_field(state_header),
                "pedido_existencia": self._validate_field(record.name),
                "fecha_prevista": self._validate_field(record.expected_date),
                "politica_entrega": self._validate_field(record.picking_policy),
                "almacen": self._validate_field(record.warehouse_id),
                "ubicacion": self._validate_field(record.location_id),
                "companhia": self._validate_field(record.company_id),
            }
            form_header.append(data_header)

        # --------------------------------- ELEMENTOS -------------------------------- #
        if data_stock_request:
            for line in data_stock_request:
                picking_policy = self._get_selection_display_name(
                    data_picking_policy_selection, line.picking_policy
                )
                state = self._get_selection_display_name(
                    data_state_selection, line.state
                )

                data = {
                    "companhia": self._validate_field(line.company_id.name),
                    "solicitud_existencia": self._validate_field(line.name),
                    "pedido": self._validate_field(line.order_id.name),
                    "producto": self._validate_field(line.product_id.display_name),
                    "categoria": self._validate_field(line.categ_id.name),
                    "fecha_prevista": self._validate_field(line.expected_date),
                    "politica_entrega": self._validate_field(picking_policy),
                    "almacen": self._validate_field(line.warehouse_id.name),
                    "ubicacion": self._validate_field(line.location_id.display_name),
                    "ruta": self._validate_field(line.route_id.name),
                    "area": self._validate_field(line.x_studio_rea_1),  # STUDIO
                    "estado_studio": self._validate_field(
                        line.x_studio_estado
                    ),  # STUDIO
                    "cant": self._validate_field(line.product_uom_qty),
                    "cant_mano": self._validate_field(
                        line.x_studio_cantidad_a_mano
                    ),  # STUDIO
                    "cant_progreso": self._validate_field(line.qty_in_progress),
                    "cant_finalizada": self._validate_field(line.qty_done),
                    "cant_cancelada": self._validate_field(line.qty_cancelled),
                    "comentario": self._validate_field(line.comment_editable),
                    "estado": self._validate_field(state),
                    "observaciones": self._validate_field(
                        line.x_studio_observaciones
                    ),  # STUDIO
                }
                form_data.append(data)

        data = {
            "ids": self,
            "model": self._name,
            "header": header,
            "form_header": form_header,
            "form_data": form_data,
        }
        return data

    # ---------------------------------------------------------------------------- #
    #                                 TODO - BOTON                                 #
    # ---------------------------------------------------------------------------- #
    def get_excel_report(self):
        data = self._get_data()
        return {
            "type": "ir.actions.report",
            "report_type": "xlsx",
            "data": {
                "model": data["model"],
                "output_format": "xlsx",
                "options": json.dumps(data, default=date_utils.json_default),
                "report_name": self._get_filename(),
            },
        }

    # ---------------------------------------------------------------------------- #
    #                             TODO - CONTENIDO XLXS                            #
    # ---------------------------------------------------------------------------- #
    def get_xlsx_report(self, data, response):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {"in_memory": True})

        # ---------------------------------------------------------------------------- #
        #                            COLORES PERSONALIZADOS                            #
        # ---------------------------------------------------------------------------- #
        bg_odoo = "#684C60"
        bg_white = "#FFFFFF"
        font_white = "#FFFFFF"
        font_black = "#000000"

        # ---------------------------------------------------------------------------- #
        #                                    ESTILOS                                   #
        # ---------------------------------------------------------------------------- #
        style_title_headboard = workbook.add_format(
            {
                "bold": True,
                "font_color": font_white,
                "bg_color": bg_odoo,
                "align": "center",
                "valign": "vcenter",
                "font_size": 20,
                "font_name": "Arial Narrow",
                "border": 1,
                "border_color": "black",
            }
        )

        style_head_headboard_1 = workbook.add_format(
            {
                "bold": True,
                "font_color": font_white,
                "bg_color": bg_odoo,
                "align": "right",
                "valign": "vcenter",
                "font_size": 11,
                "font_name": "Arial Narrow",
                "border": 1,
                "border_color": "black",
            }
        )

        style_head_headboard_2 = workbook.add_format(
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

        style_headboard = workbook.add_format(
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

        style_body = workbook.add_format(
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

        style_number = workbook.add_format(
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

        style_date = workbook.add_format(
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

        worksheet = workbook.add_worksheet("REPORTE DE TRANSFERENCIAS INTERNAS")
        worksheet.set_column("A:A", 10)
        worksheet.set_column("B:Y", 25)

        # Establecer el alto de las row_datas 1 a 3 (en este caso, 25 unidades) usando un bucle
        worksheet.set_row(0, 35)
        for row in range(8):
            worksheet.set_row(row + 1, 20)

        # ---------------------------------------------------------------------------- #
        #                                   Compañia                                   #
        # ---------------------------------------------------------------------------- #
        worksheet.merge_range(
            "A1:F1",
            "REPORTE PEDIDOS DE EXISTENCIA",
            style_title_headboard,
        )

        # ---------------------------------------------------------------------------- #
        #                                   Cabecera                                   #
        # ---------------------------------------------------------------------------- #
        row_header = 1
        column_header = 0

        for value in data["header"]:
            worksheet.write(row_header, column_header, value, style_headboard)
            column_header += 1

        # ---------------------------------------------------------------------------- #
        #                                     Datos                                    #
        # ---------------------------------------------------------------------------- #
        row_data = 2
        column_data = 0
        num_reg = 1

        for line in data["form_data"]:
            worksheet.write(row_data, column_data, num_reg, style_body)
            worksheet.write(row_data, column_data + 1, line["companhia"], style_body)
            worksheet.write(
                row_data, column_data + 2, line["solicitud_existencia"], style_body
            )
            worksheet.write(row_data, column_data + 3, line["pedido"], style_body)
            worksheet.write(row_data, column_data + 4, line["producto"], style_body)
            worksheet.write(row_data, column_data + 5, line["categoria"], style_body)
            worksheet.write(
                row_data, column_data + 6, line["fecha_prevista"], style_body
            )
            worksheet.write(
                row_data, column_data + 7, line["politica_entrega"], style_body
            )
            worksheet.write(row_data, column_data + 8, line["almacen"], style_body)
            worksheet.write(row_data, column_data + 9, line["ubicacion"], style_body)
            worksheet.write(row_data, column_data + 10, line["ruta"], style_body)
            worksheet.write(row_data, column_data + 11, line["area"], style_body)
            worksheet.write(
                row_data, column_data + 12, line["estado_studio"], style_body
            )
            worksheet.write(row_data, column_data + 13, line["cant"], style_body)
            worksheet.write(row_data, column_data + 14, line["cant_mano"], style_body)
            worksheet.write(
                row_data, column_data + 15, line["cant_progreso"], style_body
            )
            worksheet.write(
                row_data, column_data + 16, line["cant_finalizada"], style_body
            )
            worksheet.write(
                row_data, column_data + 17, line["cant_cancelada"], style_body
            )
            worksheet.write(row_data, column_data + 18, line["comentario"], style_body)
            worksheet.write(row_data, column_data + 19, line["estado"], style_body)
            worksheet.write(
                row_data, column_data + 20, line["observaciones"], style_body
            )

            row_data += 1
            num_reg += 1

        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
