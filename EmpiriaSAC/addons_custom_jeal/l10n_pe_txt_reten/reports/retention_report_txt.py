class RetentionReportTxt:
    def __init__(self, obj, data):
        self.obj = obj
        self.data = data

    def get_content(self):
        template = (
            "{ruc_proveedor}|{razon_social}|{apellido_paterno}|{apellido_materno}|{nombres}|"
            "{serie_retencion}|{numero_retencion}|{fecha_emision_retencion}|{valor_total_pago}|"
            "{tipo_pago}|{serie_pago}|{numero_pago}|{fecha_emision_pago}|{monto_pago_retencion}|\r\n"
        )

        # Utilizar una lista para acumular las líneas en lugar de concatenar strings
        content_lines = [
            template.format(
                ruc_proveedor=value.get("ruc_proveedor", ""),
                razon_social=value.get("razon_social", ""),
                apellido_paterno=value.get("apellido_paterno", ""),
                apellido_materno=value.get("apellido_materno", ""),
                nombres=value.get("nombres", ""),
                serie_retencion=value.get("serie_retencion", ""),
                numero_retencion=value.get("numero_retencion", ""),
                fecha_emision_retencion=value.get("fecha_emision_retencion", ""),
                valor_total_pago=value.get("valor_total_pago", ""),
                tipo_pago=value.get("tipo_pago", ""),
                serie_pago=value.get("serie_pago", ""),
                numero_pago=value.get("numero_pago", ""),
                fecha_emision_pago=value.get("fecha_emision_pago", ""),
                monto_pago_retencion=value.get("monto_pago_retencion", ""),
            )
            for value in self.data
        ]

        # Unir las líneas en un solo string
        return "".join(content_lines)

    def get_filename(self):
        """
        Genera el nombre del archivo TXT de retención según el formato 0626 requerido.
        El formato del nombre es:
        - 0626  : Código fijo para identificar el tipo de archivo.
        - VAT   : Número de RUC de la empresa.
        - AÑO   : Año seleccionado.
        - MES   : Período (mes) seleccionado.

        Returns:
            str: Nombre del archivo TXT generado.
        """
        # Define el formato base
        format_code = "0626"

        # Obtiene los valores necesarios para construir el nombre del archivo
        company_vat = self.obj.company_id.vat or ""
        year = str(self.obj.year) or ""
        period = str(self.obj.period).zfill(2) or ""

        # Construye el nombre del archivo con el formato requerido
        filename = f"{format_code}{company_vat}{year}{period}.txt"

        return filename
