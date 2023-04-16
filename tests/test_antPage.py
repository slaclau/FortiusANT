"""Test subclasses of AntPage."""
import pytest

from fortius_ant.antPage import AntPage

pages = AntPage.__subclasses__()


@pytest.mark.parametrize("page_type", pages)
def test_page(page_type: AntPage):
    """Test the given subclass of AntPage."""
    test_vector_length = len(page_type.message_format) - 2
    test_vector = (0,) * test_vector_length
    response_vector = (
        test_vector[0],
        page_type.data_page_number,
    ) + test_vector[1:]
    assert page_type.unpage(page_type.page(*test_vector)) == response_vector
