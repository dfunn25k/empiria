{
    'name': 'Print your order for the kitchen',
    'version': '16.0.1.2.0',
    'author': 'Ganemo',
    'website': 'https://www.ganemo.co',
    'summary': 'Allows you to send the order to the kitchen printer without using the IoT Box.',
    'category': 'Point of Sale',
    'live_test_url': 'https://www.ganemo.co/demo',
    'depends': ['pos_restaurant', 'pos_ticket_base_template'],
    'data': ['views/res_config_settings_views.xml'],
    'assets': {
        'point_of_sale.assets': [
            'pos_kitchen_receipt_without_iot/static/src/js/*.js',
            'pos_kitchen_receipt_without_iot/static/src/xml/ButtonKitchenReceipt.xml',
            'pos_kitchen_receipt_without_iot/static/src/xml/KitchenOrderChangeReceipt.xml',
            'pos_kitchen_receipt_without_iot/static/src/xml/KitchenReceiptScreen.xml'
        ]
    },
    'installable': True,
    'auto_install': False,
    'license': 'Other proprietary',
    'currency': 'USD',
    'price': 72.00
}
