# Modified by: odoo-backend agent — 2026-04-13 — Fix late_count domain, timezone, perf, filters
from odoo import fields, http
from odoo.http import request
from datetime import timedelta
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

        # OFs en retard (avec filtres date appliqués)
        now = fields.Datetime.now()
        late_count = MO.search_count(base_domain + date_domain + [
            ('state', 'in', ['confirmed', 'progress']),
            ('date_start', '<', now),
            ('qty_produced', '=', 0),
        ])

        # Disponibilité composants (avec filtres date appliqués)
        available_count = MO.search_count(base_domain + date_domain + [
            ('state', 'in', ['confirmed', 'progress']),
            ('reservation_state', '=', 'assigned'),
        ])
        waiting_count = MO.search_count(base_domain + date_domain + [
            ('state', 'in', ['confirmed', 'progress']),
            ('reservation_state', '=', 'confirmed'),
        ])

        # Production des N derniers jours
        date_n_ago = now - timedelta(days=recent_days)
        done_recent = MO.search_read(
            base_domain + [
                ('state', '=', 'done'),
                ('date_finished', '>=', date_n_ago.strftime('%Y-%m-%d')),
            ],
            fields=['product_id', 'product_qty', 'qty_produced', 'date_finished'],
            order='date_finished desc',
            limit=100,
        )

        # Production par jour (optimisé read_group)
        mchart_start = (now - timedelta(days=chart_days - 1)).strftime('%Y-%m-%d 00:00:00')
        mchart_domain = base_domain + [('state', '=', 'done'), ('date_finished', '>=', mchart_start)]
        mchart_groups = MO.read_group(mchart_domain, fields=['qty_produced:sum', 'date_finished'], groupby=['date_finished:day'])
        mchart_by_date = {}
        for g in mchart_groups:
            rng = g.get('__range', {}).get('date_finished:day', {})
            from_str = rng.get('from', '')
            if from_str:
                dk = from_str[:10]
                mchart_by_date[dk] = {'qty': g.get('qty_produced', 0), 'count': g.get('__count', 0)}
        daily_production = []
        for i in range(chart_days - 1, -1, -1):
            day = now - timedelta(days=i)
            day_key = day.strftime('%Y-%m-%d')
            data = mchart_by_date.get(day_key, {})
            daily_production.append({
                'date': day.strftime('%d/%m'),
                'count': data.get('count', 0),
                'qty': data.get('qty', 0),
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

        # Rendements des OFs terminés récents
        yield_data = []
        avg_yield = 0.0
        done_mos_for_yield = MO.search(
            base_domain + [
                ('state', '=', 'done'),
                ('date_finished', '>=', date_n_ago.strftime('%Y-%m-%d')),
            ],
            order='date_finished desc',
            limit=50,
        )
        total_raw_all = 0.0
        total_finished_all = 0.0
        total_waste_all = 0.0
        for mo in done_mos_for_yield:
            # Quantité brute matières consommées
            raw_qty = sum(
                sum(ml.quantity for ml in mv.move_line_ids) or mv.product_uom_qty
                for mv in mo.move_raw_ids.filtered(lambda m: m.state == 'done')
            )
            # Quantité produite (produit fini)
            finished_qty = mo.qty_produced or 0.0
            # Quantité déchets/pertes
            waste_qty = 0.0
            for mv in mo.move_byproduct_ids.filtered(lambda m: m.state == 'done'):
                categ_name = (mv.product_id.categ_id.complete_name or mv.product_id.categ_id.name or '').lower()
                if 'dechet' in categ_name or 'déchet' in categ_name or 'perte' in categ_name:
                    waste_qty += sum(ml.quantity for ml in mv.move_line_ids) or mv.product_uom_qty
            # Rendement = produit fini / matières premières
            mo_yield = (finished_qty / raw_qty * 100.0) if raw_qty else 0.0

            total_raw_all += raw_qty
            total_finished_all += finished_qty
            total_waste_all += waste_qty

            yield_data.append({
                'id': mo.id,
                'name': mo.name,
                'product': mo.product_id.display_name,
                'raw_qty': round(raw_qty, 2),
                'finished_qty': round(finished_qty, 2),
                'yield_pct': round(mo_yield, 1),
                'date': mo.date_finished.strftime('%d/%m/%Y') if mo.date_finished else '',
            })

        avg_yield = round(
            (total_finished_all / total_raw_all * 100.0) if total_raw_all else 0.0, 1
        )
        avg_waste = round(
            (total_waste_all / total_raw_all * 100.0) if total_raw_all else 0.0, 1
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
            'avg_yield': avg_yield,
            'avg_waste': avg_waste,
            'yield_data': yield_data,
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
