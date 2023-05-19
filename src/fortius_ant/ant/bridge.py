from fortius_ant.ant.interface import AntInterface
from fortius_ant.ant.message import AntMessage, Id


class AntBridge:
    """Bridge a master and slave interface together."""

    class BridgeInterface(AntInterface):
        """Retransmit received data on target interface."""

        def __init__(self, interface, target_interface):
            super().__init__(interface.master, interface.device_number)
            self.interface = interface
            self.target_interface = target_interface

        def _handle_broadcast_data(self, data_page_number: int, info: bytes):
            self.logger.debug(
                "Retransmit broadcast message %s from channel %d to channel %d",
                info,
                self.channel,
                self.target_interface.channel,
            )
            array_info = bytearray(info)
            array_info[0] = self.target_interface.channel
            info = bytes(array_info)
            return AntMessage.compose(Id.BroadcastData, info)

        def _handle_acknowledged_data(self, data_page_number: int, info: bytes):
            self.logger.debug(
                "Retransmit acknowledged message %s from channel %d to channel %d",
                info,
                self.channel,
                self.target_interface.channel,
            )
            array_info = bytearray(info)
            array_info[0] = self.target_interface.channel
            info = bytes(array_info)
            return AntMessage.compose(Id.AcknowledgedData, info)

        def broadcast_message(self):
            """Do not broadcast actively, only retransmit."""
            pass

    def __init__(self, master, slave):
        assert isinstance(master, AntInterface)
        assert isinstance(slave, AntInterface)
        assert master.master
        assert not slave.master

        self.master = self.BridgeInterface(master, slave)
        self.slave = self.BridgeInterface(slave, master)
