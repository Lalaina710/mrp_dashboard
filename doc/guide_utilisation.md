# Guide d'utilisation — Tableau de bord Fabrication

## Table des matières

1. [Accéder au dashboard](#1-accéder-au-dashboard)
2. [Comprendre les KPI](#2-comprendre-les-kpi)
3. [Utiliser les filtres](#3-utiliser-les-filtres)
4. [Configurer le rafraîchissement automatique](#4-configurer-le-rafraîchissement-automatique)
5. [Naviguer vers les OFs](#5-naviguer-vers-les-ofs)
6. [Lire le graphique de production](#6-lire-le-graphique-de-production)
7. [Surveiller les postes de travail](#7-surveiller-les-postes-de-travail)
8. [Suivre les ordres de travail](#8-suivre-les-ordres-de-travail)
9. [Configurer les paramètres par défaut](#9-configurer-les-paramètres-par-défaut)
10. [Cas d'usage courants](#10-cas-dusage-courants)

---

## 1. Accéder au dashboard

1. Ouvrir le menu principal **Fabrication**
2. Cliquer sur **Tableau de bord** (premier élément du menu)

Le dashboard se charge et affiche les données en temps réel.

---

## 2. Comprendre les KPI

Les 8 cartes en haut du dashboard affichent les compteurs principaux :

### Cartes d'état des OFs

- **Brouillon** (gris) — OFs créés mais pas encore confirmés
- **Confirmés** (bleu) — OFs confirmés, en attente de lancement
- **En cours** (orange) — OFs en cours de production
- **A clôturer** (violet) — Production terminée, OF à valider
- **Terminés** (vert) — OFs entièrement clôturés

### Cartes d'alerte

- **En retard** (rouge) — OFs dont la date de début prévue est dépassée et dont aucune quantité n'a été produite. Ce sont les urgences à traiter en priorité.
- **Composants OK** (turquoise) — OFs dont tous les composants sont réservés et disponibles en stock
- **En attente** (jaune) — OFs en attente de réception de composants

### Interaction

Cliquer sur n'importe quelle carte ouvre la **liste filtrée** des OFs correspondants dans une vue standard Odoo, où vous pouvez trier, exporter, ou ouvrir chaque OF.

---

## 3. Utiliser les filtres

### Ouvrir le panneau

Cliquer sur le bouton **Filtres** dans l'en-tête du dashboard. Un panneau apparaît avec les options suivantes :

### Filtres disponibles

#### Date début / Date fin
- Permet de restreindre les données à une **période précise**
- Filtre sur la date de début prévue (`date_start`) des OFs
- Exemple : voir uniquement les OFs de mars 2026

#### Responsable
- Liste déroulante contenant tous les utilisateurs ayant des OFs assignés
- Permet de voir le dashboard **du point de vue d'un opérateur ou responsable**
- "-- Tous --" affiche les données de tous les utilisateurs

#### Produit
- Liste déroulante des produits fabriqués (jusqu'à 200 produits)
- Permet de suivre la production d'un **article spécifique**
- "-- Tous --" affiche tous les produits

#### Jours graphique
- **7 jours** — vue courte, idéale pour le suivi quotidien
- **14 jours** — vue bi-hebdomadaire
- **30 jours** — vue mensuelle

#### Période stats
- Détermine la période pour le calcul affiché en haut du graphique ("30j: X OFs / Y unités")
- **7 jours** — cette semaine
- **30 jours** — ce mois (par défaut)
- **60 jours** — 2 mois
- **90 jours** — trimestre

### Appliquer les filtres

1. Configurer les filtres souhaités
2. Cliquer sur **Appliquer**
3. Le dashboard se recharge avec les données filtrées
4. Un **point bleu** apparaît sur le bouton Filtres pour indiquer que des filtres sont actifs

### Réinitialiser

Cliquer sur **Réinitialiser** pour revenir aux valeurs par défaut et recharger toutes les données.

---

## 4. Configurer le rafraîchissement automatique

### Depuis le dashboard

Le sélecteur **Auto** dans l'en-tête permet de choisir l'intervalle :

| Option | Usage recommandé |
|---|---|
| **Off** | Travail ponctuel, consultation rapide |
| **30 secondes** | Suivi en temps réel sur écran de production |
| **1 minute** | Supervision active |
| **2 minutes** | Suivi régulier |
| **5 minutes** | Affichage permanent sur écran mural |

### Depuis la configuration

Le responsable MRP peut définir l'intervalle par défaut dans la configuration (voir section 9).

### Rafraîchissement manuel

Le bouton **Actualiser** (icône de rafraîchissement) force un rechargement immédiat à tout moment.

L'heure de la dernière mise à jour est affichée à gauche des contrôles.

---

## 5. Naviguer vers les OFs

### Depuis les cartes KPI

Cliquer sur une carte → ouvre la **vue liste** des OFs filtrés par cet état.

### Depuis le tableau des OFs actifs

Cliquer sur une **ligne du tableau** → ouvre le **formulaire** de l'OF directement.

Les OFs prioritaires sont signalés par une **étoile jaune** devant la référence.

---

## 6. Lire le graphique de production

### Les barres

- Chaque barre représente un jour
- La hauteur indique la **quantité totale produite** ce jour-là (OFs terminés)
- La valeur exacte est affichée au-dessus de chaque barre
- La date est affichée en dessous (format jj/mm)

### Le résumé

En haut à droite du graphique :
- **X OFs** — nombre total d'OFs terminés sur la période stats
- **Y unités** — quantité totale produite sur la période stats

### Interpréter

- Des barres régulières indiquent une production stable
- Des barres à zéro signalent des jours sans production (weekend, arrêt, etc.)
- Une tendance à la baisse peut signaler un problème à investiguer

---

## 7. Surveiller les postes de travail

Les postes de travail sont affichés sous forme de cartes dans la colonne gauche :

| Couleur bordure | État | Signification |
|---|---|---|
| **Vert** | En production | Le poste fonctionne normalement |
| **Rouge** | Bloqué | Le poste est arrêté (panne, problème) |
| **Gris** | En maintenance | Maintenance préventive ou corrective en cours |

Chaque carte affiche aussi l'**efficacité** du poste (en %). Une efficacité de 100% signifie que le poste travaille au temps standard.

---

## 8. Suivre les ordres de travail

La section "Ordres de travail en cours" liste les opérations actives :

| Badge | Signification |
|---|---|
| **Prêt** (bleu) | L'opération peut démarrer |
| **En cours** (orange) | L'opération est en cours d'exécution |
| **En attente** (gris) | L'opération attend une étape précédente |

Chaque ligne affiche le **nom de l'opération**, le **poste de travail** assigné et l'**OF** associé.

---

## 9. Configurer les paramètres par défaut

> Réservé aux **Responsables de fabrication** (Managers MRP)

### Accéder à la configuration

**Fabrication > Configuration > Config. Dashboard**

### Créer une configuration

1. Cliquer sur **Nouveau**
2. Remplir les paramètres :
   - **Jours graphique production** — nombre de jours par défaut dans le graphique (défaut : 7)
   - **Jours statistiques récentes** — période de calcul des totaux (défaut : 30)
   - **Limite OFs actifs** — combien d'OFs afficher dans le tableau (défaut : 50)
   - **Limite ordres de travail** — combien d'ordres de travail afficher (défaut : 20)
   - **Rafraîchissement auto** — intervalle par défaut
   - **Société** — la société concernée (en multi-société)
3. Cliquer sur **Enregistrer**

### Multi-société

Si vous gérez plusieurs sociétés, créez une configuration distincte pour chacune. Le dashboard chargera automatiquement la configuration correspondant à la société active de l'utilisateur.

### Pas de configuration ?

Si aucune configuration n'existe pour la société, le dashboard utilise les valeurs par défaut :
- 7 jours pour le graphique
- 30 jours pour les stats
- 50 OFs actifs max
- 20 ordres de travail max
- Pas d'auto-refresh

---

## 10. Cas d'usage courants

### Réunion de production quotidienne

1. Ouvrir le dashboard
2. Vérifier les cartes **En retard** et **En attente** en priorité
3. Consulter le graphique pour voir la production de la veille
4. Parcourir le tableau des OFs actifs pour identifier les blocages

### Suivi sur écran d'atelier

1. Ouvrir le dashboard sur un écran dédié
2. Configurer l'auto-refresh à **30 secondes** ou **1 minute**
3. Le dashboard se met à jour en continu sans intervention

### Analyse par produit

1. Ouvrir les filtres
2. Sélectionner le produit dans la liste déroulante
3. Étendre la période stats à **90 jours**
4. Cliquer sur **Appliquer**
5. Le dashboard affiche uniquement les données de ce produit

### Suivi d'un responsable

1. Ouvrir les filtres
2. Sélectionner le responsable
3. Appliquer
4. Voir les KPI et OFs assignés à cette personne

### Analyse mensuelle

1. Ouvrir les filtres
2. Définir **Date début** = 01/03/2026, **Date fin** = 31/03/2026
3. Mettre **Jours graphique** à 30
4. Mettre **Période stats** à 30 jours
5. Appliquer
6. Le dashboard affiche la vue complète du mois de mars

---

## Raccourcis clavier

Le dashboard utilise les interactions souris standard d'Odoo :
- **Clic** sur une carte KPI → liste filtrée
- **Clic** sur une ligne du tableau → formulaire de l'OF
- **F5** ou bouton Actualiser → rafraîchir les données
