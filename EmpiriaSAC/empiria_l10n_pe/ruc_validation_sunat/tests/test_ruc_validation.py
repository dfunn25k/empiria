from odoo.tests.common import TransactionCase
from odoo.tests.common import tagged
from unittest.mock import patch, MagicMock
from ..models.apps import SunatPartner 

@tagged('post_install', '-at_install')
class TestRucValidation(TransactionCase):

    def setUp(self):
        super().setUp()
        
        self.partner = self.env['res.partner'].create({
            'name': 'Company Partner',
            'document_type_sunat_id': self.env['l10n_latam.identification.type'].search([('name','=','RUC')],limit=1).id,
            'vat':'20551583041'
        })
        self.company = self.env['res.company'].create({
            'name' : self.partner.name,
            'partner_id': self.partner.id,
            'currency_id':self.env['res.currency'].search([('name','=','PEN')]).id,
        })

        self.activity_economic = self.env['activity.economic.sunat'].create({
            'name': 'Actividad Económica Test',
            'partner_id': self.partner.id,
        })

        self.document_pay = self.env['document.pay.sunat'].create({
            'name': 'Document Pay Test',
            'partner_id': self.partner.id,
        })

        self.system_electronic = self.env['system.electronic.sunat'].create({
            'name': 'System Electronic Test',
            'partner_id': self.partner.id,
        })

        self.pattern = self.env['pattern.sunat'].create({
            'name': 'Pattern SUNAT Test',
            'partner_id': self.partner.id,
        })
        
    def test_partner_company_creation(self):
        self.assertEqual(self.partner.name, 'Company Partner')
        self.assertEqual(self.partner.vat, '20551583041')
        self.assertEqual(self.partner.document_type_sunat_id.name, 'RUC')

        self.assertEqual(self.company.name, 'Company Partner')
        self.assertEqual(self.company.partner_id.id, self.partner.id)
        self.assertEqual(self.company.currency_id.name, 'PEN')
        
    def test_validation_document(self):
        self.company.write({
            'token_api_ruc':'bffc62d789cb9befeb36f49938dc5eacf363856279bd8a32fe41c5a91fd2f65f'
        })
        
        values = {
            'vat': self.partner.vat,
            'l10n_latam_identification_type_id': self.partner.document_type_sunat_id.id,
            'id': self.partner.id
        }
        document_type_code = self.env['l10n_latam.identification.type'].browse(values.get('l10n_latam_identification_type_id')).l10n_pe_vat_code
        obj_sunat_yaros = SunatPartner(values.get('vat'), document_type_code, self.company.token_api_ruc)
        
        val_pi = obj_sunat_yaros.action_validate_api()
        handle_data =  self.partner.handle_data_sunat(values)
        ruc_partner = self.partner.action_validate_sunat(values)
        
        self.assertEqual(val_pi['name'],handle_data['name'])
        self.assertEqual(val_pi['vat'],handle_data['vat'])
        self.assertEqual(val_pi['state_contributor_sunat'],handle_data['state_contributor_sunat'])
        self.assertEqual(val_pi['condition_contributor_sunat'],handle_data['condition_contributor_sunat'])
        self.assertEqual(val_pi['street'],handle_data['street'])
        self.assertEqual(val_pi['company_type'],handle_data['company_type'])
        self.assertEqual(handle_data['id'],ruc_partner)
        