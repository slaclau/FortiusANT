"""Provide an inheritable class for implemented an ANT+ device."""

__version__ = "2023-04-16"
# 2023-04-16    Rewritten in class based fashion

from fortius_ant.usbTrainer import clsTacxTrainer
from fortius_any.antDongle import clsAntDongle, msgID_AcknowledgedData, msgID_BroadcastData, msgID_ChannelID

class AntInterface:
    """Interface for communicating as an ANT+ device."""

    interleave = 0
    interleave_reset: int
    channel: int
    device_type_id: int
    ant_dongle: clsAntDongle
    master: bool
    paired = false
    FortiusAntGui = None
    
    def __init__(self, master=true):
        self.master = master
        
    def set_gui(self, FortiusAntGui):
        self.FortiusAntGui = FortiusAntGui 

    def initialize(self):
        """Initialize interface."""
        self.interleave = 0

    def broadcast_message(self, *args):
        """Assemble the message to be sent."""
        message = self._broadcast_message(self.interleave, *args)
        if self.interleave == self.interleave_reset:
            self.interleave = 0
        self.interleave += 1
        return message

    def broadcast_message_from_trainer(self, TacxTrainer: clsTacxTrainer):
        raise NotImplementedError

    def _broadcast_message(self, interleave: int, *args):
        raise NotImplementedError

    def handle_received_info(self, channel: int, message_id: int, data_page_number: int, info: bytes):
        if channel != self.channel:
            raise WrongChannel
        _handle_received_info(message_id, data_page_number, info)
        
    def _handle_received_info(self, message_id: int, data_page_number: int, info: bytes):
        if message_id == msgID_ChannelID:
            _handle_channel_id_message(info)
        elif message_id == msgID_BroadcastMessage: 
            _handle_broadcast_message(data_page_number, info)
        elif message_id == msgID_AcknowledgedData:
            _handle_aknowledged_message(data_page_number, info)
     
            
    def _handle_channel_id_message(self, info: bytes):
        (
            Channel,
            DeviceNumber,
            DeviceTypeID,
            _TransmissionType,
        ) = ant.unmsg51_ChannelID(info)

        if DeviceNumber == 0:  # No device paired, ignore
            pass

        elif (
            Channel == self.channel
            and DeviceTypeID == self.device_type_id
        ):
            self.paired = True
            )

    def _handle_broadcast_message(self, data_page_number: int, info: bytes):
        raise NotImplementedError
        
    def _handle_aknowledged_message(self, data_page_number, info):
        raise NotImplementedError
            
class WrongChannel(Exception):
    pass
    
class UnknownMessageID(Exception)
    pass 