import random
from colorama import Fore, Back, Style, init

class Card:
    color_map = {
        'Red': Back.RED,
        'Green': Back.GREEN,
        'Blue': Back.BLUE,
        'Yellow': Back.YELLOW,
        None: Back.WHITE  # For Wild cards
    }

    @property
    def display(self):
        color_bg = self.color_map.get(self.color, Back.RESET)
        return f"{color_bg}{Fore.BLACK} {self.color} {self.value} {Style.RESET_ALL}"

    def __init__(self, color, value):
        self.color = color
        self.value = value

    def __repr__(self):
        return f"{self.color} {self.value}"

class NumberCard(Card):
    def __init__(self, color, number):
        super().__init__(color, number)

class SpecialCard(Card):
    def __init__(self, color, special_type):
        super().__init__(color, special_type)

class WildCard(Card):
    def __init__(self, wild_type):
        super().__init__(None, wild_type)

def initialize_deck():
    colors = ['Red', 'Green', 'Blue', 'Yellow']
    special_types = ['Skip', 'Reverse', 'Draw 2']
    wild_types = ['Wild', 'Wild Draw 4']

    deck = []

    # Add number cards
    for color in colors:
        deck.append(NumberCard(color, 0))  # One 0 card for each color
        for number in range(1, 10):
            deck.extend([NumberCard(color, number), NumberCard(color, number)])  # Two of each number card

    # Add special cards
    for color in colors:
        for special in special_types:
            deck.extend([SpecialCard(color, special), SpecialCard(color, special)])  # Two of each special card

    # Add wild cards
    for wild in wild_types:
        deck.extend([WildCard(wild) for _ in range(4)])  # Four of each wild card

    random.shuffle(deck)
    return deck

class UnoGame:
    def __init__(self):
        # Initialize colorama
        init(autoreset=True)

        self.draw_deck = initialize_deck()
        self.discard_pile = []
        self.players = []
        self.current_player = 0
        self.direction = 1  # 1 for clockwise, -1 for counterclockwise

    def draw_card(self):
        if not self.draw_deck:
            self.reshuffle_discard_pile()
        return self.draw_deck.pop()

    def reshuffle_discard_pile(self):
        if len(self.discard_pile) <= 1:
            raise RuntimeError("No cards left to reshuffle!")
        top_card = self.discard_pile[-1]
        to_reshuffle = self.discard_pile[:-1]
        random.shuffle(to_reshuffle)
        self.draw_deck = to_reshuffle
        self.discard_pile = [top_card]

    def setup_game(self, num_players):
        self.players = [[] for _ in range(num_players)]
        for _ in range(3):
            for player in self.players:
                player.append(self.draw_card())
        self.discard_pile.append(self.draw_card())

    def show_hands(self):
        for idx, player in enumerate(self.players):
            hand_display = ", ".join(card.display for card in player)
            print(f"Player {idx + 1}'s hand: {hand_display}")

    def show_draw_deck(self):
        for card in enumerate(self.draw_deck):
            print(f"{card}")

    def apply_special_effects(self, card):
        if isinstance(card, SpecialCard):
            if card.value == 'Reverse':
                self.direction *= -1
            elif card.value == 'Skip':
                self.next_player()
            elif card.value == 'Draw 2':
                self.handle_draw_effect(2)
        elif isinstance(card, WildCard):
            if card.value == 'Wild':
                self.choose_new_color(card)
            elif card.value == 'Wild Draw 4':
                top_card = self.discard_pile[-2]  # Get the second to last card, which is the card before the Wild Draw 4
                if isinstance(top_card, SpecialCard) and top_card.value == 'Draw 2':
                    card.color = top_card.color
                else:
                    self.choose_new_color(card)
                self.handle_draw_effect(4)

    def choose_new_color(self, card):
        colors = ['Red', 'Green', 'Blue', 'Yellow']
        print("Choose a new color:")
        for i, color in enumerate(colors):
            print(f"{i}: {color}")

        while True:
            try:
                color_choice = int(input("Enter the number corresponding to your color choice: "))
                if 0 <= color_choice < len(colors):
                    chosen_color = colors[color_choice]
                    print(f"You chose: {chosen_color}")
                    card.color = chosen_color
                    break
                else:
                    print(f"Invalid choice. Please enter a number between 0 and {len(colors) - 1}.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    def handle_draw_effect(self, draw_count):
        self.next_player()
        next_player_hand = self.players[self.current_player]

        # Check if the next player has a counter card
        has_counter_card = any(
            (card.value == 'Draw 2' and draw_count == 2) or
            (card.value == 'Wild Draw 4' and draw_count == 4)
            for card in next_player_hand
        )

        if has_counter_card:
            print(f"Player {self.current_player + 1} has a counter card. They can play it or draw {draw_count} cards.")
        else:
            for _ in range(draw_count):
                drawn_card = self.draw_card()
                next_player_hand.append(drawn_card)
                print(f"Player {self.current_player + 1} draws: {drawn_card.display}")
            # Skip their turn
            self.next_player()
            
    def next_player(self):
        self.current_player = (self.current_player + self.direction) % len(self.players)

    def start_game(self, num_players):
        self.players = [[] for _ in range(num_players)]
        for _ in range(3):
            for player in self.players:
                player.append(self.draw_card())
        self.discard_pile.append(self.draw_card())

    def play_turn(self):
        player = self.players[self.current_player]
        top_card = self.discard_pile[-1]
        print(f"Top card: {top_card.display}")

        while True:
            hand_display = ", ".join(card.display for card in player)
            print(f"Player {self.current_player + 1}'s turn. Your hand: {hand_display}")

            try:
                card_choice = int(input(f"Choose a card to play (0-{len(player)-1}) or -1 to draw: "))
                if card_choice == -1:
                    new_card = self.draw_card()
                    player.append(new_card)
                    print(f"You drew: {new_card.display}")
                elif 0 <= card_choice < len(player):
                    chosen_card = player[card_choice]
                    if self.is_valid_play(chosen_card, top_card):
                        self.discard_pile.append(player.pop(card_choice))
                        print(f"You played: {chosen_card.display}")
                        self.apply_special_effects(chosen_card)
                        break
                    else:
                        print("Invalid card. You must play a valid card or draw a card.")
                else:
                    print(f"Invalid input. Please choose a number between 0 and {len(player)-1} or -1 to draw.")
            except ValueError:
                print("Invalid input. Please enter a number.")

        self.next_player()

    def is_valid_play(self, chosen_card, top_card):
        return (chosen_card.color == top_card.color or
                chosen_card.value == top_card.value or
                isinstance(chosen_card, WildCard))

    def play_game(self):
        while True:
            self.play_turn()
            #self.show_hands()
            if any(len(player) == 0 for player in self.players):
                print(f"Player {self.current_player + 1} wins!")
                break


# Example usage
game = UnoGame()

players = 3
game.start_game(players)
game.play_game()
