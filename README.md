# Tableau de bord Fabrication (MRP Dashboard)

Module Odoo 18 — Dashboard MRP dynamique avec KPI en temps réel, filtres interactifs et configuration par société.

**Auteur :** SOPROMER  
**Version :** 18.0.2.0.0  
**Licence :** LGPL-3  
**Dépendance :** `mrp`

---

## Fonctionnalités

### KPI en temps réel (8 indicateurs)

| Indicateur | Description |
|---|---|
| **Brouillon** | Nombre d'OFs en état brouillon |
| **Confirmés** | OFs confirmés en attente de lancement |
| **En cours** | OFs en cours de production |
| **A clôturer** | OFs terminés à valider |
| **Terminés** | OFs clôturés |
| **En retard** | OFs dont la date de début est dépassée sans production |
| **Composants OK** | OFs avec composants réservés (disponibles) |
| **En attente** | OFs en attente de composants |

Chaque carte KPI est **cliquable** et ouvre la liste filtrée des OFs correspondants.

### Graphique de production

- Graphique en barres de la production quotidienne (quantité produite par jour)
- Période configurable : **7, 14 ou 30 jours**
- Résumé en haut à droite : total OFs terminés et quantités sur la période stats

### Tableau des OFs actifs

- Liste des ordres de fabrication non terminés (brouillon, confirmé, en cours, à clôturer)
- Colonnes : Référence, Produit, Progression (barre), État, Disponibilité composants
- Indicateur de priorité (étoile) pour les OFs urgents
- Cliquer sur une ligne ouvre le formulaire de l'OF
- Nombre d'enregistrements configurable (par défaut : 50)

### Postes de travail

- Vue en cartes de tous les postes de travail
- État visuel : En production (vert), Bloqué (rouge), En maintenance (gris)
- Affichage de l'efficacité (%) de chaque poste

### Ordres de travail en cours

- Liste des ordres de travail actifs (Prêt, En cours, En attente)
- Poste de travail assigné et OF associé
- Nombre configurable (par défaut : 20)

---

## Filtres dynamiques

Le panneau de filtres s'ouvre via le bouton **Filtres** dans l'en-tête du dashboard.

| Filtre | Description |
|---|---|
| **Date début** | Filtrer les OFs à partir de cette date |
| **Date fin** | Filtrer les OFs jusqu'à cette date |
| **Responsable** | Filtrer par utilisateur assigné (liste dynamique) |
| **Produit** | Filtrer par produit fabriqué (liste dynamique) |
| **Jours graphique** | Nombre de jours affichés dans le graphique (7/14/30) |
| **Période stats** | Période pour les statistiques récentes (7/30/60/90 jours) |

- Un **point bleu** apparaît sur le bouton Filtres quand des filtres sont actifs
- Bouton **Appliquer** pour lancer la recherche
- Bouton **Réinitialiser** pour revenir aux valeurs par défaut

---

## Rafraîchissement automatique

Le sélecteur dans l'en-tête permet de configurer le rafraîchissement automatique :

- **Off** — rafraîchissement manuel uniquement
- **30 secondes**
- **1 minute**
- **2 minutes**
- **5 minutes**

L'heure de la dernière mise à jour est affichée à côté des contrôles.

---

## Installation

### Prérequis

- Odoo 18 Community ou Enterprise
- Module `mrp` (Fabrication) installé et configuré

### Étapes

1. Copier le dossier `mrp_dashboard` dans le répertoire des addons personnalisés :

   ```
   cp -r mrp_dashboard /chemin/vers/odoo18/custom-addons/
   ```

2. Mettre à jour la liste des modules dans Odoo :

   **Applications > Mettre à jour la liste des applications**

3. Rechercher et installer le module :

   **Applications > Rechercher "Tableau de bord Fabrication" > Installer**

4. Ou via la ligne de commande :

   ```bash
   python odoo-bin -d ma_base -u mrp_dashboard --stop-after-init
   ```

### Mise à jour

Pour mettre à jour après modification :

```bash
python odoo-bin -d ma_base -u mrp_dashboard --stop-after-init
```

---

## Configuration

### Accéder à la configuration

**Fabrication > Configuration > Config. Dashboard**

> Seuls les **Responsables de fabrication** (groupe `mrp.group_mrp_manager`) peuvent modifier la configuration.

### Paramètres disponibles

| Paramètre | Par défaut | Description |
|---|---|---|
| Jours graphique production | 7 | Nombre de jours dans le graphique en barres |
| Jours statistiques récentes | 30 | Période pour le calcul des totaux (OFs terminés) |
| Limite OFs actifs | 50 | Nombre max d'OFs affichés dans le tableau |
| Limite ordres de travail | 20 | Nombre max d'ordres de travail affichés |
| Rafraîchissement auto | Désactivé | Intervalle de mise à jour automatique |
| Société | Société courante | Configuration par société (multi-société) |

### Multi-société

Chaque société peut avoir sa propre configuration. Le dashboard charge automatiquement la configuration de la société active de l'utilisateur.

---

## Droits d'accès

| Groupe | Voir le dashboard | Voir la config | Modifier la config |
|---|---|---|---|
| Utilisateur MRP | Oui | Oui (lecture) | Non |
| Responsable MRP | Oui | Oui | Oui |

---

## Architecture technique

```
mrp_dashboard/
├── __init__.py
├── __manifest__.py
├── .gitignore
├── controllers/
│   ├── __init__.py
│   └── main.py              # Endpoints RPC
├── models/
│   ├── __init__.py
│   └── mrp_dashboard_config.py  # Modèle de configuration
├── security/
│   └── ir.model.access.csv  # Droits d'accès
├── static/src/
│   ├── css/mrp_dashboard.css # Styles
│   ├── js/mrp_dashboard.js   # Composant OWL
│   └── xml/mrp_dashboard.xml # Template OWL
├── views/
│   ├── mrp_dashboard_views.xml        # Menu + Action client
│   └── mrp_dashboard_config_views.xml # Vues configuration
├── doc/
│   └── guide_utilisation.md  # Guide détaillé
└── README.md
```

### Endpoints API

| Route | Type | Description |
|---|---|---|
| `/mrp_dashboard/data` | JSON (POST) | Données du dashboard avec filtres |
| `/mrp_dashboard/filters_data` | JSON (POST) | Listes pour les sélecteurs de filtres |

### Paramètres de `/mrp_dashboard/data`

```json
{
  "filters": {
    "chart_days": 7,
    "recent_days": 30,
    "active_mo_limit": 50,
    "workorder_limit": 20,
    "date_from": "2026-01-01",
    "date_to": "2026-03-31",
    "responsible_id": 2,
    "product_id": 15
  }
}
```

### Technologies

- **Frontend :** OWL 2 (framework réactif Odoo), Bootstrap 5
- **Backend :** Odoo 18 HTTP Controllers, ORM
- **Modèles interrogés :** `mrp.production`, `mrp.workcenter`, `mrp.workorder`

---

## Dépannage

| Problème | Solution |
|---|---|
| Le dashboard ne s'affiche pas | Vérifier que le module `mrp` est installé. Vider le cache navigateur (Ctrl+Maj+Suppr). |
| Erreur "Access Denied" | Vérifier que l'utilisateur a le groupe "Utilisateur MRP" au minimum. |
| Les filtres responsable/produit sont vides | Normal si aucun OF n'existe encore dans le système. |
| L'auto-refresh ne fonctionne pas | Vérifier que la valeur est différente de "Off" dans le sélecteur. |
| Les données ne correspondent pas | Cliquer sur "Actualiser" pour forcer un rechargement. |

---

## Licence

Ce module est distribué sous licence [LGPL-3](https://www.gnu.org/licenses/lgpl-3.0.html).
