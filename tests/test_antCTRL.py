from fortius_ant import antCTRL


def test_page_80():
    antCTRL.Interleave = 64
    assert (
        antCTRL.BroadcastControlMessage()
        == b"\xa4\tN\x06P\xff\xff\x01\xff\x00\xd2\x04\x9d"
    )
    assert antCTRL.Interleave == 65


def test_page_81():
    antCTRL.Interleave = 129
    assert (
        antCTRL.BroadcastControlMessage() == b"\xa4\tN\x06Q\xff\x01\x015\xee*\x01\xbb"
    )
    assert antCTRL.Interleave == 1


def test_page_2():
    for antCTRL.Interleave in range(0, 129):
        if antCTRL.Interleave != 64 & antCTRL.Interleave != 129:
            assert (
                antCTRL.BroadcastControlMessage()
                == b"\xa4\tN\x06\x02\x00\x00\x00\x00\x00\x00\x10\xf7"
            )
