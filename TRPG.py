#!/usr/bin/env python3

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.columns import Columns
import os
import random
import time
import sys

sys.path.append("Characters")
sys.path.append("Adventures")
sys.path.append("Saves")
try:
    import characters as cha
    import adventures as adv
    import saves as sav
except ModuleNotFoundError:
    print("Couldn't find the necessary functions, closing the game...")
    time.sleep(2)
    sys.exit()


class GameState:
    def __init__(self):
        self.next_encounter = "first_encounter"
        self.game_over = False


class Menu:
    def __init__(self, text, options):
        self.text = text
        self.options = options

    def print_menu(self, console, numbered_choices=False):
        console.print(Panel(self.text, width=64))
        for option in self.options:
            if numbered_choices is True:
                console.print(
                    str(int(option) + 1) + ". " + self.options[option].split(":")[0]
                )
            else:
                console.print("- " + self.options[option].split(":")[0])

    def choice(self, console, numbered_choices=False, menu=False):

        if menu is True:
            self.options["menu"] = "Open the game menu"

        if numbered_choices is True:
            if menu is True:
                console.print("\n What would you like to do? (Choose a number or menu)")
            else:
                console.print("\n What would you like to do? (Choose a number)")

        else:
            joined_options = "("
            for option in self.options:
                joined_options = joined_options + "/" + str(option)
            joined_options = joined_options + ")"
            joined_options = joined_options.replace("(/", "(")
            console.print("\n What would you like to do? " + joined_options)

        choice_received = False
        while choice_received is False:

            choice = console.input(" Your choice: ")
            if numbered_choices is True:
                try:
                    choice = int(choice) - 1
                except ValueError:
                    choice = choice

            if choice in self.options:
                choice_received = True
            else:
                console.print(" That's not a valid choice, try again...")
                time.sleep(1.0)

        if menu is True:
            del self.options["menu"]

        return choice


class Encounter(Menu):
    def __init__(self, name, text, options, results):
        self.name = name
        self.results = results
        Menu.__init__(self, text, options)

    def resolve_encounter(self, game_state, console):
        encounter_resolved = False

        while encounter_resolved is False:
            os.system("clear")
            self.print_menu(console, numbered_choices=True)

            choice = self.choice(console, numbered_choices=True, menu=True)

            if choice != "menu":
                result = self.results[choice]

                if len(result) == 1:
                    game_state.next_encounter = result[0]
                    encounter_resolved = True
                else:
                    enemy = cha.read_character(result[0])

                    battle = Battle(game_state.character, enemy)
                    battle.resolve_battle(game_state, console)
                    game_state.next_encounter = result[1]
                    del self.options[choice]
                    encounter_resolved = True

            elif choice == "menu":
                game_menu(game_state, console)


class Character:
    def __init__(self, name, strength, agility, intelligence, charisma, hp, defense):
        self.name = name
        self.strength = strength
        self.agility = agility
        self.intelligence = intelligence
        self.charisma = charisma
        self.hp = hp
        self.defense = defense

    def attack(self, enemy, battle_log, console, turn):
        if self.hp > 0:
            roll = random.randint(1, 6) + random.randint(1, 6) + self.strength
            if (roll > enemy.defense) & (roll < 12 + self.strength):
                console.print(
                    " "
                    + self.name
                    + "'s attacking roll: "
                    + str(roll)
                    + "[bold green] (success)"
                )
                damage = self.strength
                enemy.hp = enemy.hp - damage
                battle_log.append(
                    "Turn "
                    + str(turn)
                    + ": "
                    + self.name
                    + " attacked "
                    + enemy.name
                    + " for "
                    + str(damage)
                    + " damage.\n"
                )

            elif roll == 12 + self.strength:
                console.print(
                    " "
                    + self.name
                    + "'s attacking roll: "
                    + str(roll)
                    + "[bold yellow] (CRITICAL)"
                )
                damage = self.strength * 2
                enemy.hp = enemy.hp - damage
                battle_log.append(
                    "Turn "
                    + str(turn)
                    + ": "
                    + self.name
                    + " attacked "
                    + enemy.name
                    + " for "
                    + str(damage)
                    + " damage.\n"
                )
            else:
                console.print(
                    " "
                    + self.name
                    + "'s attacking roll: "
                    + str(roll)
                    + "[bold red] (fail)"
                )
                battle_log.append(
                    "Turn "
                    + str(turn)
                    + ": "
                    + self.name
                    + " attacked "
                    + enemy.name
                    + " but couldn't hit. \n"
                )
        else:
            console.print(" " + self.name + " is dead.")


class Battle(Menu):
    def __init__(self, character, enemy):
        self.character = character
        self.enemy = enemy
        self.battle_log = []
        Menu.__init__(self, "", {"attack": "Attack your enemy", "flee": "Try to flee"})

    def make_sheet(self, character):
        sheet = Text()
        sheet.append(Text("- Strength:             " + str(character.strength)))
        sheet.append(Text("\n- Agility:              " + str(character.agility)))
        sheet.append(Text("\n- Intelligence:         " + str(character.intelligence)))
        sheet.append(Text("\n- Charisma:             " + str(character.charisma)))
        sheet.append(Text("\n- HP:                   " + str(character.hp)))
        sheet.append(Text("\n- Defense:              " + str(character.defense)))

        return sheet

    def print_details(self, console):
        character_sheet = self.make_sheet(self.character)
        enemy_sheet = self.make_sheet(self.enemy)

        columns = Columns(
            [
                Panel(character_sheet, title=self.character.name),
                Panel(enemy_sheet, title=self.enemy.name),
            ],
            width=30,
        )

        console.print(Panel(Text("Battle", justify="center"), width=62))
        console.print(columns)
        console.print(
            Panel("".join(self.battle_log[-6:]), title="Battle Log", width=62, height=8)
        )

    def roll_initiative(self):
        draw = True

        while draw is True:
            character_initiative = random.randint(1, 6) + self.character.agility
            enemy_initiative = random.randint(1, 6) + self.enemy.agility

            if character_initiative > enemy_initiative:
                winner = self.character.name
                draw = False
                enemy_won_roll = False
            elif character_initiative < enemy_initiative:
                winner = self.enemy.name
                draw = False
                enemy_won_roll = True

        self.battle_log.append(winner + " takes the initiative... \n")
        return enemy_won_roll

    def resolve_battle(self, game_state, console):
        battle_finished = False
        enemy_won_roll = self.roll_initiative()
        turn = 0

        while battle_finished is False:
            os.system("clear")
            turn = turn + 1
            self.print_details(console)
            choice = self.choice(console)
            console.print("")
            if choice == "attack":
                if enemy_won_roll is True:
                    self.enemy.attack(self.character, self.battle_log, console, turn)
                    time.sleep(1.0)
                    self.character.attack(self.enemy, self.battle_log, console, turn)
                    time.sleep(1.5)
                else:
                    self.character.attack(self.enemy, self.battle_log, console, turn)
                    time.sleep(1.0)
                    self.enemy.attack(self.character, self.battle_log, console, turn)
                    time.sleep(1.5)

            elif choice == "flee":
                battle_finished = True

            if self.enemy.hp <= 0:
                os.system("clear")
                self.print_details(console)
                console.print(
                    "[bold yellow]\n You won the battle! Your enemy "
                    "lays dead before you..."
                )
                input(" Press Enter to continue...")
                battle_finished = True
            elif self.character.hp <= 0:
                os.system("clear")
                self.print_details(console)
                console.print(
                    "[bold red]\n Even with all your might, this enemy "
                    "proved too powerful for you.\n Your adventure "
                    "ends here..."
                )
                input(" Press Enter to continue...")
                battle_finished = True
                game_state.game_over = True


def game_menu(game_state, console):
    os.system("clear")
    text = Text(
        "After a very tiring adventure, you finnaly find a place to rest",
        justify="center",
    )
    options = {
        "save": "Save current adventure and exit",
        "exit": "Exit without saving",
        "return": "Return to your adventure",
    }

    game_menu = Menu(text, options)
    game_menu.print_menu(console)
    choice = game_menu.choice(console)

    if choice == "save":
        sav.save_game(game_state, console)
        sys.exit()
    elif choice == "exit":
        sys.exit()


def initialize_game(game_state, console):

    text = (
        "[bold red]Welcome, adventurer! Are you ready for your next challenge?\n"
        "The world out there is full of monsters and treasures, and\n"
        "they are both waiting for you!\n"
        "Remember: Your choices always matter, so choose wisely."
    )

    options = {
        "create": "Create a character",
        "start": "Start an adventure",
        "load": "Load a saved game",
        "exit": "Exit",
    }

    os.system("clear")

    starting_menu = Menu(text, options)
    starting_menu.print_menu(console)
    choice = starting_menu.choice(console)

    if choice == "create":
        os.system("clear")
        cha.create_character(save_folder="Characters/")
        initialize_game(game_state, console)
    elif choice == "start":
        character_list = [
            f.split(".")[0] for f in os.listdir("Characters") if f.endswith("json")
        ]
        if len(character_list) > 0:
            cha.choose_character(game_state, console, character_list)
            console.print("\n")
            adv.choose_adventure(game_state, console)
        elif len(character_list) == 0:
            console.print(
                " Looks like you have not created any characters yet,"
                " try doing that first"
            )
            time.sleep(2)
            initialize_game(game_state, console)

    elif choice == "load":
        save_list = [f.split(".")[0] for f in os.listdir("Saves") if f.endswith("sav")]
        if len(save_list) > 0:
            game_state = sav.choose_save(game_state, console, save_list)
        elif len(save_list) == 0:
            console.print(" Looks like you don't have any saved files...")
            time.sleep(2)
            initialize_game(game_state, console)
    elif choice == "exit":
        console.print("Very well, see you next time, adventurer!")
        time.sleep(2)
        sys.exit()


def main_game():
    console = Console()
    gs = GameState()

    initialize_game(gs, console)
    exit_game = False
    while exit_game is False:
        gs.adventure[gs.next_encounter].resolve_encounter(gs, console)


if __name__ == "__main__":
    main_game()
