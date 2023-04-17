from fortius_ant import antCTRL

def test_antCTRL(regression_data):
    antCTRL.Initialize()
    for i in range(0,500):
        output = antCTRL.BroadcastMessage()
        regression_data.check(output)