"""Test subclasses of AntPage."""
import pytest

from fortius_ant.antMessage import AntMessage
from fortius_ant.antPage import AntPage

pages = AntPage.__subclasses__()


@pytest.mark.parametrize("page_type", pages)
def test_message(page_type: AntPage):
    """Test the given subclass of AntPage."""
    test_vector_length = len(page_type.message_format) - 2
    test_vector = (0,) * test_vector_length
    page = page_type.page(*test_vector)
    message_id = 1
    assert AntMessage.decompose(AntMessage.compose(message_id, page))[3] == page
    assert AntMessage.decompose(AntMessage.compose(message_id, page))[2] == message_id
