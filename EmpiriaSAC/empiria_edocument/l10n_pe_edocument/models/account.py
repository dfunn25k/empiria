import base64

from odoo.exceptions import UserError
from odoo.tools.float_utils import float_repr, float_round
from odoo.tools.translate import _

from odoo import api, fields, models


class AccountTax(models.Model):
    _inherit = 'account.tax'

    @api.model
    def solve_account_followup_template_module(self):
        template = self.env.ref('account_followup.template_followup_report')
        if template:
            new_template = '''
            <data inherit_id="account_reports.main_template" primary="True">

            </data>
            '''
            template.arch_base = new_template


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def _prepare_edi_vals_to_export(self):
        res = super(AccountMoveLine, self)._prepare_edi_vals_to_export()
        for tax in self.tax_ids:
            # GRA - Gratuito - Price amount calc
            if tax.l10n_pe_edi_tax_code and tax.l10n_pe_edi_tax_code == '9996':
                # Inafecto – Retiro por Bonificación - 31
                if tax.l10n_pe_edi_affectation_reason == '31':
                    price_subtotal_unit = 0.0
                # Exonerado - Transferencia gratuita - 21
                elif tax.l10n_pe_edi_affectation_reason == '21':
                    price_subtotal_unit = self.currency_id.round(
                        self.price_total / self.quantity) if self.quantity else 0.0
                # Gravado – Retiro por premio - 11
                else:
                    price_subtotal_unit = 0.0
                price_total_unit = self.currency_id.round(self.price_subtotal / self.quantity) if self.quantity else 0.0
                res.update({
                    'price_subtotal_unit': price_subtotal_unit,
                    'price_total_unit': price_total_unit,
                    'price_unit_after_discount': 0.0
                })
                break
        return res


class AccountMove(models.Model):
    _inherit = 'account.move'

    agent_retention = fields.Boolean(string='Retención?')
    base_amount_retention = fields.Float(string='Base imponible de la retención')
    porcentage_retention = fields.Char(
        string='Porcentaje de retención',
        compute='_default_porcentage',
        readonly=True
    )
    amount_retention_IGV = fields.Float(
        string='Monto de la retención',
        compute='_compute_amount_IGV'
    )
    payment_method_id = fields.Many2one(
        comodel_name='payment.methods.codes',
        string='Medio de pago',
    )

    @api.onchange('l10n_pe_edi_operation_type')
    def _onchange_payment_method(self):
        transfer_funds = self.env['payment.methods.codes'].search([('code', '=', '003')], limit=1)
        if self.l10n_pe_edi_operation_type in ['1001', '1002', '1003', '1004'] and any(transfer_funds):
            self.payment_method_id = transfer_funds.id
        else:
            self.payment_method_id = None

    @api.depends('porcentage_retention')
    def _default_porcentage(self):
        for acc_mov in self:
            acc_mov.porcentage_retention = '3%'

    @api.depends("amount_retention_IGV")
    def _compute_amount_IGV(self):
        for acc_mov in self:
            acc_mov.amount_retention_IGV = acc_mov.base_amount_retention * 0.03
            acc_mov.amount_retention_IGV = "{0:.2f}".format(acc_mov.amount_retention_IGV)

    def action_post(self):
        peru_id = self.env.ref('base.pe')
        for move in self:
            max_percent = any(move.invoice_line_ids.mapped('product_id.l10n_pe_withhold_code'))
            is_detraction = any(move.invoice_payment_term_id.line_ids.mapped('l10n_pe_is_detraction_retention'))
            detraction_operation_type = move.l10n_pe_edi_operation_type in ['1001', '1002', '1003', '1004']
            if move.l10n_latam_document_type_id.code == '01' and peru_id == move.env.company.country_id and (max_percent or is_detraction) and (
                    move.amount_total_signed >= 700 and not detraction_operation_type) and (
                    not move.agent_retention and move.journal_id.type == 'sale' and move.journal_id.l10n_latam_use_documents):
                raise UserError(_('Operación sujeta a detracción que supera la cantidad, debe indicar en el campo ' \
                                  '"operation type" que es afecta a detracción, por lo que la factura no puede ' \
                                  'ser publicada hasta que arregle el error'))
        return super(AccountMove, self).action_post()

    def _l10n_pe_edi_get_spot(self):
        spot = super(AccountMove, self)._l10n_pe_edi_get_spot()
        max_percent = max(self.invoice_line_ids.mapped('product_id.l10n_pe_withhold_percentage'), default=0)
        spot.update({'PaymentMeansCode': self.payment_method_id.code}) if spot else spot
        if 'exchange_rate' in self._fields.keys() and self.currency_id.name != 'PEN':
            amount_not_pen = float_repr(float_round((self.amount_total_signed * self.exchange_rate) * (max_percent / 100.0), precision_rounding=1),
                                        precision_digits=2)
            spot.update({'Amount': amount_not_pen}) if spot else spot
        return spot


class AccountEdiDocument(models.Model):
    _inherit = 'account.edi.document'

    def _process_job(self, job):
        super(AccountEdiDocument, self)._process_job(job)
        documents = self.env['account.edi.document']
        for doc in documents:
            if doc.state == 'sent':
                doc.write({
                    'error': False,
                    'blocking_level': False
                })

    @api.depends('move_id', 'error', 'state')
    def _compute_edi_content(self):
        """
        Override del método _compute_edi_content de addons/account_edi para manejar el resultado de
        _get_invoice_edi_content (enterprise/l10n_pe_edi) donde al momento de la implementacion retorna un markup.
        Se corrige para que se convierta en un flujo de bits.

        Observación:
        _get_invoice_edi_content llama a _generate_edi_invoice_bstr (enterprise/l10n_pe_edi) que renderiza el markup
        """

        for doc in self:
            res = b''
            if doc.state in ('to_send', 'to_cancel'):
                move = doc.move_id
                config_errors = doc.edi_format_id._check_move_configuration(move)
                if config_errors:
                    res = base64.b64encode('\n'.join(config_errors).encode('UTF-8'))
                else:
                    move_applicability = doc.edi_format_id._get_move_applicability(move)
                    if move_applicability and move_applicability.get('edi_content'):
                        res = self.handling_markkup_type_case(move_applicability['edi_content'](move))
            doc.edi_content = res

    def handling_markkup_type_case(self, file):
        return base64.b64encode(str(file).encode()) if type(file) != type(b'') else base64.b64encode(file)


class AccountMoveReversal(models.TransientModel):
    _inherit = 'account.move.reversal'

    def _prepare_default_reversal(self, move):
        values = super()._prepare_default_reversal(move)
        del values['ref']
        values.update({
            'ref': move.ref,
            'l10n_pe_edi_cancel_reason': _('Reversión de: %(move_name)s, %(reason)s',
                                           move_name=(move.name).replace(' ', ''), reason=self.reason)
            if self.reason
            else _('Reversión de: %s', move.name),
        })
        if 'l10n_latam_document_type_id' in values.keys() and self.refund_method == 'cancel':
            if self.l10n_latam_document_number and '|' in self.l10n_latam_document_number:
                part_document = self.l10n_latam_document_number
                values.update({
                    'l10n_latam_document_type_id': int(part_document.split('|')[0]) if part_document.split('|')[0] else
                    values['l10n_latam_document_type_id']
                })
        return values


class AccountDebitNote(models.TransientModel):
    _inherit = 'account.debit.note'

    def _prepare_default_values(self, move):
        values = super()._prepare_default_values(move)
        del values['ref']
        values.update({
            'ref': move.ref,
            'l10n_pe_edi_cancel_reason': '%s, %s' % (
                (move.name).replace(' ', ''), self.reason) if self.reason else move.name,
        })
        return values
