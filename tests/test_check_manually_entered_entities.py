from app.check_manually_entered_entities import check_manually_entered_entities

def test_check_manually_entered_entities():
    assert check_manually_entered_entities("abc123")  # True
    assert check_manually_entered_entities("12-34")   # True
    assert check_manually_entered_entities("a,b,c")   # True
    assert check_manually_entered_entities("ab , cd") # True
    assert not check_manually_entered_entities("a--b")    # False (double dash)
    #assert not check_manually_entered_entities("a, ,b")   # False (missing input)
    assert not check_manually_entered_entities("a,b,")    # False (comma at the end)
    #assert not check_manually_entered_entities("a,b,c,d") # False (length of each input is too short)
    assert not check_manually_entered_entities("a")       # False (length < 2)