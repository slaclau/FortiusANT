"""Test subclasses of AntPage."""
import pytest

from fortius_ant.antPage import AntPage, FEPage16, FEPage25

pages = AntPage.__subclasses__()


@pytest.mark.parametrize("page_type", pages)
def test_page(page_type: AntPage):
    """Test the given subclass of AntPage."""
    test_vector_length = page_type.get_num_args()
    response_vector_length = len(page_type.message_format) - 2
    test_vector = (0,) * test_vector_length
    response_vector = (0,) * response_vector_length
    response_vector = (
        response_vector[0],
        page_type.data_page_number,
    ) + response_vector[1:]

    response = page_type.unpage(page_type.page(*test_vector))

    if page_type == FEPage16:
        for i in range(0, response_vector_length):
            if i != 2 & i != response_vector_length:
                assert response[i] == response_vector[i]
    elif page_type == FEPage25:
        for i in range(0, response_vector_length):
            if i != response_vector_length:
                assert response[i] == response_vector[i]
    else:
        assert response == response_vector
