from odoo.tests import Form
from odoo.tests.common import tagged
from odoo.addons.hr.tests.common import TestHrCommon


class TestHrEmployee(TestHrCommon):

    def setUp(self):
        super().setUp()
        self.user_without_image = self.env['res.users'].create({
            'name': 'Marc',
            'email': 'mark23@example.com',
            'image_1920': False,
            'login': 'demo',
            'password': 'demo111_'
        })
        document = self.env['l10n_latam.identification.type'].create({
            'name': 'DNI-prueba',
            'active': True
        })
        self.employee_without_image = self.env['hr.employee'].create({
            'user_id': self.user_without_image.id,
            'image_1920': False
        })


    def test_employee_linked_partner(self):
        user_partner = self.user_without_image.partner_id
        work_contact = self.employee_without_image.work_contact_id
        self.assertEqual(user_partner, work_contact)

    def test_employee_has_avatar_even_if_it_has_no_image(self):
        self.assertTrue(self.employee_without_image.avatar_128)
        self.assertTrue(self.employee_without_image.avatar_256)
        self.assertTrue(self.employee_without_image.avatar_512)
        self.assertTrue(self.employee_without_image.avatar_1024)
        self.assertTrue(self.employee_without_image.avatar_1920)
        print('------------------TEST  OK ### 1 ###--------------------------')

    def test_employee_has_same_avatar_as_corresponding_user(self):
        self.assertEqual(self.employee_without_image.avatar_1920, self.user_without_image.avatar_1920)
        print('------------------TEST  OK ### 2 ###--------------------------')

    def test_employee_member_of_department(self):
        dept, dept_sub, dept_sub_sub, dept_other, dept_parent = self.env['hr.department'].create([
            {
                'name': 'main',
            },
            {
                'name': 'sub',
            },
            {
                'name': 'sub-sub',
            },
            {
                'name': 'other',
            },
            {
                'name': 'parent',
            },
        ])
        dept_sub.parent_id = dept
        dept_sub_sub.parent_id = dept_sub
        dept.parent_id = dept_parent
        emp, emp_sub, emp_sub_sub, emp_other, emp_parent = self.env['hr.employee'].with_user(
            self.res_users_hr_officer).create([
            {
                'name': 'employee',
                'department_id': dept.id,
            },
            {
                'name': 'employee sub',
                'department_id': dept_sub.id,
            },
            {
                'name': 'employee sub sub',
                'department_id': dept_sub_sub.id,
            },
            {
                'name': 'employee other',
                'department_id': dept_other.id,
            },
            {
                'name': 'employee parent',
                'department_id': dept_parent.id,
            },
        ])
        self.res_users_hr_officer.employee_id = emp
        self.assertTrue(emp.member_of_department)
        self.assertTrue(emp_sub.member_of_department)
        self.assertTrue(emp_sub_sub.member_of_department)
        self.assertFalse(emp_other.member_of_department)
        self.assertFalse(emp_parent.member_of_department)
        employees = emp + emp_sub + emp_sub_sub + emp_other + emp_parent
        self.assertEqual(
            employees.filtered_domain(employees._search_part_of_department('=', True)),
            emp + emp_sub + emp_sub_sub)
        self.assertEqual(
            employees.filtered_domain(employees._search_part_of_department('!=', False)),
            emp + emp_sub + emp_sub_sub)
        self.assertEqual(
            employees.filtered_domain(employees._search_part_of_department('=', False)),
            emp_other + emp_parent)
        self.assertEqual(
            employees.filtered_domain(employees._search_part_of_department('!=', True)),
            emp_other + emp_parent)
        print('------------------TEST  OK ### 3 ###--------------------------')

    def test_employee_create_from_user(self):
        employee = self.env['hr.employee'].create({
            'name': 'Test User 3 - employee'
        })
        user_1, user_2, user_3 = self.env['res.users'].create([
            {
                'name': 'Test User',
                'login': 'test_user',
                'email': 'test_user@odoo.com',
            },
            {
                'name': 'Test User 2',
                'login': 'test_user_2',
                'email': 'test_user_2@odoo.com',
                'create_employee': True,
            },
            {
                'name': 'Test User 3',
                'login': 'test_user_3',
                'email': 'test_user_3@odoo.com',
                'create_employee_id': employee.id,
            },
        ])

        self.assertFalse(user_1.employee_id)
        self.assertTrue(user_2.employee_id)
        self.assertEqual(user_3.employee_id, employee)
        print('------------------TEST  OK ### 4 ###--------------------------')

    def test_employee_create_from_signup(self):
        partner = self.env['res.partner'].create({
            'name': 'test partner'
        })
        self.env['res.users'].signup({
            'name': 'Test User',
            'login': 'test_user',
            'email': 'test_user@odoo.com',
            'password': 'test_user_password',
            'partner_id': partner.id,
        })
        self.assertFalse(self.env['res.users'].search([('login', '=', 'test_user')]).employee_id)
        print('------------------TEST  ### 5 ###--------------------------')
