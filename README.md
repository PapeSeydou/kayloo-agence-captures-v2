# KAYLOO, captures agence, vidéos 1 et 2

Capture de l'espace agence de test (« Agence Horizon Immobilier ») sur l'environnement local : fin de la
validation de compte, activation du pack Découverte, création et publication d'un bien.

- 48 captures 2880 × 1620 (viewport 1440 × 810, device scale factor 2), plus une capture mobile 780 × 1688
- Un JSON de positions par capture, et un `.txt` du texte exact pour les packs, les listes, les messages, l'e-mail
  et les pages publiques
- 13 crops d'éléments (cartes de pack, états de boutons)
- Le deck de référence (slide 12) et les scripts de reproduction

## Contenu

| Dossier | Contenu |
|---|---|
| `screens/` | Captures numérotées, JSON de positions et textes |
| `elements/` | Crops 2x des cartes et des états de boutons, avec leur JSON |
| `assets/photos/` | Six photos de biens, 2400 × 1800, sans personne ni filigrane |
| `assets/deck/` | Slide 12 du deck V3.1, texte et image |
| `assets/seed/` | Scripts de base, seed du compte, harnais de capture, fichiers d'origine des correctifs |
| `voice/` | Les 15 prises de voix-off Kore (vidéos 1 et 2), en WAV 24 kHz mono, et `voice-report.md` |
| `flow.md` | Rapport complet : ordre des écrans, tableau deck/app, écarts, crédits, limites, reproductibilité |

## Voix-off

`voice/` contient les 15 prises de la voix Kore pour les deux vidéos : 6 pour la vidéo 1, dont les re-takes et
la scène de fin « écosystème », puis 8 pour la vidéo 2. Même modèle et mêmes réglages que les prises approuvées
(`google/gemini-3.8-flash-tts`, réponse PCM 24 kHz convertie en WAV mono 16 bits), même prompt de style dans
chaque appel. Chaque fichier porte 150 ms de silence au début et à la fin.

Trois prises ont été révisées le 2026-11-11 : « registre de commerce » à la place du RCCM dans la scène 07,
une scène de fin « écosystème KAYLOO », et la mention du mobile money dans la scène des packs. Les deux prises
qu'elles remplacent sont dans `voice/_replaced/`.

`voice-report.md` liste les durées, le nombre d'essais par prise, les contrôles de prononciation faits à
l'ASR et ce qui n'a pas pu être vérifié.

## À lire avant d'utiliser les captures

1. Les packs de l'application ont été alignés sur la slide 12 du deck (4 packs, dont Premium, avec les prix et
   quotas du deck). Modification faite en base uniquement.
2. Trois écarts ne se corrigent pas en données et restent visibles : badge « Populaire » sur Premium au lieu d'une
   couronne sur Business, libellé « Leads correspondant à vos annonces » au lieu de « Leads liés à vos annonces »,
   prix écrits « X FCFA TTC » au lieu de « X F ».
3. La publication n'est pas immédiate dans l'application : une demande est créée, puis un administrateur valide.
   Les captures montrent les deux étapes.
4. L'environnement local a tourné sur SQLite, faute de Docker disponible, avec stockage local et e-mail rendu depuis
   le template. Aucun e-mail n'a été envoyé.
5. Deux correctifs locaux ont été nécessaires (portabilité SQLite des listes déroulantes, activation d'un pack à
   0 FCFA sans prestataire de paiement). Ils ont été annulés et ne doivent pas partir en production. Les fichiers
   d'origine sont dans `assets/seed/patches/`.

Le détail, les messages de validation exacts et le tableau deck/app sont dans [flow.md](flow.md).
