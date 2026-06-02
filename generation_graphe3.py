import matplotlib
matplotlib.use('TkAgg')

import matplotlib.pyplot as plt
import networkx as nx
import matplotlib.patches as mpatches
import sys
import random
import math

from neo4j import GraphDatabase
from collections import deque
from collections import defaultdict
import community as community_louvain

G=nx.Graph()

def initialiser_graphe():
    with driver.session() as session:
            session.run("MATCH (p) DETACH DELETE(p)")

def saisir_taille():
    while True:
        try:
            taille_graphe = input("Entrer la taille du graphe G à étudier : ")
            if int(taille_graphe) <= 4:
                print("La taille doit etre superieur à 3")
                continue
            return taille_graphe
        except ValueError:
            print("Veuillez inserer un entier")

def creation_des_sommets(taille_graphe , G) :
    etudiants = []
    with driver.session() as session:
        for i in range(int(taille_graphe)):
            name = f"Etudiant_{i}"
            etudiant = {
            "name": name 
            }
            G.add_node(etudiant["name"])
            etudiants.append(etudiant)
            session.run("""
                MERGE (p:Etudiant { name:$name })
                """ , name=etudiant["name"] )
    return etudiants

def creation_des_arretes(etudiants , taille_graphe , G): 
    p = math.log(int(taille_graphe)) / int((taille_graphe))
    with driver.session() as session:
        for i in range(int(taille_graphe)):
            for j in range(i+1, int(taille_graphe)):
                nom1 = etudiants[i]["name"]
                nom2 = etudiants[j]["name"]
                r = random.random()
                if ( r < p ):
                    G.add_edge(nom1 , nom2)
                    session.run("""
                        MATCH (n:Etudiant {name: $name1}) , (p:Etudiant {name:$name2})
                        MERGE (n)-[:Liaison]->(p)
                        MERGE (n)<-[:Liaison]-(p)
                        """,name1=etudiants[i]["name"],name2=etudiants[j]["name"])

def debut_parcour_graphe (etudiants , taille_graphe ):
    numero_random = random.randint(0 , int(taille_graphe) - 1)
    compteur = 0
    for eleve in etudiants:
        if compteur == numero_random:
            return eleve["name"]
        compteur += 1
        
sommet_visite = []
def coloration_graphe ( etudiants , taille_graphe , G ):
    eleve_random = debut_parcour_graphe ( etudiants , taille_graphe )
    file_attente = deque([eleve_random])
    sommet_visite.append(eleve_random)
    couleur = defaultdict(list)
    
    while len(file_attente) != 0:
        sommet = file_attente.popleft()
        voisins = list(G.neighbors(sommet))
        
        with driver.session() as session:
            voisin_meme_couleur = []
            nombre = 0
            while True:
                etiquette = f"Equipe_{nombre}"
                voisin_meme_couleur = []
                result = session.run("""
                    MATCH (n {name:$sommet}) -[]-> (p)
                    WHERE p.etiquette = $etiquette
                    RETURN p.name AS name
                    """,sommet=sommet, etiquette=etiquette)
                voisin_meme_couleur = [n['name'] for n in result]
                if len(voisin_meme_couleur) != 0:
                    nombre+=1
                    continue
                break
                
            session.run(f"""
                MATCH (n {{name:$sommet}})
                SET n.etiquette = $etiquette
                SET n:{etiquette}
                REMOVE n:Etudiant
                """,sommet=sommet,etiquette=etiquette)
            couleur[etiquette].append(sommet)
            
                
        for voisin in voisins:
            if voisin not in sommet_visite:
                file_attente.append(voisin)
                sommet_visite.append(voisin)
    return couleur

def detection_clique(etudiants, taille_graphe, G):
    couleur = coloration_graphe(etudiants, taille_graphe, G)
    nb_etiquettes = len(couleur)

    clique = []
    epuises = defaultdict(list)
    iteration = 0

    while iteration <= nb_etiquettes:
        etiquette = f"Equipe_{iteration}"

        candidat_trouve = None
        for etudiant in couleur[etiquette]:
            if etudiant in epuises[etiquette]:
                continue
            if etudiant in clique:
                continue
            if iteration == 0:
                candidat_trouve = etudiant
                break
            if all(G.has_edge(etudiant, s) for s in clique):
                candidat_trouve = etudiant
                break

        if candidat_trouve is not None:
            clique.append(candidat_trouve)
            iteration += 1

        else:
            if len(clique) >= 3:
                print(f"Un clique est trouvé : {clique}")
            if len(clique) == 0:
                break

            sommet_retire = clique.pop()
            etiquette_precedente = f"Equipe_{iteration - 1}"
            epuises[etiquette_precedente].append(sommet_retire)

            epuises[etiquette] = []

            iteration -= 1

        if len(epuises["Equipe_0"]) >= len(couleur["Equipe_0"]):
            break

    return clique
        
driver = GraphDatabase.driver("bolt://localhost:7687",auth=("neo4j", "mardymex0137"))
initialiser_graphe()
n = saisir_taille()
while True:
    etudiants = creation_des_sommets(n,G)
    creation_des_arretes(etudiants , n , G)
    if (nx.is_connected(G)):
        break
detection_clique ( etudiants , n , G )

