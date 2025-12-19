{
    'name': 'View inventory button',
    'version': '16.0.0.0.0',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'description': '',
    'depends': [
        'stock',
        'mrp',
        'stock_picking_batch'
    ],
    'data': [
        'security/stock_security.xml',
        'security/ir.model.access.csv',
        'views/stock_views.xml'
        
    ],
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 0.00,
}
