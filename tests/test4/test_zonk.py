from project.task4.zonk import *


def test_scorer():
    # Straight 1-6
    points, scoring_count, extra, zonk = Scorer.score_default([1, 2, 3, 4, 5, 6], 1)
    assert points == 1500
    assert scoring_count == 6
    assert extra is True
    assert zonk is False

    # Three pairs (e.g., 1,1,2,2,3,3)
    points, scoring_count, extra, zonk = Scorer.score_default([1, 1, 2, 2, 3, 3], 1)
    assert points == 750
    assert scoring_count == 6
    assert extra is True
    assert zonk is False

    # Three ones plus a five -> 1000 (three ones) + 50 (one five)
    points, scoring_count, extra, zonk = Scorer.score_default([1, 1, 1, 5, 2, 3], 1)
    assert points == 1050
    assert scoring_count == 4  # three ones + the five
    assert extra is False
    assert zonk is False

    # Single one and five scoring
    points, scoring_count, extra, zonk = Scorer.score_default([1, 5, 2, 2, 3, 4], 1)
    assert points == 150
    assert scoring_count == 2
    assert extra is False
    assert zonk is False

    # No scoring dice -> zonk
    points, scoring_count, extra, zonk = Scorer.score_default([2, 3, 4, 6, 2], 1)
    assert points == 0
    assert zonk is True

    # Greedy should ignore single ones and fives
    points, scoring_count, extra, zonk = Scorer.score_greedy([1, 5, 2, 2, 3, 4], 1)
    assert points == 0
    # Due to the player technically being able to score single dice but deciding not to it isn't zonk
    assert zonk is False

    # All-in doesn't score anything but a special combinations during first two throws
    points, scoring_count, extra, zonk = Scorer.score_all_in([5, 5, 5, 1, 2, 3], 1)
    assert points == 0
    assert scoring_count == 0
    assert zonk is False

    # After two throws scores like score_default
    points, scoring_count, extra, zonk = Scorer.score_all_in([5, 5, 5, 1, 2, 3], 3)
    assert points == 600
    assert scoring_count == 4
    assert zonk is False


def make_roll_sequence(seq):
    """Returns function to replace Dice.roll with"""
    it = iter(seq)

    def roll(count):
        try:
            return next(it)
        except StopIteration:
            return seq[-1]

    return roll


def test_player_zonk_turn_over(monkeypatch):
    monkeypatch.setattr(Dice, "roll", make_roll_sequence([[3, 2, 3, 4, 6, 2]]))

    player = Player("ZonkTest", Strategy.conservative, Scorer.score_default)
    original_score = player.score
    result = player.play_turn()

    assert isinstance(result, TurnResult)
    assert result.gained == 0
    assert result.zonked is True
    assert player.score == original_score


def test_player_strategies_in_play_turn(monkeypatch):
    # Conservative: stops after the first roll -> should only gain points from first roll
    monkeypatch.setattr(
        Dice, "roll", make_roll_sequence([[1, 2, 3, 4, 6, 6], [1, 1, 1, 1, 1]])
    )
    p_cons = Player("Conservative", Strategy.conservative, Scorer.score_default)
    res_cons = p_cons.play_turn()
    assert res_cons.gained == 100
    assert res_cons.zonked is False
    assert p_cons.score == 100

    # Gambling: continues while dice_remaining > 0
    monkeypatch.setattr(
        Dice,
        "roll",
        make_roll_sequence([[1, 2, 3, 4, 6, 6], [5, 5, 5, 3, 4], [1, 3], [5]]),
    )
    p_gamb = Player("Gambler", Strategy.gambling, Scorer.score_default)
    res_gamb = p_gamb.play_turn()
    assert res_gamb.gained == 750
    assert res_gamb.zonked is False
    assert p_gamb.score == 750

    # Risky: when first roll < 300 -> throws again
    monkeypatch.setattr(
        Dice, "roll", make_roll_sequence([[1, 2, 3, 4, 6, 6], [1, 1, 1, 2, 3]])
    )
    p_risky_stop = Player("RiskyStop", Strategy.risky, Scorer.score_default)
    res_risky_stop = p_risky_stop.play_turn()
    assert res_risky_stop.gained == 1100
    assert res_risky_stop.zonked is False
    assert p_risky_stop.score == 1100

    # Risky: when first roll >= 300 -> stops the turn
    monkeypatch.setattr(
        Dice, "roll", make_roll_sequence([[4, 4, 4, 2, 2, 3], [1, 1, 1]])
    )
    p_risky_go = Player("RiskyGo", Strategy.risky, Scorer.score_default)
    res_risky_go = p_risky_go.play_turn()
    assert res_risky_go.gained == 400
    assert res_risky_go.zonked is False
    assert p_risky_go.score == 400

    # Balanced (low total score): threshold is 150 -> will stop when turn_points >= 150
    monkeypatch.setattr(
        Dice, "roll", make_roll_sequence([[5, 5, 1, 2, 3, 4], [1, 1, 1]])
    )
    p_bal = Player("Balanced", Strategy.balanced, Scorer.score_default)
    res_bal = p_bal.play_turn()
    assert res_bal.gained == 200
    assert res_bal.zonked is False
    assert p_bal.score == 200

    # Balanced (high total score): threshold is 300 -> will stop when turn_points >= 300
    p_bal.score += 2800
    monkeypatch.setattr(
        Dice, "roll", make_roll_sequence([[5, 5, 1, 2, 3, 4], [1, 1, 1]])
    )
    res_bal = p_bal.play_turn()
    assert res_bal.gained == 1200
    assert res_bal.zonked is False
    assert p_bal.score == 4200


def test_game_play_and_leaderboard(monkeypatch):
    p1 = Player("Vasya", Strategy.conservative, Scorer.score_default)
    p2 = Player("Petya", Strategy.conservative, Scorer.score_default)

    monkeypatch.setattr(Dice, "roll", make_roll_sequence([[1, 2, 3, 4, 5, 6]]))

    game = Game([p1, p2], target_score=1000)
    history = game.play()

    assert game.round == 1
    assert len(history) == 1
    assert history[0].player is p1
    assert p1.score >= 1000
    assert p2.score == 0

    leaderboard = game.leaderboard()
    assert leaderboard[0][0] == "Vasya"
    assert leaderboard[1][0] == "Petya"
    assert leaderboard[0][1] >= leaderboard[1][1]
