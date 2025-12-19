{
    'name': 'Stock Fix Compute Bulk Weight',
    'version': '16.0.1.0.0',
    'author': 'Leo Daniel FS',
    'company': 'Leo Daniel FS',
    'maintainer': 'Leo Daniel FS',
    'support': 'l30dfs@gmail.com',
    'website': 'https://www.linkedin.com/in/leo-daniel-flores',
    'summary': 'Fix compute bulk weight for delivery methods',
    'description': """
This module fixes the computation of bulk weight
for delivery methods in stock module.
""",
    'category': 'Inventory/Inventory',
    'depends': [
        # Odoo community
        'stock',
        'delivery'
    ],
    'module_type': 'official',
    'application': False,
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    # Reference price
    'price': 10.00,
}
