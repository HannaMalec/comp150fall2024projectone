import json
import sys
import random
from typing import List, Optional
from enum import Enum


class EventStatus(Enum):
    UNKNOWN = "unknown"
    PASS = "pass"
    FAIL = "fail"
    PARTIAL_PASS = "partial_pass"


class Statistic:
    def __init__(self, name: str, value: int = 0, description: str = "", min_value: int = 0, max_value: int = 100):
        self.name = name
        self.value = value
        self.description = description
        self.min_value = min_value
        self.max_value = max_value

    def __str__(self):
        return f"{self.name}: {self.value}"

    def modify(self, amount: int):
        self.value = max(self.min_value, min(self.max_value, self.value + amount))


class Character:
    def __init__(self, name: str):
        self.name = name
        self.position = 0  # Start at position 0

    def update_position(self, new_position: int):
        self.position = new_position

    def __init__(self, name: str = "Bob"):
        self.name = name
        self.strength = Statistic("Strength", description="Strength is a measure of physical power.")
        self.intelligence = Statistic("Intelligence", description="Intelligence is a measure of cognitive ability.")
        self.dexterity = Statistic("Dexterity", description="Dexterity is a measure of performing intricate tasks.")
        self.constitution = Statistic("Constitution", description="Constitution is a measure of physical resilience.")
        self.vitality = Statistic("Vitality", description="Vitality is a measure of liveliness(HP).")
        self.endurance = Statistic("Endurance", description="Endurance is a measure of the ability to recover from injury and fatigue.")
        self.wisdom = Statistic("Wisdom", description="Wisdom is a measure of the ability to make decisions under pressure.")
        self.knowledge = Statistic("Knowledge", description="Knowledge is a measure of the amount of learned information.")
        self.willpower = Statistic("Willpower", description="Willpower is a measure of mental resilience.")
        self.spirit = Statistic("Spirit", description="Spirit is the measure of the aptitude for otherworldly acts.")
        self.capacity = Statistic("Capacity", description="Capacity is a measure of the potential related to specific sources.")
        # Add more stats as needed

    def __str__(self):
        return f"Character: {self.name}, Strength: {self.strength}, Intelligence: {self.intelligence}, Dexterity: {self.dexterity}, Constitution: {self.constitution}, Vitality: {self.vitality}, Endurance: {self.endurance}, Wisdom: {self.wisdom}, Knowledge: {self.knowledge}, Willpower: {self.willpower}, Spirit: {self.spirit}, Capacity: {self.capacity}"

    def get_stats(self):
        return [self.strength, self.intelligence, self.dexterity, self.constitution, self.vitality, self.endurance, self.wisdom, self.knowledge, self.willpower, self.spirit, self.capacity]  # Extend this list if there are more stats


class Event:
    def __init__(self, data: dict):
        self.primary_attribute = data['primary_attribute']
        self.secondary_attribute = data['secondary_attribute']
        self.prompt_text = data['prompt_text']
        self.pass_message = data['pass']['message']
        self.fail_message = data['fail']['message']
        self.partial_pass_message = data['partial_pass']['message']
        self.status = EventStatus.UNKNOWN

    def execute(self, party: List[Character], parser):
        print(self.prompt_text)
        character = parser.select_party_member(party)
        chosen_stat = parser.select_stat(character)
        self.resolve_choice(character, chosen_stat)

    def resolve_choice(self, character: Character, chosen_stat: Statistic):
        if chosen_stat.name == self.primary_attribute:
            self.status = EventStatus.PASS
            print(self.pass_message)
        elif chosen_stat.name == self.secondary_attribute:
            self.status = EventStatus.PARTIAL_PASS
            print(self.partial_pass_message)
        else:
            self.status = EventStatus.FAIL
            print(self.fail_message)


class Location:
    def __init__(self, events: List[Event]):
        self.events = events

    def get_event(self) -> Event:
        return random.choice(self.events)


class Game:
    def __init__(self, parser, characters: List[Character], locations: List[Location]):
        self.parser = parser
        self.party = characters
        self.locations = locations
        self.continue_playing = True

    def start(self):
        while self.continue_playing:
            location = random.choice(self.locations)
            event = location.get_event()
            event.execute(self.party, self.parser)
            if self.check_game_over():
                self.continue_playing = False
        print("Game Over.")

    def check_game_over(self):
        return len(self.party) == 0

class Die:
    def __init__(self, sides: int = 6):
        self.sides = sides

    def roll(self) -> int:
        return random.randint(1, self.sides)
    
    def roll_two_dice(self) -> int:
        return self.roll() + self.roll() #Roll dice two times and return the total
    
class GameBoard:
    def __init__(self, events: List[str]):
        self.events = events
        self.position = 0  # Start at position 0

    def move_character(self, spaces: int):
        self.position += spaces
        print(f"Moved to position: {self.position}")

        # If you exceed the number of spaces on the board in Monopoly, wrap around
        if self.position >= len(self.events):
            self.position = self.position % len(self.events)
            print("You've wrapped around the board!")

    def assign_event(self):
        event = self.events[self.position]
        print(f"Event at position {self.position}: {event}")
        return event

class UserInputParser:
    def parse(self, prompt: str) -> str:
        return input(prompt)

    def select_party_member(self, party: List[Character]) -> Character:
        while True:
            print("Please choose a piece to play as:")
            for idx, member in enumerate(party):
                print(f"{idx + 1}. {member.name}")
            try:
                choice = int(self.parse("Enter the number of the chosen piece: ")) - 1
                if 0 <= choice < len(party):
                    return party[choice]
                else:
                    print("Invalid choice, please try again.")
            except ValueError:
                print("Invalid input, please enter a number.")

    def select_stat(self, character: Character) -> Statistic:
        while True:
            print(f"Choose a stat for {character.name}:")
            stats = character.get_stats()
            for idx, stat in enumerate(stats):
                print(f"{idx + 1}. {stat.name} ({stat.value})")
            try:
                choice = int(self.parse("Enter the number of the stat to use: ")) - 1
                if 0 <= choice < len(stats):
                    return stats[choice]
                else:
                    print("Invalid choice, please try again.")
            except ValueError:
                print("Invalid input, please enter a number.")


def load_events_from_json(file_path: str) -> List[str]:
    with open(file_path, 'r') as file:
        data = json.load(file)
    return [event_data['prompt_text'] for event_data in data]  

def start_game():
    parser = UserInputParser()
    characters = [
        Character("battleship"),
        Character("race_car"),
        Character("top_hat"),
        Character("thimble")
    ]

    # Load events from the JSON file
    events = load_events_from_json('project_code/location_events/location_1.json')
    board = GameBoard(events)  # Initialize the GameBoard with events
    die = Die()  # Create a Die instance

    # Game loop for multiple players or sessions
    while True:
        print("\nChoose your character:")
        for idx, character in enumerate(characters):
            print(f"{idx + 1}. {character.name}")
        
        choice = int(parser.parse("Enter the number of your chosen character: ")) - 1
        player = characters[choice]
        print(f"monopoly_man: You have chosen: {player.name}")

        # Player's turn
        while True:
            input("monopoly_man: Press Enter to roll the dice...")
            roll_result = die.roll_two_dice()
            print(f"monopoly_man: You rolled: {roll_result}")

            board.move_character(roll_result)  # Move the player on the board
            event = board.assign_event()  # Get the event for the new position

            # Handle specific events
            if event == "monopoly_man: Go to Jail":
                print("monopoly_man: You are now in Jail!")
                # Implement jail logic as needed
                break  # End the player's turn

            # Add other event responses as needed
            print(f"monopoly_man: You encountered: {event}")

            if input("monopoly_man: Continue playing your turn? (y/n): ").lower() != 'y':
                break  # Exit the player's turn loop

        if input("monopoly_man: Do you want to continue the game? (y/n): ").lower() != 'y':
            break  # Exit the game loop

    print("Game Over!")

if __name__ == '__main__':
    start_game()