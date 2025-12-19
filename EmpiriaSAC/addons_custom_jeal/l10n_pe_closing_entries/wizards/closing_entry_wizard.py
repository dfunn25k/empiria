from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError, ValidationError
from collections import defaultdict


class ClosingEntryWizard(models.TransientModel):
    _name = "closing.entry.wizard"
    _description = "Wizard para Asientos de Cierre Contable"

    date_from = fields.Date(
        string="Fecha de Inicio",
        required=True,
        help="Fecha de inicio para el cálculo de saldos.",
    )

    date_to = fields.Date(
        string="Fecha de Fin",
        required=True,
        help="Fecha final para el cálculo de saldos.",
    )

    closing_date = fields.Date(
        string="Fecha del Asiento de Cierre", required=True, default=fields.Date.today
    )

    journal_id = fields.Many2one(
        comodel_name="account.journal",
        string="Diario",
        required=True,
        domain=[("type", "=", "general")],
    )

    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Compañía",
        required=True,
        default=lambda self: self.env.company,
    )

    narration = fields.Char(
        string="Glosa",
        default="Asiento de cierre de ejercicio",
    )

    @api.constrains("date_from", "date_to")
    def _check_dates(self):
        """Valida que la fecha de inicio no sea posterior a la fecha de fin."""
        if self.date_from > self.date_to:
            raise UserError(
                _("La fecha de inicio no puede ser posterior a la fecha de fin.")
            )

    def _get_account_balances(self):
        """
        Obtiene los saldos de los apuntes contables agrupados por cuenta y moneda.

        Este método está optimizado para obtener todos los datos necesarios en una
        sola consulta a la base de datos utilizando `read_group`.

        :return: Una lista de diccionarios, donde cada diccionario representa
                 el saldo agrupado para una cuenta y moneda.
        :rtype: list
        """
        # --- Construcción del Dominio de Búsqueda ---
        # Un dominio bien definido es clave para el rendimiento y la precisión.
        # Cada condición se explica para mayor claridad.
        domain = [
            # 1. Filtro de Fechas: Solo apuntes dentro del período seleccionado.
            ("date", ">=", self.date_from),
            ("date", "<=", self.date_to),
            # 2. Filtro de Compañía: Asegura la multi-compañía.
            ("company_id", "=", self.company_id.id),
            # 3. Filtro de Estado: Solo apuntes en asientos publicados.
            ("parent_state", "=", "posted"),
            # 4. Filtros de Cuentas:
            #    - Excluir cuentas obsoletas.
            ("account_id.deprecated", "=", False),
            #    - Excluir cuentas de tipo 'vista' que no contienen apuntes.
            ("account_id.account_type", "!=", "view"),
            #    - **Importante**: Solo incluir cuentas que tienen una
            #      'cuenta de cierre' configurada. Esto define qué se va a cerrar.
            ("account_id.closing_account_id", "!=", False),
            #    - Excluir las cuentas que son, en sí mismas, un destino de cierre.
            ("account_id.is_closing_account", "=", False),
        ]

        # --- Ejecución de read_group ---
        # Agrupamos por cuenta y moneda para manejar correctamente la lógica multi-moneda.
        # El resultado ya nos da los saldos agregados por el motor de Odoo.
        grouped_balances = self.env["account.move.line"].read_group(
            domain,
            fields=["balance", "account_id", "currency_id"],
            groupby=["account_id", "currency_id"],
            lazy=False,  # lazy=False asegura que la consulta se ejecute y devuelva todos los resultados.
        )
        return grouped_balances

    def _prepare_move_lines(self, balances_for_currency, closing_map):
        """
        Prepara las líneas de asiento para un grupo de saldos de UNA SOLA MONEDA.

        Lógica de Agrupación:
        - Para una misma cuenta de cierre, agrupa por separado la suma de todas
        las contrapartidas que van al DEBE y todas las que van al HABER.
        """
        lines_vals_list = []

        # <-- LÓGICA CLAVE: Dos acumuladores para agrupar débitos y créditos por separado.
        counterpart_debits_total = defaultdict(float)
        counterpart_credits_total = defaultdict(float)

        for balance_data in balances_for_currency:
            balance = balance_data.get("balance", 0.0)
            if self.company_id.currency_id.is_zero(balance):
                continue

            account_id = balance_data["account_id"][0]

            # --- 1. Línea principal (la cuenta que se está cerrando) ---
            lines_vals_list.append(
                {
                    "account_id": account_id,
                    "debit": abs(balance) if balance < 0 else 0.0,
                    "credit": balance if balance > 0 else 0.0,
                    "name": self.narration,
                }
            )

            # --- 2. Acumulación SEPARADA para la contrapartida ---
            closing_account_id = closing_map.get(account_id)
            if not closing_account_id:
                continue

            if balance > 0:
                # Si el saldo original es POSITIVO (un Crédito), su contrapartida es un Débito.
                # Acumulamos en el diccionario de DÉBITOS.
                counterpart_debits_total[closing_account_id] += balance
            elif balance < 0:
                # Si el saldo original es NEGATIVO (un Débito), su contrapartida es un Crédito.
                # Acumulamos el valor absoluto en el diccionario de CRÉDITOS.
                counterpart_credits_total[closing_account_id] += abs(balance)

        # --- 3. Creación de las líneas de contrapartida del DEBE ---
        for closing_account_id, total_debit in counterpart_debits_total.items():
            if not self.company_id.currency_id.is_zero(total_debit):
                lines_vals_list.append(
                    {
                        "account_id": closing_account_id,
                        "debit": total_debit,
                        "credit": 0.0,
                        "name": f"Resultado del Ejercicio - {self.narration}",
                    }
                )

        # --- 4. Creación de las líneas de contrapartida del CRÉDITO ---
        for closing_account_id, total_credit in counterpart_credits_total.items():
            if not self.company_id.currency_id.is_zero(total_credit):
                lines_vals_list.append(
                    {
                        "account_id": closing_account_id,
                        "debit": 0.0,
                        "credit": total_credit,
                        "name": f"Resultado del Ejercicio - {self.narration}",
                    }
                )

        return lines_vals_list

    def action_generate_entries(self):
        """
        Acción principal que genera los asientos de cierre con referencias descriptivas.

        La lógica agrupa los saldos por múltiples criterios para crear un asiento
        de cierre para cada grupo resultante.
        Los criterios de agrupación son:
        1. Moneda del apunte.
        2. Grupo de Cuentas ('Balance' vs. 'Resultados').
        3. Signo del Saldo (Positivo vs. Negativo).
        """
        self.ensure_one()
        all_balances = self._get_account_balances()

        if not all_balances:
            raise UserError(
                _(
                    "No se encontraron movimientos contables para cerrar en el período seleccionado."
                )
            )

        # --- Paso 1: Preparar mapas de datos para un acceso eficiente ---
        account_ids = list(set(b["account_id"][0] for b in all_balances))
        accounts = self.env["account.account"].browse(account_ids)
        closing_map = {acc.id: acc.closing_account_id.id for acc in accounts}
        account_map = {acc.id: acc for acc in accounts}

        # --- Paso 2: Lógica de Agrupación Avanzada ---
        grouped_balances = defaultdict(list)

        for balance_data in all_balances:
            account_id = balance_data["account_id"][0]
            account = account_map.get(account_id)
            balance = balance_data["balance"]

            # --- Manejo correcto de la moneda ---
            # `read_group` devuelve una tupla (id, name) para la moneda, o False si no hay.
            currency_tuple = balance_data["currency_id"]
            if currency_tuple:
                currency_id, currency_name = currency_tuple
            else:
                # Si no hay moneda en el apunte, se asume la moneda de la compañía.
                currency_id = self.company_id.currency_id.id
                currency_name = self.company_id.currency_id.name

            if not account:
                continue

            # Criterio 2: Determinar el grupo de la cuenta por su código.
            if any(account.code.startswith(c) for c in ("0", "1", "2", "3", "4", "5")):
                account_group = "Cuentas de Balance"
            elif any(account.code.startswith(c) for c in ("6", "7", "8", "9")):
                account_group = "Cuentas de Resultado"
            else:
                continue

            # Criterio 3: Determinar el signo del saldo.
            balance_sign = "Positivos" if balance >= 0 else "Negativos"

            # Construir la clave de agrupación.
            grouping_key = (currency_id, currency_name, account_group, balance_sign)
            grouped_balances[grouping_key].append(balance_data)

        # --- Paso 3: Crear un asiento de cierre por cada grupo ---
        created_moves = self.env["account.move"]
        for grouping_key, balances_for_move in grouped_balances.items():
            currency_id, currency_name, account_group, balance_sign = grouping_key

            move_lines_vals = self._prepare_move_lines(balances_for_move, closing_map)
            if not move_lines_vals:
                continue

            # --- **MEJORA**: Construcción de la referencia descriptiva ---
            # 1. Usamos un 'set' para obtener los prefijos únicos de 2 dígitos de las cuentas.
            account_prefixes = set()
            for line in move_lines_vals:
                line_account_id = line["account_id"]
                account = account_map.get(line_account_id)
                if account and not account.is_closing_account and account.code:
                    account_prefixes.add(account.code[:2])

            # 2. Ordenamos y unimos los prefijos para una visualización consistente.
            #    Ejemplo: "10, 12, 42"
            map_code = ", ".join(sorted(list(account_prefixes)))

            # 3. Creamos la referencia final, que es mucho más clara para el usuario.
            #    Ejemplo: "Cierre de Cuentas de Balance (10, 42) en USD - Saldos Positivos"
            ref_message = f"Cierre de Cuentas '{map_code}' en {currency_name} - Saldos {balance_sign}"

            move_vals = {
                "journal_id": self.journal_id.id,
                "date": self.closing_date,
                # <-- Usamos la nueva referencia mejorada
                "ref": ref_message,
                "company_id": self.company_id.id,
                "currency_id": currency_id,
                "line_ids": [(0, 0, vals) for vals in move_lines_vals],
            }
            move = self.env["account.move"].create(move_vals)
            # Descomenta la siguiente línea para publicar los asientos automáticamente.
            # move.action_post()
            created_moves |= move

        # --- Paso 4: Retornar una acción para mostrar los asientos creados ---
        if not created_moves:
            raise UserError(
                _(
                    "No se generaron asientos de cierre. Verifique la configuración de las cuentas."
                )
            )

        action = self.env["ir.actions.actions"]._for_xml_id(
            "account.action_move_journal_line"
        )
        if len(created_moves) > 1:
            action["domain"] = [("id", "in", created_moves.ids)]
        else:
            action.update(
                {
                    "views": [(False, "form")],
                    "res_id": created_moves.id,
                    "view_mode": "form",
                }
            )
        return action
