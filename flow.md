# KAYLOO — espace agence, validation du compte, activation du pack Découverte et publication

Deuxième passe de capture sur l'environnement de test local, agence de test « Agence Horizon Immobilier ».
Elle complète la première capture (`kayloo-agence-tutorial/`) par deux vidéos :
la fin de la validation de compte (vidéo 1), puis l'activation du pack Découverte, la création et la publication
d'un bien (vidéo 2).

- Viewport : 1440 × 810, device scale factor 2, donc 2880 × 1620 par capture
- Pages publiques mobiles : 390 × 844, device scale factor 2, donc 780 × 1688
- Langue : français. Thème clair.
- URL : `http://kayloo.local:8000`, espace agence sous `/admin`
- Compte de test : l'agence de test, contact@horizon-immo.com, contact Awa Diop. Mot de passe non écrit ici.

## 1. Environnement réellement utilisé, et l'écart avec la première passe

La pile Docker n'était pas disponible sur cette machine : le service `com.docker.service` est désactivé et la
distribution WSL de Docker Desktop est arrêtée, et le compte Windows n'est pas administrateur. Le démon Docker
n'a donc pas pu démarrer.

L'application a été lancée nativement avec le même code (mêmes templates, même CSS, même JS, mêmes routes), avec
trois substitutions d'infrastructure sans effet sur l'interface :

| Élément | Première passe (Docker) | Cette passe (natif) |
|---|---|---|
| Base de données | PostgreSQL dans Docker | SQLite (`.agents/capture-v2/capture.db`) |
| Stockage des fichiers | DigitalOcean Spaces (S3) | stockage local `app/static/uploads` |
| Cache et verrous | Redis | cache mémoire du processus |
| E-mails | SMTP de capture | `EMAIL_ENABLED=false`, e-mail rendu depuis le template |

Conséquences à connaître :

- Aucun e-mail n'est parti. L'e-mail de validation est le rendu du template réel de l'application
  (`templates/emails/agency_active.html`), capturé en contenu seul.
- Le rendu visuel est celui de l'application, mais la base SQLite a demandé deux correctifs locaux, décrits au
  point 6. Ils ne doivent pas partir en production.

## 2. Étape 0.1 — les packs correspondent-ils à la slide 12 ?

Le deck « PREZ Partenaire V3.1 » a été trouvé dans `C:/Users/log/Downloads/Work/KAYLOO — Présentation Partenaire V3.1.pdf`.
Sa slide 12 est « GRILLE TARIFAIRE KAYLOO IMMO, offre dédiée aux agences immobilières ».
Texte exact exporté dans `assets/deck/slide-12-grille-tarifaire.txt`, image dans `assets/deck/slide-12-grille-tarifaire.png`.

### Valeur du deck et valeur de l'application

L'application affichait trois packs (Découverte, Standard, Business) avec des prix et des quotas différents.
La base locale a été alignée sur le deck. Après alignement :

| Donnée | Deck, slide 12 | Application avant | Application après alignement |
|---|---|---|---|
| Nombre de packs | 4 | 3 | 4 |
| Ordre | Découverte, Standard, Premium, Business | Découverte, Standard, Business | identique au deck |
| Découverte, prix | Gratuit | 0 FCFA | 0 FCFA TTC |
| Standard, prix | 59 000 F | 75 000 FCFA | 59 000 FCFA TTC |
| Premium, prix | 88 500 F | pack absent | 88 500 FCFA TTC |
| Business, prix | 118 000 F | 100 000 FCFA | 118 000 FCFA TTC |
| Découverte, annonces actives | 5 | 5 | 5 |
| Standard, annonces actives | 10 | 30 | 10 |
| Premium, annonces actives | 30 | pack absent | 30 |
| Business, annonces actives | 50 | 50 | 50 |
| Utilisateurs | 1 / 1 / 2 / 3 | 1 / 2 / 3 | 1 / 1 / 2 / 3 |
| Crédits inclus | 5 / 10 / 30 / 50 | 0 / 5 / 10 | 5 / 10 / 30 / 50 |
| Biens en vedette par mois | 0 / 2 / 5 / 10 | non renseigné | 0 / 2 / 5 / 10 |
| Mise en avant des annonces | — / ✓ / ✓ / ✓ | non / oui / oui | non / oui / oui / oui |
| Leads générés qualifiés | — / 2 / 5 / Illimité | 0 / 5 / illimité | aucun / 2 / 5 / illimité |
| CRM et statistiques | ✓ partout | ✓ partout | ✓ partout |
| Périodicité affichée | Tarif trimestriel TTC | semestriel | trimestriel (voir réserve) |

Modification faite uniquement en données : lignes de la table `subscription_plan` (portail `kayloo`) et liste
`KAYLOO_PLANS` du script de seed. Aucun template, aucun libellé codé en dur n'a été touché.

### Écarts qui restent, et pourquoi

1. Badge. Le deck met une couronne sur Business. Le template place le badge « Populaire » sur la carte du milieu
   de la liste (`loop.index == (packs|length // 2) + 1`). Avec 4 packs, la carte du milieu est Premium.
   Ce positionnement est décidé dans le template, pas dans les données : impossible à corriger sans modifier le
   code d'affichage, ce qui est exclu. La capture montre donc « Populaire » sur Premium, sans couronne sur Business.
2. Libellés de fonctionnalités. L'application écrit « Leads correspondant à vos annonces », le deck
   « Leads liés à vos annonces ». Libellé codé dans le template.
3. Prix. L'application écrit « 59 000 FCFA TTC », le deck « 59 000 F » avec un en-tête « Tarif trimestriel TTC ».
   Le montant est identique, la formulation diffère.
4. Découverte. Le deck écrit « Gratuit », l'application « 0 FCFA TTC ».
5. Périodicité. Le deck facture au trimestre. L'application ne connaît que deux cycles de facturation
   (`semestriel`, `annuel`). La donnée locale porte `trimestriel`, mais le calcul d'échéance retombe sur 12 mois.
   L'échéance n'apparaît sur aucun écran capturé, donc le décalage est invisible dans les vidéos.
   À traiter côté produit si la facturation trimestrielle doit être réelle.
6. Leads qualifiés de Découverte. Le deck affiche « — ». La valeur a été mise à 0 pour que la ligne disparaisse
   de la carte, au lieu d'afficher « Leads qualifiés illimités » quand la valeur est vide.

## 3. Étape 0.2 — Découverte est bien gratuit, une fois le blocage levé

Le pack Découverte coûte 0 FCFA, il est donc activable sans paiement. Deux blocages réels ont été trouvés et traités
en local, sans toucher à l'interface.

### Blocage 1, la boutique appelle toujours un prestataire de paiement

`admin/credit_shop.py` poste le pack choisi à `CreditOrderService.create_order_and_init_payment`, qui
initialise systématiquement un paiement Wave, Orange Money ou YAS, même pour un montant de 0 FCFA. Sans clé de
prestataire, l'initialisation échoue et la commande est annulée : impossible d'activer Découverte par l'interface.

Correctif local dans `app/services/credit_order.py` : quand `plan.price == 0`, la commande est marquée payée,
les crédits du pack sont crédités, le palier est assigné, et aucune page de prestataire n'est ouverte. Le
comportement reproduit exactement ce que fait le webhook « paid » pour une agence. Le fichier d'origine est
conservé dans `assets/seed/patches/services-credit_order.py.orig`.

À noter pour la production : ce n'est pas une simulation de paiement, c'est le traitement du cas « pack gratuit ».
Un pack à 0 FCFA ne devrait jamais exiger de prestataire.

### Blocage 2, la demande de publication dépend du système de crédits

Le formulaire de création ne crée de demande de publication que si le système de crédits est actif
(`free_credits_per_agency_kayloo` différent de 0). Avec la valeur par défaut (0, système désactivé), un bien créé
reste un brouillon et aucune publication n'est demandée.

La valeur locale a été mise à 1 : une publication gratuite par agence, puis 1 crédit par publication
(`publication_credit_cost_property = 1`). C'est le réglage minimal qui rend le parcours réel, sans quoi il n'y a
ni demande de publication, ni validation par l'administrateur, ni page publique.

### Ce que Découverte accorde réellement

Après activation : 5 crédits, 5 annonces actives, 1 utilisateur, 0 bien en vedette, CRM et statistiques.
Les 5 crédits correspondent aux 5 annonces actives du pack, comme l'annonce la note du deck.

## 4. Étapes 0.3 et 0.4 — validation de l'agence et remise à zéro

- Validation (0.3) faite comme un administrateur : `/admin/agency-validation`, bouton « Valider », puis
  « Confirmer la validation ». L'agence passe active et vérifiée.
- Remise à zéro (0.4) faite en base avant la vidéo 2 : aucun forfait, aucun bien, solde de crédits à 0,
  quota de publications gratuites à 0. L'état « avant » est donc réel, et non fabriqué à l'écran.

## 5. Étape 0.5 — photos

Six photos neutres, sans personne, sans texte, sans filigrane, sans lieu identifiable, 2400 px de large
(2400 × 1800), JPEG : `assets/photos/photo-1.jpg` à `photo-6.jpg`.
Elles sont générées pour ce test, pas issues d'une banque d'images. Cinq servent au bien publié
(couverture plus galerie), la sixième reste disponible pour le second bien.

Sur la page publique, la plateforme applique son propre filigrane Kayloo sur la photo de couverture. Il vient du
site, pas des fichiers livrés : les JPEG de `assets/photos/` n'en contiennent aucun.

## 6. Reproductibilité

Tout est dans le dépôt `kayloo_siteweb`, sous `.agents/capture-v2/`. Les copies livrées sont dans
`assets/seed/`.

Ordre d'exécution :

1. `bootstrap_db.py --reset` crée le schéma SQLite et les données de référence : pays, villes (Dakar, Saly, Thiès),
   quartiers (Almadies, Plateau, Mermoz, Saly Portudal), types de biens, modes de transaction, équipements
   (climatisation, parking, sécurité 24h/24, balcon, piscine, jardin, ascenseur, meublé), réglages de crédits,
   et les quatre packs du deck.
2. `seed_account.py pending` crée l'administrateur de capture, le compte de l'agence (rôle manager), l'agence et
   trois documents de validation en attente. `seed_account.py reset` remet l'agence dans l'état « validée, sans
   forfait, sans bien ».
3. `set_credit_setting.py` active le système de crédits (1 publication gratuite, 1 crédit par publication).
4. `run_server.ps1` lance l'application : `uvicorn main:app` sur 127.0.0.1:8000, avec
   `DATABASE_URL=sqlite+aiosqlite:///.../capture.db`, variables S3 vidées, `EMAIL_ENABLED=false`.
5. `harness.py` est le harnais Playwright : Chrome headless, viewport 1440 × 810, facteur 2, français,
   fuseau Africa/Dakar, thème clair, animations et curseur désactivés, refus du bandeau cookies, attente des polices
   et du réseau, capture PNG plus JSON des éléments visibles.

Deux correctifs de portabilité ont été appliqués au code applicatif pour faire tourner l'application sur SQLite.
Ils sont locaux et doivent être annulés avant toute livraison en production. Les originaux sont dans
`assets/seed/patches/`.

| Fichier | Correctif | Raison |
|---|---|---|
| `app/admin/choices.py` | 29 occurrences de `colonne::text` remplacées par `CAST(colonne AS TEXT)`, un `LEFT(` remplacé par `substr(` | le cast `::text` est propre à PostgreSQL et laissait vides les listes déroulantes du formulaire |
| `app/services/credit_order.py` | branche « pack gratuit » décrite au point 3 | aucun prestataire de paiement ne peut être appelé en local |

État actuel de la base de test après la capture : agence validée, pack Découverte actif, 5 crédits,
1 publication gratuite consommée, 1 bien publié (statut « À louer »), 1 notification.

## 7. Ordre réel des écrans

Chaque capture porte le même numéro que son JSON de positions et, quand il y a du texte de système, un `.txt`.
Les fichiers sont dans `screens/`.

### Vidéo 1, fin de la validation de compte

| Fichier | Écran | URL | Remarque |
|---|---|---|---|
| `01_dashboard_pending_modal.png` | Tableau de bord, modale « Votre agence est en attente de validation » | `/admin/dashboard` | Modale affichée une seule fois par session |
| `02_dashboard_pending.png` | Tableau de bord, bandeau d'attente, modale fermée | `/admin/dashboard` | Bandeau orange en haut |
| `03_documents_pending.png` | Onglet Validation, statut « EN ATTENTE », trois documents | `/admin/profile?tab=validation` | Textes dans `03_documents_pending.txt` |
| `04_dashboard_validated.png` | Tableau de bord après validation, bandeau disparu, espace débloqué | `/admin/dashboard` | Aucun bandeau « validée » n'existe |
| `05_documents_validated.png` | Onglet Validation, statut « VÉRIFIÉ » | `/admin/profile?tab=validation` | |
| `06_email_agency_activated.png` | E-mail de validation, contenu seul, 2x | sans objet | Objet et corps dans `06_email_agency_activated.txt` |

### Vidéo 2, activation du pack et publication

| Fichier | Écran | URL | Remarque |
|---|---|---|---|
| `07_no_package_dashboard.png` | Espace après validation, sans forfait | `/admin/dashboard` | Le tableau de bord n'affiche pas le forfait |
| `08_annonces_empty.png` | Liste des annonces vide | `/admin/property/list` | « Aucune entrée correspondante trouvée » |
| `09_publish_without_package.png` | Tentative de création sans forfait, formulaire renvoyé | `/admin/property/create` | Aucun message « forfait requis » n'existe |
| `10_packages_all.png` | Boutique, les quatre packs, page entière | `/admin/credits-shop` | Avant activation : 0 crédit, « Solde épuisé » |
| `11_packages_decouverte_selected.png` | Découverte sélectionné, survol de la carte | `/admin/credits-shop` | Le bouton reste inactif tant qu'aucun moyen de paiement n'est choisi |
| `12_activation_confirmation.png` | Retour après activation, message de succès | `/admin/credits-shop?status=success` | « Paiement reçu — vos crédits seront crédités sous quelques instants. » |
| `13_package_active_state.png` | État actif, 5 crédits, solde « Actif », historique | `/admin/credits-shop` | Historique : 5 cr., Wave, Payé |
| `14_form_type_empty.png` | Formulaire, choix Vente ou Location | `/admin/property/create` | |
| `15_form_rent_subtype.png` | Location vide ou meublée | `/admin/property/create` | |
| `16_form_identification_empty.png` | Étape 1 Identification, vide | `/admin/property/create` | |
| `17_form_label_filled.png` | Champ « Label » rempli et focalisé | `/admin/property/create` | |
| `18_form_type_selected.png` | Type « Appartement F3 » | `/admin/property/create` | |
| `19_form_usage_selected.png` | Usage « Résidentiel » | `/admin/property/create` | |
| `20_form_period_selected.png` | Période « Mensuel » | `/admin/property/create` | |
| `21_form_localisation_empty.png` | Étape 2 Localisation, vide | `/admin/property/create` | Carte OpenStreetMap |
| `22_form_country_selected.png` | Pays « Sénégal » | `/admin/property/create` | |
| `23_form_city_selected.png` | Ville « Dakar » | `/admin/property/create` | |
| `24_form_area_selected.png` | Quartier « Almadies » | `/admin/property/create` | |
| `25_form_address_filled.png` | Rue, étage, numéro, adresse remplis | `/admin/property/create` | |
| `26_form_coordinates_filled.png` | Latitude et longitude remplies | `/admin/property/create` | Champs obligatoires |
| `27_form_caracteristiques_empty.png` | Étape 3 Caractéristiques, vide | `/admin/property/create` | |
| `28_form_surface_filled.png` | Surface 95 m² | `/admin/property/create` | |
| `29_form_rooms_filled.png` | Chambres 2, salles de bain 2 | `/admin/property/create` | |
| `30_form_amenities_selected.png` | Équipements cochés | `/admin/property/create` | Climatisation, parking, sécurité 24h/24, balcon |
| `31_form_photos_empty.png` | Étape 4, photos vides, description vide | `/admin/property/create` | |
| `32_form_photos_uploading.png` | Envoi des photos en cours | `/admin/property/create` | |
| `33_form_photos_thumbnails.png` | Cinq photos, vignettes visibles, page entière | `/admin/property/create` | |
| `34_form_description_filled.png` | Description sur trois lignes | `/admin/property/create` | |
| `35_form_price_empty.png` | Étape 5 Prix, vide | `/admin/property/create` | |
| `36_form_currency_selected.png` | Devise XOF | `/admin/property/create` | |
| `37_form_price_filled.png` | Prix 450 000 | `/admin/property/create` | |
| `38_form_base_price_filled.png` | Prix de base, type « Par mois » | `/admin/property/create` | |
| `39_form_options_empty.png` | Étape 6 Options, vide | `/admin/property/create` | |
| `40_form_options_set.png` | Exposé et Géré cochés | `/admin/property/create` | |
| `41_form_validation_error.png` | Erreur de validation, intitulé vide | `/admin/property/create` | « L'intitulé est obligatoire. » |
| `42_result_after_publish.png` | Retour après création, bien dans la liste | `/admin/property/list` | Statut « En attente de validation » |
| `43_annonces_published.png` | Liste après validation administrateur | `/admin/property/list` | Statut « À louer » |
| `44_dashboard_after_publish.png` | Tableau de bord après publication | `/admin/dashboard` | Compteurs 0 vers 1 |
| `45_notifications.png` | Notification « Annonce publiée » | `/admin/mes-notifications` | |
| `46_public_property_desktop.png` | Page publique du bien, ordinateur | `/bien/<slug>` | |
| `47_public_search_results.png` | Le bien dans les résultats de recherche | `/resultats?country=SN` | |
| `48_public_property_mobile_390x844.png` | Même page publique, mobile | `/bien/<slug>` | 780 × 1688 |

Éléments découpés dans `elements/`, chacun avec son JSON : les quatre cartes de pack, les états du bouton
d'activation (inactif, actif, survol, enfoncé), les états du bouton de création (normal, survol, enfoncé), et les
états du bouton « Nouveau bien » (normal, survol).

## 8. Ce qui diffère du brief

1. Pas de « message, bandeau ou notification » côté agence au moment de la validation. Le bandeau d'attente
   disparaît et l'espace se débloque, sans message de félicitation. Le seul message explicite est l'e-mail
   « Votre agence est maintenant active — Kayloo ».
2. Aucun contrôle « forfait obligatoire » à la création d'un bien. Sans forfait, la création est acceptée tant que
   le quota de publications gratuites n'est pas épuisé, puis l'application refuse avec
   « Crédits insuffisants pour publier cette annonce : rechargez vos crédits Kayloo. »
3. Le bouton de la liste s'appelle « Nouveau bien », et le raccourci du tableau de bord « Nouvelle annonce ».
   Il n'y a pas de bouton « Ajouter un bien ».
4. Le formulaire n'a ni onglet de contact ni option de visibilité fine. L'étape 6 propose seulement quatre cases :
   Exposé, Géré, Masqué, Archivé, plus la disponibilité et les champs d'acquisition.
5. Aucun aperçu ni résumé avant publication. Le dernier écran du formulaire crée directement l'annonce.
6. Le bouton final s'appelle « Créer l'annonce », pas « Publier ».
7. Aucun message de succès après création. Le retour se fait sur la liste, avec la nouvelle ligne au statut
   « En attente de validation ».
8. La publication n'est pas immédiate. Une demande de publication est créée automatiquement, puis un administrateur
   doit cliquer « Valider et publier » dans `/admin/property-validate/<id>`. C'est cette validation qui rend le bien
   public et déclenche la notification « Annonce publiée ».
9. Les compteurs du tableau de bord affichent un nombre et un pourcentage, pas un ratio « 1/5 ». Aucun écran
   n'affiche « 0/5 » ou « 1/5 ».
10. Aucune notification de prospect. Le compte n'a reçu aucune demande, donc aucun e-mail ni notification de lead.
11. La page de résultats affiche l'emplacement publicitaire du site à l'état de réserve (« Emplacement
    Publicitaire »), faute de bannière réservée en base locale. C'est le comportement normal du site, pas un
    résidu de capture.

## 9. Messages de validation observés

- « L'intitulé est obligatoire. » quand le champ Label est vide.
- « La latitude est obligatoire. »
- « La longitude est obligatoire. » Les coordonnées sont obligatoires, la carte n'est qu'une aide.
- « Crédits insuffisants pour publier cette annonce : rechargez vos crédits Kayloo. » quand le quota gratuit est
  épuisé et le solde insuffisant (message du code, non déclenché dans cette capture).
- Sélection de pack sans moyen de paiement : le bouton reste inactif et affiche
  « Sélectionnez un pack et un moyen de paiement ». Avec un moyen choisi, il devient « Passer au paiement — Wave ».

## 10. Comment les crédits sont consommés

- Coût d'une publication d'annonce : 1 crédit (`publication_credit_cost_property`, réglable dans
  `/admin/credit-settings`).
- Une agence dispose d'abord d'un quota de publications gratuites (`free_credits_per_agency_kayloo`, mis à 1 ici).
  La première publication consomme ce quota, pas les crédits.
- Les boosts et les leads ne consomment pas de crédits. La mise en avant et les biens en vedette sont des quotas
  du pack, pas des dépenses de crédits.
- Dans la capture : 5 crédits après activation, 1 publication gratuite consommée, solde inchangé à 5 après
  publication.

## 11. Comment la limite d'annonces de Découverte est appliquée

La limite n'est pas décorative : `effective_kayloo_listing_limit()` renvoie `max_active_listings` du pack, et
`PropertyService.publish()` refuse la publication au-delà du nombre d'annonces actives de l'agence avec
`plan_limit_listings`. C'est un contrôle serveur, au moment de la publication, pas un compteur à l'écran.
Pour Découverte, la limite vaut 5.

## 12. Conventions des fichiers

- Chaque capture a un JSON du même nom : `{ "screen", "file", "url", "viewport", "device_scale_factor",
  "full_page", "scroll", "elements": [...] }`.
- Chaque élément listé porte `label`, `type` (input, button, checkbox, upload, card, link), `x`, `y`,
  `width`, `height` en pixels de l'image exportée, et `tap`.
- `tap: true` marque les éléments réellement actionnés dans le parcours.
- `scroll` donne la position de défilement au moment de la capture, pour les pages entières et les étapes longues.
- Les fichiers `.txt` reprennent le texte exact à l'écran pour les packs, les listes, les textes de système et
  l'e-mail.
- Les crops de `elements/` sont à 2x avec 14 px de marge ; leur JSON donne la position de l'élément dans l'image
  du crop.
- Les `.txt` couvrent les packs, les listes, les messages de système, les erreurs de validation, l'e-mail et les
  pages publiques. Les étapes de formulaire n'en ont pas : elles ne contiennent ni liste, ni texte légal, ni
  texte de système.

## 13. Non couvert

- Écran de prestataire de paiement : jamais ouvert, par interdiction explicite. L'activation de Découverte ne passe
  d'ailleurs par aucun prestataire.
- Second bien (villa à Saly) : non créé. La liste ne contient qu'une ligne, suffisante pour les deux vidéos.
- Message de limite atteinte (optionnel) : non capturé, il faudrait publier cinq annonces.
- Notification de prospect : aucune, faute de demande entrante sur ce compte de test.
