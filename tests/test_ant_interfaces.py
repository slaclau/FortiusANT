from fortius_ant import antCTRL, antFE
import random

random.seed(0)

def test_antCTRL(data_regression):
    antCTRL.Initialize()
    output = ()
    for i in range(0,500):
        output = output + (antCTRL.BroadcastControlMessage(),)
    data_regression.check(output)
        
def test_antFE(data_regression, mocker):
    mocker.patch('time.time',return_value=0)
    antFE.Initialize()
    for i in range(0,500):
        output = output + (antFE.BroadcastTrainerDataMessage(
        random.randint() / 3,
        random.randint() / 3,
        random.randint() / 3,
        random.randint() / 3
        ),)
    data_regression.check(output)