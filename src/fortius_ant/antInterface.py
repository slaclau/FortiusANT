"""Provide an inheritable class for implemented an ANT+ device."""


class AntInterface:
    """Interface for communicating as an ANT+ device."""

    def Initialize(self):
        """Initialize interface."""
        raise NotImplementedError

    def BroadcastMessage(self):
        """Assemble the message to be sent."""
        raise NotImplementedError
