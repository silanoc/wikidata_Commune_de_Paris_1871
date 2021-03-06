#! /usr/bin/env python3
# coding: utf-8
"""Author : Gabriel-le / Silanoc
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

Convertion
- https://stackoverflow.com/questions/4135344/is-there-any-direct-way-to-generate-pdf-from-markdown-file-by-python?fbclid=IwAR3fH9J_1-lDj5P1X4j52uhuIS5_9w0CIgxmfmQuwbVlWZp6KPYfb6jyJys
-- https://pypi.org/project/Markdown/
-- https://github.com/xhtml2pdf/xhtml2pdf
"""

#--------------------- Les imports----------------------------------------------------------------------------------------
from posixpath import split
import sys
import os
import datetime
#-------
import pandas as pd
#-------
import matplotlib.pyplot as plt
import seaborn as sns
#----- pour conversion md -> html
import markdown
#----- pour conversion html -> pdf
from xhtml2pdf import pisa  
#------Pour faire les requete via l'API de wikidata
from SPARQLWrapper import SPARQLWrapper, JSON

#-------------------- Requêter wikidata ---------------------------------------------------------------------------------
"""Comme le projet se fait à partir l'API wikidata, il nous faut deux variables
- endpoint_url pour faire les requeste sur wikidata
- la requete en elle même, en sparl faite sur https://query.wikidata.org/
-- on peut metre une autre requête à la place, il faudra juste que les entêtes soient concordants 
--- comme wikidata propose des ente standardisé, il suffit de ne pas les changer """

endpoint_url = "https://query.wikidata.org/sparql"

query = """SELECT ?communard ?communardLabel ?sexe_ou_genreLabel ?date_de_naissance ?lieu_de_naissanceLabel ?conjointLabel (GROUP_CONCAT(DISTINCT ?occupationLabel; SEPARATOR = ", ") AS ?LeursoccupationsLabel) (GROUP_CONCAT(DISTINCT ?prenomLabel; SEPARATOR = ", ") AS ?prenoms) ?date_de_mort ?circonstances_de_la_mortLabel ?cause_de_la_mortLabel WHERE {
  SERVICE wikibase:label {
    bd:serviceParam wikibase:language "fr".
    ?communard rdfs:label ?communardLabel.
    ?sexe_ou_genre rdfs:label ?sexe_ou_genreLabel.
    ?occupation rdfs:label ?occupationLabel.
    ?lieu_de_naissance rdfs:label ?lieu_de_naissanceLabel.
    ?conjoint rdfs:label ?conjointLabel.
    ?prenom rdfs:label ?prenomLabel.
    ?circonstances_de_la_mort rdfs:label ?circonstances_de_la_mortLabel.
    ?cause_de_la_mort rdfs:label ?cause_de_la_mortLabel.
  }
  ?communard wdt:P106 wd:Q1780490.
  OPTIONAL { ?communard wdt:P21 ?sexe_ou_genre. }
  OPTIONAL { ?communard wdt:P569 ?date_de_naissance. }
  OPTIONAL { ?communard wdt:P19 ?lieu_de_naissance. }
  OPTIONAL { ?communard wdt:P106 ?occupation. }
  OPTIONAL { ?communard wdt:P26 ?conjoint. }
  OPTIONAL { ?communard wdt:P735 ?prenom. }
  OPTIONAL { ?communard wdt:P570 ?date_de_mort. }
  OPTIONAL { ?communard wdt:P1196 ?circonstances_de_la_mort. }
  OPTIONAL { ?communard wdt:P509 ?cause_de_la_mort. }
  
}
GROUP BY ?communard ?communardLabel ?sexe_ou_genreLabel ?date_de_naissance ?lieu_de_naissanceLabel ?conjointLabel ?date_de_mort ?circonstances_de_la_mortLabel ?cause_de_la_mortLabel"""

#------------------- Les classes objets ------------------------------------------------------------------------------------
class Rapport():
    """Création d'un fichier .md qui receuillera tous les resultats.
    Le place dans un dossier rapport, sous-dossier d'où est lancé le programme.
    Méthode : 
    - creation : créer, ouvre et fait le début du fichier md
    - creation_html : transforme le fichier md dans un autre fichier en html
    - creation_pdf : fransforme le fichier html en pdf"""
    
    def __init__(self):
        """création du fichier en utilisant la méthode creation
        Ajoute un titre, des métdonnées textuelles et une intro au format md"""
        #--- création ---
        self.creation()
        #--- variables textes ---
        self.date = datetime.datetime.now()
        titre = "# Tout savoir des communard·e·s de Wikidata"
        meta_autaire = f"- autaire : Gabriel-le"
        meta_date = f"""- date de création du script : 9 mars 2022, \n- dernière version : 11 mars 2022 \n
- rapport généré le : {self.date.day}/{self.date.month}/{self.date.year} à {self.date.hour}h{self.date.minute} """
        intro = """Présentation à partir des éléments de Wikidata à propos des personnes qui ont fait la Commune de Paris 1871. \n
Fait par Gabriel-le avec les éléments connues dans wikidata le 9 mars 2022."""
        methodologie = f"""## Méthodologie \n
Wikidata est une base de données libre, liée à Wikipédia. Son remplissage est fait de façon collaborative. \n
Ce document est fait à partir des éléments s'y trouvants le {self.date.day}/{self.date.month}/{self.date.year} à {self.date.hour}h{self.date.minute}. \n
Sont pris en compte toutes les personne dont le champs 'occupation' (P21) comprends la valeur 'communard' (Q1780490)'."""
        #--- écriture sur le fichier
        self.ecriture(titre, intro, meta_autaire, meta_date, methodologie)

    def creation(self):
        """méthode appelé par __init__
        création du dossier et du fichier dedans
        try/except au cas où"""
        # Création du dossier qui contiendra le rapport et tout ce qui en dépend
        try:
            os.mkdir('rapport')
            print("dossier 'rapport' créé")
        except:
            print("dossier non créé")
        # Création du fichier en lui même. En écriture, écrit par dessus s'il existe
        try:
            self.titre_rapport = "Tout_savoir_des_communard_e_s_de_wikidata.md"
            self.chemin_titre = "rapport/" + self.titre_rapport
            self.fichier = open(self.chemin_titre, "w")
            print("fichier 'Tout_savoir_des_communard_e_s_de_wikidata.md' créé")            
        except:
            print("fichier non créé")
            
    def creation_html(self):
        """ écrit ligne à ligne le fichier md dans un autre fichier html"""
        #--- fermeture (de lécriture) du fichier md
        self.fichier.close()
        #--- creation du fichier html
        try:
            self.titre_rapport = "Tout_savoir_des_communard_e_s_de_wikidata.html"
            self.chemin_titre = "rapport/" + self.titre_rapport
            print("fichier 'Tout_savoir_des_communard_e_s_de_wikidata.html' créé")            
        except:
            print("fichier html non créé")
        #--- replissage html
        fichier_md = open("rapport/Tout_savoir_des_communard_e_s_de_wikidata.md", "r")
        fichier_html = open("rapport/Tout_savoir_des_communard_e_s_de_wikidata.html", "w")
        tout_md = "".join(fichier_md.readlines())
        html = markdown.markdown(tout_md)
        fichier_html.write(html)
        fichier_html.close()
        fichier_md.close()
        
    def creation_pdf(self):
        """Creation du fichier pdf à partir du html"""
        fichier_html = open("rapport/Tout_savoir_des_communard_e_s_de_wikidata.html", "r")
        source_html = "".join(fichier_html.readlines())
        fichier_html.close()
        fichier_pdf = "rapport/Tout_savoir_des_communard_e_s_de_wikidata.pdf"
        result_file = open(fichier_pdf, "w+b")
        # convert HTML to PDF
        pisa_status = pisa.CreatePDF(
            source_html,                # the HTML to convert
            dest=result_file)           # file handle to recieve result
        # close output file
        result_file.close()
        
    def ecriture(self, *args):
        """ Ecrire dans le fichier md
        - dans Rapport (lui meme), mettre les arguments de l'intro du fichier
        - méthode à utiliser dans les celles de Analyse
        pour écrire dans le fichier md les arguments du type titre, contexte, nombre, graphique, comentaire..."""
        for arg in range(len(args)):
            self.fichier.write(args[arg] + "\n")

class Analyse():
    """C'est l'élement clef du programme.
    Fait une requete sur wikidata et mets les resultats dans une instance de Rapport.
    Pour cela :
    - on utilise une requete dont la formulation est proposé par wikidata. C'est requete_wikidata.
    - avec pandas on transforme ce résultat en pandas pour en faire des traitements d'analyse.
    - avec seaborn on fait les graphique
    """

    def __init__(self,endpoint_url, query):
        """à l'initialisation, la requete est exécutée via une méthode 
        et le résultat retourné dans le dataframe qui servira de référence"""
        #--- variable de la requete et le dataframe de référence
        self.endpoint_url = endpoint_url
        self.query = query
        self.df_tout_le_monde = self.requete_wikidata()
        #--- pour savoir combien al y a de communard·e·s
        self.nb_de_personne = self.df_tout_le_monde.shape[0]
        #--- création de l'instance de Rapport, dans laquelle on écrit tout
        self.rapport = Rapport()

    def requete_wikidata(self):
        """exécuter la requete et mettre le résultat dans un dataframe"""
        #--- requête
        user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
        sparql = SPARQLWrapper(self.endpoint_url, agent=user_agent)
        sparql.setQuery(self.query)
        sparql.setReturnFormat(JSON)
        #--- transformation en dataframe
        results = sparql.query().convert()
        df_results = pd.json_normalize(results["results"]["bindings"])
        #--- renvoie
        return df_results

    def a_propos_du_df(self):
        """pour avoir des infos sur le df"""
        print("shape")
        print(self.df_tout_le_monde.shape)
        # très important pour avoir les initulés des colonnes !
        print("colonnes")
        print(self.df_tout_le_monde.columns)
        print("info")
        print(self.df_tout_le_monde.info())

    def liste_des_personnes(self):
        """Faire la liste de toutes les personnes concernées.
        mettre dans une texte
        exporter dans le document rapport"""
        #--- pour être sur qu'il n'y a pas de doublons, utilisation d'un set
        #--- C'est plus simple à lire avec un tri par ordre alphabetique (sort_values)
        set_personne = self.df_tout_le_monde['communardLabel.value'].sort_values()
        #--- mettre dans un srting 
        txt_qui = ""
        for personne in set_personne:
            txt_qui = txt_qui + personne + ", "
        #--- pour retirer le dernie ", "
        txt_qui = txt_qui[:-2]
        #--- affichage de contrôle
        #print(txt_qui)
        #--- mettre dans le rapport
        titre = "## Liste des personnes étudiées" 
        contexte = f"Simple liste des {len(set_personne)} personnes avec leur appellation d'usage dans wikidata. Par ordre alphabétique de l'item, le prénom le plus souvent."
        self.rapport.ecriture(titre, contexte, txt_qui)

    def genre(self):
        """Compte le nombre de personne par genre et en fait un camembert"""
        #----- compte
        #--- Compte le nombre de personne par genre
        compte_genre = self.df_tout_le_monde['sexe_ou_genreLabel.value'].value_counts()
        #--- Attribuer les valeurs pour masculin, féminin, autre/non attribués
        compte_masculin = compte_genre[0]
        compte_feminin = compte_genre[1]
        compte_autre = int(self.nb_de_personne) - int(compte_masculin) - int(compte_feminin)
        #----- Graphique
        #--- convertie la serie en df et renomme les colonnes
        df_compte_genre = compte_genre.to_frame()
        df_compte_genre = df_compte_genre.rename(columns = {'' : 'genre'})
        df_compte_genre = df_compte_genre.rename(columns = {'sexe_ou_genreLabel.value' : 'nombre'})
        #print(df_compte_genre)
        #--- graph en lui même
        colors = sns.color_palette('deep')[0:4:3]
        labels = ["masculin", "féminin"]
        plt.pie(data = df_compte_genre, x = df_compte_genre['nombre'], labels = labels, colors = colors, autopct='%.0f%%')
        nom_graphique = "camembert_genre.png"
        chemin_graphique = "rapport/" + nom_graphique
        plt.savefig(chemin_graphique)
        #plt.show()
        plt.close()
        #----- Dans le rapport
        #--- variable
        titre = ("## Répartition par genre")
        contexte = ("""Dans wikidata, on peut remplir le 'sexe ou genre' (P21) pour les personnes. Certaines personnes peuvent ne pas avoir ce champs renseigné.
                    Voyons comment se répartissent selon leur genre les communard·e·s ayant une fiche dans wikidata.""")
        nombre = (f"Sur {self.nb_de_personne}, il y a {compte_feminin} femmes, {compte_masculin} hommes, et {compte_autre} personne dont le genre n'est pas renseigné ou autre")
        #--- ecriture
        self.rapport.ecriture(titre,contexte,nombre, f"![camembert par genre]({nom_graphique})" )

    def ville_naissance(self):
        """ Compte le nombre de personne par lieu de naissance.
        Création d'un tableau au format md avec des |
        ou
        utilisation de to_markdown. Il est mieux pour le fichier md, mais pas mieux pour html"""
        #--- Compte le nombre de personne par lieu de naissance
        compte_ville = self.df_tout_le_monde['lieu_de_naissanceLabel.value'].value_counts()
        df_compte_ville = compte_ville.to_frame()
        df_compte_ville.reset_index(inplace = True)
        df_compte_ville.sort_values(by = ['lieu_de_naissanceLabel.value','index'], inplace=True, ascending=False)
        md_tableau_compte = df_compte_ville.to_markdown()
        #- Contrôle
        #print(df_compte_ville)
        #--- Création du tableau
        #- les 2 premières lignes
        #titre = """|Ville de naissance|Nombre de personne|\n|---|---|\n"""
        #md_tableau_compte = """|Ville de naissance|Nombre de personne|\n|---|---|\n"""
        #- boucles sur le df pour créer toutes les lignes
        #for i in range(len(df_compte_ville)):
        #    md_tableau_compte += f"|{df_compte_ville.iloc[i,0]}|{df_compte_ville.iloc[i,1]}|\n"
        #- Contrôle
        #print(md_tableau_compte)
        #---------Dans le rapport
        titre = ("## D'où viennent les communard·e·s")
        contexte = ("""Dans wikidata, on peut remplir le 'lieu_de_naissance' (P19) pour les personnes. Certaines personnes peuvent ne pas avoir ce champs renseigné. \n
le plus souvent il s'agit d'une ville, mais al peut y avoir un arrondissement, pays... \n
Comptons par lieux combien de communard·e·s (ayant une fiche dans wikidata) y sont né·e·s. \n Trie par nombre descoissant de personne et ordre inverse de l'alphabet \n""")
        espace =" \n "
        nombre = md_tableau_compte
        #--- écriture
        self.rapport.ecriture(titre, contexte, titre,  md_tableau_compte, espace, espace)    

    def annee_naissance(self):
        """Compte dans un dictionnaire le nombre de personne par années de naissance et en faire un graphique en barre"""
        #--- Compter el nombre de personne par année de naissance
        dico_date={}
        for i in range(len(self.df_tout_le_monde)):
            # chercher la date de naissance par ligne, et en prendre que les 4 premier caractère qui corresponde à l'année
            # mettre dans un dico le nombre d'occurence par année
            # try pour gérer les dates inconnues, non rempli ou au format étrange
            try :
                annee_naiss = self.df_tout_le_monde.loc[i,'date_de_naissance.value'][:4]
                #print(annee_naiss)
                if annee_naiss in dico_date:
                    dico_date[annee_naiss] += 1
                else:
                    dico_date[annee_naiss] = 1     
            except:
                pass
        #print(dico_date)
        # -- Transformer le dico en dataframe
        df_date_naissance = pd.DataFrame(list(dico_date.items()),columns=['année', 'nb'])
        df_date_naissance = df_date_naissance.sort_values(by='année')
        #print(df_date_naissance)
        # -- Graphique
        #plt.figure(figsize=(17,4))
        sns.catplot(x="année", y="nb", kind="bar", data=df_date_naissance)
        plt.xticks(rotation= 90)
        plt.tight_layout()
        nom_graphique = "barre_annee_naissance.png"
        chemin_graphique = "rapport/" + nom_graphique
        plt.savefig(chemin_graphique)
        #plt.show()
        plt.close()
        #-------- Dans le rapport
        titre = ("## Répartition par année de naissance")
        contexte = ("""Dans wikidata, on peut remplir la 'date de naissance' (P569) pour les personnes. Certaines personnes peuvent ne pas avoir ce champs renseigné.
                    Voyons comment se répartissent selon leur naissance, donc âge les communard·e·s ayant une fiche dans wikidata.""")
        #--- écriture
        self.rapport.ecriture(titre, contexte, f"![barres par années de naissance]({nom_graphique})")             

    def occupation(self):
        """ La requête est telle, que dans la colonne occupation une personne peut en avoir plusieurs.
Même structure que pour âge, mais tout le monde à au moins 1 occupation : communard, donc pas besoin de try
Par contre besoin d'aller chercher dans la liste des occupation le cas échéant"""
        #--- mettre dans un dico le nombre de personnes par occupation
        dico_occupation = {}
        for i in range(len(self.df_tout_le_monde)):
            occupS = self.df_tout_le_monde.loc[i,'LeursoccupationsLabel.value']
            lst_occup = occupS.split(", ")
            for j in lst_occup:
                if j in dico_occupation:
                        dico_occupation[j] += 1
                else:
                    dico_occupation[j] = 1 
        # -- comme tout le monde est communard, garde la valeur de controle dans une variable et supprime du dico
        nb_communard = dico_occupation['communard']
        del dico_occupation['communard']
        #print(dico_occupation)
        # -- Transformer le dico en dataframe
        df_occupation = pd.DataFrame(list(dico_occupation.items()), columns=['occupation', 'nb'])
        df_occupation = df_occupation.sort_values(by='occupation')
        # -- lisibilité : 2 df, un pour ceux d'un seul métier, à transformer en texte à afficher. L'autre pour le graphique.
        df_occupation_unique = df_occupation.loc[df_occupation['nb'] == 1]
        txt_occupation_unique = ""
        for i in range(df_occupation_unique.shape[0]):
            txt_occupation_unique = txt_occupation_unique + ", " + df_occupation_unique.iloc[i,0]
        txt_occupation_unique = txt_occupation_unique[2:]
        #print(txt_occupation_unique)
        df_occupation_multiple = df_occupation.loc[df_occupation['nb'] > 1]
        # -- Graphique
        sns.catplot(y = "occupation", x = "nb", kind = "bar", data = df_occupation_multiple)
        plt.xticks(rotation = 90)
        plt.tight_layout()
        nom_graphique = "barre_occupation.png"
        chemin_graphique = "rapport/" + nom_graphique
        plt.savefig(chemin_graphique)
        #plt.show()
        plt.close()
        #----- Rapport
        titre = "## Quelles étaient les occupations des communard·e·s ?" 
        contexte = ("""Dans wikidata, on peut remplir la propriété « occupation » (P106) pour les personnes. Cela correspond approximativement à une profession.
C'est aussi un élément remarquable de la personne. Ainsi le champ occupation peut inclure communard, c'est d'ailleurs par ce champ que l'on a fait l'extrait des personnes. \n
Voyons comment se répartissent selon leur occupation les communard·e·s ayant une fiche dans wikidata. \n
Pour faciliter la lecture, les occupations exercées par une seule personne sont dans une liste, celles par plusieurs personnes dans un graphique.""")
        #--- écriture
        self.rapport.ecriture(titre, contexte, txt_occupation_unique, f"![barres par occupation]({nom_graphique})") 
        
    def carte_cause_et_annee_mort(self):
        """Comme il y a peu de donnée, et beaucoup de jour  différent, on va remplacer date la date de déces précise par année-mois
        Les données causes et circonstances de la mort étant peur renseigner, on va travailler sur les deux champs.
        Il s'agit de faire les stats sur les causes/circonstances par année/mois, et en trouver le nombre de personne concernées  
        todo : c'est le numéro de colonne qui est rentrée, il risque de changer !!!      
        """
        #--- Changer les dates deces, colonne 16 
        for communard in range(self.df_tout_le_monde.shape[0]):
            date = self.df_tout_le_monde.iloc[communard,16] 
            date = str(date)[0:7]
            self.df_tout_le_monde.iloc[communard, 16] = date         
        #--- crosstab sur cause
        cross_cause = pd.crosstab(self.df_tout_le_monde["cause_de_la_mortLabel.value"], self.df_tout_le_monde["date_de_mort.value"])
        cross_cause_md = cross_cause.to_markdown()           
        #--- crosstab sur circonstance
        cross_circonstance = pd.crosstab(self.df_tout_le_monde["circonstances_de_la_mortLabel.value"], self.df_tout_le_monde["date_de_mort.value"])
        cross_circonstance_md = cross_circonstance.to_markdown()
        #--- graph cause
        sns.heatmap(cross_cause, cmap="BuPu") #cmap : gére la couleur
        plt.xticks(rotation = 90)
        plt.tight_layout()
        nom_graphique1 = "carte_cause_date_deces.png"
        chemin_graphique1 = "rapport/" + nom_graphique1
        plt.savefig(chemin_graphique1)
        #plt.show()
        plt.close()
        #--- graph circonstance
        sns.heatmap(cross_circonstance, cmap="BuPu")
        plt.xticks(rotation = 90)
        plt.tight_layout()
        nom_graphique2 = "carte_circonstance_date_deces.png"
        chemin_graphique2 = "rapport/" + nom_graphique2
        plt.savefig(chemin_graphique2)
        #plt.show()
        plt.close()
        #--- texte
        titre = "## Cause de décès dans le temps"
        contexte = """Dans wikidata les propiété cause de la mort et circonstances de la mort peuvent être renseigné. \n 
Le nombre de fiche correctement renseigné est faible, mais voyons par année-mois combien de personens sont maorte par cause/circonstance. \n
Les deux conceptes sont sufisament différents pour ne pas fair un seul graph, mais deux"""
        soustitre1 = "### Par Cause"
        soustitre2 = "### Par circonstance"
        #--- écriture
        self.rapport.ecriture(titre, contexte, 
                              soustitre1, cross_cause_md, f"![graph par cause et année de mort]({nom_graphique1})",
                              soustitre2, cross_circonstance_md, f"![graph par circonstance et année de mort]({nom_graphique2})",)
        
        
    def converti_en_pdf(self):
        self.rapport.creation_html()
        self.rapport.creation_pdf()
           
    def pipeline(self):
        try:
            self.requete_wikidata()
            print("requete : ok")
        except:
            print("requete : error")
        try:
            print("-----------------")        
            self.a_propos_du_df()
            print("-----------------")   
        except:
            print("à propos du df : error")
        try:
            self.liste_des_personnes()
            print("liste personnes : ok")
        except:
            print("liste personnes : error")
        try:
            self.genre()
            print("genre : ok")
        except:
            print("genre : error")
        try:
            self.annee_naissance()
            print("année naissance : ok")
        except:
            print("année naissance : error")
        try:
            self.ville_naissance()
            print("ville naissance : ok")
        except:
            print("ville naissance : error")
        try:
            self.occupation()
            print("occupation : ok")
        except:
            print("occupation : error")   
        try:
            self.carte_cause_et_annee_mort()
            print("cause_et_annee_mort : ok")
        except:
            print("cause_et_annee_mort : error")     
        try:
            self.converti_en_pdf()
            print("conversion ok")            
        except:
           print("conversion : error")
  
        
if __name__ == "__main__":
    print("début traitement")
    r2 = Analyse(endpoint_url, query)
    r2.pipeline()
    print("fin traitement")