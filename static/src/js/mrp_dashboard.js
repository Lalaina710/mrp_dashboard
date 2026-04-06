/** @odoo-module **/

import { Component, useState, onWillStart, onMounted, onWillUnmount } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { rpc } from "@web/core/network/rpc";

class MrpDashboard extends Component {
    static template = "mrp_dashboard.MrpDashboard";
    static props = ["*"];

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({
            loading: true,
            data: {},
            // Filtres dynamiques
            filters: {
                chart_days: 7,
                recent_days: 30,
                active_mo_limit: 50,
                workorder_limit: 20,
                date_from: '',
                date_to: '',
                responsible_id: 0,
                product_id: 0,
            },
            // Données des listes déroulantes
            responsibles: [],
            products: [],
            // Panneau filtres visible/masqué
            showFilters: false,
            // Auto-refresh
            autoRefreshInterval: 0,
            // Dernière mise à jour
            lastUpdate: '',
        });
        this._refreshTimer = null;

        onWillStart(async () => {
            await this.loadFiltersData();
            await this.loadConfig();
            await this.loadData();
        });

        onMounted(() => {
            this._startAutoRefresh();
        });

        onWillUnmount(() => {
            this._stopAutoRefresh();
        });
    }

    async loadConfig() {
        try {
            const config = await this.orm.call(
                'mrp.dashboard.config', 'get_config', []
            );
            this.state.filters.chart_days = config.chart_days;
            this.state.filters.recent_days = config.recent_days;
            this.state.filters.active_mo_limit = config.active_mo_limit;
            this.state.filters.workorder_limit = config.workorder_limit;
            this.state.autoRefreshInterval = config.auto_refresh_interval;
        } catch (e) {
            console.warn("Config non disponible, valeurs par défaut utilisées");
        }
    }

    async loadFiltersData() {
        try {
            const data = await rpc("/mrp_dashboard/filters_data", {});
            this.state.responsibles = data.responsibles || [];
            this.state.products = data.products || [];
        } catch (e) {
            console.warn("Impossible de charger les filtres:", e);
        }
    }

    async loadData() {
        this.state.loading = true;
        try {
            const filters = { ...this.state.filters };
            // Nettoyer les filtres vides
            if (!filters.responsible_id) delete filters.responsible_id;
            if (!filters.product_id) delete filters.product_id;
            if (!filters.date_from) delete filters.date_from;
            if (!filters.date_to) delete filters.date_to;

            this.state.data = await rpc("/mrp_dashboard/data", { filters });
            this.state.lastUpdate = new Date().toLocaleTimeString("fr-FR");
        } catch (e) {
            console.error("MRP Dashboard error:", e);
            this.state.data = {
                state_counts: {},
                late_count: 0,
                available_count: 0,
                waiting_count: 0,
                daily_production: [],
                active_mos: [],
                done_recent_count: 0,
                done_recent_qty: 0,
                workcenters: [],
                workorders: [],
                avg_yield: 0,
                avg_waste: 0,
                yield_data: [],
            };
        }
        this.state.loading = false;
    }

    // --- Gestion des filtres ---

    toggleFilters() {
        this.state.showFilters = !this.state.showFilters;
    }

    onFilterChange(field, ev) {
        const value = ev.target.value;
        if (['chart_days', 'recent_days', 'active_mo_limit', 'workorder_limit',
             'responsible_id', 'product_id'].includes(field)) {
            this.state.filters[field] = parseInt(value) || 0;
        } else {
            this.state.filters[field] = value;
        }
    }

    applyFilters() {
        this.loadData();
    }

    resetFilters() {
        this.state.filters = {
            chart_days: 7,
            recent_days: 30,
            active_mo_limit: 50,
            workorder_limit: 20,
            date_from: '',
            date_to: '',
            responsible_id: 0,
            product_id: 0,
        };
        this.loadData();
    }

    // --- Auto-refresh ---

    onRefreshIntervalChange(ev) {
        this.state.autoRefreshInterval = parseInt(ev.target.value) || 0;
        this._startAutoRefresh();
    }

    _startAutoRefresh() {
        this._stopAutoRefresh();
        const interval = this.state.autoRefreshInterval;
        if (interval > 0) {
            this._refreshTimer = setInterval(() => this.loadData(), interval * 1000);
        }
    }

    _stopAutoRefresh() {
        if (this._refreshTimer) {
            clearInterval(this._refreshTimer);
            this._refreshTimer = null;
        }
    }

    // --- Formatage et helpers ---

    formatQty(qty) {
        if (!qty) return "0";
        return Math.round(qty).toLocaleString("fr-FR");
    }

    getBarHeight(qty) {
        const maxQty = Math.max(
            ...this.state.data.daily_production.map((d) => d.qty),
            1
        );
        return Math.max((qty / maxQty) * 150, 4);
    }

    getProgress(mo) {
        if (!mo.product_qty) return 0;
        return Math.round((mo.qty_produced / mo.product_qty) * 100);
    }

    getStateLabel(state) {
        const labels = {
            draft: "Brouillon",
            confirmed: "Confirmé",
            progress: "En cours",
            to_close: "A clôturer",
            done: "Terminé",
            cancel: "Annulé",
        };
        return labels[state] || state;
    }

    getAvailClass(mo) {
        const s = mo.components_availability_state;
        if (s === "available") return "available";
        if (s === "expected") return "expected";
        if (s === "late") return "late_avail";
        if (s === "unavailable") return "unavailable";
        return "unavailable";
    }

    getAvailLabel(mo) {
        const s = mo.components_availability_state;
        if (s === "available") return "Disponible";
        if (s === "expected") return "Attendu";
        if (s === "late") return "En retard";
        return "N/A";
    }

    hasActiveFilters() {
        const f = this.state.filters;
        return f.date_from || f.date_to || f.responsible_id || f.product_id
            || f.chart_days !== 7 || f.recent_days !== 30;
    }

    openMOs(state) {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: `OFs - ${this.getStateLabel(state)}`,
            res_model: "mrp.production",
            views: [
                [false, "list"],
                [false, "form"],
            ],
            domain: [["state", "=", state]],
            target: "current",
        });
    }

    openLateMOs() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "OFs en retard",
            res_model: "mrp.production",
            views: [
                [false, "list"],
                [false, "form"],
            ],
            domain: [
                ["state", "in", ["confirmed", "progress"]],
                ["is_delayed", "=", true],
            ],
            target: "current",
        });
    }

    openMO(moId) {
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "mrp.production",
            res_id: moId,
            views: [[false, "form"]],
            target: "current",
        });
    }
}

registry.category("actions").add("mrp_dashboard.MrpDashboard", MrpDashboard);
