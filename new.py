import json
import math
import os
import random
import sys

import pygame

# --- CONFIGURATION ---

LARGEUR, HAUTEUR = 1400, 900
FPS = 60

# Polices
pygame.font.init()
POLICE_TITRE = pygame.font.SysFont("agencyfb", 60)
POLICE_TXT = pygame.font.SysFont("arial", 26)
POLICE_PETIT = pygame.font.SysFont("arial", 18)

# Couleurs: Thème Sombre/Sobre
NOIR = (10, 10, 15)
GRIS_FONCE = (30, 30, 35)
ARGENT = (195, 200, 205)
ARGENT_FONCE = (100, 105, 110)
BLEU_BUTTON = (70, 130, 180)
OR = (255, 215, 0)
ROUGE_ALERT = (220, 60, 60)
VERT_SUCCESS = (50, 200, 100)

# Constantes Cartes
CARTE_W, CARTE_H = 110, 150
MARGE_X, MARGE_Y = 20, 25
COLS = 7

# États : 0:Menu, 1:Intro, 2:Jeu, 3:Valeurs, 4:Fin
ETATS = ["MENU", "INTRO", "JEU", "VALEURS", "FIN"]


def charger_donnees():
    try:
        with open("base.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None


def get_color(name):
    # Couleur unique par nom
    h = abs(hash(name)) % 360
    c = pygame.Color(0)
    c.hsla = (h, 70, 50, 100)
    return (c.r, c.g, c.b)


def get_age_label(age):
    try:
        a = int(age)
    except:
        return str(age)
    for lo, hi, label in [
        (0, 4, "0-4"),
        (5, 9, "5-9"),
        (10, 14, "10-14"),
        (15, 19, "15-19"),
        (20, 24, "20-24"),
        (25, 29, "25-29"),
        (30, 34, "30-34"),
        (35, 39, "35-39"),
        (40, 44, "40-44"),
        (45, 49, "45-49"),
        (50, 54, "50-54"),
        (55, 59, "55-59"),
        (60, 64, "60-64"),
        (65, 69, "65-69"),
        (70, 74, "70-74"),
        (75, 79, "75-79"),
        (80, 84, "80-84"),
        (85, 89, "85-89"),
        (90, 120, "90+"),
    ]:
        if lo <= a <= hi:
            return label
    return str(age)


def get_val(p, t):
    for l in p.get("liens", []):
        if l.get("type") == t or l.get("type_lien") == t:
            return l.get("result") or l.get("valeur")
    return None


def draw_card(surf, card):
    x, y = card["x"], card["y"]

    # Carte éliminée
    if not card["visible"]:
        r = pygame.Rect(x, y, CARTE_W, CARTE_H)
        pygame.draw.rect(surf, (50, 20, 20), r, border_radius=8)
        pygame.draw.rect(surf, ROUGE_ALERT, r, 2, border_radius=8)
        pygame.draw.line(
            surf, ROUGE_ALERT, (x + 10, y + 10), (x + CARTE_W - 10, y + CARTE_H - 10), 4
        )
        pygame.draw.line(
            surf, ROUGE_ALERT, (x + CARTE_W - 10, y + 10), (x + 10, y + CARTE_H - 10), 4
        )
        return

    # Animation de retournement
    if card["flip"] > 0:
        card["flip"] += 0.08
        if card["flip"] >= 1.0:
            card["flip"] = -1  # Done
        else:
            w = int(CARTE_W * abs(math.cos(card["flip"] * math.pi)))
            ox = x + (CARTE_W - w) // 2
            pygame.draw.rect(surf, GRIS_FONCE, (ox, y, w, CARTE_H), border_radius=8)
            return

    # Carte Normale
    r = pygame.Rect(x, y, CARTE_W, CARTE_H)
    sur = r.collidepoint(pygame.mouse.get_pos())
    pygame.draw.rect(surf, GRIS_FONCE, r, border_radius=8)
    pygame.draw.rect(
        surf, ARGENT if sur else ARGENT_FONCE, r, 2 if sur else 1, border_radius=8
    )

    # Zone photo
    py = y + 8
    ph = CARTE_H // 2
    pygame.draw.rect(
        surf,
        get_color(card["p"]["name"]),
        (x + 6, py, CARTE_W - 12, ph),
        border_radius=5,
    )

    # Initiales
    ini = "".join(w[0].upper() for w in card["p"]["name"].split()[:2])
    ti = POLICE_TITRE.render(ini, True, (255, 255, 255))
    surf.blit(ti, ti.get_rect(center=(x + CARTE_W // 2, py + ph // 2)))

    # Nom (Multi-ligne)
    ny = y + ph + 20
    words = card["p"]["name"].split()
    line = words[0] if words else ""
    for w in words[1:]:
        if POLICE_PETIT.size(line + " " + w)[0] <= CARTE_W - 15:
            line += " " + w
        else:
            ts = POLICE_PETIT.render(line, True, ARGENT)
            surf.blit(ts, ts.get_rect(center=(x + CARTE_W // 2, ny)))
            ny += 18
            line = w
    if line:
        ts = POLICE_PETIT.render(line, True, ARGENT)
        surf.blit(ts, ts.get_rect(center=(x + CARTE_W // 2, ny)))


# Variables Globales
personnes = None
cartes = []
mystere = None
questions_list = []
btn_questions = []
resultat_dernier = None
etat_jeu_idx = 0  # 0:MENU, 1:INTRO, 2:JEU, 3:VALEURS, 4:FIN
nb_questions = 0
q_select = None
valeurs_possible = []
scroll_offset = 0


def init_partie():
    global cartes, mystere, questions_list, btn_questions, scroll_offset
    # Selection aléatoire
    selection = random.sample(personnes, min(32, len(personnes)))
    mystere = random.choice(selection)

    # Centrer la grille
    total_w = COLS * (CARTE_W + MARGE_X) - MARGE_X
    start_x = (LARGEUR - total_w) // 2
    start_y = 100

    cartes = []
    for i, p in enumerate(selection):
        col, row = i % COLS, i // COLS
        x = start_x + col * (CARTE_W + MARGE_X)
        y = start_y + row * (CARTE_H + MARGE_Y)
        cartes.append({"p": p, "x": x, "y": y, "visible": True, "flip": 0.0})

    # Setup Questions
    vus = set()
    questions_list = []
    for p in personnes:
        for l in p.get("liens", []):
            t = l.get("type") or l.get("type_lien")
            if t and t not in vus:
                vus.add(t)
                questions_list.append(t)

    bx, by = 1080, 120
    btn_questions = []
    for i, q in enumerate(questions_list):
        btn_questions.append(
            {
                "rect": pygame.Rect(bx, by + i * 55, 280, 50),
                "text": q.replace("_", " ").title(),
                "data": q,
                "hover": False,
            }
        )

    scroll_offset = 0
    nb_questions = 0


# --- BOUCLE PRINCIPALE ---


def main():
    global \
        personnes, \
        etat_jeu_idx, \
        btn_questions, \
        scroll_offset, \
        valeurs_possible, \
        q_select, \
        resultat_dernier, \
        nb_questions
    global cartes, mystere

    # Init Pygame
    pygame.init()
    ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
    pygame.display.set_caption("L'Affaire - Edition Sombre")
    horloge = pygame.time.Clock()

    # Charger Données
    personnes = charger_donnees()
    if not personnes:
        print("Erreur: base.json introuvable.")
        return

    # Background Menu
    bg_menu = None
    try:
        bg_menu = pygame.image.load("images/fond_menu.jpg").convert()
        bg_menu = pygame.transform.scale(bg_menu, (LARGEUR, HAUTEUR))
    except:
        # Dégradé par défaut
        bg_menu = pygame.Surface((LARGEUR, HAUTEUR))
        for y in range(HAUTEUR):
            t = y / HAUTEUR
            c = (int(10 + 10 * t), int(10 + 5 * t), int(15 + 10 * t))
            pygame.draw.line(bg_menu, c, (0, y), (LARGEUR, y))

    while True:
        souris = pygame.mouse.get_pos()

        # --- ÉVÉNEMENTS ---
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Molette scroll question
            if etat_jeu_idx == 2 and ev.type == pygame.MOUSEWHEEL:
                scroll_offset -= ev.y * 40
                total_h = len(btn_questions) * 55
                max_s = max(0, total_h - 650)
                scroll_offset = max(0, min(scroll_offset, max_s))

            # --- STATE: MENU ---
            if etat_jeu_idx == 0 and ev.type == pygame.MOUSEBUTTONDOWN:
                r = pygame.Rect(600, 550, 200, 60)
                if r.collidepoint(souris):
                    etat_jeu_idx = 1  # Intro

            # --- STATE: INTRO ---
            elif etat_jeu_idx == 1 and ev.type == pygame.MOUSEBUTTONDOWN:
                r = pygame.Rect(600, 600, 200, 50)
                if r.collidepoint(souris):
                    init_partie()
                    etat_jeu_idx = 2  # Game

            # --- STATE: JEU ---
            elif etat_jeu_idx == 2:
                if ev.type == pygame.MOUSEBUTTONDOWN:
                    # 1. Cartes
                    for c in cartes:
                        if c["visible"]:
                            r = pygame.Rect(c["x"], c["y"], CARTE_W, CARTE_H)
                            if r.collidepoint(souris):
                                if c["p"]["name"] == mystere["name"]:
                                    etat_jeu_idx = 4  # Win
                                else:
                                    c["visible"] = False
                                    c["flip"] = 0.0
                                    nb_questions += 1
                                    # Test Lose
                                    if not any(x["visible"] for x in cartes):
                                        etat_jeu_idx = 4  # Lose
                    # 2. Questions
                    y_off = 120 - scroll_offset
                    for b in btn_questions:
                        real_y = y_off + btn_questions.index(b) * 55
                        r = pygame.Rect(b["rect"].x, real_y, b["rect"].w, b["rect"].h)
                        if r.collidepoint(souris):
                            q_select = b["data"]
                            # Calcul Valeurs
                            vals = set()
                            for p in personnes:
                                v = get_val(p, q_select)
                                if v is not None:
                                    vals.add(
                                        get_age_label(v)
                                        if q_select == "age"
                                        else str(v)
                                    )
                            valeurs_possible = sorted(
                                list(vals),
                                key=lambda x: (
                                    (
                                        int(x.split("+")[0])
                                        if "+" in x
                                        else int(x.split("-")[0])
                                    )
                                    if q_select == "age"
                                    else x
                                ),
                            )
                            etat_jeu_idx = 3  # Select Values

                # Accusation via clic (Optionnel: si on clique sur une carte non visible)
                # (Code géré ci-dessus)

            # --- STATE: VALEURS ---
            elif etat_jeu_idx == 3:
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                    etat_jeu_idx = 2
                elif ev.type == pygame.MOUSEBUTTONDOWN:
                    bx, by = 380, 250
                    bl, bh, gap = 140, 40, 15
                    cols = 4
                    for i, val in enumerate(valeurs_possible):
                        col, row = i % cols, i // cols
                        r = pygame.Rect(
                            bx + col * (bl + gap), by + row * (bh + gap), bl, bh
                        )
                        if r.collidepoint(souris):
                            # Logique
                            target = get_val(mystere, q_select)
                            target_str = (
                                get_age_label(target)
                                if q_select == "age"
                                else str(target)
                            )
                            elim = 0
                            for c in cartes:
                                if c["visible"]:
                                    val_c = get_val(c["p"], q_select)
                                    val_str = (
                                        get_age_label(val_c)
                                        if q_select == "age"
                                        else str(val_c)
                                        if val_c
                                        else ""
                                    )
                                    if val_str != target_str:
                                        c["visible"] = False
                                        c["flip"] = 0.0
                                        elim += 1
                            nb_questions += 1
                            resultat_dernier = (
                                q_select.replace("_", " ").title(),
                                str(target_str),
                                elim,
                            )
                            etat_jeu_idx = 2
                            # Test Win
                            restants = [c for c in cartes if c["visible"]]
                            if (
                                len(restants) == 1
                                and restants[0]["p"]["name"] == mystere["name"]
                            ):
                                etat_jeu_idx = 4
                            break

            # --- STATE: FIN ---
            elif etat_jeu_idx == 4:
                if ev.type == pygame.MOUSEBUTTONDOWN:
                    # Back Menu
                    if pygame.Rect(350, 650, 180, 50).collidepoint(souris):
                        etat_jeu_idx = 0
                    # Replay
                    elif pygame.Rect(800, 650, 180, 50).collidepoint(souris):
                        etat_jeu_idx = 1

        # --- RENDU ---

        if etat_jeu_idx == 0:  # MENU
            ecran.blit(bg_menu, (0, 0))
            titre = POLICE_TITRE.render("L'AFFAIRE", True, ARGENT)
            ecran.blit(titre, titre.get_rect(center=(LARGEUR // 2, 250)))
            t2 = POLICE_TXT.render(
                "Trouvez le mystère parmi les indices.", True, (180, 180, 180)
            )
            ecran.blit(t2, t2.get_rect(center=(LARGEUR // 2, 350)))

            btn_rect = pygame.Rect(600, 550, 200, 60)
            col = BLEU_BUTTON if btn_rect.collidepoint(souris) else (80, 80, 90)
            pygame.draw.rect(ecran, col, btn_rect, border_radius=10)
            pygame.draw.rect(ecran, ARGENT, btn_rect, 2, border_radius=10)
            ecran.blit(POLICE_TXT.render("JOUER", True, ARGENT), btn_rect.move(60, 15))

            info = POLICE_PETIT.render(
                f"{len(personnes)} dossiers disponibles", True, (120, 120, 120)
            )
            ecran.blit(info, (20, HAUTEUR - 30))

        elif etat_jeu_idx == 1:  # INTRO
            ecran.blit(bg_menu, (0, 0))
            titre = POLICE_TITRE.render("DÉBUT DE L'ENQUÊTE", True, ARGENT)
            ecran.blit(titre, titre.get_rect(center=(LARGEUR // 2, 250)))
            t2 = POLICE_TXT.render(
                "Cliquez sur les cartes pour éliminer les suspects.", True, ARGENT_FONCE
            )
            ecran.blit(t2, t2.get_rect(center=(LARGEUR // 2, 350)))

            btn_rect = pygame.Rect(600, 600, 200, 50)
            col = BLEU_BUTTON if btn_rect.collidepoint(souris) else (80, 80, 90)
            pygame.draw.rect(ecran, col, btn_rect, border_radius=10)
            pygame.draw.rect(ecran, ARGENT, btn_rect, 2, border_radius=10)
            ecran.blit(
                POLICE_TXT.render("COMMENCER", True, ARGENT), btn_rect.move(35, 12)
            )

        elif etat_jeu_idx == 2:  # JEU
            ecran.fill(NOIR)
            pygame.draw.rect(ecran, ARGENT, (5, 5, LARGEUR - 10, HAUTEUR - 10), 2)

            # Cartes
            for c in cartes:
                draw_card(ecran, c)

            # Panneau Questions
            px, py, pw, ph = 1070, 40, 300, HAUTEUR - 80
            pygame.draw.rect(ecran, GRIS_FONCE, (px, py, pw, ph), border_radius=10)
            pygame.draw.rect(ecran, ARGENT_FONCE, (px, py, pw, ph), 2, border_radius=10)

            ecran.blit(
                POLICE_TXT.render("POSER UNE QUESTION", True, OR), (px + 10, py + 20)
            )

            # Dessiner Questions avec Scroll
            y_cursor = 80 - scroll_offset
            for b in btn_questions:
                b["rect"].y = y_cursor
                sur = b["rect"].collidepoint(souris)
                col = (
                    (BLEU_BUTTON[0] + 20, BLEU_BUTTON[1] + 20, BLEU_BUTTON[2] + 20)
                    if sur
                    else (60, 60, 70)
                )
                pygame.draw.rect(ecran, col, b["rect"], border_radius=5)
                pygame.draw.rect(
                    ecran,
                    ARGENT if sur else ARGENT_FONCE,
                    b["rect"],
                    1,
                    border_radius=5,
                )
                ecran.blit(
                    POLICE_PETIT.render(b["text"], True, ARGENT),
                    (b["rect"].x + 15, b["rect"].y + 14),
                )
                y_cursor += 55

            # Résultat dernier
            if resultat_dernier:
                lbl, rep, elim = resultat_dernier
                t = POLICE_PETIT.render(
                    f"{lbl}: {rep} ({elim} susp. élim.)", True, VERT_SUCCESS
                )
                ecran.blit(t, (px + 10, HAUTEUR - 80))

        elif etat_jeu_idx == 3:  # OVERLAY VALEURS
            dim = pygame.Surface((LARGEUR, HAUTEUR))
            dim.fill((0, 0, 0, 200))
            ecran.blit(dim, (0, 0))

            bx, by, bw, bh = 300, 150, 800, 600
            pygame.draw.rect(ecran, (25, 25, 30), (bx, by, bw, bh), border_radius=15)
            pygame.draw.rect(ecran, OR, (bx, by, bw, bh), 3, border_radius=15)

            q_title = q_select.replace("_", " ").upper()
            ecran.blit(
                POLICE_TITRE.render(f"Question: {q_title}", True, ARGENT),
                (bx + 30, by + 40),
            )

            # Grille Valeurs
            bx_btn, by_btn = bx + 100, by + 120
            bl, bh_btn, gap = 150, 45, 20
            cols = 4
            for i, val in enumerate(valeurs_possible):
                col, row = i % cols, i // cols
                r = pygame.Rect(
                    bx_btn + col * (bl + gap), by_btn + row * (bh_btn + gap), bl, bh_btn
                )
                sur = r.collidepoint(souris)
                col_bg = BLEU_BUTTON if sur else (70, 70, 80)
                pygame.draw.rect(ecran, col_bg, r, border_radius=8)
                pygame.draw.rect(ecran, ARGENT, r, 2, border_radius=8)
                ecran.blit(POLICE_TXT.render(str(val), True, ARGENT), r.move(40, 12))

            ecran.blit(
                POLICE_PETIT.render("[ÉCHAP] Retour", True, (100, 100, 100)),
                (bx + bw // 2 - 60, by + bh - 40),
            )

        elif etat_jeu_idx == 4:  # FIN
            ecran.fill(NOIR)
            win = False
            reste = [c for c in cartes if c["visible"]]
            if len(reste) == 1 and reste[0]["p"]["name"] == mystere["name"]:
                win = True

            box_c = pygame.Rect(300, 200, 800, 550)
            pygame.draw.rect(ecran, (20, 20, 25), box_c, border_radius=20)
            col_f = VERT_SUCCESS if win else ROUGE_ALERT
            pygame.draw.rect(ecran, col_f, box_c, 4, border_radius=20)

            msg = "CERCLE FERMÉ - GAGNÉ" if win else "PERDU"
            ecran.blit(
                POLICE_TITRE.render(msg, True, col_f),
                (box_c.centerx - POLICE_TITRE.size(msg)[0] // 2, 240),
            )

            # Afficher le mystère
            mc = next((c for c in cartes if c["p"]["name"] == mystere["name"]), None)
            if mc:
                # Dessiner la carte mystère
                draw_card(ecran, mc)
                # Centrer manuellement
                mc_rect = pygame.Rect(mc["x"], mc["y"], CARTE_W, CARTE_H)
                mc_rect.center = (box_c.centerx, 400)
                # On redessine pour le centrer
                tmp_x, tmp_y = mc["x"], mc["y"]
                mc["x"], mc["y"] = mc_rect.x, mc_rect.y
                draw_card(ecran, mc)
                mc["x"], mc["y"] = tmp_x, tmp_y

            ecran.blit(
                POLICE_TXT.render(f"C'était : {mystere['name']}", True, ARGENT),
                (
                    box_c.centerx
                    - POLICE_TXT.size(f"C'était : {mystere['name']}")[0] // 2,
                    520,
                ),
            )
            ecran.blit(
                POLICE_TXT.render(
                    f"Questions posées : {nb_questions}", True, ARGENT_FONCE
                ),
                (
                    box_c.centerx
                    - POLICE_TXT.size(f"Questions posées : {nb_questions}")[0] // 2,
                    560,
                ),
            )

            # Boutons
            b1 = pygame.Rect(350, 650, 180, 50)
            b2 = pygame.Rect(800, 650, 180, 50)
            for b in [b1, b2]:
                pygame.draw.rect(
                    ecran,
                    BLEU_BUTTON if b.collidepoint(souris) else (60, 60, 70),
                    b,
                    border_radius=8,
                )
                pygame.draw.rect(ecran, ARGENT, b, 2, border_radius=8)

            ecran.blit(POLICE_TXT.render("MENU", True, ARGENT), b1.move(50, 12))
            ecran.blit(POLICE_TXT.render("REJOUER", True, ARGENT), b2.move(40, 12))

        pygame.display.flip()
        horloge.tick(FPS)


if __name__ == "__main__":
    main()
