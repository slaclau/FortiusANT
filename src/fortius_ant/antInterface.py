"""Provide an inheritable class for implemented an ANT+ device."""

__version__ = "2023-04-16"
# 2023-04-16    Rewritten in class based fashion


class AntInterface:
    """Interface for communicating as an ANT+ device."""

    interleave = 0
    interleave_reset: int

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

    def _broadcast_message(self, interleave: int, *args):
        raise NotImplementedError
