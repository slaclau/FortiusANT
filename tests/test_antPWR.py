from fortius_ant import antPWR

from random import randint, seed

seed(0)

def test_full_cycle(mocker):
    mocker.patch("time.time", return_value=0)
    antPWR.Initialize()
    out = ()
    for i in range(0, 500):
        message = antPWR.BroadcastMessage(randint(0,1000))
        out = out + (message,)
        # assert message == expected_result[i]
    print(out)
    assert False

