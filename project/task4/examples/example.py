"""
Пример запуска игры
"""

from project.task4.zonk import Player
from project.task4.zonk import Strategy
from project.task4.zonk import Game


def main():
    players = [
        Player("Anton", Strategy.conservative),
        Player("Gosha", Strategy.risky),
        Player("Pasha", Strategy.balanced),
    ]

    game = Game(players, target_score=5000, max_rounds=20)
    print("Starting game")
    game.play()
    print("Final leaderboard:")
    for name, score in game.leaderboard():
        print(f"  {name}: {score}")


if __name__ == "__main__":
    main()
