import base64
import io
import logging
import zipfile

from lxml import etree

from odoo import _, api, models

_logger = logging.getLogger(__name__)


class AccountInvoiceQRCode(models.Model):
    _inherit = 'account.move'

    def create_data_qr_code(self):
        """Create a data for qr_code for render in xml.
        Example:
            <img t-att-src="'/report/barcode/?barcode_type=%s&amp;value=%s&amp;width=%s&amp;height=%s' % ('QR', o.create_data_qr_code(), 100, 100)"/>
        """

        template = '{ruc}|{document_type_name}|{series}|{correlative}|{total_igv}|{total_amount}|' \
                   '{date_invoice}|{document_type_name_user}|{document_number_user}|{signature_hash}|\r\n'

        is_l10n_pe = self.env['ir.module.module'].sudo().search([('name', '=', 'l10n_pe')])
        is_l10n_pe_edi = self.env['ir.module.module'].sudo().search([('name', '=', 'l10n_pe_edi')])
        date_invoice = self.invoice_date.strftime('%d-%m-%Y') if self.invoice_date else ''
        series = self.name.replace(' ', '').split('-')[0] or '0000' if '-' in self.name else ''
        correlative = self.name.replace(' ', '').split('-')[1] or '' if '-' in self.name else ''
        edi_format_code=self.env['account.edi.format'].sudo().search([('code', '=', 'pe_ubl_2_1')])
        edi_attachment_zipped = self._get_edi_attachment(self.env.ref('l10n_pe_edi.edi_pe_ubl_2_1')) if edi_format_code else False
        if not edi_attachment_zipped:
            signature_hash = ''
        else:
            edi_attachment_str = self.env['account.move']._l10n_pe_edi_unzip_edi_document_generate(base64.decodebytes(edi_attachment_zipped.with_context(bin_size=False).datas))
            edi_tree = etree.fromstring(edi_attachment_str) if edi_attachment_str else False
            signature_hash = edi_tree.xpath('//ds:DigestValue', namespaces={'ds': 'http://www.w3.org/2000/09/xmldsig#'})[0].text if edi_tree else ''
        data = template.format(
            ruc=self.company_id.vat or '',
            document_type_name=self.company_id.partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code or '' if is_l10n_pe.state == 'installed' else '',
            series=series,
            correlative=correlative,
            total_igv=self.amount_tax or 0.0,
            total_amount=self.amount_total or 0.0,
            date_invoice=date_invoice,
            document_type_name_user=self.partner_id.l10n_latam_identification_type_id.l10n_pe_vat_code or '' if is_l10n_pe.state == 'installed' else '',
            document_number_user=self.commercial_partner_id.vat or '00000000',
            signature_hash=signature_hash or '' if is_l10n_pe.state== 'installed' and is_l10n_pe_edi.state== 'installed' else '',
        )
        return data

    @api.model
    def _l10n_pe_edi_unzip_edi_document_generate(self, zip_str):
        try:
            buffer = io.BytesIO(zip_str)
            zipfile_obj = zipfile.ZipFile(buffer)
            filenames = zipfile_obj.namelist()
            xml_filenames = [x for x in filenames if x.endswith(('.xml', '.XML'))]
            filename_to_decode = xml_filenames[0] if xml_filenames else filenames[0]
            content = zipfile_obj.read(filename_to_decode)
            buffer.close()
            return content
        except (zipfile.BadZipFile, IndexError) as e:
            _logger.error("Error while unzipping EDI document: %s", e)
            return False
