#! /usr/bin/env python3
# coding: utf-8

class Rapport():
    """Création d'un doc .md qui receuillera tous les resultats.
    Méthode : creation/ouverture"""
    def __init_(self):
        pass
    
    def creation(self):
        pass
    
class Analyse():
    """Element clef.
    Fait les requete sur wikidata et mets les resultats dans une instance de Rapport"""
    def __init__(self):
        pass
    
    def requete_wikidata(self):
        pass
    
    def liste_des_personnes(self):
        pass
    
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
    r2 = Analyse()
    print("action")