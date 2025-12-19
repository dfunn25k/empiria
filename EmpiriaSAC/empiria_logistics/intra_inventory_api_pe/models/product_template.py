from odoo import api, fields, models

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    intralot= fields.Boolean(
        string="Intralot",
        help='Si activas esta casilla, se realizará una sincronización enviando la información a Intralot, en los siguientes casos: \n'
        'a) Ajuste de Inventario: Si el lugar y el producto tienen marcado el campo Intralot. \n'
        'b) En la Transferencia: Si la ubicación de origen y destino, tienen al mismo tiempo, marcado el campo Intralot, se sincronizará con la tinka, aquellos productos que tengan marcado el campo intralot.'
    )