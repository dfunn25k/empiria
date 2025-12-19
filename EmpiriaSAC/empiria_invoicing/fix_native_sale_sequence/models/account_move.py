from odoo import _, api, fields, models, tools
import re


class AccountMove(models.Model):
    _inherit = "account.move"

    def _get_last_sequence_domain(self, relaxed=False):
        """
        Hereda y modifica la lógica del método `_get_last_sequence_domain`,
        ajustando la condición cuando `sequence_number_reset == 'never'`.
        """
        self.ensure_one()

        # Llamar al método original para obtener la condición base
        where_string, param = super()._get_last_sequence_domain(relaxed)

        if not relaxed:
            # Determinar si el registro actual está relacionado con un pago
            is_payment = self.payment_id or self._context.get("is_payment")

            # Obtener el ID real del registro, considerando si es un nuevo objeto
            current_move_id = self.id or self._origin.id

            # Construcción del dominio de búsqueda para encontrar el último documento válido
            search_domain = [
                ("journal_id", "=", self.journal_id.id),
                ("id", "!=", current_move_id),
                # Evitar registros sin numeración
                ("name", "not in", ("/", "", False)),
            ]

            # Filtrar por tipo de documento si el diario tiene secuencia separada para notas de crédito
            if self.journal_id.refund_sequence:
                refund_types = ("out_refund", "in_refund")
                search_domain.append(
                    (
                        "move_type",
                        "in" if self.move_type in refund_types else "not in",
                        refund_types,
                    )
                )

            # Filtrar si el diario tiene secuencia separada para pagos
            if self.journal_id.payment_sequence:
                search_domain.append(("payment_id", "!=" if is_payment else "=", False))

            # Obtener el último comprobante del mismo diario ordenado por fecha descendente
            last_move = self.search(search_domain, order="date desc", limit=1)
            last_move_name = last_move.name if last_move else ""

            # Determinar el tipo de reseteo de la secuencia
            sequence_reset_type = self._deduce_sequence_number_reset(last_move_name)

            # Si la secuencia nunca se reinicia, modificar la expresión regular para evitar reinicios no deseados
            if sequence_reset_type == "never":
                sequence_pattern = (
                    r"^(?P<prefix1>.*?)(?P<year>((?<=\\D)|(?<=^))((20|21)?\\d{2}))"
                    r"(?P<prefix2>\\D+?)(?P<seq>\\d*)(?P<suffix>\\D*?)$"
                )
                param["anti_regex"] = (
                    re.sub(r"\?P<\w+>", "?:", sequence_pattern.split("(?P<seq>")[0])
                    + "$"
                )

        return where_string, param
