from odoo import models, fields, api


class StockLot(models.Model):
    _inherit = 'stock.lot'

    status = fields.Many2one(
        comodel_name='stock.production.lot.status',
        string='Status',
        help='Este campo se aprovecha mejor, cuando se trata de productos que utilizan el método de seguimiento de serie, porque nos ayuda a identificar el '
             'estatus del producto relacionado a la serie. Cuando se establece un status en una transferencia o ajuste de inventario, se almacena el valor en este campo.'
    )


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    status = fields.Many2one(
        comodel_name='stock.production.lot.status',
        string='Status',
        compute='_compute_status',
        inverse='_inverse_status',
        readonly=False,
        store=True
    )

    @api.depends('lot_id')
    def _compute_status(self):
        for record in self:
            if record.lot_id and record.lot_id.status:
                record.status = record.lot_id.status
            else:
                record.status = False

    def _inverse_status(self):
        pass


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    status = fields.Char(
        string='Status',
        compute='_compute_status',
        readonly=True,
        store=True
    )

    @api.depends('lot_id')
    def _compute_status(self):
        for record in self:
            if record.lot_id.status.code and record.lot_id.status.name:
                record.status = "%s - %s" % (record.lot_id.status.code, record.lot_id.status.name)
            else:
                record.status = ''


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        res = super().button_validate()
        for line in self.move_line_ids_without_package:
            if line.lot_id and line.status:
                line.lot_id.status = line.status
        return res
