from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class StockMove(models.Model):
    _inherit = "stock.move"

    def force_consume_materials(self):
        """
        Fuerza el consumo de los materiales asociados a este movimiento de stock.
        Intenta reservar el stock (si no está ya) y marca el movimiento como 'hecho',
        efectivamente descontando el stock del almacén.
        """
        self.ensure_one()

        if self.state == "cancel":
            raise UserError(
                _("No se puede forzar el consumo de un movimiento cancelado.")
            )
        if self.quantity_done <= 0:
            raise ValidationError(
                _("La cantidad consumida debe ser mayor que cero para consumir.")
            )
        if self.quantity_done > self.product_uom_qty:
            raise ValidationError(
                _("La cantidad consumida no puede ser mayor a la cantidad planificada.")
            )

        if self.quantity_done > self.forecast_availability:
            raise ValidationError(
                _(
                    "La cantidad consumida no puede ser mayor a la cantidad reservada en el stock."
                )
            )

        # Marca el movimiento como 'hecho', creando los movimientos de stock reales
        if self.state in ["confirmed", "partially_available", "assigned"]:
            self._action_done(cancel_backorder=False)
        elif self.state == "done":
            # Ya estaba marcado como consumido
            pass
        else:
            raise UserError(
                _(
                    f"No se pudo procesar el consumo para el movimiento {self.display_name}. Estado actual: {self.state}"
                )
            )

        # Intenta reservar el stock si aún no está reservado
        self._action_assign()
