from typing import List, Tuple, Optional, Callable
from collections import Counter
import random


class Dice:
    """Class for rolling dice."""

    @staticmethod
    def roll(count: int) -> List[int]:
        return [random.randint(1, 6) for _ in range(count)]


class Scorer:
    """
    Score calculation strategy class.
    Each method is an algorithm that collects rolled dice into a scoring combination.
    """

    @staticmethod
    def score_default(dice: List[int], rolls_made: int) -> Tuple[int, int, bool, bool]:
        """
        Default scoring method scores special combinations first,
        then searches for three or more of a kind,
        then scores single ones and fives.
        """
        counts = Counter(dice)
        points = 0
        scoring_count = 0
        extra_throw = False
        zonked = False

        if list(counts.keys()) == [1, 2, 3, 4, 5, 6]:
            points = 1500
            scoring_count = 6
            extra_throw = True
            return points, scoring_count, extra_throw, zonked

        if list(counts.values()) == [2, 2, 2]:
            points = 750
            scoring_count = 6
            extra_throw = True
            return points, scoring_count, extra_throw, zonked

        for face in range(1, 7):
            c = counts.get(face, 0)
            if c >= 3:
                if face == 1:
                    base = 1000
                else:
                    base = face * 100
                gained = base * (c - 2)
                points += gained
                scoring_count += c
                counts[face] = 0

        ones = counts.get(1, 0)
        fives = counts.get(5, 0)
        if ones:
            points += ones * 100
            scoring_count += ones
        if fives:
            points += fives * 50
            scoring_count += fives

        if points == 0:
            zonked = True

        return points, scoring_count, extra_throw, zonked

    @staticmethod
    def score_greedy(dice: List[int], rolls_made: int) -> Tuple[int, int, bool, bool]:
        """Scores only special combinations and three-or-more-of-a-kind."""
        counts = Counter(dice)
        points = 0
        scoring_count = 0
        extra_throw = False
        zonked = False

        if list(counts.keys()) == [1, 2, 3, 4, 5, 6]:
            points = 1500
            scoring_count = 6
            extra_throw = True
            return points, scoring_count, extra_throw, zonked

        if list(counts.values()) == [2, 2, 2]:
            points = 750
            scoring_count = 6
            extra_throw = True
            return points, scoring_count, extra_throw, zonked

        for face in range(1, 7):
            c = counts.get(face, 0)
            if c >= 3:
                if face == 1:
                    base = 1000
                else:
                    base = face * 100
                gained = base * (c - 2)
                points += gained
                scoring_count += c
                counts[face] = 0

        if points == 0:
            zonked = True

        return points, scoring_count, extra_throw, zonked

    @staticmethod
    def score_all_in(dice: List[int], rolls_made: int) -> Tuple[int, int, bool, bool]:
        """Tries to score a special combination for three rolls, then scores in the default way."""
        counts = Counter(dice)
        points = 0
        scoring_count = 0
        extra_throw = False
        zonked = False

        if list(counts.keys()) == [1, 2, 3, 4, 5, 6]:
            points = 1500
            scoring_count = 6
            extra_throw = True
            return points, scoring_count, extra_throw, zonked

        if list(counts.values()) == [2, 2, 2]:
            points = 750
            scoring_count = 6
            extra_throw = True
            return points, scoring_count, extra_throw, zonked

        for face in range(1, 7):
            c = counts.get(face, 0)
            if c >= 3:
                if face == 1:
                    base = 1000
                else:
                    base = face * 100
                gained = base * (c - 2)
                points += gained
                scoring_count += c
                counts[face] = 0

        ones = counts.get(1, 0)
        fives = counts.get(5, 0)
        if ones:
            points += ones * 100
            scoring_count += ones
        if fives:
            points += fives * 50
            scoring_count += fives

        if points == 0:
            zonked = True

        return points, scoring_count, extra_throw, zonked


class Strategy:
    """
    Bot strategy class.
    Each strategy is an algorithm for deciding whether to continue the turn.
    """

    @staticmethod
    def conservative(player_score: int, turn_points: int, dice_remaining: int) -> bool:
        """Strategy that always ends the turn after the first roll."""
        return False

    @staticmethod
    def gambling(player_score: int, turn_points: int, dice_remaining: int) -> bool:
        """Strategy that continues the turn as long as there are dice to roll."""
        return dice_remaining > 0

    @staticmethod
    def risky(player_score: int, turn_points: int, dice_remaining: int) -> bool:
        """Strategy that does not end the turn until it has at least 300 points."""
        return turn_points >= 300 and dice_remaining > 0

    @staticmethod
    def balanced(player_score: int, turn_points: int, dice_remaining: int) -> bool:
        """
        Strategy that, with a low total score, rolls until getting 300 points;
        with a higher total score, rolls until getting 150 points.
        """
        if player_score >= 3000:
            return turn_points >= 300 and dice_remaining > 0
        else:
            return turn_points >= 150 and dice_remaining > 0


class Player:
    """Bot player with a given strategy."""

    def __init__(self, name: str, strategy: Callable, scoring_algo: Callable) -> None:
        self.name = name
        self.strategy = strategy
        self.scoring_algo = scoring_algo
        self.score = 0

    def __str__(self) -> str:
        return f"Player {self.name} score={self.score}"

    def play_turn(self):
        max_dice = 6
        turn_points = 0
        rolls_made = 0
        dice_remaining = max_dice

        while True:
            roll = Dice.roll(dice_remaining)
            rolls_made += 1
            points, scoring_count, extra_roll, zonk = self.scoring_algo(
                roll, rolls_made
            )

            if points == 0 and zonk:
                turn_points = 0
                return TurnResult(self, 0, zonked=True)

            turn_points += points
            dice_remaining -= scoring_count

            if extra_roll:
                dice_remaining = max_dice

            desire_to_continue = self.strategy(self.score, turn_points, dice_remaining)
            if not desire_to_continue:
                self.score += turn_points
                return TurnResult(self, turn_points, zonked=False)


class TurnResult:
    def __init__(self, player: Player, gained: int, zonked: bool):
        self.player = player
        self.gained = gained
        self.zonked = zonked


class Game:
    """
    Game class: stores a list of players, state (round, current index), and ending parameters.
    You can run play() to play until the end or until max_rounds is reached.
    """

    def __init__(
        self,
        players: List[Player],
        target_score: int = 10000,
        max_rounds: Optional[int] = None,
    ):
        self.players = players
        self.target_score = target_score
        self.max_rounds = max_rounds
        self.round = 0
        self.history: List[TurnResult] = []

    def play_round(self) -> None:
        """Play one round (one turn for each player)."""
        self.round += 1
        for player in self.players:
            result = player.play_turn()
            self.history.append(result)
            print(
                f"Round {self.round} - {player.name} -> gained={result.gained} zonked={result.zonked}"
            )
            for p in self.players:
                print(p)
            if self.someone_reached_target():
                return

    def someone_reached_target(self) -> bool:
        return any(p.score >= self.target_score for p in self.players)

    def play(self) -> List[TurnResult]:
        """Play until someone reaches target_score or until max_rounds is exceeded."""
        while True:
            if self.max_rounds is not None and self.round >= self.max_rounds:
                break
            self.play_round()
            if self.someone_reached_target():
                break
        return self.history

    def leaderboard(self) -> List[tuple]:
        return sorted(((p.name, p.score) for p in self.players), key=lambda x: -x[1])
