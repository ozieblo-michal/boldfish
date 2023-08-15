from app.validate_deck_name import validate_deck_name

def test_validate_deck_name():

    assert validate_deck_name("abc")     # True
    assert validate_deck_name("Hello")   # True
    assert not validate_deck_name("123")     # False (contains digits)
    assert not validate_deck_name("a b")     # False (contains spaces)
    assert not validate_deck_name("ab")      # False (length < 3)