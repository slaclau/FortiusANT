from fortius_ant import antFE

from random import randint, seed

seed(0)

def test_full_cycle(mocker):
    mocker.patch("time.time", return_value=0)
    antFE.Initialize()
    out = ()
    for i in range(0, 500):
        message = antFE.BroadcastTrainerDataMessage(randint(0,100), randint(0,100), randint(0,100), randint(0,100))
        out = out + (message,)
        # assert message == expected_result[i]
    print(out)
    assert False