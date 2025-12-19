from odoo import _, api, fields, models, tools


class AccountMove(models.Model):
    _inherit = "account.move"

    # ---------------------------------------------------------------------------- #
    #                           TODO - METODOS EXTENDIDOS                          #
    # ---------------------------------------------------------------------------- #
    def action_register_payment(self):
        """
        Extiende la acción de registro de pago para incluir un tipo de cambio forzado
        desde la factura, usando el contexto del asistente.

        Se implementa la lógica condicional basada en el número de registros:
            - Si se selecciona UNA SOLA factura, se pasa su tipo de cambio específico
              al asistente de pago como un valor por defecto.
            - Si se seleccionan VARIAS facturas, no se pasa ningún tipo de cambio,
              permitiendo al usuario introducir una tasa manual para todo el lote.
        """
        # Se obtiene la acción estándar de Odoo.
        action = super().action_register_payment()

        # El sistema propone el tipo de cambio forzado de una única factura.
        if len(self) == 1:
            # Obtiene el tipo de cambio forzado al contexto
            forced_rate = self.to_force_exchange_rate or 0.0
            # Prepara el contexto para pasar el valor por defecto al asistente.
            extra_context = {"default_to_force_exchange_rate": forced_rate}

            # Actualiza el contexto de la acción.
            action_context = action.get("context", {})
            action["context"] = {**action_context, **extra_context}

        return action
