# Tout savoir des communard·e·s de Wikidata

Author : Gabriel-le / Silanoc

Date : mars 2022

## Description :
- ce programme interroge l'API Wikidata, via https://query.wikidata.org/sparql
- il est optimisé pour faire une requête autour des communard·e·s (personnes ayant participées à la Commune de Paris de 1871
- il peut être facilement modifié pour s'adapter à une autre requête
- il transforme le résultat de la requête en un dataframe (pandas)
- un certain nombre d'analyse est faite : ratio par genre, origine des personnes...
- un résultat textuel ou chiffré est fait, et si possible un graphique (seaborn).
- tous ces résultats sont écrit dans fichier .md (Markdown) en vue d'être converti en pdf
- on a donc un pipeline de la collecte de données à leur présentation en passant par leur traitement.
- que ce soit la requête, les analyses/graphique, écriture du rapport tout est recalculé à chaque fois, avec écriture par dessus !

## Architecture :
- deux classes objets.
- Rapport : c'est lui qui créé le fichier md et les premières lignes génériques.
- Analyse : créé une instance de rapport, fait les analyses et les écrits dans rapport

## Conversion 
- l'idée initiale, tout est construit autour de celle-ci, est d'écrire dans un fichier md et le transformer en pdf
    - avec visual code et les entensions, c'est facile à faire avec quelques cliques de souris
    - mon objectif est d'automatiser cela
    - en passant par un fichier html intermédiaire cela fonctionne presque. Le tableau n'est pas mis en forme et les images non affichées. Tout le reste est ok. Le pipeline fonctionne donc à des "détails près.
    - comme dans d'autres projets, j'avais fait des import dans un fichier html, j'avais envie de tester autre chose
- https://stackoverflow.com/questions/4135344/is-there-any-direct-way-to-generate-pdf-from-markdown-file-by-python?fbclid=IwAR3fH9J_1-lDj5P1X4j52uhuIS5_9w0CIgxmfmQuwbVlWZp6KPYfb6jyJys
    - https://pypi.org/project/Markdown/
    - https://github.com/xhtml2pdf/xhtml2pdf
 
## Ecriture inclusive :
- autaire : version neutre d'auteur/autrice
- al : pronom neutre non-binaire 3e personne du singulier
- communard·e·s : se lit à voix haute communardes et communards (ordre alphabétique)
