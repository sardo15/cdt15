{
    'name': """
        Print Invoices in Ticket Format |
        Imprimir Facturas en Formato Ticket
    """,

    'summary': """
        Allows to print the customer invoices in a ticket format like point of sale order. |
        Permite imprimir las facturas de los clientes en un formato de ticket como orden de punto de venta.
    """,

    'description': """
        Adds a new print button on the customer invoice and a paper format to print the invoice in a ticket format. |
        Agrega un nuevo botón de impresión en la factura del cliente y un formato de papel para imprimir la factura en un formato de ticket.
    """,

	'author': 'Develogers',
    'website': 'https://develogers.com',
    'support': 'especialistas@develogers.com',
    'live_test_url': 'https://demo.develogers.com',
    'license': 'LGPL-3',

    'category': 'Invoice',
    'version': '14.0',
    
    'price': 59.99,
    'currency': 'EUR',

    'depends': [
        'base',
        'account',
        'l10n_pe',        
    ],

    'data': [
        'report/account_move_report_templates.xml',
        'report/account_move_report.xml',
    ],
    
    'images': ['static/description/banner.gif'],
    
    'application': True,
    'installable': True,
    'auto_install': False,
}
