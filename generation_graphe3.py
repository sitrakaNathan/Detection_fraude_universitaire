import matplotlib
matplotlib.use('TkAgg')

import matplotlib.pyplot as plt
import networkx as nx
import matplotlib.patches as mpatches
import sys
import random
import math

from neo4j import GraphDatabase
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


FACULTE = ["Science" , "EGS" , "Lettre" , "Droit" , "Medecine"]
NIVEAU_NOTE = ["Mauvais" , "Moyenne" , "Bon" , "Tres_bon"]

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
    p = math.log(taille_graphe) / (taille_graphe)
    with driver.session() as session:
        for i in range(int(taille_graphe)):
            for j in range(i+1, int(taille_graphe)):
                nom1 = etudiants[i]["name"]
                nom2 = etudiants[j]["name"]
                r = random.random()
                print(f"pour {nom1} et {nom2} = {r}")
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
            print(f"{numero_random} vaut {eleve}")
            return eleve["name"]
        compteur += 1
        
clique = []
def coloration_graphe ( etudiants , taille_graphe , G ):
    eleve_random = debut_parcour_graphe ( etudiants , taille_graphe )
    clique.append(eleve_random)
    voisin = list(G.neighbors(eleve_random))
    for eleve in voisin:
        if all(G.has_edge(eleve , etudiant) for etudiant in clique):
            clique.append(eleve)
    print(clique)
        
            


driver = GraphDatabase.driver("bolt://localhost:7687",auth=("neo4j", "mardymex0137"))
initialiser_graphe()
n = saisir_taille()
while True:
    etudiants = creation_des_sommets(n,G)
    creation_des_arretes(etudiants , n , G)
    if (nx.is_connected(G)):
        break
recherche_clique ( etudiants , n , G )

"""
liste_degree = calcule_degree()
liste_intermediaire = calcule_intermediarite(G)
for id_etudiant, score in sorted(
    liste_intermediaire.items(),
    key=lambda x: x[1],
    reverse=True
):
    print(f"Etudiant {id_etudiant} : {score}")
partition = calcule_communautes_louvain(G)

afficher_communautes(partition)
"""


"""
On va utiliser le parcours en profondeur pour verifier les sous cliques dans G' . on verifie si le voisin du sommet mise en random est relie au sommet pple ( ce qui est deja evident ) , ensuite on marque le chemin , on verifie ensuite un autre chemin menant vers d autre sommet voisin du voisin de sommet pple , s il n est pas relie avec les autre sommet deja parcouru (y compris celle du sommet pple , on ne peut prendre ce sommet ) . Enfin on assemble tout les cliques obtenues
"""
