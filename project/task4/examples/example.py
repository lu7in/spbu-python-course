"""
Game example
"""

from project.task4.zonk import *


def main():
    players = [
        Player("Anton", Strategy.balanced, Scorer.score_default),
        Player("Gosha", Strategy.conservative, Scorer.score_greedy),
        Player("Pasha", Strategy.risky, Scorer.score_all_in),
    ]

    game = Game(players, target_score=10000, max_rounds=50)
    print("Starting game")
    game.play()
    print("Final leaderboard:")
    for name, score in game.leaderboard():
        print(f"  {name}: {score}")


if __name__ == "__main__":
    main()
