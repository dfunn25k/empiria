from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    l10n_pe_withhold_code = fields.Selection(
        selection_add=[
            ('044', 'Servicio de beneficio de minerales metálicos gravados con el IGV'),
            ('045', 'Minerales de oro y sus concentrados gravados con el IGV'),
        ]
    )
