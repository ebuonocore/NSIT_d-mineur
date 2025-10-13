""" Jeu démineur créé le 03/11/2021
    Prérequis: Bibliothèques, POO, graphe, listes, dictionnaires, récursivité.
"""

import random as rd

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
        self.Xmax = Xmax
        if Xmax == None or Xmax < 5:
            self.Xmax = 5
        self.Ymax = Ymax
        if Ymax == None or Ymax < 5:
            self.Ymax = 5
        self.prolifération = prolifération # Pourcentage de cases minées
        self.fin_partie = False
        # Lance les méthodes d'initialisation du plateau
        self.cases = self.construire_cases() # Construction du tableau des cases du plateau
        self.relier_cases_voisines() # Construction des listes de cases voisines
        self.remplir_mines() # Place aléatoirement les mines
        self.calculer_voisinage() # Calcule le nombre de mines sue les cases voisines

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
        """ Ouvre la case cible.
        """
        message =""
        case.visite = True
        if case.mine: # Si la case est minée: Fin de partie
            self.découvre_plateau()
            self.fin_partie = True
            message = "GAME OVER"
            return False
        if case.mines_voisines == 0: # Si la case n'est pas minée: Explore les cases voisines
            for voisin in case.cases_voisines:
                if voisin.visite == False:
                    self.jouer(voisin)
        if self.tester_victoire(): # La partie est finie si les cases non-minées sont visitées
            self.découvre_plateau()
            self.fin_partie = True
            message = "VICTOIRE"
        if message != "":
            print(message)
        return True

    def découvre_plateau(self):
        """ Découvre toutes les cases du plateau en fin de partie
        """
        for y in range(self.Ymax):
                for x in range(self.Xmax):
                    self.cases[y][x].visite = True
        self.dessiner_ascii()

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
        self.dessiner_ascii()

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
            self.dessiner_ascii() # Mise à jour de l'affichage

    def dessiner_ascii(self):
        """ Affiche le plateau en ASCII
        """
        print()
        print("   ",end="")
        for x in range(self.Xmax):
           print(x%10,end=" ")
        print()
        print("   ",end="")
        for x in range(self.Xmax):
           print(".",end=" ")
        print()
        for y in range(self.Ymax):
            print(y%10,end=". ")
            for x in range(self.Xmax):
                case = self.cases[y][x]
                if case.visite: # Affiche les cases visitées: Neutres avec ou sans indice, minées
                    caractère= 'O'
                    indice = str(self.cases[y][x].mines_voisines)
                    if indice != '0' and not(case.mine):
                        caractère = str(indice)
                    if case.mine:
                        caractère = "M"#chr(0x1F4A3)
                else: # Affiche les cases non-visitées: Marquées ou non
                    caractère= 'X'
                    if case.marque:
                        caractère= '+'
                print(caractère,end=" ")
            print()

if __name__ == "__main__":
    # Instanciation du plateau de jeu
    p = Plateau(20, 10, 10)
    print("Donnez les coordonnées de la case à jouer sous la forme x,y.")
    #p.dessiner_ascii()
    while p.fin_partie == False:
        jeu = input(">")
        if ',' in jeu:
            x_car, y_car = jeu.split(',')
            x = int(x_car)
            y = int(y_car)
            case = p.cases[y][x]
            p.jouer(case)
            p.dessiner_ascii()