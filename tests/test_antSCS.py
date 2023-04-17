from fortius_ant import antSCS

from random import randint, seed

seed(0)

def test_full_cycle(mocker):
    mocker.patch("time.time", return_value=0)
    antSCS.Initialize()
    out = ()
    for i in range(0, 500):
        message = antSCS.BroadcastMessage(i / 2, i / 3, i / 4, i / 5)
        out = out + (message,)
        # assert message == expected_result[i]
    print(out)
    assert False