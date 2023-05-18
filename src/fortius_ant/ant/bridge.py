from typing import TypeVar, Generic

from fortius_ant.ant.interface import AntInterface
from fortius_ant.ant.message import AntMessage, Id

class AntBridge:

    class BridgeInterface(AntInterface):
        def __init__(self, interface, target_channel):
            self.interface = interface
            self.target_channel = target_channel
            
        def _handle_broadcast_data(data_page_number: int, info: bytes):
            self.logger.debug("Retransmit broadcast message %s from channel %d to channel %d", info, self.channel, self.target_channel)
            info[0] = self.target_channel
            return AntMessage.compose(Id.BroadcastData, info)
 
        def _handle_acknowledged_data(data_page_number: int, info: bytes):
            self.logger.debug("Retransmit acknowledged message %s from channel %d to channel %d", info, self.channel, self.target_channel)
            info[0] = self.target_channel
            return AntMessage.compose(Id.AcknowledgedData, info)

    def __init__(self, master, slave):
        assert isinstance(master, AntInterface)
        assert isinstance(slave, AntInterface)
        assert master.master
        assert not slave.master
        
        self.master = BridgeInterface(master, slave.channel)
        self.slave = BridgeInterface(slace, master.channel)

