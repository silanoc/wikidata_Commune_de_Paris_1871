# Tout savoir des communard·e·s de Wikidata

Author : Gabriel-le / Silanoc

Date : mars 2022

Description :
- ce programme interroge l'API Wikidata, via https://query.wikidata.org/sparql
- il est optimisé pour faire une requête autour des communard·e·s (personnes ayant participées à la Commune de Paris de 1871
- il peut être facilement modifié pour s'adapter à une autre requête
- il transforme le résultat de la requête en un dataframe (pandas)
- un certain nombre d'analyse est faite : ratio par genre, origine des personnes...
- un résultat textuel ou chiffré est fait, et si possible un graphique (seaborn).
- tous ces résultats sont écrit dans fichier .md (Markdown) en vue d'être converti en pdf
- on a donc un pipeline de la collecte de données à leur présentation en passant par leur traitement.
- que ce soit la requête, les analyses/graphique, écriture du rapport tout est recalculé à chaque fois, avec écriture par dessus !

Architecture :
- deux classes objets.
- Rapport : c'est lui qui créé le fichier md et les premières lignes génériques.
- Analyse : créé une instance de rapport, fait les analyses et les écrits dans rapport

Ecriture inclusive :
- autaire : version neutre d'auteur/autrice
- al : pronom neutre non-binaire 3e personne du singulier
- communard·e·s : se lit à voix haute communardes et communards (ordre alphabétique)
