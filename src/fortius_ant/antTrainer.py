from fortius_ant.ant.interface import AntInterface, UnknownDataPage
from fortius_ant.antPage import Page221_01, Page221_02, Page221_03


class AntTrainer(AntInterface):
    """Ant Trainer interface."""

    channel = 5

    def _handle_broadcast_message(self, data_page_number: int, info: bytes):
        if data_page_number == 173:
            sub_page_number = info[2]
            print(f"Page {data_page_number}, sub page: {sub_page_number}")

        elif data_page_number == 221:
            sub_page_number = info[2]
            if sub_page_number == 1:
                print(f"221_01: {Page221_01.unpage(info)[3:]}")
            elif sub_page_number == 2:
                print(f"221_02: {Page221_02.unpage(info)[3:]}")
            elif sub_page_number == 3:
                print(f"221_03: {Page221_03.unpage(info)[3:]}")
            else:
                print(f"Page {data_page_number}, sub page: {sub_page_number}")
        else:
            raise UnknownDataPage(data_page_number)

    def _handle_acknowledged_message(self, data_page_number, info):
        print(f"Acknowledged: {data_page_number}: {info}")
