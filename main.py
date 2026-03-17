import json
import math
import random
import sys

import pygame

pygame.init()

# Variable de base: taille et FPS
info = pygame.display.Info()
WIDTH = info.current_w
HEIGHT = info.current_h
FPS = 60

# Variable de couleur
SURFACE = (20, 23, 32)
CARTE_FD = (26, 30, 42)
CARTE_EL = (16, 17, 22)
BORDURE = (50, 55, 72)
BLANC = (220, 225, 240)
GRIS = (100, 108, 130)
ACCENT = (255, 200, 60)
VERT = (70, 200, 130)
ROUGE = (210, 65, 75)
ROUGE_FD = (80, 24, 32)
BTN_Q_COL = (32, 38, 58)

# Text pygame
TITRE = pygame.font.Font(None, 68)
GRAND = pygame.font.Font(None, 48)
MOY = pygame.font.Font(None, 32)
PETIT = pygame.font.Font(None, 26)
MINI = pygame.font.Font(None, 20)
CARTE = pygame.font.Font(None, 17)

# Couleur des cartes
COULEURS_CARTES = [
    (55, 90, 180),
    (170, 55, 95),
    (55, 150, 110),
    (150, 95, 35),
    (95, 55, 170),
    (35, 130, 170),
    (170, 130, 35),
    (110, 55, 55),
    (55, 110, 55),
    (150, 75, 150),
    (75, 150, 150),
    (130, 110, 55),
]

# Les âges par tranches
AGES = [
    (0, 4, "0-4 ans"),
    (5, 9, "5-9 ans"),
    (10, 14, "10-14 ans"),
    (15, 19, "15-19 ans"),
    (20, 24, "20-24 ans"),
    (25, 29, "25-29 ans"),
    (30, 34, "30-34 ans"),
    (35, 39, "35-39 ans"),
    (40, 44, "40-44 ans"),
    (45, 49, "45-49 ans"),
    (50, 54, "50-54 ans"),
    (55, 59, "55-59 ans"),
    (60, 64, "60-64 ans"),
    (65, 69, "65-69 ans"),
    (70, 74, "70-74 ans"),
    (75, 79, "75-79 ans"),
    (80, 84, "80-84 ans"),
    (85, 89, "85-89 ans"),
    (90, 120, "90+ ans"),
]

# Les état du jeux
ETAT_ERREUR = "erreur"
ETAT_MENU = "menu"
ETAT_JEU = "jeu"
ETAT_CHOIX = "choix"
ETAT_GAGNE = "gagne"
ETAT_PERDU = "perdu"

# Taille et position
CARTE_WIDTH = 148
CARTE_HEIGHT = 194
COLS = 9
MARGE_X = 16
MARGE_Y = 14

ZONE_WIDTH = 380
ZONE_X = WIDTH - ZONE_WIDTH - 20
ZONE_Y = 238
ZONE_HEIGHT = HEIGHT - ZONE_Y - 40
BTN_HEIGHT = 36
BTN_GAP = 6
BTN_COL = 2


# Lenny
# Afficher le texte facilement
def afficher_texte(screen, texte, police, couleur, x, y, ancre="topleft"):
    img = police.render(texte, True, couleur)
    r = img.get_rect()
    setattr(r, ancre, (x, y))  # oui c'est plus simple comme ça (Antoine)
    screen.blit(img, r)


# Lenny
# Dessiner la zone pour les boutons des questions a droite
def dessiner_panneau(screen, rect, fond=SURFACE, bordure=BORDURE, rayon=10):
    pygame.draw.rect(screen, fond, rect, border_radius=rayon)
    pygame.draw.rect(screen, bordure, rect, 1, border_radius=rayon)


# Lenny et Tymeo (Antoine)
# Utilitaire pour couper le texte
def couper_texte(texte, police, max_l):
    words = texte.split()
    lignes = []
    current = []
    for m in words:
        current.append(m)

        # check ligne trop longue
        if police.size(" ".join(current))[0] > max_l:
            if len(current) > 1:
                current.pop()
                lignes.append(" ".join(current))
                current = [m]
            else:
                lignes.append(m)
                current = []
    if current:
        lignes.append(" ".join(current))
    return lignes[:2]  # retourne uniquement les 2 permières lignes


# Tymeo (aidé voir README.md)
# Couleur des profiles (trop galère de mettre des images)
def couleur_avatar(nom):
    return COULEURS_CARTES[abs(hash(nom)) % len(COULEURS_CARTES)]


# Lenny et Antoine
# Créer un dégradé (pas plus explicite possible)
def creer_degrade(l, h, haut, bas):
    s = pygame.Surface((l, h))
    for y in range(h):
        t = y / h
        c = tuple(int(haut[i] + (bas[i] - haut[i]) * t) for i in range(3))
        pygame.draw.line(s, c, (0, y), (l, y))
    return s


# Antoine
# Charge les données du json avec support des errors
def load_data():
    try:
        with open("./base.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"Error loading data: {e}")
        return None


# Antoine
# Récuperer la valeur des liens
def link_value(personne, type_lien):
    liens_list = personne.get("liens", personne.get("links", []))
    for lien in liens_list:
        t = lien.get("type") or lien.get("type_lien")
        if t == type_lien:
            return lien.get("result") or lien.get("valeur")
    return None


# Antoine
# Le type des questions (age, proximité ect...)
def questions_types(personnes):
    vus = set()
    result = []
    for p in personnes:
        liens_list = p.get("liens", p.get("links", []))
        for lien in liens_list:
            t = lien.get("type") or lien.get("type_lien")
            if t and t not in vus:
                vus.add(t)
                result.append(t)
    return result


# Lenny et Antoine
# Tranche d'age pour la question sur l'age
def age_en_tranche(age):
    try:
        a = int(age)
    except (ValueError, TypeError):
        return str(age)

    for lo, hi, label in AGES:
        if lo <= a <= hi:
            return label
    return str(age)


# Lenny et Antoine
# Trier les tranche d'age
def trier_tranche(label):
    try:
        num_str = label.replace("90+", "90").split("-")[0].split()[0]
        return int(num_str)
    except Exception:
        return 999  # Nombre maximum (au cas où)


# Tymeo
# (!) Permet de montrer une liste des valeurs sur l'age
def valeurs_disponibles(personnes, qt):
    if qt == "age":
        vals = set()
        for p in personnes:
            val = link_value(p, qt)
            if val is not None:
                vals.add(age_en_tranche(val))
        return sorted(vals, key=trier_tranche)

    vals = []
    vus = set()
    for p in personnes:
        v = link_value(p, qt)
        if v is not None:
            str_v = str(v)
            if str_v not in vus:
                vus.add(str_v)
                vals.append(str_v)
    return sorted(vals)


# Lenny et Antoine
# Créer les boutons (pas plus compliqué que ça)
def creer_bouton(x, y, l, h, label, couleur, police=None):
    if police is None:
        police = PETIT
    return {
        "rect": pygame.Rect(x, y, l, h),
        "label": label,
        "couleur": couleur,
        "police": police,
        "survol": False,
    }


# Lenny
# Mettre à jour le système de survolage pour les boutons (comme le html)
def maj_bouton(bouton, souris):
    bouton["survol"] = bouton["rect"].collidepoint(souris)


# Lenny et Antoine
# Dessiner les boutons avec les couleurs le texte ect...
def dessiner_bouton(screen, bouton):
    if bouton["survol"]:
        c = tuple(min(v + 25, 255) for v in bouton["couleur"])
    else:
        c = bouton["couleur"]

    pygame.draw.rect(screen, c, bouton["rect"], border_radius=8)
    pygame.draw.rect(screen, BORDURE, bouton["rect"], 1, border_radius=8)

    afficher_texte(
        screen,
        bouton["label"],
        bouton["police"],
        BLANC,
        bouton["rect"].centerx,
        bouton["rect"].centery,
        "center",
    )


# Lenny
# Simple et efficace regarde la souris et le bouton
def bouton_clique(bouton, pos):
    return bouton["rect"].collidepoint(pos)


# Lenny et Antoine
# Créer une carte avec les infos de base
def creer_carte(personne, x, y):
    return {
        "personne": personne,
        "x": x,
        "y": y,
        "elimine": False,
        "survol": False,
        "flip": -1.0,
    }


# Lenny et Antoine
# nombre de carte n'on éliminé restante
def nb_restants(cartes):
    count = 0
    for c in cartes:
        if not c["elimine"]:
            count += 1
    return count


# Lenny et Antoine
# Eliminer une carte (juste une animation)
def eliminer_carte(carte):
    if not carte["elimine"]:
        carte["elimine"] = True
        carte["flip"] = 0.0


# Lenny et Antoine
# Logique pour les cartes cliqué
def carte_cliquee(carte, pos):
    in_x = carte["x"] <= pos[0] <= carte["x"] + CARTE_WIDTH
    in_y = carte["y"] <= pos[1] <= carte["y"] + CARTE_HEIGHT
    return not carte["elimine"] and in_x and in_y


# Tymeo
# Mise à jour des cartes
def maj_carte(carte, souris):
    if carte["flip"] >= 0:
        carte["flip"] += 0.07
        if carte["flip"] >= 1.0:
            carte["flip"] = -1.0

    in_x = carte["x"] <= souris[0] <= carte["x"] + CARTE_WIDTH
    in_y = carte["y"] <= souris[1] <= carte["y"] + CARTE_HEIGHT
    carte["survol"] = not carte["elimine"] and in_x and in_y


# Antoine et Tymeo
# Dessiner les carte (simple)
def dessiner_carte(screen, carte):
    x = carte["x"]
    y = carte["y"]

    if carte["flip"] >= 0:
        scale = abs(math.cos(carte["flip"] * math.pi))
        fl = max(4, int(CARTE_WIDTH * scale))
        rx = x + (CARTE_WIDTH - fl) // 2
        r = pygame.Rect(rx, y, fl, CARTE_HEIGHT)

        if carte["flip"] < 0.5:
            col = CARTE_FD
            bc = BORDURE
        else:
            col = CARTE_EL
            bc = ROUGE_FD

        pygame.draw.rect(screen, col, r, border_radius=8)
        pygame.draw.rect(screen, bc, r, 1, border_radius=8)

        if carte["flip"] >= 0.5:
            m = 10
            pygame.draw.line(
                screen, ROUGE, (rx + m, y + m), (rx + fl - m, y + CARTE_HEIGHT - m), 2
            )
            pygame.draw.line(
                screen, ROUGE, (rx + fl - m, y + m), (rx + m, y + CARTE_HEIGHT - m), 2
            )
        return

    if carte["elimine"]:
        r = pygame.Rect(x, y, CARTE_WIDTH, CARTE_HEIGHT)
        pygame.draw.rect(screen, CARTE_EL, r, border_radius=8)
        pygame.draw.rect(screen, ROUGE_FD, r, 1, border_radius=8)

        m = 14
        pygame.draw.line(
            screen,
            (60, 22, 28),
            (x + m, y + m),
            (x + CARTE_WIDTH - m, y + CARTE_HEIGHT - m),
            2,
        )
        pygame.draw.line(
            screen,
            (60, 22, 28),
            (x + CARTE_WIDTH - m, y + m),
            (x + m, y + CARTE_HEIGHT - m),
            2,
        )
        return

    r = pygame.Rect(x, y, CARTE_WIDTH, CARTE_HEIGHT)

    if carte["survol"]:
        bc = ACCENT
        ep = 2
    else:
        bc = BORDURE
        ep = 1

    pygame.draw.rect(screen, CARTE_FD, r, border_radius=8)
    pygame.draw.rect(screen, bc, r, ep, border_radius=8)

    ph = int(CARTE_HEIGHT * 0.56)
    ar = pygame.Rect(x + 6, y + 6, CARTE_WIDTH - 12, ph)
    pygame.draw.rect(
        screen, couleur_avatar(carte["personne"]["name"]), ar, border_radius=6
    )

    name_parts = carte["personne"]["name"].split()
    initiales = "".join(m[0].upper() for m in name_parts[:2])
    afficher_texte(
        screen,
        initiales,
        pygame.font.Font(None, 32),
        BLANC,
        x + CARTE_WIDTH // 2,
        y + 6 + ph // 2,
        "center",
    )

    ny = y + 6 + ph + 9
    lignes_nom = couper_texte(carte["personne"]["name"], CARTE, CARTE_WIDTH - 12)
    for i in range(len(lignes_nom)):
        afficher_texte(
            screen,
            lignes_nom[i],
            CARTE,
            BLANC,
            x + CARTE_WIDTH // 2,
            ny + i * 14,
            "center",
        )


# Tymeo
# Lance une nouvelle partie
def lancer_partie(etat):
    personnes = etat["personnes"]

    nb_personnages = min(36, len(personnes))
    choisis = random.sample(personnes, nb_personnages)

    etat["mystere"] = random.choice(choisis)
    etat["nb_questions"] = 0
    etat["dernier_res"] = None
    etat["qt_selec"] = None
    etat["boutons_val"] = []

    sx = 36
    sy = 130
    etat["cartes"] = []
    for i in range(len(choisis)):
        p = choisis[i]
        col_idx = i % COLS
        row_idx = i // COLS
        cx = sx + col_idx * (CARTE_WIDTH + MARGE_X)
        cy = sy + row_idx * (CARTE_HEIGHT + MARGE_Y)
        etat["cartes"].append(creer_carte(p, cx, cy))

    bl = (ZONE_WIDTH - 16 - (BTN_COL - 1) * BTN_GAP) // BTN_COL
    etat["boutons_qt"] = []
    question_types = questions_types(personnes)
    for i in range(len(question_types)):
        qt = question_types[i]
        rangee = i // BTN_COL
        col = i % BTN_COL
        bx = ZONE_X + 8 + col * (bl + BTN_GAP)
        by = ZONE_Y + rangee * (BTN_HEIGHT + BTN_GAP)
        b = creer_bouton(
            bx, by, bl, BTN_HEIGHT, qt.replace("_", " ").capitalize(), BTN_Q_COL
        )
        b["qt"] = qt
        etat["boutons_qt"].append(b)

    etat["etat"] = ETAT_JEU


# Tymeo
# Créer les boutons des valeur possible pour les question (genre age, couleur ect...)
def construire_boutons_valeurs(etat, qt):
    vals = valeurs_disponibles(etat["personnes"], qt)

    bx0 = WIDTH // 2 - 300
    by0 = 315
    bl = 192
    bh = 42
    ecart = 10
    par_col = 3

    etat["boutons_val"] = []
    for i in range(len(vals)):
        v = vals[i]
        rangee = i // par_col
        col = i % par_col
        b = creer_bouton(
            bx0 + col * (bl + ecart),
            by0 + rangee * (bh + ecart),
            bl,
            bh,
            str(v),
            (48, 58, 105),
        )
        b["valeur"] = v
        etat["boutons_val"].append(b)


# Tymeo
# Permet de poser une question et eliminer des cartes
def poser_question(etat, qt, valeur):
    val_mystere = link_value(etat["mystere"], qt)

    if qt == "age":
        cible = age_en_tranche(val_mystere)
        elimines = 0
        for c in etat["cartes"]:
            if not c["elimine"]:
                age_carte = age_en_tranche(link_value(c["personne"], qt))
                if age_carte != cible:
                    eliminer_carte(c)
                    elimines += 1
        reponse = cible
    else:
        elimines = 0
        for c in etat["cartes"]:
            if not c["elimine"]:
                val_carte = str(link_value(c["personne"], qt) or "")
                if val_carte != str(val_mystere or ""):
                    eliminer_carte(c)
                    elimines += 1
        reponse = str(val_mystere)

    etat["nb_questions"] += 1
    etat["dernier_res"] = (qt.replace("_", " ").capitalize(), reponse, elimines)
    etat["etat"] = ETAT_JEU
    verifier_fin(etat)


# Tymeo
# Accuse un personnage
def accuser(etat, carte):
    if carte["personne"]["name"] == etat["mystere"]["name"]:
        etat["etat"] = ETAT_GAGNE
    else:
        eliminer_carte(carte)
        etat["nb_questions"] += 1
        etat["etat"] = ETAT_PERDU


# Lenny
# Verifie si la partie est fini
def verifier_fin(etat):
    restants = []
    for c in etat["cartes"]:
        if not c["elimine"]:
            restants.append(c)

    if len(restants) == 1:
        if restants[0]["personne"]["name"] == etat["mystere"]["name"]:
            etat["etat"] = ETAT_GAGNE
    elif len(restants) == 0:
        etat["etat"] = ETAT_PERDU


# Tymeo
# Detect si on clique dans la zone des bouton de question
def clic_dans_zone(etat, pos):
    zone = pygame.Rect(ZONE_X, ZONE_Y, ZONE_WIDTH, ZONE_HEIGHT)
    if not zone.collidepoint(pos):
        return None

    for b in etat["boutons_qt"]:
        if b["rect"].collidepoint(pos):
            return b
    return None


# Lenny
# Affiche un message d'erreur si le json est pas trouvé
def dessiner_erreur(screen):
    afficher_texte(
        screen,
        "Erreure : base.json introuvable",
        GRAND,
        ROUGE,
        WIDTH // 2,
        HEIGHT // 2 - 44,
        "center",
    )
    afficher_texte(
        screen,
        "Placez base.json dans le meme dossier que ce script.",
        PETIT,
        GRIS,
        WIDTH // 2,
        HEIGHT // 2 + 4,
        "center",
    )
    afficher_texte(
        screen,
        "Appuyez sur une touche pour quiter.",
        MINI,
        GRIS,
        WIDTH // 2,
        HEIGHT // 2 + 40,
        "center",
    )


# Tymeo
# Dessine le menu principal du jeu
def dessiner_menu(screen, etat):
    afficher_texte(
        screen, "QUI EST L'IMPLIQUE ?", TITRE, ACCENT, WIDTH // 2, 168, "center"
    )
    afficher_texte(screen, "Edition Familiale", MOY, GRIS, WIDTH // 2, 236, "center")

    pygame.draw.line(
        screen, BORDURE, (WIDTH // 2 - 280, 264), (WIDTH // 2 + 280, 264), 1
    )

    dessiner_panneau(screen, pygame.Rect(WIDTH // 2 - 255, 288, 510, 95))
    afficher_texte(
        screen,
        "Posez des question pour eliminer les suspect.",
        PETIT,
        BLANC,
        WIDTH // 2,
        316,
        "center",
    )
    afficher_texte(
        screen,
        "Designez le personnage mystère avant de manquer d'indices.",
        PETIT,
        GRIS,
        WIDTH // 2,
        348,
        "center",
    )

    dessiner_bouton(screen, etat["btn_jouer"])

    afficher_texte(
        screen,
        f"{len(etat['personnes'])} personnages charger dans la base",
        MINI,
        GRIS,
        WIDTH // 2,
        488,
        "center",
    )


# Antoine
# Dessine les boutons dans une zone
def dessiner_zone_questions(screen, etat, souris):
    zone = pygame.Rect(ZONE_X, ZONE_Y + 8, ZONE_WIDTH, ZONE_HEIGHT)
    afficher_texte(screen, "Poser une question :", PETIT, GRIS, ZONE_X + 8, ZONE_Y - 22)
    pygame.draw.rect(screen, (14, 17, 30), zone, border_radius=6)

    for b in etat["boutons_qt"]:
        maj_bouton(b, souris)
        dessiner_bouton(screen, b)

    pygame.draw.rect(screen, BORDURE, zone, 1, border_radius=6)


# Antoine
# Dessiner le jeux tout simplemennt
def dessiner_jeu(screen, etat, souris):
    afficher_texte(
        screen, "QUI EST L'IMPLIQUE ?", MOY, ACCENT, WIDTH // 2 - 80, 36, "center"
    )

    info_r = pygame.Rect(22, 12, 225, 54)
    dessiner_panneau(screen, info_r)
    afficher_texte(
        screen,
        f"Restants : {nb_restants(etat['cartes'])} / {len(etat['cartes'])}",
        PETIT,
        BLANC,
        info_r.centerx,
        info_r.centery - 8,
        "center",
    )
    afficher_texte(
        screen,
        f"Questions : {etat['nb_questions']}",
        MINI,
        GRIS,
        info_r.centerx,
        info_r.centery + 12,
        "center",
    )

    for c in etat["cartes"]:
        dessiner_carte(screen, c)

    dessiner_panneau(screen, pygame.Rect(ZONE_X - 14, 68, ZONE_WIDTH + 28, HEIGHT - 96))

    mh = pygame.Rect(ZONE_X, 80, ZONE_WIDTH, 58)
    dessiner_panneau(screen, mh, fond=(28, 36, 62), bordure=ACCENT)
    afficher_texte(
        screen,
        "PERSONNAGE MYSTERE",
        MINI,
        ACCENT,
        mh.centerx,
        mh.centery - 10,
        "center",
    )
    afficher_texte(
        screen,
        "Posez des questions ou designez-le.",
        MINI,
        GRIS,
        mh.centerx,
        mh.centery + 10,
        "center",
    )

    if etat["dernier_res"]:
        lbl = etat["dernier_res"][0]
        rep = etat["dernier_res"][1]
        elim = etat["dernier_res"][2]
        lr = pygame.Rect(ZONE_X, 148, ZONE_WIDTH, 58)
        dessiner_panneau(screen, lr, fond=(20, 44, 30), bordure=VERT)
        afficher_texte(
            screen, f"{lbl} : {rep}", MINI, VERT, lr.centerx, lr.centery - 10, "center"
        )
        afficher_texte(
            screen,
            f"{elim} elimine(s)",
            MINI,
            GRIS,
            lr.centerx,
            lr.centery + 10,
            "center",
        )

    dessiner_zone_questions(screen, etat, souris)
    afficher_texte(
        screen,
        "Cliquer sur un personnage pour l'acuser.",
        MINI,
        GRIS,
        ZONE_X + 8,
        ZONE_Y + ZONE_HEIGHT + 8,
    )


# Antoine et Tymeo
# Dessiner la popup pour choisir la valeur de la questions
def dessiner_overlay_valeurs(screen, etat):
    dim = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    dim.fill((0, 0, 0, 165))
    screen.blit(dim, (0, 0))

    boite = pygame.Rect(WIDTH // 2 - 365, 150, 730, 515)
    label = etat["qt_selec"].replace("_", " ").upper()

    if etat["qt_selec"] == "age":
        sous = "Tranche d'age (5 ans) :"
    else:
        sous = "Quelle valeure ?"

    dessiner_panneau(screen, boite, fond=(16, 20, 38), bordure=ACCENT)
    afficher_texte(
        screen, f"Question : {label}", MOY, ACCENT, WIDTH // 2, 190, "center"
    )
    afficher_texte(screen, sous, PETIT, GRIS, WIDTH // 2, 228, "center")
    pygame.draw.line(
        screen, BORDURE, (WIDTH // 2 - 260, 248), (WIDTH // 2 + 260, 248), 1
    )

    for b in etat["boutons_val"]:
        dessiner_bouton(screen, b)

    afficher_texte(
        screen, "[ ESC ] Annuler", MINI, GRIS, WIDTH // 2, boite.bottom - 20, "center"
    )


# Antoine, Tymeo et Lenny
# Dessiner l'écran quand on perd (rejouer ou menu principale)
def dessiner_fin(screen, etat, gagne):
    for c in etat["cartes"]:
        dessiner_carte(screen, c)

    dim = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    dim.fill((0, 0, 0, 155))
    screen.blit(dim, (0, 0))

    boite = pygame.Rect(WIDTH // 2 - 310, 160, 620, 485)
    border_col = VERT if gagne else ROUGE
    dessiner_panneau(screen, boite, fond=(16, 20, 38), bordure=border_col)

    if gagne:
        afficher_texte(screen, "TROUVE !", TITRE, ACCENT, WIDTH // 2, 232, "center")
        afficher_texte(
            screen,
            "Vous avez identifié le personnage mystére.",
            PETIT,
            BLANC,
            WIDTH // 2,
            292,
            "center",
        )
    else:
        afficher_texte(screen, "PERDU !", TITRE, ROUGE, WIDTH // 2, 232, "center")
        afficher_texte(
            screen,
            "C'étais pas le bon personnage.",
            PETIT,
            BLANC,
            WIDTH // 2,
            292,
            "center",
        )

    rv = pygame.Rect(WIDTH // 2 - 220, 322, 440, 118)
    dessiner_panneau(screen, rv, fond=(24, 30, 52), bordure=ACCENT)
    afficher_texte(
        screen, "Personnage mystère :", MINI, GRIS, WIDTH // 2, 342, "center"
    )
    afficher_texte(
        screen, etat["mystere"]["name"], MOY, BLANC, WIDTH // 2, 370, "center"
    )

    liens = etat["mystere"].get("liens", etat["mystere"].get("links", []))
    for rangee in range(2):
        debut = rangee * 3
        lot = liens[debut : debut + 3]
        if lot:
            parts = []
            for l in lot:
                type_val = l.get("type") or l.get("type_lien", "?")
                result_val = l.get("result") or l.get("valeur", "?")
                parts.append(type_val.capitalize() + " : " + str(result_val))
            ligne = "  |  ".join(parts)
            afficher_texte(
                screen, ligne, MINI, GRIS, WIDTH // 2, 400 + rangee * 18, "center"
            )

    afficher_texte(
        screen,
        f"Questions posees : {etat['nb_questions']}",
        PETIT,
        GRIS,
        WIDTH // 2,
        458,
        "center",
    )

    dessiner_bouton(screen, etat["btn_rejouer"])
    dessiner_bouton(screen, etat["btn_menu"])


# Antoine
# fonction principal du jeux
def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
    pygame.display.set_caption("Qui est implique ?")
    timer = pygame.time.Clock()

    # Creer le fond gradient (voir le README.md)
    fond = creer_degrade(WIDTH, HEIGHT, (12, 14, 20), (18, 22, 38))

    # Charge le json fais par Grok
    persones = load_data()

    # Initialiser le status du jeux
    etat = {
        "etat": ETAT_ERREUR if persones is None else ETAT_MENU,
        "personnes": persones or [],
        "cartes": [],
        "mystere": None,
        "boutons_qt": [],
        "boutons_val": [],
        "qt_selec": None,
        "nb_questions": 0,
        "dernier_res": None,
        "btn_jouer": creer_bouton(
            WIDTH // 2 - 130, 408, 260, 58, "JOUER", (38, 42, 40), GRAND
        ),
        "btn_rejouer": creer_bouton(
            WIDTH // 2 - 140, 528, 280, 52, "Rejouer", (38, 42, 40), MOY
        ),
        "btn_menu": creer_bouton(
            WIDTH // 2 - 140, 592, 280, 52, "Menu principal", (38, 42, 40), MOY
        ),
    }

    running = True
    while running:
        souris = pygame.mouse.get_pos()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False

            elif etat["etat"] == ETAT_ERREUR:
                if ev.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                    running = False

            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    if etat["etat"] == ETAT_CHOIX:
                        etat["etat"] = ETAT_JEU
                    else:
                        running = False

            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                pos = ev.pos

                if etat["etat"] == ETAT_MENU:
                    if bouton_clique(etat["btn_jouer"], pos):
                        lancer_partie(etat)

                elif etat["etat"] == ETAT_JEU:
                    b = clic_dans_zone(etat, pos)
                    if b:
                        etat["qt_selec"] = b["qt"]
                        construire_boutons_valeurs(etat, b["qt"])
                        etat["etat"] = ETAT_CHOIX
                    else:
                        for c in etat["cartes"]:
                            if carte_cliquee(c, pos):
                                accuser(etat, c)
                                break

                elif etat["etat"] == ETAT_CHOIX:
                    for b in etat["boutons_val"]:
                        if bouton_clique(b, pos):
                            poser_question(etat, etat["qt_selec"], b["valeur"])
                            break

                elif etat["etat"] in (ETAT_GAGNE, ETAT_PERDU):
                    if bouton_clique(etat["btn_rejouer"], pos):
                        lancer_partie(etat)
                    elif bouton_clique(etat["btn_menu"], pos):
                        etat["etat"] = ETAT_MENU

        if etat["etat"] == ETAT_MENU:
            maj_bouton(etat["btn_jouer"], souris)
        elif etat["etat"] in (ETAT_GAGNE, ETAT_PERDU):
            maj_bouton(etat["btn_rejouer"], souris)
            maj_bouton(etat["btn_menu"], souris)
        elif etat["etat"] == ETAT_JEU:
            for c in etat["cartes"]:
                maj_carte(c, souris)
        elif etat["etat"] == ETAT_CHOIX:
            for b in etat["boutons_val"]:
                maj_bouton(b, souris)

        # Rendering
        screen.blit(fond, (0, 0))

        if etat["etat"] == ETAT_ERREUR:
            dessiner_erreur(screen)
        elif etat["etat"] == ETAT_MENU:
            dessiner_menu(screen, etat)
        elif etat["etat"] in (ETAT_JEU, ETAT_CHOIX):
            dessiner_jeu(screen, etat, souris)
            if etat["etat"] == ETAT_CHOIX:
                dessiner_overlay_valeurs(screen, etat)
        elif etat["etat"] == ETAT_GAGNE:
            dessiner_fin(screen, etat, True)
        elif etat["etat"] == ETAT_PERDU:
            dessiner_fin(screen, etat, False)

        pygame.display.flip()
        timer.tick(FPS)

    pygame.quit()
    sys.exit()


main()
