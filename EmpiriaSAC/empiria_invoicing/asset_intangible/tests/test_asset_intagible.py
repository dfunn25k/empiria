from lxml import etree
from odoo.tests import TransactionCase, tagged

@tagged('post_install', '-at_install')
class TestAssetIntangible(TransactionCase):

    def setUp(self):
        super(TestAssetIntangible, self).setUp()
        self.AssetIntangible = self.env['asset.intangible']
        self.AccountMove = self.env['account.move']
        self.AccountMoveLine = self.env['account.move.line']

    def test_01_create_asset_intangible(self):
        """Test creation of asset intangible"""
        asset = self.AssetIntangible.create({
            'name': 'Test Asset',
            'bool_asset_intagible': True,
            'operation_date': '2024-08-23',
        })
        self.assertTrue(asset, "Asset Intangible should be created")
        self.assertEqual(asset.name, 'Test Asset')
        self.assertTrue(asset.bool_asset_intagible)
        self.assertEqual(str(asset.operation_date), '2024-08-23')

    def test_02_name_search(self):
        """Test name_search method"""
        self.AssetIntangible.create({'name': 'Test Asset 1'})
        self.AssetIntangible.create({'name': 'Test Asset 2'})
        
        results = self.AssetIntangible.name_search('Test')
        self.assertEqual(len(results), 2, "Should find 2 assets")

    def test_03_account_move_line_asset_intangible(self):
        """Test asset_intangible_id in account.move.line"""
        asset = self.AssetIntangible.create({'name': 'Test Asset'})
        # Crear una cuenta para usar en la línea de movimiento
        account = self.env['account.account'].create({
            'name': 'Test Account',
            'code': 'TEST',
            'account_type': 'asset_current',
        })
        move = self.AccountMove.create({
            'move_type': 'entry',
            'line_ids': [(0, 0, {
                'name': 'Test line',
                'account_id': account.id,
                'asset_intangible_id': asset.id,
            })],
        })
        self.assertEqual(move.line_ids[0].asset_intangible_id, asset)

    def test_04_field_existence(self):
        """Test field existence in models"""
        self.assertIn('asset_intangible_id', self.env['account.move.line']._fields, 
                    "asset_intangible_id should exist in account.move.line model")

    def test_05_menu_item_creation(self):
        """Test menu item creation"""
        menu = self.env.ref('asset_intangible.menu_action_asset_intangible', raise_if_not_found=False)
        self.assertTrue(menu, "Menu item for Asset / Intangible should be created")
        self.assertEqual(menu.name, "Asset / Intangible")

    def test_06_asset_intangible_views(self):
        """Test asset.intangible views"""
        form_view = self.env.ref('asset_intangible.asset_intangible_form_view', raise_if_not_found=False)
        self.assertTrue(form_view, "Form view for asset.intangible should be created")

        tree_view = self.env.ref('asset_intangible.asset_intangible_tree_view', raise_if_not_found=False)
        self.assertTrue(tree_view, "Tree view for asset.intangible should be created")

        search_view = self.env.ref('asset_intangible.asset_intangible_search_view', raise_if_not_found=False)
        self.assertTrue(search_view, "Search view for asset.intangible should be created")
        print('--------TEST - Asset Intangible - OK-------')







        




