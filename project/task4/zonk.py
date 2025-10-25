from typing import List, Tuple, Optional, Callable
from collections import Counter
import random


class Dice:
    """Класс для подбрасывания кубиков."""

    @staticmethod
    def roll(count: int) -> List[int]:
        return [random.randint(1, 6) for _ in range(count)]


class Scorer:
    """
    Подсчёт очков для набора кубиков.
    Возвращает (points, scoring_count, extra_throw) — количество очков за бросок и сколько кубиков даёт эти очки.
    Правила
    - По одному каждого достоинства = 1500 и доп. бросок
    - Три пары = 750 и доп. бросок
    - Три единицы = 1000
    - Три одинаковых (2..6) = достоинство * 100
    - Четверка/пятёрка/шестёрка того же достоинства: очки за первую тройку умножаются на кол-во кубиков того же достоинства -3
    - Одиночные 1 = 100
    - Одиночные 5 = 50
    """

    @staticmethod
    def score(dice: List[int]) -> Tuple[int, int, bool]:
        counts = Counter(dice)
        points = 0
        scoring_count = 0
        extra_throw = False

        if list(counts.keys()) == [1, 2, 3, 4, 5, 6]:
            points = 1500
            scoring_count = 6
            extra_throw = True
            return points, scoring_count, extra_throw

        if list(counts.values()) == [2, 2, 2]:
            points = 750
            scoring_count = 6
            extra_throw = True
            return points, scoring_count, extra_throw

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

        return points, scoring_count, extra_throw


class Strategy:
    """
    Класс стратегий ботов,
    каждая стратегия является алгоритмом принятия решения о продолжении хода
    """

    @staticmethod
    def conservative(player_score: int, turn_points: int, dice_remaining: int) -> bool:
        """Стратегия всегда останавливающая ход после первого броска."""
        return False

    @staticmethod
    def gambling(player_score: int, turn_points: int, dice_remaining: int) -> bool:
        """Стратегия продолжающая ход пока есть возможность бросать кости"""
        return dice_remaining > 0

    @staticmethod
    def risky(player_score: int, turn_points: int, dice_remaining: int) -> bool:
        """Стратегия, не прекращающая ход, пока не наберёт 300 очков."""
        return turn_points >= 300 and dice_remaining > 0

    @staticmethod
    def balanced(player_score: int, turn_points: int, dice_remaining: int) -> bool:
        """Стратегия, которая при малом количестве очков бросает до получения 300, при большем до получения 150 очков."""
        if player_score >= 3000:
            return turn_points >= 300 and dice_remaining > 0
        else:
            return turn_points >= 150 and dice_remaining > 0


class Player:
    """Игрок-бот с заданной стратегией."""

    def __init__(self, name: str, strategy: Callable):
        self.name = name
        self.strategy = strategy
        self.score = 0

    def __str__(self) -> str:
        return f"Player {self.name} score={self.score}"

    def play_turn(self):
        max_dice = 6
        turn_points = 0
        dice_remaining = max_dice

        while True:
            roll = Dice.roll(dice_remaining)
            points, scoring_count, extra_roll = Scorer.score(roll)

            if points == 0:
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
    Класс игры: хранит список игроков, состояние (раунд, текущий индекс), параметры окончания.
    Можно запустить play() для игры до конца или до max_rounds.
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
        """Провести один круг (один ход каждого игрока)."""
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
        """Играть пока кто-то не дойдёт до target_score или пока не будет превышено max_rounds."""
        while True:
            if self.max_rounds is not None and self.round >= self.max_rounds:
                break
            self.play_round()
            if self.someone_reached_target():
                break
        return self.history

    def leaderboard(self) -> List[tuple]:
        return sorted(((p.name, p.score) for p in self.players), key=lambda x: -x[1])
