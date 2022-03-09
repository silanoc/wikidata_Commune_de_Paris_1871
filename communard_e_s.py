#! /usr/bin/env python3
# coding: utf-8

#--------------------- Les imports----------------------------------------------------------------------------------------
import sys
import pandas as pd
# Pour faire les requete via l'API de wikidata
from SPARQLWrapper import SPARQLWrapper, JSON

#-------------------- Requêter wikidata ---------------------------------------------------------------------------------
"""Comme le projet se fait à partir de wikidata, il nous faut deux variables
- url pour faire les requeste sur wikidata
- la requete en elle même, en sparl faite sur https://query.wikidata.org/
-- on peut metre une autre reqûete à la place, il faudra juste que les ente soit concordant 
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
    def __init_(self):
        pass
    
    def creation(self):
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
        print(txt_qui)
    
    def genre(self):
        pass
    
    def prenom(self):
        pass
    
    def occupation(self):
        pass
    
    def pipeline(self):
        self.requete_wikidata()
        self.liste_des_personnes()
        self.genre()
        self.prenom()
        self.occupation()
    
if __name__ == "__main__":
    r = Rapport()
    r2 = Analyse(endpoint_url, query)
    #print(r2.df_tout_le_monde)
    r2.liste_des_personnes()
    print("action")