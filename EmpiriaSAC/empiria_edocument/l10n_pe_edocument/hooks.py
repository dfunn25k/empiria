from odoo import api, SUPERUSER_ID

def post_init_update_tax (cr,registry):
    querys = ["""UPDATE account_tax SET sequence = 8, NAME = '0% Transferencia Gratuita', l10n_pe_edi_unece_category = 'Z', l10n_pe_edi_affectation_reason = '21', amount = 100	WHERE id IN (SELECT res_id FROM ir_model_data WHERE model = 'account.tax' AND module = 'l10n_pe' AND name = '1_sale_tax_gra')""",
              """DELETE FROM account_tax_repartition_line WHERE refund_tax_id IN (SELECT res_id FROM ir_model_data WHERE model = 'account.tax' AND module = 'l10n_pe' AND name = '1_sale_tax_gra')""",
              """DELETE FROM account_tax_repartition_line WHERE invoice_tax_id IN (SELECT res_id FROM ir_model_data WHERE model = 'account.tax' AND module = 'l10n_pe' AND name = '1_sale_tax_gra')""",
              """INSERT INTO account_tax_repartition_line (invoice_tax_id,account_id,company_id,sequence,repartition_type,use_in_tax_closing,create_date, write_date,factor_percent) VALUES((SELECT res_id FROM ir_model_data WHERE model = 'account.tax' AND module = 'l10n_pe' AND name = '1_sale_tax_gra'),null, (SELECT COMPANY_ID FROM ACCOUNT_TAX where id in (SELECT res_id FROM ir_model_data WHERE model = 'account.tax' AND module = 'l10n_pe' AND name = '1_sale_tax_gra')), 1, 'base', false,CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0)""",
              """INSERT INTO account_tax_repartition_line (invoice_tax_id,account_id,company_id,sequence,repartition_type,use_in_tax_closing,create_date, write_date,factor_percent) VALUES((SELECT res_id FROM ir_model_data WHERE model = 'account.tax' AND module = 'l10n_pe' AND name = '1_sale_tax_gra'),null,  (SELECT COMPANY_ID FROM ACCOUNT_TAX where id in (SELECT res_id FROM ir_model_data WHERE model = 'account.tax' AND module = 'l10n_pe' AND name = '1_sale_tax_gra')), 2, 'tax', false, CURRENT_TIMESTAMP,CURRENT_TIMESTAMP, -100)""",
              """INSERT INTO account_tax_repartition_line (refund_tax_id,account_id,company_id,sequence,repartition_type,use_in_tax_closing,create_date, write_date,factor_percent) VALUES((SELECT res_id FROM ir_model_data WHERE model = 'account.tax' AND module = 'l10n_pe' AND name = '1_sale_tax_gra'), null, (SELECT COMPANY_ID FROM ACCOUNT_TAX where id in (SELECT res_id FROM ir_model_data WHERE model = 'account.tax' AND module = 'l10n_pe' AND name = '1_sale_tax_gra')), 1, 'base', false, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0)""",
              """INSERT INTO account_tax_repartition_line (refund_tax_id,account_id,company_id,sequence,repartition_type,use_in_tax_closing,create_date, write_date,factor_percent) VALUES((SELECT res_id FROM ir_model_data WHERE model = 'account.tax' AND module = 'l10n_pe' AND name = '1_sale_tax_gra'),null,  (SELECT COMPANY_ID FROM ACCOUNT_TAX where id in (SELECT res_id FROM ir_model_data WHERE model = 'account.tax' AND module = 'l10n_pe' AND name = '1_sale_tax_gra')), 2, 'tax', false, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, -100)"""       
    ]
    for query in querys:
        cr.execute(query)
    
    post_init_account_tax(cr)

def post_init_account_tax(cr):
    env = api.Environment(cr, SUPERUSER_ID, {})
    country_code    = env['res.country'].search([('code','=','PE')], limit=1)
    company_country = env['res.company'].search([])

    if len(company_country) == 1:
        company = company_country[0]
        if company.country_id.id != country_code.id:
            return 

        account_4011 = env['account.account'].search([('name','=',env.ref('l10n_pe.chart40111').name), ('company_id', '=', company.id)], limit=1)
        account_6419 = env['account.account'].search([('name','=',env.ref('l10n_pe.chart6419').name), ('company_id', '=', company.id)], limit=1)

        update_tax_record(env, company, account_4011, account_6419)
    else:
        for company in company_country:
            if company.country_id.id != country_code.id:
                continue

            account_4011 = env['account.account'].search([('name','=',env.ref('l10n_pe.chart40111').name), ('company_id', '=', company.id)], limit=1)
            account_6419 = env['account.account'].search([('name','=',env.ref('l10n_pe.chart6419').name), ('company_id', '=', company.id)], limit=1)

            update_tax_record(env, company, account_4011, account_6419)

def update_tax_record(env, company, account_4011, account_6419):
    account_tax_22 = env.ref('l10n_pe_edocument.account_tax_22', False)

    if not account_4011 or not account_6419 or not account_tax_22:
        return 

    account_tax_22.write({
        'company_id': company.id,
        'invoice_repartition_line_ids':[(5, 0, 0),
            (0,0, {'repartition_type': 'base'}),
            (0,0, {
                'factor_percent': 100,
                'repartition_type': 'tax',
                'account_id': account_4011.id,
            }),
        ],
        'refund_repartition_line_ids':[(5, 0, 0),
            (0,0, {'repartition_type': 'base'}),
            (0,0, {
                'factor_percent': 100,
                'repartition_type': 'tax',
                'account_id': account_6419.id,
            }),
        ]
    })