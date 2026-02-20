import pygame
from sys import exit
import random

pygame.init()

# resolution 
screen = pygame.display.set_mode((1000, 600)) 

# title 
pygame.display.set_caption("UNO")
try:
    img = pygame.image.load('icons8-uno-100.png')
    pygame.display.set_icon(img)
except: pass

Clock = pygame.time.Clock()
try:
    font = pygame.font.Font('UnoAssets/font/Pixeltype.ttf' , 50)
except:
    font = pygame.font.Font(None, 50)

font_surface = font.render('Uno Game' , False , 'White')

CARD_IMAGES = {}
PLAYER_BG_COLOURS = [(30, 40, 60), (40, 50, 30)]

def load_and_scale(path, size=(100, 150)):
    img = pygame.image.load(path).convert_alpha()
    return pygame.transform.scale(img, size)

def cards_img():
    colours = ["Red", "Blue", "Yellow", "Green"]
    colour_bases = {
        "Red": load_and_scale("UnoAssets/Assets/red_base.png"),
        "Blue": load_and_scale("UnoAssets/Assets/blue_base.png"),
        "Green": load_and_scale("UnoAssets/Assets/green_base.png"),
        "Yellow": load_and_scale("UnoAssets/Assets/yellow_base.png")
    }
    for colour_name, card_base in colour_bases.items():
        for i in range(10):
            overlay = load_and_scale(f"UnoAssets/Assets/_{i}.png")
            combined = card_base.copy()
            combined.blit(overlay, (0, 0))
            CARD_IMAGES[f"{colour_name} {i}"] = combined
        actions = {"draw_two": "_draw2.png", "skip": "_interdit.png", "reverse": "_revers.png"}
        for action_name, file in actions.items():
            overlay = load_and_scale(f"UnoAssets/Assets/{file}")
            combined = card_base.copy()
            combined.blit(overlay, (0, 0))
            CARD_IMAGES[f"{colour_name} {action_name}"] = combined
    CARD_IMAGES["wild"] = load_and_scale("UnoAssets/Assets/_wild.png")
    CARD_IMAGES["wild_draw_four"] = load_and_scale("UnoAssets/Assets/_wild_draw.png")
    CARD_IMAGES["back"] = load_and_scale("UnoAssets/Assets/back.png")

def build_deck():
    colours = ["Red", "Blue", "Yellow", "Green"]
    values = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, "draw_two", "skip", "reverse"]
    wilds = ["wild", "wild_draw_four"]
    deck = []
    for colour in colours:
        for value in values:
            card = f"{colour} {value}"
            deck.append(card)
            if value != 0: deck.append(card)
    for _ in range(4):
        deck.append(wilds[0])
        deck.append(wilds[1])
    random.shuffle(deck)
    return deck 

def give_cards(deck, num):
    cards_drawn = []
    for i in range(num):
        if deck: cards_drawn.append(deck.pop(0))
    return cards_drawn

# idk what this is chat gpt wrote this 
def can_play(card, top):
    if "wild" in card: 
        return True
    c_split = card.split()
    t_split = top.split()
    if c_split[0] == t_split[0]: 
        return True
    if len(c_split) > 1 and len(t_split) > 1 and c_split[1] == t_split[1]: 
        return True
    return False

cards_img()
uno_deck = build_deck()
players = [give_cards(uno_deck, 7), give_cards(uno_deck, 7)]
current_turn, current_direction = 0, 1
deck_top = uno_deck.pop(0)
playing = True
choosing_colour = False
wild_type_played = ""

# ik yaha se
while True:
    if playing: 
        screen.fill(PLAYER_BG_COLOURS[current_turn])
    else: 
        screen.fill((20, 20, 20))

    mouse_pos, clicked = pygame.mouse.get_pos(), False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); exit()
        if event.type == pygame.MOUSEBUTTONDOWN: 
            clicked = True

    if playing:
        if len(uno_deck) < 10: 
            uno_deck.extend(build_deck())

        if deck_top in CARD_IMAGES: 
            display_top = deck_top
        elif "wild_draw_four" in deck_top: 
            display_top = "wild_draw_four"
        elif "wild" in deck_top: 
            display_top = "wild"
        else: 
            display_top = "back"
        screen.blit(CARD_IMAGES[display_top], (450, 200))

        if "wild" in deck_top:
            top_colour = deck_top.split()[0]
            pygame.draw.circle(screen, top_colour, (500, 370), 20)

        # Draw Deck
        deck_rect = pygame.Rect(300, 200, 100, 150)
        screen.blit(CARD_IMAGES.get("back"), (300, 200))
        
        if not choosing_colour and clicked and deck_rect.collidepoint(mouse_pos):
            new_card = give_cards(uno_deck, 1)
            if new_card:
                players[current_turn].append(new_card[0])
                current_turn = (current_turn + current_direction) % len(players)

        # Draw Player Hand
        player_hand = players[current_turn]
        card_played_idx = -1
        num_cards = len(player_hand)
        start_x, max_width = 50, 800
        spacing = min(90, max_width // num_cards) if num_cards > 0 else 90

        if not choosing_colour:
            for i, card in enumerate(player_hand):
                x, y = start_x + (i * spacing), 420
                card_rect = pygame.Rect(x, y, 100, 150)
                draw_y = y - 30 if card_rect.collidepoint(mouse_pos) else y
                
                if card in CARD_IMAGES: 
                    img_key = card
                elif "wild_draw_four" in card: 
                    img_key = "wild_draw_four"
                elif "wild" in card: 
                    img_key = "wild"
                else: 
                    img_key = "back"
                
                screen.blit(CARD_IMAGES[img_key], (x, draw_y))
                
                if clicked and card_rect.collidepoint(mouse_pos):
                    if can_play(card, deck_top):
                        card_to_play, card_played_idx = card, i 
                        if "wild" in card_to_play:
                            choosing_colour = True
                            wild_type_played = card_to_play
                        else:
                            deck_top = card_to_play
                            player_hand.pop(card_played_idx)
                            
                            if len(player_hand) == 0:
                                playing = False
                                break

                            next_p = (current_turn + current_direction) % len(players)
                            if "draw_two" in card_to_play:
                                players[next_p].extend(give_cards(uno_deck, 2))
                                current_turn = (next_p + current_direction) % len(players) 
                            elif "skip" in card_to_play:
                                current_turn = (next_p + current_direction) % len(players)
                            elif "reverse" in card_to_play:
                                if len(players) == 2:
                                    current_turn = (next_p + current_direction) % len(players)
                                else:
                                    current_direction *= -1
                                    current_turn = (current_turn + current_direction) % len(players)
                            else:
                                current_turn = (current_turn + current_direction) % len(players)
                        
                        card_played_idx = -1 
                        break 

        if choosing_colour:
            overlay = pygame.Surface((1000, 600), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0,0))
            colours_list = [("Red", (255,0,0)), ("Blue", (0,0,255)), ("Green", (0,255,0)), ("Yellow", (255,255,0))]
            for idx, (name, colour_val) in enumerate(colours_list):
                rect = pygame.Rect(280 + (idx * 115), 250, 100, 100)
                pygame.draw.rect(screen, colour_val, rect)
                if clicked and rect.collidepoint(mouse_pos):
                    deck_top = f"{name} {wild_type_played}"
                    choosing_colour = False
                    player_hand.pop(card_played_idx)
                    card_played_idx = -1
                    
                    if len(player_hand) == 0:
                        playing = False
                    else:
                        next_p = (current_turn + current_direction) % len(players)
                        if "wild_draw_four" in wild_type_played:
                            players[next_p].extend(give_cards(uno_deck, 4))
                            current_turn = (next_p + current_direction) % len(players)
                        else:
                            current_turn = (current_turn + current_direction) % len(players)

        screen.blit(font.render(f"Player {current_turn + 1}'s Turn", True, "White"), (400, 20))
    else:
        screen.blit(font.render(f"PLAYER {current_turn + 1} WINS!", True, "Green"), (400, 300))
        if pygame.key.get_pressed()[pygame.K_r]:
            uno_deck = build_deck()
            players = [give_cards(uno_deck, 7), give_cards(uno_deck, 7)]
            current_turn, playing = 0, True
            deck_top = uno_deck.pop(0)

    pygame.display.update()
    Clock.tick(60)