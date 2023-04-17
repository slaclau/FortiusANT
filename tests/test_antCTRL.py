from fortius_ant import antCTRL

def test_antCTRL(data_regression):
    antCTRL.Initialize()
    for i in range(0,500):
        output = antCTRL.BroadcastControlMessage()
        data_regression.check(output)