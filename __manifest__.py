{
    'name': 'Tableau de bord Fabrication',
    'version': '18.0.3.0.0',
    'category': 'Manufacturing',
    'summary': 'Dashboard MRP dynamique avec KPI, filtres et configuration',
    'description': 'Tableau de bord interactif pour le suivi de la fabrication avec filtres dynamiques, rafraîchissement auto et configuration.',
    'author': 'SOPROMER',
    'depends': ['mrp'],
    'data': [
        'security/mrp_dashboard_groups.xml',
        'security/ir.model.access.csv',
        'views/mrp_dashboard_config_views.xml',
        'views/mrp_dashboard_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'mrp_dashboard/static/src/css/mrp_dashboard.css',
            'mrp_dashboard/static/src/xml/mrp_dashboard.xml',
            'mrp_dashboard/static/src/js/mrp_dashboard.js',
        ],
    },
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
}
