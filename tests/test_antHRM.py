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
        assert message == expected_result[i]
    print(out)
    
expected_result = (b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00+\xb6', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00\\\xc1', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00 \xbd', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00\x12\x8f', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00/2', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00B_', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00\x1c\x01', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00EX', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x004\xa9', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00\n\x97', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00\x11\x8c', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x005\xa8', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00IT', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00UH', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00-0', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00\r\x10', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x008\xa5', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x008\xa5', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00 \xbd', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00=\xa0', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x001,', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00\x1d\x00', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x003.', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00\x1f\x02', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00S\xce', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00>\xa3', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x003\xae', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00K\xd6', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00\t\x14', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00!<', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00$9', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00DY', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x000\xad', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00F\xdb', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00\x03\x9e', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00N\xd3', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00OR', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00dy', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00= ', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00\x1f\x02', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00$\xb9', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00\x06\x9b', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00O\xd2', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00*\xb7', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x003.', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00QL', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00\x0e\x13', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00EX', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00\x07\x9a', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00\x13\x8e', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00\\\xc1', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x003\xae', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00\x04\x19', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00c~', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x006+', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00^C', b'\xa4\tN\x01\x82\x01W\x17\x00\x00\x003\x12', b'\xa4\tN\x01\x82\x01W\x17\x00\x00\x008\x19', b'\xa4\tN\x01\x82\x01W\x17\x00\x00\x00\x0e/', b'\xa4\tN\x01\x82\x01W\x17\x00\x00\x00\\}', b'\xa4\tN\x01\x03\x01\x013\x00\x00\x00;\xe9', b'\xa4\tN\x01\x03\x01\x013\x00\x00\x00N\x9c', b'\xa4\tN\x01\x03\x01\x013\x00\x00\x00<\xee', b'\xa4\tN\x01\x03\x01\x013\x00\x00\x00\x15\xc7', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00\x16\x8b', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00,\xb1', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00=\xa0', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x005\xa8', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00\x15\x08', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00LQ', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00%8', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00b\x7f', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00A\xdc', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00\x0f\x92', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x000\xad', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00-\xb0', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00\x13\x0e', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00QL', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00.3', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00c~', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00=\xa0', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00Q\xcc', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00C\xde', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00a\xfc', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00\x07\x1a', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00\x1a\x07', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00!<', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00\x17\n', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00]\xc0', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00K\xd6', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00*\xb7', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00&\xbb', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x001,', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00RO', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00\x06\x1b', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00&;', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00G\xda', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x008\xa5', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00\x05\x98', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00X\xc5', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x005(', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00#>', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x001,', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00^C', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00\x1b\x86', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00-\xb0', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00\x12\x8f', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00\x11\x8c', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00\x0f\x12', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00OR', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00.3', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00\x16\x0b', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00\x04\x99', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x008\xa5', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00J\xd7', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x003\xae', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00<!', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00\n\x17', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00SN', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00[F', b'\xa4\tN\x01\x82\x01W\x17\x00\x00\x00[z', b'\xa4\tN\x01\x82\x01W\x17\x00\x00\x00Xy', b'\xa4\tN\x01\x82\x01W\x17\x00\x00\x00\n+', b'\xa4\tN\x01\x82\x01W\x17\x00\x00\x00dE', b'\xa4\tN\x01\x03\x01\x013\x00\x00\x007\xe5', b'\xa4\tN\x01\x03\x01\x013\x00\x00\x00F\x94', b'\xa4\tN\x01\x03\x01\x013\x00\x00\x00]\x8f', b'\xa4\tN\x01\x03\x01\x013\x00\x00\x00G\x95', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00\x12\x8f', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00\x16\x8b', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00\x14\x89', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00\x1b\x86', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00\x16\x0b', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00\x1e\x03', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00\x04\x19', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00DY', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00\x12\x8f', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00@\xdd', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00.\xb3', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00P\xcd', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00_B', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00%8', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00\\A', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00+6', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00X\xc5', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00\x10\x8d', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x005\xa8', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00c\xfe', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00"?', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00\x15\x08', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00,1', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00QL', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00A\xdc', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00+\xb6', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00E\xd8', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00Y\xc4', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00\x13\x0e', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x001,', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00_B', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00`}', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00H\xd5', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00(\xb5', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00\x1f\x82', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x001\xac', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00-0', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x002/', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00= ', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00B_', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00(\xb5', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x005\xa8', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x005\xa8', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00\r\x90', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00XE', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00\x14\t', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00\x13\x0e', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00\x01\x1c', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00K\xd6', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00M\xd0', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00R\xcf', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00[\xc6', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00C^', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00\x0e\x13', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00ZG', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00dy', b'\xa4\tN\x01\x82\x01W\x17\x00\x00\x00Sr', b'\xa4\tN\x01\x82\x01W\x17\x00\x00\x00Z{', b'\xa4\tN\x01\x82\x01W\x17\x00\x00\x00\x1b:', b'\xa4\tN\x01\x82\x01W\x17\x00\x00\x00Ml', b'\xa4\tN\x01\x03\x01\x013\x00\x00\x00S\x81', b'\xa4\tN\x01\x03\x01\x013\x00\x00\x00N\x9c', b'\xa4\tN\x01\x03\x01\x013\x00\x00\x00B\x90', b'\xa4\tN\x01\x03\x01\x013\x00\x00\x00\x0f\xdd', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00#\xbe', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00Y\xc4', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00^\xc3', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00O\xd2', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00\x16\x0b', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x001,', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00\x0b\x16', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00\x05\x18', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00\x02\x9f', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00\x0f\x92', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00/\xb2', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00]\xc0', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00>#', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00)4', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00\x0e\x13', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00WJ', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00:\xa7', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x000\xad', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00K\xd6', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00Z\xc7', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00!<', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00VK', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00?"', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00dy', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00\x1e\x83', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00\x15\x88', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00H\xd5', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00G\xda', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00\n\x17', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00dy', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00B_', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00\x16\x0b', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00\x04\x99', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00S\xce', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00\x16\x8b', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00C\xde', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x005(', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00NS', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00UH', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00\x1b\x06', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x009\xa4', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00[\xc6', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00X\xc5', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x004\xa9', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00"?', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00\x03\x1e', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00LQ', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00\x12\x0f', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x002\xaf', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00\x16\x8b', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x009\xa4', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00I\xd4', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00\x07\x1a', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x001,', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00\x0c\x11', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00SN', b'\xa4\tN\x01\x82\x01W\x17\x00\x00\x00Lm', b'\xa4\tN\x01\x82\x01W\x17\x00\x00\x004\x15', b'\xa4\tN\x01\x82\x01W\x17\x00\x00\x00+\n', b'\xa4\tN\x01\x82\x01W\x17\x00\x00\x00\x1e?', b'\xa4\tN\x01\x03\x01\x013\x00\x00\x00A\x93', b'\xa4\tN\x01\x03\x01\x013\x00\x00\x00;\xe9', b'\xa4\tN\x01\x03\x01\x013\x00\x00\x00\x06\xd4', b'\xa4\tN\x01\x03\x01\x013\x00\x00\x00>\xec', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00P\xcd', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00\x0e\x93', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00#\xbe', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00A\xdc', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00?"', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00GZ', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00SN', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x003.', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00=\xa0', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00"\xbf', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00\x18\x85', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00\x1e\x83', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00F[', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00/2', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00\x15\x08', b"\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00':", b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00N\xd3', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00\x13\x8e', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00;\xa6', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00\t\x94', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00\t\x14', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00>#', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x003.', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00IT', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x005\xa8', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00H\xd5', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00\x0c\x91', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00"\xbf', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00>#', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00\x1e\x03', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00\x0f\x12', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00&;', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00\x13\x8e', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00/\xb2', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00\r\x90', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00\x12\x8f', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00UH', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00\x08\x15', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00VK', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00\x12\x0f', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00L\xd1', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00H\xd5', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00\x1a\x87', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00\x01\x9c', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00\x05\x18', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x004)', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00HU', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00ZG', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00a\xfc', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00N\xd3', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00?\xa2', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00\\\xc1', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00YD', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00\x0e\x13', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00= ', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00HU', b'\xa4\tN\x01\x82\x01W\x17\x00\x00\x00-\x0c', b'\xa4\tN\x01\x82\x01W\x17\x00\x00\x00dE', b'\xa4\tN\x01\x82\x01W\x17\x00\x00\x00,\r', b'\xa4\tN\x01\x82\x01W\x17\x00\x00\x00\r,', b'\xa4\tN\x01\x03\x01\x013\x00\x00\x00X\x8a', b'\xa4\tN\x01\x03\x01\x013\x00\x00\x00\x01\xd3', b'\xa4\tN\x01\x03\x01\x013\x00\x00\x00\x1f\xcd', b'\xa4\tN\x01\x03\x01\x013\x00\x00\x00\x1e\xcc', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00@\xdd', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00(\xb5', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00$\xb9', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00\x1d\x80', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00\x02\x1f', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00@]', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00.3', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00B_', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00,\xb1', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00\x0c\x91', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00\n\x97', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00(\xb5', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00JW', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x007*', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00\x1d\x00', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00_B', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x000\xad', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x001\xac', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00b\xff', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00\x13\x8e', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00\x1e\x03', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00%8', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00\x1a\x07', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00`}', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00d\xf9', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00>\xa3', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00U\xc8', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00.\xb3', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00%8', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x002/', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00OR', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00\x11\x0c', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00d\xf9', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00\x10\x8d', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x004\xa9', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00.\xb3', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00A\\', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00= ', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00\x1e\x03', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00TI', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00[\xc6', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x000\xad', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00Q\xcc', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00.\xb3', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x008%', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00$9', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00.3', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x004)', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00c\xfe', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00c\xfe', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00\\\xc1', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00%\xb8', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00\x0e\x13', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00>#', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00&;', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00\x10\r', b'\xa4\tN\x01\x82\x01W\x17\x00\x00\x00:\x1b', b'\xa4\tN\x01\x82\x01W\x17\x00\x00\x00\x145', b'\xa4\tN\x01\x82\x01W\x17\x00\x00\x00-\x0c', b'\xa4\tN\x01\x82\x01W\x17\x00\x00\x00 \x01', b'\xa4\tN\x01\x03\x01\x013\x00\x00\x00`\xb2', b'\xa4\tN\x01\x03\x01\x013\x00\x00\x00\x18\xca', b'\xa4\tN\x01\x03\x01\x013\x00\x00\x00,\xfe', b'\xa4\tN\x01\x03\x01\x013\x00\x00\x00@\x92', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00\x1e\x83', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00\x0f\x92', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00X\xc5', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x002\xaf', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x002/', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00<!', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00B_', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00<!', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00I\xd4', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00P\xcd', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00\x1d\x80', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00W\xca', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x004)', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00A\\', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00(5', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00?"', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00\x1e\x83', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00)\xb4', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00C\xde', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00X\xc5', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00\x01\x1c', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00\x0c\x11', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00= ', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00)4', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x003\xae', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00\x1e\x83', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x008\xa5', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00\x07\x9a', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00JW', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00c~', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00\x06\x1b', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x005(', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00\x0c\x91', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00"\xbf', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00\x1a\x87', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00]\xc0', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00*7', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00\x17\n', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00\x0f\x12', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00\x18\x05', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00Z\xc7', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00/\xb2', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00\x04\x99', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00\x1e\x83', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00\x06\x1b', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00\x02\x1f', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x001,', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00EX', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00\x01\x9c', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00\x11\x8c', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00\x0f\x92', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00N\xd3', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00NS', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00\x1a\x07', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00\x0b\x16', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00_B', b'\xa4\tN\x01\x82\x01W\x17\x00\x00\x00<\x1d', b'\xa4\tN\x01\x82\x01W\x17\x00\x00\x00\x1a;', b'\xa4\tN\x01\x82\x01W\x17\x00\x00\x00\x01 ', b'\xa4\tN\x01\x82\x01W\x17\x00\x00\x00Cb', b'\xa4\tN\x01\x03\x01\x013\x00\x00\x00P\x82', b'\xa4\tN\x01\x03\x01\x013\x00\x00\x006\xe4', b'\xa4\tN\x01\x03\x01\x013\x00\x00\x00\t\xdb', b'\xa4\tN\x01\x03\x01\x013\x00\x00\x00E\x97', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00\x17\x8a', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00\x1e\x83', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00\x1e\x83', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x006\xab', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x001,', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00= ', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00\x01\x1c', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x008%', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00\x1b\x86', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x001\xac', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00b\xff', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00\x06\x9b', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00OR', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00#>', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00\x04\x19', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00KV', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00-\xb0', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00[\xc6', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x000\xad', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00,\xb1', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00WJ', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00;&', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00SN', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00\x12\x0f', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00M\xd0', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00C\xde', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00\x0c\x91', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00!\xbc', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00\x0e\x13', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00\\A', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00\x0e\x13', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00#>', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00\x04\x99', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00Y\xc4', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00\x13\x8e', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00P\xcd', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00c~', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00UH', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00\x12\x0f', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x001,', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00\x1b\x86', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00J\xd7', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00U\xc8', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00)\xb4', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00\x1a\x07', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x006+', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00B_', b'\xa4\tN\x01\x00\xff\xff\xff\x00\x00\x00A\\', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00\x10\x8d', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00H\xd5', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00\x0e\x93', b'\xa4\tN\x01\x80\xff\xff\xff\x00\x00\x00Y\xc4')