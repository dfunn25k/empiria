from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError, ValidationError
from ..reports.retention_report_txt import RetentionReportTxt
from ..reports.retention_report_excel import RetentionReportExcel
import base64

MONTHS = [
    ("1", "Enero"),
    ("2", "Febrero"),
    ("3", "Marzo"),
    ("4", "Abril"),
    ("5", "Mayo"),
    ("6", "Junio"),
    ("7", "Julio"),
    ("8", "Agosto"),
    ("9", "Septiembre"),
    ("10", "Octubre"),
    ("11", "Noviembre"),
    ("12", "Diciembre"),
]

READONLY_FIELD_STATES = {state: [("readonly", True)] for state in ["load", "cancel"]}


class RetentionFileTxt(models.Model):
    _name = "retention.file.txt"
    _description = "Generar Archivo TXT PDT 626"
    _check_company_auto = True
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date, name DESC"

    state = fields.Selection(
        selection=[
            ("draft", "Borrador"),
            ("load", "Generado"),
            ("cancel", "Cancelado"),
        ],
        string="Estado",
        default="draft",
        tracking=True,
        required=True,
        help=(
            "Indica el estado actual del registro: \n"
            "- 'Borrador': Estado inicial cuando el registro está en borrador.\n"
            "- 'Generado': Estado cuando el archivo TXT ha sido generado.\n"
            "- 'Cancelado': Estado cuando el registro ha sido cancelado."
        ),
    )

    name = fields.Char(
        string="Número de Comprobante de Retención",
        required=True,
        readonly=True,
        store=True,
        copy=False,
        tracking=True,
        default=lambda self: _("Nuevo"),
        index=True,
        help="Número único asignado al comprobante de retención. Se genera automáticamente.",
    )

    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Compañía",
        default=lambda self: self.env.company,
        readonly=True,
        index=True,
        states=READONLY_FIELD_STATES,
        help="Compañía a la que pertenece este registro.",
    )

    year = fields.Selection(
        selection=[
            (str(year), str(year)) for year in range(2020, fields.Date.today().year + 1)
        ],
        string="Año",
        default=lambda self: str(fields.Date.today().year),
        required=True,
        tracking=True,
        states=READONLY_FIELD_STATES,
        help="Seleccione el año del período, comenzando desde 2020.",
    )

    period = fields.Selection(
        selection=MONTHS,
        string="Período",
        default=lambda self: str(fields.Date.today().month),
        required=True,
        tracking=True,
        states=READONLY_FIELD_STATES,
        help="Seleccione el mes correspondiente al período (1 al 12).",
    )

    date = fields.Date(
        string="Fecha",
        default=fields.Date.context_today,
        required=True,
        readonly=True,
        states=READONLY_FIELD_STATES,
        help="Fecha en la que se generó este registro. Por defecto es la fecha actual.",
    )

    today_date = fields.Date(
        string="Fecha de Generación",
        readonly=True,
        states=READONLY_FIELD_STATES,
        help="Fecha actual para referencia.",
    )

    xls_filename_retention = fields.Char(
        string="Nombre del archivo Excel",
        help="Nombre del archivo generado para el reporte en formato Excel.",
        states=READONLY_FIELD_STATES,
    )

    xls_binary_retention = fields.Binary(
        string="Reporte en Excel",
        help="Archivo binario que contiene el reporte en formato Excel.",
        states=READONLY_FIELD_STATES,
    )

    txt_filename_retention = fields.Char(
        string="Nombre del Archivo TXT",
        states=READONLY_FIELD_STATES,
        help="Nombre del archivo TXT generado para la retención.",
    )

    txt_binary_retention = fields.Binary(
        string="Archivo TXT de Retención",
        states=READONLY_FIELD_STATES,
        help="Archivo generado en formato TXT para la declaración de retención.",
    )

    error_dialog = fields.Text(
        string="Mensaje de Error",
        readonly=True,
        states=READONLY_FIELD_STATES,
        help="Mensaje de error que se muestra en caso de que ocurra un problema durante la generación del archivo.",
    )

    record_ids = fields.Many2many(
        comodel_name="account.move.line",
        string="Comprobantes de Retención",
        required=True,
        states=READONLY_FIELD_STATES,
        help="Líneas de comprobantes de retención que se incluirán en el archivo TXT.",
        # domain=[("move_id.move_type", "in", ["in_invoice", "in_refund"])],
    )

    # ---------------------------------------------------------------------------- #
    #                            TODO - METODO CONSTRINT                           #
    # ---------------------------------------------------------------------------- #
    @api.constrains("record_ids")
    def _check_unique_record_ids(self):
        # Buscar todos los registros que ya están en uso
        for record in self:
            all_other_records = self.search(
                [
                    ("id", "!=", record.id),
                    ("state", "!=", "cancel"),
                ]
            )

            if all_other_records:
                used_record_ids = all_other_records.mapped("record_ids")

                # Verificar si hay algún registro repetido
                for record_id in record.record_ids:
                    if record_id in used_record_ids:
                        raise ValidationError(
                            "El asiento contable %s ya está asignado a otro registro. No se pueden repetir los apuntes contables."
                            % record_id.name,
                        )

    # ---------------------------------------------------------------------------- #
    #                                TODO - METODOS                                #
    # ---------------------------------------------------------------------------- #
    def split_string_by_hyphen(self, value):
        """
        Divide un string en dos partes usando el primer guion encontrado.
        Devuelve la primera parte hasta el guion y la segunda parte después del guion.

        Args:
            value (str): El string a dividir.

        Returns:
            tuple: Dos cadenas de texto, la primera antes del guion y la segunda después del guion.
        """
        if not isinstance(value, str) or not value:
            raise ValidationError("El valor debe ser un string no vacío.")

        # Divide el string en dos partes usando el primer guion encontrado
        parts = value.split("-", 1)

        if len(parts) < 2:
            raise ValidationError("El campo debe contener exactamente un '-'.")

        # Retorna las partes antes y después del guion como cadenas de texto
        before_hyphen = " ".join(parts[0].split()[:4])
        after_hyphen = " ".join(parts[1].split()[:8])

        return before_hyphen, after_hyphen

    def truncate_field_value(self, value, mode=None, length=None):
        """
        Trunca o ajusta el valor de un campo según el modo especificado.

        Args:
            value (str): El valor del campo a procesar.
            mode (str): Modo de truncamiento. Puede ser "exact" para una longitud exacta o
                        "max" para una longitud máxima permitida. El valor por defecto es "exact".
            length (int): La longitud objetivo del valor. El valor por defecto es 40.

        Returns:
            str: El valor procesado según el modo especificado.

        Raises:
            ValueError: Si el valor no es una cadena de texto o si el modo no es válido.
        """
        if not value:
            return ""

        if mode == "exact":
            return value[:length] if len(value) == length else ""
        elif mode == "max":
            return value[:length] if len(value) > length else value
        else:
            raise ValueError("El modo debe ser 'exact' o 'max'.")

    def format_date_dd_mm_yyyy(self, date_value):
        """
        Convierte una fecha en el formato 'dd/mm/aaaa'.

        Args:
            date_value (datetime.date): La fecha a formatear.

        Returns:
            str: La fecha formateada en 'dd/mm/aaaa'. Si la fecha es nula, retorna una cadena vacía.
        """
        if not date_value:
            return ""

        return date_value.strftime("%d/%m/%Y")

    def format_amount(self, amount):
        """
        Formatea el monto para que tenga como máximo 12 enteros y 2 decimales.
        El resultado no contiene comas.

        Args:
            amount (float): El importe a formatear.

        Returns:
            str: El importe formateado como string, o una cadena vacía si no es válido.
        """
        if not amount:
            return ""

        # Convierte el monto a un string sin comas y con dos decimales
        formatted_amount = f"{amount:.2f}".replace(",", "")

        # Verifica que el monto no exceda los 12 enteros
        if len(formatted_amount.split(".")[0]) > 12:
            raise ValueError("El importe excede el límite de 12 enteros.")

        return formatted_amount

    def action_generate_report(self, data_aml):
        list_data = []

        # Inicializar el campo de error para limpiar cualquier mensaje previo
        self.write({"error_dialog": ""})

        try:
            for obj_move_line in data_aml:
                # Obtener y truncar el RUC del proveedor
                ruc_proveedor = self.truncate_field_value(
                    obj_move_line.partner_id.vat, "exact", 11
                )

                # Inicializar valores por defecto para el proveedor
                razon_social = apellido_paterno = apellido_materno = nombres = ""

                # Si el tipo de identificación es RUC (Código '6')
                if (
                    obj_move_line.partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code
                    == "6"
                ):
                    # Truncar los campos relacionados con el nombre del proveedor
                    razon_social = self.truncate_field_value(
                        obj_move_line.partner_id.name, "max", 40
                    )
                    apellido_paterno = self.truncate_field_value(
                        obj_move_line.partner_id.first_name, "max", 20
                    )
                    apellido_materno = self.truncate_field_value(
                        obj_move_line.partner_id.second_name, "max", 20
                    )
                    nombres = self.truncate_field_value(
                        obj_move_line.partner_id.partner_name, "max", 20
                    )

                # Separar la serie y número de la retención
                serie_retencion, numero_retencion = self.split_string_by_hyphen(
                    obj_move_line.name
                )

                # Formatear la fecha de emisión de la retención y el monto
                fecha_emision_retencion = self.format_date_dd_mm_yyyy(
                    obj_move_line.date
                )
                monto_pago_retencion = self.format_amount(obj_move_line.credit)

                # Obtener el tipo de pago
                tipo_pago = (
                    obj_move_line.supplier_invoice_id.l10n_latam_document_type_id.code
                )

                # Separar la serie y número del pago
                serie_pago, numero_pago = self.split_string_by_hyphen(
                    obj_move_line.supplier_invoice_id.ref
                )

                # Formatear la fecha de emisión y el valor total del pago
                fecha_emision_pago = self.format_date_dd_mm_yyyy(
                    obj_move_line.supplier_invoice_id.invoice_date
                )
                valor_total_pago = self.format_amount(
                    obj_move_line.amount_total_converted
                )

                # Crear el diccionario con los valores formateados
                values = {
                    "ruc_proveedor": ruc_proveedor,
                    "razon_social": razon_social,
                    "apellido_paterno": apellido_paterno,
                    "apellido_materno": apellido_materno,
                    "nombres": nombres,
                    "serie_retencion": serie_retencion,
                    "numero_retencion": numero_retencion,
                    "fecha_emision_retencion": fecha_emision_retencion,
                    "valor_total_pago": valor_total_pago,
                    "tipo_pago": tipo_pago,
                    "serie_pago": serie_pago,
                    "numero_pago": numero_pago,
                    "fecha_emision_pago": fecha_emision_pago,
                    "monto_pago_retencion": monto_pago_retencion,
                }
                list_data.append(values)

            self.action_generate_reports(list_data)
        except (ValueError, OSError) as e:
            # Captura errores de valor y del sistema, actualiza el campo de error
            self.write({"error_dialog": f"Error: {str(e)}"})
        except Exception as e:
            # Captura cualquier otro error inesperado
            self.write(
                {"error_dialog": f"Error inesperado al generar el reporte: {str(e)}"}
            )

    # Método auxiliar para codificar contenido en base64
    def encode_base64(self, content, file_type=None):
        if content:
            return base64.b64encode(content.encode() if file_type == "txt" else content)
        return b"\n"  # Usar b"\n" para retornar bytes vacíos en lugar de una cadena

    def action_generate_reports(self, list_data):
        # Generar el reporte de retención en formato Excel
        retention_report_xls = RetentionReportExcel(self, list_data)
        retention_content_xls = retention_report_xls.get_content()

        # Generar el reporte de retención en formato TXT
        retention_report_txt = RetentionReportTxt(self, list_data)
        retention_content_txt = retention_report_txt.get_content()

        # Preparar los datos para actualizar el registro actual
        data = {
            "xls_filename_retention": retention_report_xls.get_filename(),
            "xls_binary_retention": self.encode_base64(retention_content_xls, "xlsx"),
            "txt_filename_retention": retention_report_txt.get_filename(),
            "txt_binary_retention": self.encode_base64(retention_content_txt, "txt"),
            "today_date": fields.Date.today(),
            "state": "load",
        }

        # Actualizar el registro con los datos generados
        self.write(data)

    def get_next_transaction_code(self):
        """Obtiene el siguiente código de transacción a partir de la secuencia 'retention.report'."""
        return self.env["ir.sequence"].next_by_code("retention.report") or _("Nuevo")

    # ---------------------------------------------------------------------------- #
    #                          TODO - METODOS DE LA CLASE                          #
    # ---------------------------------------------------------------------------- #
    @api.model
    def create(self, vals):
        """Crea un nuevo registro y asigna un número único al campo 'name' si no está presente."""

        # Asigna el próximo código de transacción si 'name' es 'Nuevo' o no está definido
        if vals.get("name", _("Nuevo")) == _("Nuevo"):
            vals["name"] = self.get_next_transaction_code()

        return super(RetentionFileTxt, self).create(vals)

    def unlink(self):
        """
        Sobrescribe el método unlink para evitar la eliminación de registros en estado 'load'.
        Solo se permite la eliminación cuando el registro está en estado 'Borrador'.
        """
        for record in self:
            if record.state == "load":
                raise UserError(
                    "No se puede eliminar este registro mientras esté en estado 'Generado'. "
                    "Regrese el estado a 'Borrador' para permitir la eliminación."
                )

        return super(RetentionFileTxt, self).unlink()

    # ---------------------------------------------------------------------------- #
    #                              TODO - ACCION BOTON                             #
    # ---------------------------------------------------------------------------- #
    def action_report(self):
        """
        Genera el reporte TXT de retención basado en los comprobantes seleccionados.
        En caso de error, muestra un mensaje indicando la necesidad de contactar al administrador.
        """
        for record in self:
            try:
                # Obtener los registros de líneas de asientos contables seleccionados
                selected_records = record.record_ids

                # Generar el reporte utilizando los registros seleccionados
                self.action_generate_report(selected_records)

            except Exception as e:
                # Lanzar un mensaje de error específico si ocurre una excepción
                raise ValidationError(
                    _(
                        "Se produjo un error al generar el reporte. Por favor, contacte al administrador del sistema.\nDetalles del error: %s"
                    )
                    % str(e)
                )

    def action_rollback(self):
        """
        Método para revertir el estado del registro a 'draft' (borrador).
        """
        for record in self:
            record.write(
                {
                    "state": "draft",
                    "xls_filename_retention": False,
                    "xls_binary_retention": False,
                    "txt_filename_retention": False,
                    "txt_binary_retention": False,
                    "today_date": False,
                    "error_dialog": False,
                }
            )

    def action_cancel(self):
        """
        Método que cambia el estado del registro a 'cancel'.
        """
        for record in self:
            record.write({"state": "cancel"})
