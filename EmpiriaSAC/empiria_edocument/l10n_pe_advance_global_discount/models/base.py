from odoo import api, fields, models, _
from odoo.tools.float_utils import float_repr, float_round
from odoo.tools.misc import formatLang, format_date, get_lang

from collections import defaultdict

import json


class AccountMove(models.Model):
    _inherit = 'account.move'

    multiplier_factor_field = fields.Char(string='Multiplier Label', compute='_compute_multiplier_factor_field', store=True)
    amount_field_advance = fields.Char(string='Amount Label', compute='_compute_multiplier_factor_field', store=True)
    debit_field_advance = fields.Char(string='Debit Label', compute='_compute_multiplier_factor_field', store=True)
    advance_lines_negatives = fields.Float(string='Advance Lines Negative')
    tax_totals_json = fields.Char(
        string="Invoice Totals JSON",
        compute='_compute_tax_totals_json',
        readonly=False,
        help='Edit Tax amounts if you encounter rounding issues.')

    @api.depends('line_ids.amount_currency', 'line_ids.tax_base_amount', 'line_ids.tax_line_id', 'partner_id',
                 'currency_id', 'amount_total', 'amount_untaxed')
    def _compute_tax_totals_json(self):
        """ Computed field used for custom widget's rendering.
            Only set on invoices.
        """
        for move in self:
            if not move.is_invoice(include_receipts=True):
                # Non-invoice moves don't support that field (because of multicurrency: all lines of the invoice share the same currency)
                move.tax_totals_json = None
                continue

            tax_lines_data = move._prepare_tax_lines_data_for_totals_from_invoice()

            move.tax_totals_json = json.dumps({
                **self._get_tax_totals(move.partner_id, tax_lines_data, move.amount_total, move.amount_untaxed,
                                       move.currency_id),
                'allow_tax_edition': move.is_purchase_document(include_receipts=False) and move.state == 'draft',
            })

    @api.model
    def _get_tax_totals(self, partner, tax_lines_data, amount_total, amount_untaxed, currency):
        account_tax = self.env['account.tax']

        grouped_taxes = defaultdict(
            lambda: defaultdict(lambda: {'base_amount': 0.0, 'tax_amount': 0.0, 'base_line_keys': set()}))
        subtotal_priorities = {}
        for line_data in tax_lines_data:
            tax_group = line_data['tax'].tax_group_id

            # Update subtotals priorities
            if tax_group.preceding_subtotal:
                subtotal_title = tax_group.preceding_subtotal
                new_priority = tax_group.sequence
            else:
                # When needed, the default subtotal is always the most prioritary
                subtotal_title = _("Untaxed Amount")
                new_priority = 0

            if subtotal_title not in subtotal_priorities or new_priority < subtotal_priorities[subtotal_title]:
                subtotal_priorities[subtotal_title] = new_priority

            # Update tax data
            tax_group_vals = grouped_taxes[subtotal_title][tax_group]

            if 'base_amount' in line_data:
                # Base line
                if tax_group == line_data.get('tax_affecting_base', account_tax).tax_group_id:
                    # In case the base has a tax_line_id belonging to the same group as the base tax,
                    # the base for the group will be computed by the base tax's original line (the one with tax_ids and no tax_line_id)
                    continue

                if line_data['line_key'] not in tax_group_vals['base_line_keys']:
                    # If the base line hasn't been taken into account yet, at its amount to the base total.
                    tax_group_vals['base_line_keys'].add(line_data['line_key'])
                    tax_group_vals['base_amount'] += line_data['base_amount']

            else:
                # Tax line
                tax_group_vals['tax_amount'] += line_data['tax_amount']

        # Compute groups_by_subtotal
        groups_by_subtotal = {}
        for subtotal_title, groups in grouped_taxes.items():
            groups_vals = [{
                'tax_group_name': group.name,
                'tax_group_amount': amounts['tax_amount'],
                'tax_group_base_amount': amounts['base_amount'],
                'formatted_tax_group_amount': formatLang(self.env, amounts['tax_amount'], currency_obj=currency),
                'formatted_tax_group_base_amount': formatLang(self.env, amounts['base_amount'], currency_obj=currency),
                'tax_group_id': group.id,
                'group_key': '%s-%s' % (subtotal_title, group.id),
            } for group, amounts in sorted(groups.items(), key=lambda l: l[0].sequence)]

            groups_by_subtotal[subtotal_title] = groups_vals

        # Compute subtotals
        subtotals_list = []  # List, so that we preserve their order
        previous_subtotals_tax_amount = 0
        for subtotal_title in sorted((sub for sub in subtotal_priorities), key=lambda x: subtotal_priorities[x]):
            subtotal_value = amount_untaxed + previous_subtotals_tax_amount
            subtotals_list.append({
                'name': subtotal_title,
                'amount': subtotal_value,
                'formatted_amount': formatLang(self.env, subtotal_value, currency_obj=currency),
            })

            subtotal_tax_amount = sum(group_val['tax_group_amount'] for group_val in groups_by_subtotal[subtotal_title])
            previous_subtotals_tax_amount += subtotal_tax_amount

        # Assign json-formatted result to the field
        return {
            'amount_total': amount_total,
            'amount_untaxed': amount_untaxed,
            'formatted_amount_total': formatLang(self.env, amount_total, currency_obj=currency),
            'formatted_amount_untaxed': formatLang(self.env, amount_untaxed, currency_obj=currency),
            'groups_by_subtotal': groups_by_subtotal,
            'subtotals': subtotals_list,
            'allow_tax_edition': False,
        }

    def _prepare_tax_lines_data_for_totals_from_invoice(self, tax_line_id_filter=None, tax_ids_filter=None):
        self.ensure_one()

        tax_line_id_filter = tax_line_id_filter or (lambda aml, tax: True)
        tax_ids_filter = tax_ids_filter or (lambda aml, tax: True)

        balance_multiplicator = -1 if self.is_inbound() else 1
        tax_lines_data = []

        for line in self.line_ids:
            if line.tax_line_id and tax_line_id_filter(line, line.tax_line_id):
                tax_lines_data.append({
                    'line_key': 'tax_line_%s' % line.id,
                    'tax_amount': line.amount_currency * balance_multiplicator,
                    'tax': line.tax_line_id,
                })

            if line.tax_ids:
                for base_tax in line.tax_ids.flatten_taxes_hierarchy():
                    if tax_ids_filter(line, base_tax):
                        tax_lines_data.append({
                            'line_key': 'base_line_%s' % line.id,
                            'base_amount': line.amount_currency * balance_multiplicator,
                            'tax': base_tax,
                            'tax_affecting_base': line.tax_line_id,
                        })

        return tax_lines_data

    @api.depends('invoice_payment_term_id', 'agent_retention', 'invoice_line_ids')
    def _compute_multiplier_factor_field(self):
        for rec in self:
            invoice_info = False
            if rec.tax_totals_json:
                invoice_info = json.loads(rec.tax_totals_json)
            if rec.invoice_payment_term_id and rec.invoice_payment_term_id.line_ids:
                for payment in rec.invoice_payment_term_id.line_ids:
                    if payment.l10n_pe_is_detraction_retention:
                        rec.multiplier_factor_field = str(round(payment.value_amount / 100, 4))
            else:
                rec.multiplier_factor_field = False
            if rec.line_ids:
                for line in rec.line_ids:
                    if line.l10n_pe_is_detraction_retention and invoice_info:
                        rec.amount_field_advance = str(round(line.amount_currency, 2))
                        rec.debit_field_advance = str(round(float(invoice_info['amount_total']), 2))
            else:
                rec.amount_field_advance = False
                rec.debit_field_advance = False

    def _l10n_pe_edi_get_spot(self):
        spot = super(AccountMove, self)._l10n_pe_edi_get_spot()
        max_percent = max(self.invoice_line_ids.mapped('product_id.l10n_pe_withhold_percentage'), default=0)
        spot.update({'Amount': float_repr(
            float_round((json.loads(self.tax_totals_json)['amount_total'] + self.advance_lines_negatives) * (max_percent / 100.0), precision_rounding=2),
            precision_digits=2)}) if spot else spot
        if 'exchange_rate' in self._fields.keys() and self.currency_id.name != 'PEN':
            amount_not_pen =  float_repr(
            float_round(((json.loads(self.tax_totals_json)['amount_total'] + self.advance_lines_negatives) * self.exchange_rate) * (max_percent / 100.0), precision_rounding=1),
            precision_digits=2)
            spot.update({'Amount': amount_not_pen}) if spot else spot
        return spot


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    l10n_pe_advance_invoice = fields.Char(string='Factura Anticipo FXXX-X')


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    l10n_pe_advance = fields.Boolean(string='Anticipo')

    @api.onchange('l10n_pe_advance')
    def checkbox_set_true_advance(self):
        for product in self:
            if product.l10n_pe_advance:
                product.global_discount = True

    @api.onchange('global_discount')
    def checkbox_set_true_discount(self):
        for product in self:
            if product.global_discount:
                product.l10n_pe_advance = True


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.onchange('l10n_pe_advance')
    def checkbox_set_true_advance(self):
        for product in self:
            if product.l10n_pe_advance:
                product.global_discount = True

    @api.onchange('global_discount')
    def checkbox_set_true_discount(self):
        for product in self:
            if product.global_discount:
                product.l10n_pe_advance = True
