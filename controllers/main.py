from odoo import http
from odoo.http import request
from datetime import datetime, timedelta
from werkzeug.exceptions import Forbidden


class MrpDashboardController(http.Controller):

    @http.route('/mrp_dashboard/data', type='json', auth='user')
    def get_dashboard_data(self, **kwargs):
        if not request.env.user.has_group('mrp_dashboard.group_mrp_dashboard_user'):
            raise Forbidden("Accès non autorisé au dashboard fabrication")
        MO = request.env['mrp.production']

        # Récupérer les paramètres dynamiques (filtres du frontend)
        filters = kwargs.get('filters', {})
        chart_days = filters.get('chart_days', 7)
        recent_days = filters.get('recent_days', 30)
        active_mo_limit = filters.get('active_mo_limit', 50)
        workorder_limit = filters.get('workorder_limit', 20)
        date_from = filters.get('date_from')
        date_to = filters.get('date_to')
        responsible_id = filters.get('responsible_id')
        product_id = filters.get('product_id')

        # Construire le domaine de base à partir des filtres
        base_domain = []
        if responsible_id:
            base_domain.append(('user_id', '=', responsible_id))
        if product_id:
            base_domain.append(('product_id', '=', product_id))

        # Domaine temporel pour les filtres date
        date_domain = []
        if date_from:
            date_domain.append(('date_start', '>=', date_from))
        if date_to:
            date_domain.append(('date_start', '<=', date_to))

        # Compteurs par état
        states = ['draft', 'confirmed', 'progress', 'to_close', 'done', 'cancel']
        state_counts = {}
        for state in states:
            domain = base_domain + date_domain + [('state', '=', state)]
            state_counts[state] = MO.search_count(domain)

        # OFs en retard
        late_count = MO.search_count(base_domain + [
            ('state', 'in', ['confirmed', 'progress']),
            ('date_start', '<', datetime.now()),
            ('qty_produced', '=', 0),
        ])

        # Disponibilité composants
        available_count = MO.search_count(base_domain + [
            ('state', 'in', ['confirmed', 'progress']),
            ('reservation_state', '=', 'assigned'),
        ])
        waiting_count = MO.search_count(base_domain + [
            ('state', 'in', ['confirmed', 'progress']),
            ('reservation_state', '=', 'confirmed'),
        ])

        # Production des N derniers jours
        date_n_ago = datetime.now() - timedelta(days=recent_days)
        done_recent = MO.search_read(
            base_domain + [
                ('state', '=', 'done'),
                ('date_finished', '>=', date_n_ago.strftime('%Y-%m-%d')),
            ],
            fields=['product_id', 'product_qty', 'qty_produced', 'date_finished'],
            order='date_finished desc',
            limit=100,
        )

        # Production par jour (N derniers jours)
        daily_production = []
        for i in range(chart_days - 1, -1, -1):
            day = datetime.now() - timedelta(days=i)
            day_start = day.replace(hour=0, minute=0, second=0).strftime('%Y-%m-%d %H:%M:%S')
            day_end = day.replace(hour=23, minute=59, second=59).strftime('%Y-%m-%d %H:%M:%S')
            domain = base_domain + [
                ('state', '=', 'done'),
                ('date_finished', '>=', day_start),
                ('date_finished', '<=', day_end),
            ]
            count = MO.search_count(domain)
            qty = sum(mo['qty_produced'] for mo in MO.search_read(
                domain, fields=['qty_produced'],
            ))
            daily_production.append({
                'date': day.strftime('%d/%m'),
                'count': count,
                'qty': qty,
            })

        # OFs actifs
        active_domain = base_domain + [
            ('state', 'in', ['draft', 'confirmed', 'progress', 'to_close']),
        ]
        if date_from:
            active_domain.append(('date_start', '>=', date_from))
        if date_to:
            active_domain.append(('date_start', '<=', date_to))

        active_mos = MO.search_read(
            active_domain,
            fields=[
                'name', 'product_id', 'product_qty', 'qty_produced',
                'state', 'date_start', 'date_deadline', 'priority',
                'reservation_state', 'components_availability_state',
                'user_id', 'is_delayed',
            ],
            order='priority desc, date_start asc',
            limit=active_mo_limit,
        )

        # Postes de travail
        workcenters = request.env['mrp.workcenter'].search_read(
            [],
            fields=['name', 'working_state', 'time_efficiency'],
        )

        # Ordres de travail en cours
        workorders = request.env['mrp.workorder'].search_read(
            [('state', 'in', ['ready', 'progress', 'waiting'])],
            fields=['name', 'state', 'workcenter_id', 'production_id',
                    'duration_expected', 'duration'],
            order='state desc',
            limit=workorder_limit,
        )

        # Config pour le frontend
        config = request.env['mrp.dashboard.config'].get_config()

        return {
            'state_counts': state_counts,
            'late_count': late_count,
            'available_count': available_count,
            'waiting_count': waiting_count,
            'daily_production': daily_production,
            'active_mos': active_mos,
            'done_recent_count': len(done_recent),
            'done_recent_qty': sum(r['qty_produced'] for r in done_recent),
            'workcenters': workcenters,
            'workorders': workorders,
            'config': config,
        }

    @http.route('/mrp_dashboard/filters_data', type='json', auth='user')
    def get_filters_data(self):
        """Retourne les données pour les listes déroulantes des filtres."""
        if not request.env.user.has_group('mrp_dashboard.group_mrp_dashboard_user'):
            raise Forbidden("Accès non autorisé au dashboard fabrication")
        # Responsables ayant des OFs
        users = request.env['mrp.production'].read_group(
            [('user_id', '!=', False)],
            fields=['user_id'],
            groupby=['user_id'],
        )
        responsible_list = [
            {'id': u['user_id'][0], 'name': u['user_id'][1]}
            for u in users if u['user_id']
        ]

        # Produits fabriqués
        products = request.env['mrp.production'].read_group(
            [],
            fields=['product_id'],
            groupby=['product_id'],
            limit=200,
        )
        product_list = [
            {'id': p['product_id'][0], 'name': p['product_id'][1]}
            for p in products if p['product_id']
        ]

        return {
            'responsibles': responsible_list,
            'products': product_list,
        }
