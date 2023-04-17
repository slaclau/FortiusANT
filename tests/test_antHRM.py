from fortius_ant import antHRM

from random import randint, seed

seed(0)

def test_full_cycle(mocker):
    mocker.patch("time.time", return_value=0)
    antHRM.Initialize()
    out = ()
    for i in range(0, 500):
        message = antHRM.BroadcastHeartrateMessage(randint(1,100))
        out = out + (message,)
        # assert message == expected_result[i]
    print(out)
    assert False