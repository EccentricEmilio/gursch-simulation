# tests/test_game_engine.py
def test_determine_throw_amounts(engine):
    throw_amounts = engine.determine_throw_amounts()
    assert throw_amounts == [1, 1]

def test_swap_cards(engine):
    player = "Alice"
    old_hand = engine.state.players_hands[player].copy()
    swap_cards = old_hand[:1]
    engine.swap_cards(swap_cards, player)
    new_hand = engine.state.players_hands[player]
    assert len(new_hand) == len(old_hand)
    for card in swap_cards:
        assert card not in new_hand

def test_process_throw_round_updates_phase(engine):
    engine.state.phase = 1  # THROW_PHASE
    engine.process_throw_round()
    assert engine.state.round_index == 1

def test_is_legal_lead(engine):
    move = engine.state.players_hands["Alice"][:1]
    from state import Move
    move_obj = Move(move)
    assert engine.is_legal_lead(move_obj) == True

def test_is_legal_move_lead(engine):
    from state import Move
    move_obj = Move(engine.state.players_hands["Alice"][:1])
    engine.state.current_round = MagicMock()
    engine.state.current_round.starting_player = "Alice"
    assert engine.is_legal_move("Alice", move_obj) == True

def test_apply_move_removes_cards(engine):
    from state import Move
    player = "Alice"
    legal_moveset = {Move(engine.state.players_hands[player][:1])}
    engine.state.current_round = MagicMock()
    engine.state.current_round.starting_player = player
    engine.apply_move(player, ["Alice", "Bob"])
    assert len(engine.state.players_hands[player]) < 3

def test_calculate_losers_sets_losers(engine):
    from state import Move, TurnRecord, RoundRecord
    move = Move([engine.state.players_hands["Alice"][0]])
    turn = TurnRecord("Alice", 0, move)
    engine.state.board.append(RoundRecord(0, 2, [turn], engine.state.players_hands))
    engine.calculate_losers()
    assert "Alice" in engine.state.losers
