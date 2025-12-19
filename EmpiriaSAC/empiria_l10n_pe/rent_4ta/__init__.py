from . import models
from . import reports

from odoo import api, SUPERUSER_ID

def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _create_purchase_taxes(env)

def _create_purchase_taxes(env):

    companies = env['res.company'].search([('chart_template_id', '!=', False)])
    for company in companies:
        l10n_pe_id = env.ref('l10n_pe.%s_chart40172' % (company.id)).id

        tax_group_id_rta = env['account.tax.group'].create([
            {
                'name': 'RTA',
                'country_id': env.ref('base.pe').id,
                'l10n_pe_edi_code':'RTA'
            }
        ])
        tax_group_id_4ta = env['account.tax.group'].create([
            {
                'name': '4TA',
                'country_id': env.ref('base.pe').id,
                'l10n_pe_edi_code':'4TA'
            }
        ])

        env['account.tax'].create([
            {
                'sequence': 30,
                'name': 'RTA 0%',
                'amount_type': 'percent',
                'type_tax_use': 'purchase',
                'amount': 0,
                'description': 'RTA',
                'country_id': env.ref('base.pe').id,
                'tax_group_id': tax_group_id_rta.id,
                'include_base_amount': 0,
                'invoice_repartition_line_ids': [
                    (0, 0, {'factor_percent': 100, 'repartition_type': 'base'}),
                    (0, 0, {'factor_percent': 100, 'repartition_type': 'tax'})
                ],
                'refund_repartition_line_ids': [
                    (0, 0, {'factor_percent': 100, 'repartition_type': 'base'}),
                    (0, 0, {'factor_percent': 100, 'repartition_type': 'tax'})
                ],
                'company_id': company.id
            },
            {
                'sequence': 31,
                'name': 'RTA 8%',
                'amount_type': 'percent',
                'type_tax_use': 'purchase',
                'amount': -8,
                'description': '4TA',
                'country_id': env.ref('base.pe').id,
                'tax_group_id': tax_group_id_4ta.id,
                'include_base_amount': 0,
                'invoice_repartition_line_ids': [
                    (0, 0, {'factor_percent': 100, 'repartition_type': 'base'}),
                    (0, 0, {'factor_percent': 100, 'repartition_type': 'tax', 'account_id': l10n_pe_id})
                ],
                'refund_repartition_line_ids': [
                    (0, 0, {'factor_percent': 100, 'repartition_type': 'base'}),
                    (0, 0, {'factor_percent': 100, 'repartition_type': 'tax', 'account_id': l10n_pe_id})
                ],
                'company_id': company.id
            }
        ])
