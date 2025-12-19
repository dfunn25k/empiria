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

STATE_SELECTION = [
    ("draft", "Borrador"),
    ("waiting", "Esperando otra operación"),
    ("confirmed", "Esperando"),
    ("assigned", "Listo"),
    ("done", "Realizado"),
    ("cancel", "Cancelado"),
]

OPERATION_TYPE_SELECTION = [
    ("incoming", "Recibo"),
    ("outgoing", "Entrega"),
    ("internal", "Transferencia interna"),
    ("mrp_operation", "Fabricación"),
]


class ReportInternalTransfers(models.TransientModel):
    _name = "report.internal.transfers"
    _description = "Informe Detalle de Transferencias Internas"

    # ---------------------------------------------------------------------------- #
    #                                 TODO - CAMPOS                                #
    # ---------------------------------------------------------------------------- #
    type = fields.Selection(
        [
            ("date", "Fecha"),
            ("transfer", "Transferencia"),
        ],
        string="Filtrar por",
        default="date",
        required=True,
    )

    date_start = fields.Date(
        "Fecha Inicio",
        default=fields.Date.today,
    )

    date_end = fields.Date(
        "Fecha Fin",
        default=fields.Date.today,
    )

    types_operations_ids = fields.Many2many(
        comodel_name="stock.picking.type",
        string="Tipos de Operaciones",
        domain="[('company_id', '=?', company_id), ('code', '=?', operation_type)]",
        required=True,
    )

    transferencia_ids = fields.Many2many(
        comodel_name="stock.picking",
        string="Transferencia",
        domain="[('state', '=?', state), ('company_id', '=?', company_id), ('picking_type_id', 'in', types_operations_ids),]",
    )

    state = fields.Selection(
        selection=STATE_SELECTION,
        string="Estado",
        default="done",
        required=True,
    )

    operation_type = fields.Selection(
        selection=OPERATION_TYPE_SELECTION,
        string="Tipo de operación",
        default="internal",
        required=True,
    )

    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Compañía",
        required=True,
        default=lambda self: self.env.user.company_id,
    )

    product_ids = fields.Many2many(
        comodel_name="product.product",
        string="Productos",
    )

    # ---------------------------------------------------------------------------- #
    #                              TODO - VALIDACIONES                             #
    # ---------------------------------------------------------------------------- #
    @api.onchange("type")
    def onchange_type(self):
        if self.type == "date":
            self.transferencia_ids = False
        elif self.type == "transfer":
            self.date_start = False
            self.date_end = False

    @api.onchange("company_id", "state", "operation_type")
    def onchange_reset_transferencia(self):
        if self.company_id and self._origin.company_id != self.company_id:
            self.transferencia_ids = False

        if self.state and self._origin.state != self.state:
            self.transferencia_ids = False

        if self.operation_type and self._origin.operation_type != self.operation_type:
            self.transferencia_ids = False

    @api.onchange("company_id", "operation_type")
    def _onchange_reset_types_operations_ids(self):
        if self.company_id and self.operation_type:
            data_stock_picking_type = self._get_data_stock_picking_type()

            if data_stock_picking_type:
                self.types_operations_ids = data_stock_picking_type.ids
            else:
                self.types_operations_ids = False

    # ---------------------------------------------------------------------------- #
    #                                TODO - METODOS                                #
    # ---------------------------------------------------------------------------- #
    def _get_formatted_dates(self):
        formatted_start_date = (
            fields.Date.to_string(self.date_start) if self.date_start else ""
        )
        formatted_end_date = (
            fields.Date.to_string(self.date_end) if self.date_end else ""
        )
        return formatted_start_date, formatted_end_date

    def _get_data_stock_picking_type(self):
        domain_picking_type = [
            ("company_id", "=", self.company_id.id),
            ("active", "=", True),
            ("code", "=", self.operation_type),
        ]
        return self.env["stock.picking.type"].search(domain_picking_type)

    def _get_data_stock_picking(self):
        domain_picking = []

        if self.transferencia_ids:
            domain_picking.append(("id", "in", self.transferencia_ids.ids))
        elif self.date_start and self.date_end:
            if self.date_start > self.date_end:
                raise ValidationError(
                    "La fecha de inicio no puede ser mayor que la fecha de fin."
                )

            additional_domain = [
                ("company_id", "=", self.company_id.id),
                ("state", "=", self.state),
                ("date_done", ">=", self.date_start),
                ("date_done", "<=", self.date_end),
                ("picking_type_id", "in", self.types_operations_ids.ids),
            ]
            domain_picking.extend(additional_domain)
        return self.env["stock.picking"].search(
            domain_picking,
            order="name desc",
        )

    def _get_data_stock_move(self):
        data_stock_picking = self._get_data_stock_picking()
        domain = [("picking_id", "in", data_stock_picking.ids)]

        if self.product_ids:
            domain.append(("product_id", "in", self.product_ids.ids))

        return self.env["stock.move"].search(
            domain,
            order="picking_type_id desc",
        )

    def _get_selection_display_name(self, data_selection, state_value):
        return next(
            (label for value, label in data_selection if value == state_value), ""
        )

    def _get_filename(self):
        now = datetime.now()
        date = now.strftime("%d-%m-%Y")
        operation_type = self._get_selection_display_name(
            OPERATION_TYPE_SELECTION, self.operation_type
        )
        return f"Reporte_detallado_{operation_type}_{date}"

    # Método para validar y retornar un valor nulo o vacío si no existe
    def _validate_field_value(self, value, empty_value=""):
        return value if value else empty_value

    def _get_data(self):
        form_data = []
        formatted_start_date, formatted_end_date = self._get_formatted_dates()
        data_stock_move = self._get_data_stock_move()

        for line in data_stock_move:
            picking_id = line.picking_id
            product_id = line.product_id

            # Buscar la última compra del producto
            last_product_purchase = self.env["purchase.order.line"].search(
                [
                    ("state", "in", ["purchase", "done"]),
                    ("product_id", "=", product_id.id),
                ],
                order="id DESC",
                limit=1,
            )

            # last_product_purchase = self.env["product.supplierinfo"].search(
            #     [("product_tmpl_id", "=", product_id.product_tmpl_id.id)],
            #     order="create_date desc",
            #     limit=1,
            # )

            state_display_name = self._get_selection_display_name(
                STATE_SELECTION, picking_id.state
            )

            data = {
                # --------------------------------- CABECERA --------------------------------- #
                "compania": self._validate_field_value(picking_id.company_id.name),
                "contacto": self._validate_field_value(picking_id.partner_id.name),
                "referencia": self._validate_field_value(picking_id.name),
                "tipo_operacion": self._validate_field_value(
                    picking_id.picking_type_id.display_name
                ),
                "fecha_efectiva": self._validate_field_value(picking_id.date_done),
                "documento_origen": self._validate_field_value(picking_id.origin),
                "ubicacion_destino": self._validate_field_value(
                    picking_id.location_dest_id.complete_name
                ),
                "ubicacion_origen": self._validate_field_value(
                    picking_id.location_id.complete_name
                ),
                "estado": self._validate_field_value(state_display_name),
                # --------------------------------- OPERACION -------------------------------- #
                "categoria_producto": self._validate_field_value(
                    product_id.categ_id.display_name
                ),
                "producto": self._validate_field_value(product_id.display_name),
                "realizado": self._validate_field_value(line.quantity_done),
                "udm": self._validate_field_value(line.product_uom.name),
                # ------------------------------- ULTIMA COMPRA ------------------------------ #
                "referencia_pedido": self._validate_field_value(
                    last_product_purchase.order_id.name
                ),
                "fecha_confirmacion": self._validate_field_value(
                    last_product_purchase.date_approve
                ),
                "proveedor": self._validate_field_value(
                    last_product_purchase.partner_id.name
                ),
                "cantidad_total": self._validate_field_value(
                    last_product_purchase.product_uom_qty
                ),
                "precio_unitario": self._validate_field_value(
                    last_product_purchase.price_unit
                ),
                "impuestos": self._validate_field_value(
                    last_product_purchase.taxes_id.display_name
                ),
                "moneda": self._validate_field_value(
                    last_product_purchase.order_id.currency_id.name
                ),
                # "fecha": self._validate_field_value(last_product_purchase.create_date),
            }
            form_data.append(data)

        data = {
            "ids": self,
            "model": self._name,
            "form_data": form_data,
            "start_date": formatted_start_date,
            "end_date": formatted_end_date,
        }
        return data

    # ---------------------------------------------------------------------------- #
    #                                 TODO - BOTON                                 #
    # ---------------------------------------------------------------------------- #
    def action_search_salida(self):
        data = self._get_data()
        return self.env.ref(
            "detail_report_internal_transfers.action_report_action_report_internal_transfers"
        ).report_action(self, data=data)

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
                "options": json.dumps(data, default=date_utils.json_default),
                "output_format": "xlsx",
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

        # Establecer el alto de las filas 1 a 3 (en este caso, 25 unidades) usando un bucle
        worksheet.set_row(0, 35)
        for row in range(8):
            worksheet.set_row(row + 1, 20)

        # ---------------------------------------------------------------------------- #
        #                                   Compañia                                   #
        # ---------------------------------------------------------------------------- #
        worksheet.merge_range(
            "A1:F1",
            "REPORTE DETALLADO DE TRANSFERENCIAS INTERNAS",
            style_title_headboard,
        )

        worksheet.merge_range("A2:B2", "Fecha consultada: ", style_head_headboard_1)

        worksheet.write(1, 2, "Del: ", style_head_headboard_1)
        worksheet.write(1, 3, data["start_date"], style_date)

        worksheet.write(1, 4, "Hasta: ", style_head_headboard_1)
        worksheet.write(1, 5, data["end_date"], style_date)

        worksheet.merge_range("O2:U2", "Ultima compra", style_title_headboard)

        # ---------------------------------------------------------------------------- #
        #                                   Cabecera                                   #
        # ---------------------------------------------------------------------------- #
        worksheet.write(2, 0, "FILA", style_headboard)
        worksheet.write(2, 1, "COMPAÑIA", style_headboard)
        worksheet.write(2, 2, "CONTACTO", style_headboard)
        worksheet.write(2, 3, "TRANSFERENCIA", style_headboard)
        worksheet.write(2, 4, "TIPO DE OPERACIÓN", style_headboard)
        worksheet.write(2, 5, "FECHA EFECTIVA", style_headboard)
        worksheet.write(2, 6, "DOCUMENTO ORIGEN", style_headboard)
        worksheet.write(2, 7, "DE", style_headboard)
        worksheet.write(2, 8, "PARA", style_headboard)
        worksheet.write(2, 9, "ESTADO", style_headboard)
        # --------------------------------- OPERACIÓN -------------------------------- #
        worksheet.write(2, 10, "CATEGORIA DEL PRODUCTO", style_headboard)
        worksheet.write(2, 11, "PRODUCTO", style_headboard)
        worksheet.write(2, 12, "REALIZADO", style_headboard)
        worksheet.write(2, 13, "UNIDAD DE MEDIDA", style_headboard)
        # ------------------------------- ULTIMA COMPRA ------------------------------ #
        worksheet.write(2, 14, "REFERENCIA DEL PEDIDO", style_headboard)
        worksheet.write(2, 15, "FECHA CONFIRMACIÓN", style_headboard)
        worksheet.write(2, 16, "PROVEEDOR", style_headboard)
        worksheet.write(2, 17, "CANTIDAD TOTAL", style_headboard)
        worksheet.write(2, 18, "PRECIO UNITARIO", style_headboard)
        worksheet.write(2, 19, "IMPUESTOS", style_headboard)
        worksheet.write(2, 20, "MONEDA", style_headboard)

        # ---------------------------------------------------------------------------- #
        #                                     Datos                                    #
        # ---------------------------------------------------------------------------- #
        fila = 3
        columna = 0
        num_reg = 1

        for line in data["form_data"]:
            worksheet.write(fila, columna, num_reg, style_body)
            worksheet.write(fila, columna + 1, line["compania"], style_body)
            worksheet.write(fila, columna + 2, line["contacto"], style_body)
            worksheet.write(fila, columna + 3, line["referencia"], style_body)
            worksheet.write(fila, columna + 4, line["tipo_operacion"], style_body)
            worksheet.write(fila, columna + 5, line["fecha_efectiva"], style_date)
            worksheet.write(fila, columna + 6, line["documento_origen"], style_body)
            worksheet.write(fila, columna + 7, line["ubicacion_origen"], style_body)
            worksheet.write(fila, columna + 8, line["ubicacion_destino"], style_body)
            worksheet.write(fila, columna + 9, line["estado"], style_body)
            # --------------------------------- OPERACIÓN -------------------------------- #
            worksheet.write(fila, columna + 10, line["categoria_producto"], style_body)
            worksheet.write(fila, columna + 11, line["producto"], style_body)
            worksheet.write(fila, columna + 12, line["realizado"], style_number)
            worksheet.write(fila, columna + 13, line["udm"], style_body)
            # ------------------------------- ULTIMA COMPRA ------------------------------ #
            worksheet.write(fila, columna + 14, line["referencia_pedido"], style_body)
            worksheet.write(fila, columna + 15, line["fecha_confirmacion"], style_date)
            worksheet.write(fila, columna + 16, line["proveedor"], style_body)
            worksheet.write(fila, columna + 17, line["cantidad_total"], style_number)
            worksheet.write(fila, columna + 18, line["precio_unitario"], style_number)
            worksheet.write(fila, columna + 19, line["impuestos"], style_body)
            worksheet.write(fila, columna + 20, line["moneda"], style_body)

            fila += 1
            num_reg += 1

        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
