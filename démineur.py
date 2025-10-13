""" Jeu démineur créé le 03/11/2021
    Prérequis: Bibliothèques, POO, graphe, listes, dictionnaires, récursivité,
        gestion des évènements, interface graphique Tkinter
"""

import random as rd
from tkinter import * # Importation de la bibliothèque  Tkinter
from PIL import Image, ImageTk
from tkinter import font as tkfont

MARGE = 5 # Epaisseur de la marge du plateau

class Case():
    """ Case du plateau
    """
    def __init__(self):
        self.cases_voisines = [] # Listes de cases contiguës
        self.mine = False # La case est-elle minée?
        self.visite = False # La case a-t-elle été visitée?
        self.marque = False # La case est-elle marquée comme bombe suspecte?
        self.mines_voisines = 0 # Combien de mines sur les cases voisines

class Plateau():
    """ Plateau de jeu du démineur constitué de Xmax colonnes et Ymax lignes.
    """
    def __init__(self, Xmax = None, Ymax = None, prolifération=30):
        self.tk = Tk()
        self.Xmax = Xmax
        if Xmax == None or Xmax < 5:
            self.Xmax = 5
        self.Ymax = Ymax
        if Ymax == None or Ymax < 5:
            self.Ymax = 5
        self.zoom, self.WIDTH, self.HEIGHT = self.dimensions_plateau()
        self.can = Canvas(self.tk, width=self.WIDTH+2*MARGE, height=self.HEIGHT+2*MARGE, bg='white')
        self.prolifération = prolifération # Pourcentage de cases minées
        self.fin_partie = False
        self.cases = self.construire_cases() # Construction du tableau des cases du plateau
        self.relier_cases_voisines() # Construction des listes de cases voisines
        self.remplir_mines() # Place aléatoirement les mines
        self.calculer_voisinage() # Calcule le nombre de mines sue les cases voisines
        self.images = self.construire_banque_images() # Importation de la banque d'images dans un dictionnaire

    def dimensions_plateau(self):
        WIDTH = self.tk.winfo_screenwidth() * 2 // 3
        HEIGHT = self.tk.winfo_screenheight() *2 // 3
        Xzoom = WIDTH // self.Xmax # Maximum de pixels par case en abscisses
        Yzoom = HEIGHT // self.Ymax # Maximum de pixels par case en ordonnées
        zoom = min(Xzoom, Yzoom)
        return zoom, zoom*self.Xmax, zoom*self.Ymax

    def construire_cases(self):
        cases = []
        for y in range(self.Ymax):
            ligne = []
            for x in range(self.Xmax):
                c = Case()
                ligne.append(c)
            cases.append(ligne)
        return cases

    def remplir_mines(self):
        """ Place les mines sur le plateau
        """
        nb_mines = self.Xmax * self.Ymax * self.prolifération // 100
        while nb_mines > 0:
            x = rd.randint(0, self.Xmax-1)
            y = rd.randint(0, self.Ymax-1)
            if self.cases[y][x].mine == False:
                self.cases[y][x].mine = True
                nb_mines -= 1

    def couple_valide(self, x, y):
        """ Renvoie True si (x,y) désigne une case du plateau
        """
        return 0<=x<self.Xmax and 0<=y<self.Ymax

    def relier_cases_voisines(self):
        """ Créer la listes des cases voisines pour cahque case
        """
        for y in range(self.Ymax):
            for x in range(self.Xmax):
                case = self.cases[y][x]
                for dy in range(y-1,y+2):
                    for dx in range(x-1,x+2):
                        if self.couple_valide(dx,dy):
                            case.cases_voisines.append(self.cases[dy][dx])

    def calculer_voisinage(self):
        """ Renseigne l'attribut mines_voisines de chaque case: Calcul le nombre de mines adjacentes
        """
        for y in range(self.Ymax):
            for x in range(self.Xmax):
                case = self.cases[y][x]
                for voisin in case.cases_voisines:
                    case.mines_voisines += int(voisin.mine)

    def tester_victoire(self):
        """ Renvoie True si seules les cases minées ne sont pas visitées
        """
        for y in range(self.Ymax):
            for x in range(self.Xmax):
                case = self.cases[y][x]
                if case.visite == False and case.mine == False:
                    return False
        self.fin_partie = True
        return True

    def jouer(self, case):
        """ Ouvre la case cible. cible est un str de la forme x,y
        """
        case.visite = True
        if case.mine: # Si la case est minée: Fin de partie
            self.découvre_plateau()
            self.fin_partie = True
            self.images["panneau_fin_partie"] = self.images["panneau_fin"]
            return False
        if case.mines_voisines == 0: # Si la case n'est pas minée: Explore les cases voisines
            for voisin in case.cases_voisines:
                if voisin.visite == False:
                    self.jouer(voisin)
        if self.tester_victoire(): # La partie est finie si les cases non-minées sont visitées
            self.découvre_plateau()
            self.images["panneau_fin_partie"] = self.images["panneau_ok"]
        return True

    def découvre_plateau(self):
        """ Découvre toutes les cases du plateau en fin de partie
        """
        for y in range(self.Ymax):
                for x in range(self.Xmax):
                    self.cases[y][x].visite = True
        self.afficher()

    def selectionner(self, event):
        """ Gestion du clic gauche: Détecte la case cliquée
            Visite la case cliquée
        """
        Xpix = event.x - MARGE
        Ypix = event.y - MARGE
        x = Xpix//self.zoom
        y = Ypix//self.zoom
        if self.couple_valide(x, y):
            case = self.cases[y][x]
            if case.visite == False:
                self.jouer(case)
        self.afficher()

    def marquer(self, event):
        """ Gestion du clic droit: Inverse l'état de la marque de la case
            Pose ou supprime le drapeau sur la case si elle n'est pas visitée
        """
        Xpix = event.x - MARGE
        Ypix = event.y - MARGE
        x = Xpix//self.zoom
        y = Ypix//self.zoom
        if self.couple_valide(x, y):
            case = self.cases[y][x]
            case.marque = not(case.marque) # Inversion de l'état de la marque
            self.afficher() # Mise à jour de l'affichage

    def afficher(self):
        """ Affiche le plateau dans une fenêtre Tkinter
        """
        SIZE = self.zoom//2
        normal_font = tkfont.Font(family="Helvetica", size=SIZE, weight="bold")
        for y in range(self.Ymax):
            for x in range(self.Xmax):
                case = self.cases[y][x]
                if case.visite: # Affiche les cases visitées: Neutres avec ou sans indice, minées
                    img = self.images["case_ouverte"]
                    if case.mine:
                        img = self.images["case_bombe"]
                    self.can.create_image(x*self.zoom+MARGE, y*self.zoom+MARGE, anchor = NW, image = img)
                    indice = str(self.cases[y][x].mines_voisines)
                    if indice != '0' and not(case.mine):
                        self.can.create_text((x+0.5)*self.zoom+MARGE,(y+0.5)*self.zoom+MARGE,anchor=CENTER,text = indice, fill='black', font=normal_font)
                else: # Affiche les cases non-visitées: Marquées ou non
                    img = self.images["case_grise"]
                    if case.marque:
                        img = self.images["case_marque"]
                    self.can.create_image(x*self.zoom+MARGE, y*self.zoom+MARGE, anchor = NW, image = img)
        if self.fin_partie:
            x = self.WIDTH //2 + MARGE
            y = self.HEIGHT //2 + MARGE
            self.can.create_image(x, y, anchor = CENTER, image = self.images["panneau_fin_partie"])

    def construire_banque_images(self):
        banque = {}
        zoom = self.zoom
        case_grise = Image.open("images/case_grise.png")
        case_grise = case_grise.resize((zoom, zoom))
        case_grise_tk = ImageTk.PhotoImage(case_grise)
        case_bombe = Image.open("images/case_bombe.png")
        case_bombe = case_bombe.resize((zoom, zoom))
        case_bombe_tk = ImageTk.PhotoImage(case_bombe)
        case_ouverte = Image.open("images/case_ouverte.png")
        case_ouverte = case_ouverte.resize((zoom, zoom))
        case_ouverte_tk = ImageTk.PhotoImage(case_ouverte)
        case_marque = Image.open("images/case_marque.png")
        case_marque = case_marque.resize((zoom, zoom))
        case_marque_tk = ImageTk.PhotoImage(case_marque)
        panneau_fin = Image.open("images/panneau_game_over.png")
        panneau_fin_tk = ImageTk.PhotoImage(panneau_fin)
        rapport_largeur = panneau_fin_tk.width() / self.WIDTH
        rapport_hauteur = panneau_fin_tk.height() / self.HEIGHT
        rapport = max(rapport_hauteur, rapport_largeur)
        largeur = int(panneau_fin_tk.width() // rapport)
        hauteur = int(panneau_fin_tk.height() // rapport)
        panneau_fin = panneau_fin.resize((largeur, hauteur))
        panneau_fin_tk = ImageTk.PhotoImage(panneau_fin)
        panneau_ok = Image.open("images/panneau_bravo.png")
        panneau_ok_tk = ImageTk.PhotoImage(panneau_ok)
        largeur = int(panneau_ok_tk.width() // rapport)
        hauteur = int(panneau_ok_tk.height() // rapport)
        panneau_ok = panneau_ok.resize((largeur, hauteur))
        panneau_ok_tk = ImageTk.PhotoImage(panneau_ok)
        banque["case_grise"] = case_grise_tk
        banque["case_bombe"] = case_bombe_tk
        banque["case_ouverte"] = case_ouverte_tk
        banque["case_marque"] = case_marque_tk
        banque["panneau_fin"] = panneau_fin_tk
        banque["panneau_ok"] = panneau_ok_tk
        banque["panneau_fin_partie"] = None
        return banque

if __name__ == "__main__":
    # Insyanciation du plateau de jeu
    p = Plateau(20, 10, 5)
    p.can.pack()
    # Surveillance des clics sur le canevas
    p.tk.bind("<Button-1>", p.selectionner)
    p.tk.bind("<Button-3>", p.marquer)
    p.afficher()
    p.tk.mainloop()