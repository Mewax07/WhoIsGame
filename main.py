import json
import math
import random
import sys

import pygame

pygame.init()

LARGEUR, HAUTEUR, FPS = 1480, 900, 60

PANNEAU = (22, 28, 48)
CARTE_FOND = (28, 36, 62)
CARTE_EL = (20, 20, 30)
BORDURE = (45, 55, 90)
BLANC = (230, 235, 248)
GRIS = (110, 120, 150)
OR = (255, 195, 45)
CYAN = (70, 190, 240)
VERT = (55, 195, 120)
ROUGE = (215, 65, 75)
ROUGE_FONC = (100, 28, 38)

POLICE_TITRE = pygame.font.Font(None, 74)
POLICE_GRAND = pygame.font.Font(None, 50)
POLICE_MOY = pygame.font.Font(None, 34)
POLICE_PETIT = pygame.font.Font(None, 26)
POLICE_MINI = pygame.font.Font(None, 20)
POLICE_CARTE = pygame.font.Font(None, 17)

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
ETAT_VALEUR = "valeur"
ETAT_GAGNE = "gagne"
ETAT_PERDU = "perdu"

CARTE_L = 145
CARTE_H = 190
COLS = 6
MARGE_X = 18
MARGE_Y = 16

ZONE_QT_X = 1148
ZONE_QT_Y = 240
ZONE_QT_L = 310
ZONE_QT_H = 580
BH = 44
GAP = 10


# Lenny et Antoine
def creer_fond():
    s = pygame.Surface((LARGEUR, HAUTEUR))
    for y in range(HAUTEUR):
        t = y / HAUTEUR
        c = (int(14 + 6 * t), int(18 + 8 * t), int(32 + 16 * t))
        pygame.draw.line(s, c, (0, y), (LARGEUR, y))
    return s


# Lenny et Tymeo
def texte_centre(ecran, texte, police, couleur, cx, cy):
    s = police.render(texte, True, couleur)
    ecran.blit(s, s.get_rect(center=(cx, cy)))


# Lenny et Tymeo
def texte_gauche(ecran, texte, police, couleur, x, y):
    ecran.blit(police.render(texte, True, couleur), (x, y))


# Lenny et Tymeo
def panneau(ecran, rect, couleur=None, bordure=None, rayon=10):
    if couleur is None:
        couleur = PANNEAU
    if bordure is None:
        bordure = BORDURE
    pygame.draw.rect(ecran, couleur, rect, border_radius=rayon)
    pygame.draw.rect(ecran, bordure, rect, 1, border_radius=rayon)


# Lenny et Tymeo
def couper_texte(texte, police, max_l):
    mots, lignes, cur = texte.split(), [], []
    for m in mots:
        cur.append(m)
        if police.size(" ".join(cur))[0] > max_l:
            if len(cur) > 1:
                cur.pop()
                lignes.append(" ".join(cur))
                cur = [m]
            else:
                lignes.append(m)
                cur = []
    if cur:
        lignes.append(" ".join(cur))
    return lignes[:2]


# Lenny et Tymeo
def couleur_nom(nom):
    return COULEURS_CARTES[abs(hash(nom)) % len(COULEURS_CARTES)]


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
        return int(label.split("-")[0].replace("90+", "90").split()[0])
    except Exception:
        return 999


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
    vus, ordre = set(), []
    for p in personnes:
        for lien in p.get("liens", p.get("links", [])):
            t = lien.get("type") or lien.get("type_lien")
            if t and t not in vus:
                vus.add(t)
                ordre.append(t)
    return ordre


# Tymeo
def valeurs_disponibles(personnes, qt):
    if qt == "age":
        vus = set()
        for p in personnes:
            v = valeur_lien(p, qt)
            if v is not None:
                vus.add(age_en_tranche(v))
        return sorted(vus, key=trier_tranche)
    vals, vus = [], set()
    for p in personnes:
        v = valeur_lien(p, qt)
        if v is not None and str(v) not in vus:
            vus.add(str(v))
            vals.append(str(v))
    return sorted(vals)


# Lenny et Antoine
def creer_bouton(x, y, l, h, texte, couleur, police=None):
    return {
        "rect": pygame.Rect(x, y, l, h),
        "texte": texte,
        "couleur": couleur,
        "police": police or POLICE_PETIT,
        "survol": False,
    }


# Lenny
def maj_bouton(bouton, souris):
    bouton["survol"] = bouton["rect"].collidepoint(souris)


# Lenny et Antoine
def dessiner_bouton(ecran, bouton):
    c = (
        tuple(min(v + 22, 255) for v in bouton["couleur"])
        if bouton["survol"]
        else bouton["couleur"]
    )
    pygame.draw.rect(ecran, c, bouton["rect"], border_radius=8)
    pygame.draw.rect(ecran, BORDURE, bouton["rect"], 1, border_radius=8)
    s = bouton["police"].render(bouton["texte"], True, BLANC)
    ecran.blit(s, s.get_rect(center=bouton["rect"].center))


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
        "flip_t": -1.0,
    }


# Lenny et Antoine
def nb_restants(cartes):
    return sum(1 for c in cartes if not c["elimine"])


# Lenny et Antoine
def eliminer_carte(carte):
    if not carte["elimine"]:
        carte["elimine"] = True
        carte["flip_t"] = 0.0


# Lenny et Antoine
def carte_cliquee(carte, pos):
    return (
        not carte["elimine"]
        and carte["x"] <= pos[0] <= carte["x"] + CARTE_L
        and carte["y"] <= pos[1] <= carte["y"] + CARTE_H
    )


# Tymeo
def maj_carte(carte, souris):
    if carte["flip_t"] >= 0:
        carte["flip_t"] += 0.07
        if carte["flip_t"] >= 1.0:
            carte["flip_t"] = -1.0
    x, y = carte["x"], carte["y"]
    carte["survol"] = (
        not carte["elimine"]
        and x <= souris[0] <= x + CARTE_L
        and y <= souris[1] <= y + CARTE_H
    )


# Antoine et Tymeo
def dessiner_carte(ecran, carte):
    x, y = carte["x"], carte["y"]

    if carte["flip_t"] >= 0:
        fx = abs(math.cos(carte["flip_t"] * math.pi))
        fw = max(4, int(CARTE_L * fx))
        ox = x + (CARTE_L - fw) // 2
        r = pygame.Rect(ox, y, fw, CARTE_H)
        if carte["flip_t"] < 0.5:
            pygame.draw.rect(ecran, CARTE_FOND, r, border_radius=8)
            pygame.draw.rect(ecran, BORDURE, r, 1, border_radius=8)
        else:
            pygame.draw.rect(ecran, CARTE_EL, r, border_radius=8)
            pygame.draw.rect(ecran, ROUGE_FONC, r, 1, border_radius=8)
            m = 12
            pygame.draw.line(
                ecran, ROUGE, (ox + m, y + m), (ox + fw - m, y + CARTE_H - m), 3
            )
            pygame.draw.line(
                ecran, ROUGE, (ox + fw - m, y + m), (ox + m, y + CARTE_H - m), 3
            )
        return

    if carte["elimine"]:
        r = pygame.Rect(x, y, CARTE_L, CARTE_H)
        pygame.draw.rect(ecran, CARTE_EL, r, border_radius=8)
        pygame.draw.rect(ecran, ROUGE_FONC, r, 1, border_radius=8)
        m = 14
        pygame.draw.line(
            ecran, (80, 28, 36), (x + m, y + m), (x + CARTE_L - m, y + CARTE_H - m), 3
        )
        pygame.draw.line(
            ecran, (80, 28, 36), (x + CARTE_L - m, y + m), (x + m, y + CARTE_H - m), 3
        )
        return

    r = pygame.Rect(x, y, CARTE_L, CARTE_H)
    pygame.draw.rect(ecran, CARTE_FOND, r, border_radius=8)
    bc = OR if carte["survol"] else BORDURE
    bw = 2 if carte["survol"] else 1
    pygame.draw.rect(ecran, bc, r, bw, border_radius=8)

    ph = int(CARTE_H * 0.57)
    ar = pygame.Rect(x + 7, y + 7, CARTE_L - 14, ph)
    nom = carte["personne"]["name"]
    pygame.draw.rect(ecran, couleur_nom(nom), ar, border_radius=6)

    initiales = "".join(w[0].upper() for w in nom.split()[:2])
    si = pygame.font.Font(None, 34).render(initiales, True, BLANC)
    ecran.blit(si, si.get_rect(center=(x + CARTE_L // 2, y + 7 + ph // 2)))

    ny = y + 7 + ph + 10
    for i, ligne in enumerate(couper_texte(nom, POLICE_CARTE, CARTE_L - 12)):
        sl = POLICE_CARTE.render(ligne, True, BLANC)
        ecran.blit(sl, sl.get_rect(center=(x + CARTE_L // 2, ny + i * 15)))


# Tymeo
def lancer_partie(etat):
    personnes = etat["personnes"]
    nb = min(32, len(personnes))
    choisis = random.sample(personnes, nb)
    etat["mystere"] = random.choice(choisis)
    etat["scroll_qt"] = 0

    etat["cartes"] = []
    sx, sy = 38, 130
    for i, p in enumerate(choisis):
        row, col = divmod(i, COLS)
        etat["cartes"].append(
            creer_carte(
                p, sx + col * (CARTE_L + MARGE_X), sy + row * (CARTE_H + MARGE_Y)
            )
        )

    couleurs_bt = [CYAN, VERT, (200, 100, 200), OR, (200, 115, 55), (120, 180, 100)]
    etat["boutons_qt"] = []
    for i, qt in enumerate(types_questions(personnes)):
        b = creer_bouton(
            ZONE_QT_X + 8,
            0,
            ZONE_QT_L - 20,
            BH,
            qt.replace("_", " ").capitalize(),
            couleurs_bt[i % len(couleurs_bt)],
        )
        b["qt"] = qt
        etat["boutons_qt"].append(b)

    etat["nb_questions"] = 0
    etat["dernier_res"] = None
    etat["qt_selec"] = None
    etat["boutons_qv"] = []
    etat["etat"] = ETAT_JEU


# Tymeo
def construire_boutons_valeurs(etat, qt):
    vals = valeurs_disponibles(etat["personnes"], qt)
    bx0, by0 = LARGEUR // 2 - 300, 315
    bl, bh, gap, par_ligne = 190, 42, 10, 6
    etat["boutons_qv"] = []
    for i, v in enumerate(vals):
        row, col = divmod(i, par_ligne)
        b = creer_bouton(
            bx0 + col * (bl + gap),
            by0 + row * (bh + gap),
            bl,
            bh,
            str(v),
            (55, 65, 120),
        )
        b["valeur"] = v
        etat["boutons_qv"].append(b)


# Tymeo
def poser_question(etat, qt, valeur):
    mv = valeur_lien(etat["mystere"], qt)
    if qt == "age":
        tranche_m = age_en_tranche(mv)
        elim = 0
        for c in etat["cartes"]:
            if c["elimine"]:
                continue
            if age_en_tranche(valeur_lien(c["personne"], qt)) != tranche_m:
                eliminer_carte(c)
                elim += 1
        reponse = tranche_m
    else:
        elim = 0
        for c in etat["cartes"]:
            if c["elimine"]:
                continue
            if str(valeur_lien(c["personne"], qt) or "") != str(mv or ""):
                eliminer_carte(c)
                elim += 1
        reponse = str(mv)
    etat["nb_questions"] += 1
    etat["dernier_res"] = (qt.replace("_", " ").capitalize(), reponse, elim)
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


# Lenny
def scroll_total(boutons_qt):
    return len(boutons_qt) * (BH + GAP)


# Lenny
def clamp_scroll(etat):
    total = scroll_total(etat["boutons_qt"])
    etat["scroll_qt"] = max(0, min(etat["scroll_qt"], max(0, total - ZONE_QT_H)))


# Lenny
def scroll_event(etat, direction):
    etat["scroll_qt"] += direction * 30
    clamp_scroll(etat)


# Antoine
def dessiner_scrollbox_qt(ecran, etat, souris):
    clamp_scroll(etat)
    scroll = etat["scroll_qt"]
    total = scroll_total(etat["boutons_qt"])

    texte_gauche(
        ecran, "Poser une question :", POLICE_PETIT, GRIS, ZONE_QT_X + 8, ZONE_QT_Y - 22
    )

    zone_rect = pygame.Rect(ZONE_QT_X, ZONE_QT_Y, ZONE_QT_L, ZONE_QT_H)
    pygame.draw.rect(ecran, (16, 20, 38), zone_rect, border_radius=6)

    ecran.set_clip(zone_rect)

    for i, b in enumerate(etat["boutons_qt"]):
        vy = ZONE_QT_Y + i * (BH + GAP) - scroll
        b["rect"].x = ZONE_QT_X + 8
        b["rect"].y = vy
        b["survol"] = (
            (not ecran.get_clip() or True)
            and b["rect"].collidepoint(souris)
            and zone_rect.collidepoint(souris)
        )
        if vy + BH > ZONE_QT_Y and vy < ZONE_QT_Y + ZONE_QT_H:
            dessiner_bouton(ecran, b)

    ecran.set_clip(None)

    pygame.draw.rect(ecran, BORDURE, zone_rect, 1, border_radius=6)

    if total > ZONE_QT_H:
        sb_x = ZONE_QT_X + ZONE_QT_L + 3
        th_h = max(24, int(ZONE_QT_H * ZONE_QT_H / total))
        ratio = scroll / (total - ZONE_QT_H)
        th_y = ZONE_QT_Y + int(ratio * (ZONE_QT_H - th_h))
        pygame.draw.rect(
            ecran, BORDURE, pygame.Rect(sb_x, ZONE_QT_Y, 4, ZONE_QT_H), border_radius=2
        )
        pygame.draw.rect(ecran, OR, pygame.Rect(sb_x, th_y, 4, th_h), border_radius=2)


# Tymeo
def clic_dans_scrollbox(etat, pos):
    zone_rect = pygame.Rect(ZONE_QT_X, ZONE_QT_Y, ZONE_QT_L, ZONE_QT_H)
    if not zone_rect.collidepoint(pos):
        return None
    for b in etat["boutons_qt"]:
        if b["rect"].collidepoint(pos):
            return b
    return None


# Lenny
def dessiner_ecran_erreur(ecran):
    texte_centre(
        ecran,
        "Erreur : base.json introuvable",
        POLICE_GRAND,
        ROUGE,
        LARGEUR // 2,
        HAUTEUR // 2 - 40,
    )
    texte_centre(
        ecran,
        "Placez base.json dans le meme dossier que ce script puis relancez.",
        POLICE_PETIT,
        GRIS,
        LARGEUR // 2,
        HAUTEUR // 2 + 5,
    )
    texte_centre(
        ecran,
        "Appuyez sur une touche ou cliquez pour quitter.",
        POLICE_MINI,
        GRIS,
        LARGEUR // 2,
        HAUTEUR // 2 + 42,
    )


# Tymeo
def dessiner_menu(ecran, etat):
    texte_centre(ecran, "QUI EST L'IMPLIQUE ?", POLICE_TITRE, OR, LARGEUR // 2, 175)
    texte_centre(ecran, "Edition Familiale", POLICE_MOY, GRIS, LARGEUR // 2, 242)
    pygame.draw.line(
        ecran, BORDURE, (LARGEUR // 2 - 280, 268), (LARGEUR // 2 + 280, 268), 1
    )
    panneau(ecran, pygame.Rect(LARGEUR // 2 - 260, 293, 520, 95))
    texte_centre(
        ecran,
        "Posez des questions pour eliminer les suspects.",
        POLICE_PETIT,
        BLANC,
        LARGEUR // 2,
        323,
    )
    texte_centre(
        ecran,
        "Designez le personnage mystere avant de manquer d'indices.",
        POLICE_PETIT,
        GRIS,
        LARGEUR // 2,
        355,
    )
    dessiner_bouton(ecran, etat["bouton_jouer"])
    texte_centre(
        ecran,
        str(len(etat["personnes"])) + " personnages charges dans la base",
        POLICE_MINI,
        GRIS,
        LARGEUR // 2,
        490,
    )


# Antoine
def dessiner_jeu(ecran, etat, souris):
    texte_centre(ecran, "QUI EST L'IMPLIQUE ?", POLICE_MOY, OR, LARGEUR // 2 - 100, 38)
    sr = pygame.Rect(22, 14, 220, 50)
    panneau(ecran, sr)
    texte_centre(
        ecran,
        "Restants : "
        + str(nb_restants(etat["cartes"]))
        + " / "
        + str(len(etat["cartes"])),
        POLICE_PETIT,
        BLANC,
        sr.centerx,
        sr.centery - 7,
    )
    texte_centre(
        ecran,
        "Questions : " + str(etat["nb_questions"]),
        POLICE_MINI,
        GRIS,
        sr.centerx,
        sr.centery + 12,
    )

    for c in etat["cartes"]:
        dessiner_carte(ecran, c)

    panneau(ecran, pygame.Rect(ZONE_QT_X - 14, 70, 340, HAUTEUR - 100))

    mh = pygame.Rect(ZONE_QT_X, 82, 294, 60)
    panneau(ecran, mh, couleur=(30, 40, 70), bordure=OR)
    texte_centre(
        ecran, "PERSONNAGE MYSTERE", POLICE_MINI, OR, mh.centerx, mh.centery - 9
    )
    texte_centre(
        ecran,
        "Posez des questions ou designez-le.",
        POLICE_MINI,
        GRIS,
        mh.centerx,
        mh.centery + 11,
    )

    if etat["dernier_res"]:
        lbl, rep, elim = etat["dernier_res"]
        lr = pygame.Rect(ZONE_QT_X, 152, 294, 56)
        panneau(ecran, lr, couleur=(22, 48, 32), bordure=VERT)
        texte_centre(
            ecran, lbl + " : " + rep, POLICE_MINI, VERT, lr.centerx, lr.centery - 9
        )
        texte_centre(
            ecran,
            str(elim) + " elimine(s)",
            POLICE_MINI,
            GRIS,
            lr.centerx,
            lr.centery + 11,
        )

    dessiner_scrollbox_qt(ecran, etat, souris)

    bas = ZONE_QT_Y + ZONE_QT_H + 8
    texte_gauche(
        ecran,
        "Cliquez sur un personnage pour l'accuser.",
        POLICE_MINI,
        GRIS,
        ZONE_QT_X + 8,
        bas,
    )


# Antoine et Tymeo et Lenny
def dessiner_overlay_valeurs(ecran, etat):
    dim = pygame.Surface((LARGEUR, HAUTEUR), pygame.SRCALPHA)
    dim.fill((0, 0, 0, 155))
    ecran.blit(dim, (0, 0))
    box = pygame.Rect(LARGEUR // 2 - 360, 155, 720, 510)
    panneau(ecran, box, couleur=(18, 24, 44), bordure=OR)
    label = etat["qt_selec"].replace("_", " ").upper()
    texte_centre(ecran, "Question : " + label, POLICE_MOY, OR, LARGEUR // 2, 192)
    sous = "Tranche d'age (5 ans) :" if etat["qt_selec"] == "age" else "Quelle valeur ?"
    texte_centre(ecran, sous, POLICE_PETIT, GRIS, LARGEUR // 2, 228)
    pygame.draw.line(
        ecran, BORDURE, (LARGEUR // 2 - 260, 248), (LARGEUR // 2 + 260, 248), 1
    )
    for b in etat["boutons_qv"]:
        dessiner_bouton(ecran, b)
    texte_centre(
        ecran, "[ ESC ] Annuler", POLICE_MINI, GRIS, LARGEUR // 2, box.bottom - 20
    )


# Antoine et Tymeo
def dessiner_fin(ecran, etat, gagne):
    for c in etat["cartes"]:
        dessiner_carte(ecran, c)
    dim = pygame.Surface((LARGEUR, HAUTEUR), pygame.SRCALPHA)
    dim.fill((0, 0, 0, 145))
    ecran.blit(dim, (0, 0))
    box = pygame.Rect(LARGEUR // 2 - 310, 165, 620, 475)
    panneau(ecran, box, couleur=(18, 24, 44), bordure=VERT if gagne else ROUGE)
    if gagne:
        texte_centre(ecran, "TROUVE !", POLICE_TITRE, OR, LARGEUR // 2, 238)
        texte_centre(
            ecran,
            "Vous avez identifie le personnage mystere.",
            POLICE_PETIT,
            BLANC,
            LARGEUR // 2,
            296,
        )
    else:
        texte_centre(ecran, "PERDU !", POLICE_TITRE, ROUGE, LARGEUR // 2, 238)
        texte_centre(
            ecran,
            "Ce n'etait pas le bon personnage.",
            POLICE_PETIT,
            BLANC,
            LARGEUR // 2,
            296,
        )
    rv = pygame.Rect(LARGEUR // 2 - 220, 325, 440, 115)
    panneau(ecran, rv, couleur=(25, 32, 58), bordure=OR)
    texte_centre(ecran, "Personnage mystere :", POLICE_MINI, GRIS, LARGEUR // 2, 345)
    texte_centre(ecran, etat["mystere"]["name"], POLICE_MOY, BLANC, LARGEUR // 2, 373)
    liens = etat["mystere"].get("liens", etat["mystere"].get("links", []))
    for rang, debut in enumerate([0, 3]):
        batch = liens[debut : debut + 3]
        if batch:
            ligne = "  |  ".join(
                (l.get("type") or l.get("type_lien", "?")).capitalize()
                + " : "
                + str(l.get("result") or l.get("valeur", "?"))
                for l in batch
            )
            texte_centre(ecran, ligne, POLICE_MINI, GRIS, LARGEUR // 2, 400 + rang * 18)
    texte_centre(
        ecran,
        "Questions posees : " + str(etat["nb_questions"]),
        POLICE_PETIT,
        GRIS,
        LARGEUR // 2,
        458,
    )
    dessiner_bouton(ecran, etat["bouton_rejouer"])
    dessiner_bouton(ecran, etat["bouton_menu"])


# Antoine
def main():
    ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
    pygame.display.set_caption("Qui est impliqué ?")
    horloge = pygame.time.Clock()
    fond = creer_fond()
    personnes = charger_donnees()

    etat = {
        "etat": ETAT_ERREUR if personnes is None else ETAT_MENU,
        "personnes": personnes or [],
        "cartes": [],
        "mystere": None,
        "boutons_qt": [],
        "boutons_qv": [],
        "qt_selec": None,
        "nb_questions": 0,
        "dernier_res": None,
        "scroll_qt": 0,
        "bouton_jouer": creer_bouton(
            LARGEUR // 2 - 130, 410, 260, 58, "JOUER", (40, 110, 65), POLICE_GRAND
        ),
        "bouton_rejouer": creer_bouton(
            LARGEUR // 2 - 140, 530, 280, 52, "Rejouer", (40, 90, 160), POLICE_MOY
        ),
        "bouton_menu": creer_bouton(
            LARGEUR // 2 - 140, 595, 280, 52, "Menu principal", (50, 55, 80), POLICE_MOY
        ),
    }

    en_cours = True
    while en_cours:
        souris = pygame.mouse.get_pos()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                en_cours = False

            elif etat["etat"] == ETAT_ERREUR:
                if ev.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                    en_cours = False

            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE and etat["etat"] == ETAT_VALEUR:
                    etat["etat"] = ETAT_JEU

            elif ev.type == pygame.MOUSEWHEEL and etat["etat"] == ETAT_JEU:
                scroll_event(etat, -ev.y)

            elif ev.type == pygame.MOUSEBUTTONDOWN:
                pos = ev.pos

                if ev.button == 4 and etat["etat"] == ETAT_JEU:
                    scroll_event(etat, -1)
                elif ev.button == 5 and etat["etat"] == ETAT_JEU:
                    scroll_event(etat, 1)

                elif ev.button == 1:
                    if etat["etat"] == ETAT_MENU:
                        if bouton_clique(etat["bouton_jouer"], pos):
                            lancer_partie(etat)

                    elif etat["etat"] == ETAT_JEU:
                        b = clic_dans_scrollbox(etat, pos)
                        if b:
                            etat["qt_selec"] = b["qt"]
                            construire_boutons_valeurs(etat, b["qt"])
                            etat["etat"] = ETAT_VALEUR
                        else:
                            for c in etat["cartes"]:
                                if carte_cliquee(c, pos):
                                    accuser(etat, c)
                                    break

                    elif etat["etat"] == ETAT_VALEUR:
                        for b in etat["boutons_qv"]:
                            if bouton_clique(b, pos):
                                poser_question(etat, etat["qt_selec"], b["valeur"])
                                break

                    elif etat["etat"] in (ETAT_GAGNE, ETAT_PERDU):
                        if bouton_clique(etat["bouton_rejouer"], pos):
                            lancer_partie(etat)
                        elif bouton_clique(etat["bouton_menu"], pos):
                            etat["etat"] = ETAT_MENU

        if etat["etat"] == ETAT_MENU:
            maj_bouton(etat["bouton_jouer"], souris)
        elif etat["etat"] in (ETAT_GAGNE, ETAT_PERDU):
            maj_bouton(etat["bouton_rejouer"], souris)
            maj_bouton(etat["bouton_menu"], souris)
        elif etat["etat"] == ETAT_JEU:
            for c in etat["cartes"]:
                maj_carte(c, souris)
        elif etat["etat"] == ETAT_VALEUR:
            for b in etat["boutons_qv"]:
                maj_bouton(b, souris)

        ecran.blit(fond, (0, 0))
        if etat["etat"] == ETAT_ERREUR:
            dessiner_ecran_erreur(ecran)
        elif etat["etat"] == ETAT_MENU:
            dessiner_menu(ecran, etat)
        elif etat["etat"] in (ETAT_JEU, ETAT_VALEUR):
            dessiner_jeu(ecran, etat, souris)
            if etat["etat"] == ETAT_VALEUR:
                dessiner_overlay_valeurs(ecran, etat)
        elif etat["etat"] == ETAT_GAGNE:
            dessiner_fin(ecran, etat, True)
        elif etat["etat"] == ETAT_PERDU:
            dessiner_fin(ecran, etat, False)

        pygame.display.flip()
        horloge.tick(FPS)

    pygame.quit()
    sys.exit()


main()
