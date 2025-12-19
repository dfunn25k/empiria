from odoo import fields, models, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    is_transfer_total_assets_dam_ds = fields.Boolean(string='¿Traslado por el total de los bienes de la DAM/DS?')
    container_number_one = fields.Selection(
        selection=[
            ('of_the_dam', 'De la DAM'),
            ('another_container', 'Otro contenedor'),
            ('without_container', 'Sin contenedor')
        ],
        string='Nro. del contenedor 1'
    )
    container_number_two = fields.Selection(
        selection=[
            ('of_the_dam', 'De la DAM'),
            ('another_container', 'Otro contenedor'),
            ('without_container', 'Sin contenedor')
        ],
        string='Nro. del contenedor 2'
    )
    container_one_registered_number = fields.Char(string='Nro. del contenedor 1 registrado')
    container_one_precinct_number = fields.Char(string='Nro. del precinto (contenedor 1)')
    container_two_registered_number = fields.Char(string='Nro. del contenedor 2 registrado')
    container_two_precinct_number = fields.Char(string='Nro. del precinto (contenedor 2)')
    pallets_number = fields.Char(string='Nro. de bultos o pallets')
    airport_catalog_id = fields.Many2one(
        comodel_name='airport.catalog',
        string='Aeropuerto'
    )
    port_catalog_id = fields.Many2one(
        comodel_name='port.catalog',
        string='Puerto'
    )

    @api.onchange('container_number_one')
    def _onchange_container_number_one(self):
        if self.container_number_one == 'without_container':
            self.update({
                'container_one_registered_number': False,
                'container_one_precinct_number': False,
                'container_number_two': False,
                'container_two_registered_number': False,
                'container_two_precinct_number': False
            })
        else:
            self.update({
                'container_one_registered_number': False,
                'container_one_precinct_number': False,
                'pallets_number': False
            })

    @api.onchange('container_number_two')
    def _onchange_container_number_two(self):
        if self.container_number_two in ['of_the_dam', 'another_container', 'without_container', '', False]:
            self.update({
                'container_two_registered_number': False,
                'container_two_precinct_number': False
            })

    @api.onchange('airport_catalog_id')
    def _onchange_airport_catalog_id(self):
        if self.airport_catalog_id:
            self.port_catalog_id = False

    @api.onchange('port_catalog_id')
    def _onchange_port_catalog_id(self):
        if self.port_catalog_id:
            self.airport_catalog_id = False

    def _l10n_pe_edi_generate_missing_data_error_list(self):
        errors = super()._l10n_pe_edi_generate_missing_data_error_list()
        if self.l10n_pe_edi_reason_for_transfer in ['08', '09']:
            if 'Favor de incluir el Distrito en el contacto del cliente.' in errors:
                errors.remove('Favor de incluir el Distrito en el contacto del cliente.')
            if not (self.l10n_pe_edi_related_document_type and self.l10n_pe_edi_document_number):
                errors.append('No puedes generar la Guía de Remisión Remitente con motivo de traslado importación/exportación hasta que subsanen lo siguiente: Debes colocar en el campo "related document type" el documento relacionado, que para este caso es "Declaración Simplificada (DS)" o "Declaración Aduanera de Mercaderías (DAM)" o luego colocar el número relacionado".')
        return errors
