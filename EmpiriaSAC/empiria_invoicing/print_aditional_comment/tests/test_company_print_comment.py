from odoo.tests import common
from odoo.tests.common import tagged
from lxml import etree

@tagged('post_install', '-at_install')
class TestCompanyPrintComment(common.TransactionCase):

    def setUp(self):
        super().setUp()
        self.company =self.env['res.company'].create({
            'name': 'Test Company',
            'street': '123 Test Street',
            'city': 'Test City',
            'country_id': self.env.ref('base.pe').id,
            'additional_information':'Informacion adicional del campo'
         
        }) 
     
    def test_company_comment(self):
        
        self.assertEqual(self.company.name,'Test Company')
        self.assertEqual(self.company.street,'123 Test Street')
        self.assertEqual(self.company.city,'Test City')
        self.assertEqual(self.company.country_id.id,self.env.ref('base.pe').id)
        
        view_id = self.env.ref('print_aditional_comment.res_company_form_view_inherit_print_aditional_comment')
        view = self.env['ir.ui.view'].browse(view_id.id)
        
        xml_tree = etree.fromstring(view.arch)
        field = xml_tree.xpath("//field[@name='additional_information']")[0]
        field_name = field.get('name')
        
        self.assertTrue(field_name)
        self.assertEqual( view.model,'res.company')
    