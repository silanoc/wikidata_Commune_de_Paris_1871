#! /usr/bin/env python3
# coding: utf-8

#--------------------- Les imports----------------------------------------------------------------------------------------
import sys
import os
#-------
import pandas as pd
#-------
import matplotlib.pyplot as plt
import seaborn as sns
# ----- pour conversion md -> pdf
#import md2pdf
#import markdown2pdf3
#from markdown import markdown
#import pdfkit
# Pour faire les requete via l'API de wikidata
from SPARQLWrapper import SPARQLWrapper, JSON

#-------------------- Requêter wikidata ---------------------------------------------------------------------------------
"""Comme le projet se fait à partir de wikidata, il nous faut deux variables
- url pour faire les requeste sur wikidata
- la requete en elle même, en sparl faite sur https://query.wikidata.org/
-- on peut metre une autre reqûete à la place, il faudra juste que les entêtes soient concordants 
--- comme wikidata propose des ente standardisé, il suffit de ne pas les changer """

endpoint_url = "https://query.wikidata.org/sparql"

query = """SELECT ?communard ?communardLabel ?pr_nom ?pr_nomLabel ?sexe_ou_genre ?sexe_ou_genreLabel ?date_de_naissance ?lieu_de_naissance ?lieu_de_naissanceLabel WHERE {
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
  ?communard wdt:P106 wd:Q1780490.
  OPTIONAL { ?communard wdt:P21 ?sexe_ou_genre. }
  OPTIONAL { ?communard wdt:P569 ?date_de_naissance. }
  OPTIONAL { ?communard wdt:P19 ?lieu_de_naissance. }
}"""

#------------------- Les classes objets ------------------------------------------------------------------------------------
class Rapport():
    """Création d'un doc .md qui receuillera tous les resultats.
    Méthode : creation/ouverture"""
    def __init__(self):
        self.creation()
        titre = "# Tout savoir des communard·e·s de Wikidata"
        intro = """Présentation à partir des éléments de Wikidata à propos des personnes qui ont fait la Commune de Paris 1871. \n
Fait par Gabriel-le avec les éléments connues dans wikidata le 9 mars 2022."""
        methodologie = """## Méthodologie \n
Wikidata est une base de données libre, liée à Wikipédia. Son remplissage est fait de façon collaborative. \n
Ce document est fait à partir des éléments s'y trouvants le 9 mars 2022. \n
Sont pris en compte toutes les personne dont le champs 'occupation' (P21) comprends la valeur 'communard' (Q1780490)'."""
        self.fichier.write(titre + "\n")
        self.fichier.write(intro + "\n")
        self.fichier.write(methodologie + "\n")

    def creation(self):
        # Création du dossier qui contiendra le rappor et tout se qui en dépend
        try:
            os.mkdir('rapport')
        except:
            pass
        # Création du fichier en lui même. En écriture, écrit par dessus s'il existe
        try:
            self.titre_rapport = "Tout_savoir_des_communard_e_s_de_wikidata.md"
            self.chemin_titre = "rapport/" + self.titre_rapport
            self.fichier = open(self.chemin_titre, "w")
        except:
            pass


class Analyse():
    """C'est l'élement clef du programme.
    Fait une requete sur wikidata et mets les resultats dans une instance de Rapport.
    Pour cela :
    - on utilse une requete dont la formulation est proposé par wikidata. C'est requete_wikidata
    - avec pandas on transforme ce résultat en pandas pour en faire des traitements d'analyse."""

    def __init__(self,endpoint_url, query):
        """à l'initialisation, la requete est exécuté via une méthode 
        et retourné dans le dataframe qui servira de référence"""
        self.endpoint_url = endpoint_url
        self.query = query
        self.df_tout_le_monde = self.requete_wikidata()
        self.nb_de_personne = self.df_tout_le_monde.shape[0]
        self.rapport = Rapport()

    def requete_wikidata(self):
        """exécuter la requet et mettre le résultat dans un dataframe"""
        # requête
        user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
        sparql = SPARQLWrapper(self.endpoint_url, agent=user_agent)
        sparql.setQuery(self.query)
        sparql.setReturnFormat(JSON)
        # transformation en dataframe
        results = sparql.query().convert()
        df_results = pd.json_normalize(results["results"]["bindings"])
        # renvoie
        return df_results

    def a_propos_du_df(self):
        """pour avoir des infos sur le df"""
        print("shape")
        print(self.df_tout_le_monde.shape)
        print("colonnes")
        print(self.df_tout_le_monde.columns)
        print("info")
        print(self.df_tout_le_monde.info())

    def liste_des_personnes(self):
        """Faire la liste de toutes les personnes concernées.
        mettre dans une texte
        exporter dans le document rapport"""
        # pour être sur qu'il n'y a pas de doublons, utilisation d'un set
        set_personne = self.df_tout_le_monde['communardLabel.value']
        # dans un string
        txt_qui = ""
        for personne in set_personne:
            txt_qui = txt_qui + personne + ", "
        # pour retirer le dernie ", "
        txt_qui = txt_qui[:-2]
        # affichage de contrôle
        # print(txt_qui)
        # mettre dans le rapport
        titre = "## Liste des personnes étudiées" 
        contexte = "Simple liste de toutes les personnes avec leur appellation d'usage dans wikidata."
        self.rapport.fichier.write(titre + "\n")
        self.rapport.fichier.write(contexte + "\n" + "\n")
        self.rapport.fichier.write(txt_qui+ "\n")

    def genre(self):
        """Compte le nombre de personne par genre et en fait un camembert"""
        #-------- compte
        # Compte le nombre de personne par genre
        compte_genre = self.df_tout_le_monde['sexe_ou_genreLabel.value'].value_counts()
        # Attribuer les valeurs pour masculin, féminin, autre/non attribués
        compte_masculin = compte_genre[0]
        compte_feminin = compte_genre[1]
        compte_autre = int(self.nb_de_personne) - int(compte_masculin) - int(compte_feminin)
        #-------- Graphique
        # convertie la serie en df et renome les colonnes
        df_compte_genre = compte_genre.to_frame()
        df_compte_genre = df_compte_genre.rename(columns = {'':'genre'})
        df_compte_genre = df_compte_genre.rename(columns = {'sexe_ou_genreLabel.value':'nombre'})
        print(df_compte_genre)
        # graph en lui même
        colors = sns.color_palette('deep')[0:4:3]
        labels = ["masculin", "féminin"]
        plt.pie(data = df_compte_genre, x = df_compte_genre['nombre'], labels = labels, colors = colors, autopct='%.0f%%')
        nom_graphique = "camembert_genre.png"
        chemin_graphique = "rapport/" + nom_graphique
        plt.savefig(chemin_graphique)
        # plt.show()
        plt.close()
        #-------- Dans le rapport
        titre = ("## Répartition par genre")
        contexte = ("""Dans wikidata, on peut remplir le 'sexe ou genre' (P21) pour les personnes. Certaines personnes peuvent ne pas avoir ce champs renseigné.
                    Voyons comment se répartissent selon leur genre les communard·e·s ayant une fiche dans wikidata.""")
        nombre = (f"Sur {self.nb_de_personne}, il y a {compte_feminin} femmes, {compte_masculin} hommes, et {compte_autre} personne dont le genre n'est pas renseigné ou autre")
        df = df_compte_genre
        self.rapport.fichier.write(titre + "\n")
        self.rapport.fichier.write(contexte + "\n")
        self.rapport.fichier.write(nombre+ "\n")
        self.rapport.fichier.write(f"![camembert par genre]({nom_graphique})"+ "\n")


    def prenom(self):
        pass

    def occupation(self):
        pass
        

    def converti_en_pdf(self):
        pass
                
    def pipeline(self):
        self.requete_wikidata()
        self.liste_des_personnes()
        self.genre()
        self.prenom()
        self.occupation()
        self.converti_en_pdf()

if __name__ == "__main__":
    #r = Rapport()
    r2 = Analyse(endpoint_url, query)
    #print(r2.df_tout_le_monde)
    r2.liste_des_personnes()
    r2.genre()
    r2.converti_en_pdf()
    print("action")