import project.task4.zonk as zonk
from project.task4.zonk import Scorer, Player, Game, Strategy


def test_scorer_straight_and_three_pairs_and_triples():
    # Straight 1-6
    points, scoring_count, extra = Scorer.score([1, 2, 3, 4, 5, 6])
    assert points == 1500
    assert scoring_count == 6
    assert extra is True

    # Three pairs (2,2,3,3,4,4)
    points, scoring_count, extra = Scorer.score([2, 2, 3, 3, 4, 4])
    assert points == 750
    assert scoring_count == 6
    assert extra is True

    # Triple ones
    points, scoring_count, extra = Scorer.score([1, 1, 1])
    assert points == 1000
    assert scoring_count == 3
    assert extra is False

    # Triple twos
    points, scoring_count, extra = Scorer.score([2, 2, 2])
    assert points == 200
    assert scoring_count == 3
    assert extra is False

    # Four of a kind (3,3,3,3) -> 300 * 2 = 600
    points, scoring_count, extra = Scorer.score([3, 3, 3, 3])
    assert points == 600
    assert scoring_count == 4
    assert extra is False

    # Six ones (1,1,1,1,1,1) -> 1000 * 4 = 4000
    points, scoring_count, extra = Scorer.score([1, 1, 1, 1, 1, 1])
    assert points == 4000
    assert scoring_count == 6
    assert extra is False

    # Singles: two 1s and one 5 -> 2*100 + 1*50 = 250
    points, scoring_count, extra = Scorer.score([1, 1, 5, 2, 4, 6])
    assert points == 250
    assert scoring_count == 3
    assert extra is False


def make_roll_sequence(seq):
    """Возвращает функцию для подмены Dice.roll"""
    it = iter(seq)

    def roll(count):
        try:
            return next(it)
        except StopIteration:
            # если последовательность исчерпана, возвращать последний элемент
            return seq[-1]

    return roll


def test_player_play_turn_stop_and_zonk(monkeypatch):

    player = Player("A", Strategy.gambling)
    monkeypatch.setattr(
        zonk.Dice,
        "roll",
        make_roll_sequence(
            [[1, 2, 3, 4, 5, 6], [1, 2, 3, 4, 5, 6], [1, 1, 1, 1, 1, 1]]
        ),
    )
    result = player.play_turn()
    assert result.zonked is False
    assert result.gained == 7000
    assert player.score == 7000

    player2 = Player("B", Strategy.gambling)
    monkeypatch.setattr(
        zonk.Dice, "roll", make_roll_sequence([[1, 2, 3, 4, 5, 6], [2, 3, 4, 2, 3, 6]])
    )
    result2 = player2.play_turn()
    assert result2.zonked is True
    assert result2.gained == 0
    assert player2.score == 0  # Зонк обнуляет заработанные ранее очки


def test_player_strategy(monkeypatch):
    # Стратегия: продолжать, пока turn_points < 200
    def strategy(player_score, turn_points, dice_remaining):
        return turn_points < 200

    player1 = Player("C", strategy)
    rolls1 = [
        [1, 2, 3, 4, 6, 6],  # ones=1 -> 100
        [5, 5, 5],  # triple fives -> 500
    ]
    monkeypatch.setattr(zonk.Dice, "roll", make_roll_sequence(rolls1))
    result1 = player1.play_turn()

    assert result1.gained == 600
    assert result1.zonked is False
    assert player1.score == 600

    player2 = Player("D", strategy)
    rolls2 = [
        [1, 1, 3, 4, 6, 6],  # ones=2 -> 200
        [5, 5, 5],  # triple fives -> 500
    ]
    monkeypatch.setattr(zonk.Dice, "roll", make_roll_sequence(rolls2))
    result2 = player2.play_turn()

    # Второй бросок не произойдёт из-за стратегии игрока (бросать пока меньше 200 очков)
    assert result2.gained == 200
    assert result2.zonked is False
    assert player2.score == 200


def test_game_play_and_leaderboard(monkeypatch):
    # Два игрока, стратегия: не продолжать
    p1 = Player("Vasya", Strategy.conservative)
    p2 = Player("Petya", Strategy.conservative)

    # Подменяем броски так, чтобы первый игрок сразу получил 1500
    monkeypatch.setattr(zonk.Dice, "roll", make_roll_sequence([[1, 2, 3, 4, 5, 6]]))

    game = Game([p1, p2], target_score=1000)
    history = game.play()

    # Игра завершится после первого хода
    assert game.round == 1
    assert len(history) == 1
    assert history[0].player is p1
    assert p1.score >= 1000
    assert p2.score == 0

    # Сначала Vasya, затем Petya
    leaderboard = game.leaderboard()
    assert leaderboard[0][0] == "Vasya"
    assert leaderboard[1][0] == "Petya"
    assert leaderboard[0][1] >= leaderboard[1][1]
