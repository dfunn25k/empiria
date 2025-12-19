from odoo import fields
from odoo.tests import TransactionCase
from odoo.exceptions import ValidationError

class TestAccountMoveLine(TransactionCase):

    def setUp(self):
        super(TestAccountMoveLine, self).setUp()
        self.partner_model = self.env['res.partner']
        self.account_move_line_model = self.env['account.move.line']
        self.account_move_model = self.env['account.move']
        self.account_account_model = self.env['account.account']

        self.company = self.env.ref('base.main_company')

        self.account = self.account_account_model.search([('company_id', '=', self.company.id)], limit=1)
        if not self.account:
            raise ValueError("No se encontró ninguna cuenta para la empresa principal")

        self.move = self.account_move_model.create({
            'move_type': 'entry',
            'date': fields.Date.today(),
            'company_id': self.company.id,
        })

    def test_create_account_move_line_with_addresses(self):
        origin_partner = self.partner_model.create({
            'name': 'Dirección de Origen',
            'email': 'origen@example.com',
            'company_id': self.company.id,
        })
        destiny_partner = self.partner_model.create({
            'name': 'Dirección de Destino',
            'email': 'destino@example.com',
            'company_id': self.company.id,
        })

        move_line = self.account_move_line_model.with_context(check_move_validity=False).create({
            'name': 'Test Move Line',
            'move_id': self.move.id,
            'account_id': self.account.id,
            'origin_address': origin_partner.id,
            'destiny_address': destiny_partner.id,
            'debit': 100,
            'credit': 0,
            'company_id': self.company.id,
        })

        self.assertEqual(move_line.origin_address, origin_partner)
        self.assertEqual(move_line.destiny_address, destiny_partner)

    def test_update_account_move_line_addresses(self):
        move_line = self.account_move_line_model.with_context(check_move_validity=False).create({
            'name': 'Test Move Line',
            'move_id': self.move.id,
            'account_id': self.account.id,
            'debit': 100,
            'credit': 0,
            'company_id': self.company.id,
        })

        new_origin_partner = self.partner_model.create({
            'name': 'Nueva Dirección de Origen',
            'email': 'nuevo_origen@example.com',
            'company_id': self.company.id,
        })
        new_destiny_partner = self.partner_model.create({
            'name': 'Nueva Dirección de Destino',
            'email': 'nuevo_destino@example.com',
            'company_id': self.company.id,
        })

        move_line.write({
            'origin_address': new_origin_partner.id,
            'destiny_address': new_destiny_partner.id,
        })

        self.assertEqual(move_line.origin_address, new_origin_partner)
        self.assertEqual(move_line.destiny_address, new_destiny_partner)
