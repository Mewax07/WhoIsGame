import json
import math
import random
import sys

import pygame

pygame.init()

info = pygame.display.Info()
WIDTH = info.current_w
HEIGHT = info.current_h
FPS = 60

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

TITRE = pygame.font.Font(None, 68)
GRAND = pygame.font.Font(None, 48)
MOY = pygame.font.Font(None, 32)
PETIT = pygame.font.Font(None, 26)
MINI = pygame.font.Font(None, 20)
CARTE = pygame.font.Font(None, 17)

COULEURS_AVATAR = [
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

TRANCHES_AGE = [
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

ETAT_ERREUR = "erreur"
ETAT_MENU = "menu"
ETAT_JEU = "jeu"
ETAT_CHOIX = "choix"
ETAT_GAGNE = "gagne"
ETAT_PERDU = "perdu"

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
def afficher_texte(screen, texte, police, couleur, x, y, ancre="topleft"):
    img = police.render(texte, True, couleur)
    r = img.get_rect()
    setattr(r, ancre, (x, y))
    screen.blit(img, r)


# Lenny
def dessiner_panneau(screen, rect, fond=SURFACE, bordure=BORDURE, rayon=10):
    pygame.draw.rect(screen, fond, rect, border_radius=rayon)
    pygame.draw.rect(screen, bordure, rect, 1, border_radius=rayon)


# Lenny et Tymeo (Antoine)
def couper_texte(texte, police, max_l):
    words = texte.split()
    lignes = []
    current = []
    for m in words:
        current.append(m)
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
    return lignes[:2]


# Tymeo
def couleur_avatar(nom):
    return COULEURS_AVATAR[abs(hash(nom)) % len(COULEURS_AVATAR)]


# Lenny et Antoine
def creer_degrade(l, h, haut, bas):
    s = pygame.Surface((l, h))
    for y in range(h):
        t = y / h
        c = tuple(int(haut[i] + (bas[i] - haut[i]) * t) for i in range(3))
        pygame.draw.line(s, c, (0, y), (l, y))
    return s


# Antoine
def charger_donnees():
    try:
        with open("./base.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None


# Antoine
def valeur_lien(personne, type_lien):
    for lien in personne.get("liens", personne.get("links", [])):
        t = lien.get("type") or lien.get("type_lien")
        if t == type_lien:
            return lien.get("result") or lien.get("valeur")
    return None


# Antoine
def types_questions(personnes):
    vus = set()
    result = []
    for p in personnes:
        for lien in p.get("liens", p.get("links", [])):
            t = lien.get("type") or lien.get("type_lien")
            if t and t not in vus:
                vus.add(t)
                result.append(t)
    return result


# Lenny et Antoine
def age_en_tranche(age):
    try:
        a = int(age)
    except (ValueError, TypeError):
        return str(age)
    for lo, hi, label in TRANCHES_AGE:
        if lo <= a <= hi:
            return label
    return str(age)


# Lenny et Antoine
def trier_tranche(label):
    try:
        return int(label.replace("90+", "90").split("-")[0].split()[0])
    except Exception:
        return 999


# Tymeo
def valeurs_disponibles(personnes, qt):
    if qt == "age":
        vals = {
            age_en_tranche(valeur_lien(p, qt))
            for p in personnes
            if valeur_lien(p, qt) is not None
        }
        return sorted(vals, key=trier_tranche)
    vals = []
    vus = set()
    for p in personnes:
        v = valeur_lien(p, qt)
        if v is not None and str(v) not in vus:
            vus.add(str(v))
            vals.append(str(v))
    return sorted(vals)


# Lenny et Antoine
def creer_bouton(x, y, l, h, label, couleur, police=None):
    return {
        "rect": pygame.Rect(x, y, l, h),
        "label": label,
        "couleur": couleur,
        "police": police or PETIT,
        "survol": False,
    }


# Lenny
def maj_bouton(bouton, souris):
    bouton["survol"] = bouton["rect"].collidepoint(souris)


# Lenny et Antoine
def dessiner_bouton(surf, bouton):
    c = (
        tuple(min(v + 25, 255) for v in bouton["couleur"])
        if bouton["survol"]
        else bouton["couleur"]
    )
    pygame.draw.rect(surf, c, bouton["rect"], border_radius=8)
    pygame.draw.rect(surf, BORDURE, bouton["rect"], 1, border_radius=8)
    afficher_texte(
        surf,
        bouton["label"],
        bouton["police"],
        BLANC,
        bouton["rect"].centerx,
        bouton["rect"].centery,
        "center",
    )


# Lenny
def bouton_clique(bouton, pos):
    return bouton["rect"].collidepoint(pos)


# Lenny et Antoine
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
def nb_restants(cartes):
    return sum(1 for c in cartes if not c["elimine"])


# Lenny et Antoine
def eliminer_carte(carte):
    if not carte["elimine"]:
        carte["elimine"] = True
        carte["flip"] = 0.0


# Lenny et Antoine
def carte_cliquee(carte, pos):
    return (
        not carte["elimine"]
        and carte["x"] <= pos[0] <= carte["x"] + CARTE_WIDTH
        and carte["y"] <= pos[1] <= carte["y"] + CARTE_HEIGHT
    )


# Tymeo
def maj_carte(carte, souris):
    if carte["flip"] >= 0:
        carte["flip"] += 0.07
        if carte["flip"] >= 1.0:
            carte["flip"] = -1.0
    carte["survol"] = (
        not carte["elimine"]
        and carte["x"] <= souris[0] <= carte["x"] + CARTE_WIDTH
        and carte["y"] <= souris[1] <= carte["y"] + CARTE_HEIGHT
    )


# Antoine et Tymeo
def dessiner_carte(surf, carte):
    x = carte["x"]
    y = carte["y"]

    if carte["flip"] >= 0:
        scale = abs(math.cos(carte["flip"] * math.pi))
        fl = max(4, int(CARTE_WIDTH * scale))
        rx = x + (CARTE_WIDTH - fl) // 2
        r = pygame.Rect(rx, y, fl, CARTE_HEIGHT)
        col = CARTE_FD if carte["flip"] < 0.5 else CARTE_EL
        bc = BORDURE if carte["flip"] < 0.5 else ROUGE_FD
        pygame.draw.rect(surf, col, r, border_radius=8)
        pygame.draw.rect(surf, bc, r, 1, border_radius=8)
        if carte["flip"] >= 0.5:
            m = 10
            pygame.draw.line(
                surf, ROUGE, (rx + m, y + m), (rx + fl - m, y + CARTE_HEIGHT - m), 2
            )
            pygame.draw.line(
                surf, ROUGE, (rx + fl - m, y + m), (rx + m, y + CARTE_HEIGHT - m), 2
            )
        return

    if carte["elimine"]:
        r = pygame.Rect(x, y, CARTE_WIDTH, CARTE_HEIGHT)
        pygame.draw.rect(surf, CARTE_EL, r, border_radius=8)
        pygame.draw.rect(surf, ROUGE_FD, r, 1, border_radius=8)
        m = 14
        pygame.draw.line(
            surf,
            (60, 22, 28),
            (x + m, y + m),
            (x + CARTE_WIDTH - m, y + CARTE_HEIGHT - m),
            2,
        )
        pygame.draw.line(
            surf,
            (60, 22, 28),
            (x + CARTE_WIDTH - m, y + m),
            (x + m, y + CARTE_HEIGHT - m),
            2,
        )
        return

    r = pygame.Rect(x, y, CARTE_WIDTH, CARTE_HEIGHT)
    bc = ACCENT if carte["survol"] else BORDURE
    ep = 2 if carte["survol"] else 1
    pygame.draw.rect(surf, CARTE_FD, r, border_radius=8)
    pygame.draw.rect(surf, bc, r, ep, border_radius=8)

    ph = int(CARTE_HEIGHT * 0.56)
    ar = pygame.Rect(x + 6, y + 6, CARTE_WIDTH - 12, ph)
    pygame.draw.rect(
        surf, couleur_avatar(carte["personne"]["name"]), ar, border_radius=6
    )

    initiales = "".join(m[0].upper() for m in carte["personne"]["name"].split()[:2])
    afficher_texte(
        surf,
        initiales,
        pygame.font.Font(None, 32),
        BLANC,
        x + CARTE_WIDTH // 2,
        y + 6 + ph // 2,
        "center",
    )

    ny = y + 6 + ph + 9
    for i, ligne in enumerate(
        couper_texte(carte["personne"]["name"], CARTE, CARTE_WIDTH - 12)
    ):
        afficher_texte(
            surf, ligne, CARTE, BLANC, x + CARTE_WIDTH // 2, ny + i * 14, "center"
        )


# Tymeo
def lancer_partie(etat):
    personnes = etat["personnes"]
    choisis = random.sample(personnes, min(36, len(personnes)))

    etat["mystere"] = random.choice(choisis)
    etat["nb_questions"] = 0
    etat["dernier_res"] = None
    etat["qt_selec"] = None
    etat["boutons_val"] = []

    sx = 36
    sy = 130
    etat["cartes"] = [
        creer_carte(
            p,
            sx + (i % COLS) * (CARTE_WIDTH + MARGE_X),
            sy + (i // COLS) * (CARTE_HEIGHT + MARGE_Y),
        )
        for i, p in enumerate(choisis)
    ]

    bl = (ZONE_WIDTH - 16 - (BTN_COL - 1) * BTN_GAP) // BTN_COL
    etat["boutons_qt"] = []
    for i, qt in enumerate(types_questions(personnes)):
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
def construire_boutons_valeurs(etat, qt):
    vals = valeurs_disponibles(etat["personnes"], qt)
    bx0 = WIDTH // 2 - 300
    by0 = 315
    bl = 192
    bh = 42
    ecart = 10
    par_col = 3

    etat["boutons_val"] = []
    for i, v in enumerate(vals):
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
def poser_question(etat, qt, valeur):
    val_mystere = valeur_lien(etat["mystere"], qt)

    if qt == "age":
        cible = age_en_tranche(val_mystere)
        elimines = 0
        for c in etat["cartes"]:
            if (
                not c["elimine"]
                and age_en_tranche(valeur_lien(c["personne"], qt)) != cible
            ):
                eliminer_carte(c)
                elimines += 1
        reponse = cible
    else:
        elimines = 0
        for c in etat["cartes"]:
            if not c["elimine"] and str(valeur_lien(c["personne"], qt) or "") != str(
                val_mystere or ""
            ):
                eliminer_carte(c)
                elimines += 1
        reponse = str(val_mystere)

    etat["nb_questions"] += 1
    etat["dernier_res"] = (qt.replace("_", " ").capitalize(), reponse, elimines)
    etat["etat"] = ETAT_JEU
    verifier_fin(etat)


# Tymeo
def accuser(etat, carte):
    if carte["personne"]["name"] == etat["mystere"]["name"]:
        etat["etat"] = ETAT_GAGNE
    else:
        eliminer_carte(carte)
        etat["nb_questions"] += 1
        etat["etat"] = ETAT_PERDU


# Lenny
def verifier_fin(etat):
    restants = [c for c in etat["cartes"] if not c["elimine"]]
    if (
        len(restants) == 1
        and restants[0]["personne"]["name"] == etat["mystere"]["name"]
    ):
        etat["etat"] = ETAT_GAGNE
    elif len(restants) == 0:
        etat["etat"] = ETAT_PERDU


# Tymeo
def clic_dans_zone(etat, pos):
    if not pygame.Rect(ZONE_X, ZONE_Y, ZONE_WIDTH, ZONE_HEIGHT).collidepoint(pos):
        return None
    for b in etat["boutons_qt"]:
        if b["rect"].collidepoint(pos):
            return b
    return None


# Lenny
def dessiner_erreur(surf):
    afficher_texte(
        surf,
        "Erreure : base.json introuvable",
        GRAND,
        ROUGE,
        WIDTH // 2,
        HEIGHT // 2 - 44,
        "center",
    )
    afficher_texte(
        surf,
        "Placez base.json dans le meme dossier que ce script.",
        PETIT,
        GRIS,
        WIDTH // 2,
        HEIGHT // 2 + 4,
        "center",
    )
    afficher_texte(
        surf,
        "Appuyez sur une touche pour quiter.",
        MINI,
        GRIS,
        WIDTH // 2,
        HEIGHT // 2 + 40,
        "center",
    )


# Tymeo
def dessiner_menu(surf, etat):
    afficher_texte(
        surf, "QUI EST L'IMPLIQUE ?", TITRE, ACCENT, WIDTH // 2, 168, "center"
    )
    afficher_texte(surf, "Edition Familiale", MOY, GRIS, WIDTH // 2, 236, "center")
    pygame.draw.line(surf, BORDURE, (WIDTH // 2 - 280, 264), (WIDTH // 2 + 280, 264), 1)
    dessiner_panneau(surf, pygame.Rect(WIDTH // 2 - 255, 288, 510, 95))
    afficher_texte(
        surf,
        "Posez des question pour eliminer les suspect.",
        PETIT,
        BLANC,
        WIDTH // 2,
        316,
        "center",
    )
    afficher_texte(
        surf,
        "Designez le personnage mystère avant de manquer d'indices.",
        PETIT,
        GRIS,
        WIDTH // 2,
        348,
        "center",
    )
    dessiner_bouton(surf, etat["btn_jouer"])
    afficher_texte(
        surf,
        f"{len(etat['personnes'])} personnages charger dans la base",
        MINI,
        GRIS,
        WIDTH // 2,
        488,
        "center",
    )


# Antoine
def dessiner_zone_questions(surf, etat, souris):
    zone = pygame.Rect(ZONE_X, ZONE_Y, ZONE_WIDTH, ZONE_HEIGHT)
    afficher_texte(surf, "Poser une question :", PETIT, GRIS, ZONE_X + 8, ZONE_Y - 22)
    pygame.draw.rect(surf, (14, 17, 30), zone, border_radius=6)
    for b in etat["boutons_qt"]:
        maj_bouton(b, souris)
        dessiner_bouton(surf, b)
    pygame.draw.rect(surf, BORDURE, zone, 1, border_radius=6)


# Antoine
def dessiner_jeu(surf, etat, souris):
    afficher_texte(
        surf, "QUI EST L'IMPLIQUE ?", MOY, ACCENT, WIDTH // 2 - 80, 36, "center"
    )

    info_r = pygame.Rect(22, 12, 225, 54)
    dessiner_panneau(surf, info_r)
    afficher_texte(
        surf,
        f"Restants : {nb_restants(etat['cartes'])} / {len(etat['cartes'])}",
        PETIT,
        BLANC,
        info_r.centerx,
        info_r.centery - 8,
        "center",
    )
    afficher_texte(
        surf,
        f"Questions : {etat['nb_questions']}",
        MINI,
        GRIS,
        info_r.centerx,
        info_r.centery + 12,
        "center",
    )

    for c in etat["cartes"]:
        dessiner_carte(surf, c)

    dessiner_panneau(surf, pygame.Rect(ZONE_X - 14, 68, ZONE_WIDTH + 28, HEIGHT - 96))

    mh = pygame.Rect(ZONE_X, 80, ZONE_WIDTH, 58)
    dessiner_panneau(surf, mh, fond=(28, 36, 62), bordure=ACCENT)
    afficher_texte(
        surf,
        "PERSONNAGE MYSTERE",
        MINI,
        ACCENT,
        mh.centerx,
        mh.centery - 10,
        "center",
    )
    afficher_texte(
        surf,
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
        dessiner_panneau(surf, lr, fond=(20, 44, 30), bordure=VERT)
        afficher_texte(
            surf, f"{lbl} : {rep}", MINI, VERT, lr.centerx, lr.centery - 10, "center"
        )
        afficher_texte(
            surf,
            f"{elim} elimine(s)",
            MINI,
            GRIS,
            lr.centerx,
            lr.centery + 10,
            "center",
        )

    dessiner_zone_questions(surf, etat, souris)
    afficher_texte(
        surf,
        "Cliquer sur un personnage pour l'acuser.",
        MINI,
        GRIS,
        ZONE_X + 8,
        ZONE_Y + ZONE_HEIGHT + 8,
    )


# Antoine et Tymeo
def dessiner_overlay_valeurs(surf, etat):
    dim = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    dim.fill((0, 0, 0, 165))
    surf.blit(dim, (0, 0))

    boite = pygame.Rect(WIDTH // 2 - 365, 150, 730, 515)
    label = etat["qt_selec"].replace("_", " ").upper()
    sous = (
        "Tranche d'age (5 ans) :" if etat["qt_selec"] == "age" else "Quelle valeure ?"
    )

    dessiner_panneau(surf, boite, fond=(16, 20, 38), bordure=ACCENT)
    afficher_texte(surf, f"Question : {label}", MOY, ACCENT, WIDTH // 2, 190, "center")
    afficher_texte(surf, sous, PETIT, GRIS, WIDTH // 2, 228, "center")
    pygame.draw.line(surf, BORDURE, (WIDTH // 2 - 260, 248), (WIDTH // 2 + 260, 248), 1)

    for b in etat["boutons_val"]:
        dessiner_bouton(surf, b)

    afficher_texte(
        surf, "[ ESC ] Annuler", MINI, GRIS, WIDTH // 2, boite.bottom - 20, "center"
    )


# Antoine et Tymeo et Lenny
def dessiner_fin(surf, etat, gagne):
    for c in etat["cartes"]:
        dessiner_carte(surf, c)

    dim = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    dim.fill((0, 0, 0, 155))
    surf.blit(dim, (0, 0))

    boite = pygame.Rect(WIDTH // 2 - 310, 160, 620, 485)
    dessiner_panneau(surf, boite, fond=(16, 20, 38), bordure=VERT if gagne else ROUGE)

    if gagne:
        afficher_texte(surf, "TROUVE !", TITRE, ACCENT, WIDTH // 2, 232, "center")
        afficher_texte(
            surf,
            "Vous avez identifié le personnage mystére.",
            PETIT,
            BLANC,
            WIDTH // 2,
            292,
            "center",
        )
    else:
        afficher_texte(surf, "PERDU !", TITRE, ROUGE, WIDTH // 2, 232, "center")
        afficher_texte(
            surf,
            "C'étais pas le bon personnage.",
            PETIT,
            BLANC,
            WIDTH // 2,
            292,
            "center",
        )

    rv = pygame.Rect(WIDTH // 2 - 220, 322, 440, 118)
    dessiner_panneau(surf, rv, fond=(24, 30, 52), bordure=ACCENT)
    afficher_texte(surf, "Personnage mystère :", MINI, GRIS, WIDTH // 2, 342, "center")
    afficher_texte(surf, etat["mystere"]["name"], MOY, BLANC, WIDTH // 2, 370, "center")

    liens = etat["mystere"].get("liens", etat["mystere"].get("links", []))
    for rangee, debut in enumerate([0, 3]):
        lot = liens[debut : debut + 3]
        if lot:
            ligne = "  |  ".join(
                (l.get("type") or l.get("type_lien", "?")).capitalize()
                + " : "
                + str(l.get("result") or l.get("valeur", "?"))
                for l in lot
            )
            afficher_texte(
                surf, ligne, MINI, GRIS, WIDTH // 2, 400 + rangee * 18, "center"
            )

    afficher_texte(
        surf,
        f"Questions posees : {etat['nb_questions']}",
        PETIT,
        GRIS,
        WIDTH // 2,
        458,
        "center",
    )
    dessiner_bouton(surf, etat["btn_rejouer"])
    dessiner_bouton(surf, etat["btn_menu"])


# Antoine
def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
    pygame.display.set_caption("Qui est implique ?")
    timer = pygame.time.Clock()
    fond = creer_degrade(WIDTH, HEIGHT, (12, 14, 20), (18, 22, 38))
    persones = charger_donnees()

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
            WIDTH // 2 - 130, 408, 260, 58, "JOUER", (38, 105, 62), GRAND
        ),
        "btn_rejouer": creer_bouton(
            WIDTH // 2 - 140, 528, 280, 52, "Rejouer", (38, 88, 155), MOY
        ),
        "btn_menu": creer_bouton(
            WIDTH // 2 - 140, 592, 280, 52, "Menu principal", (48, 52, 78), MOY
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
