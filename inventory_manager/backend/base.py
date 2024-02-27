from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Update:
    # row, column
    location: tuple[int, int]
    data: str


class Table(ABC):
    @abstractmethod
    def get_data(self, sheet: str) -> list[list[str]]:
        raise NotImplementedError()

    @abstractmethod
    def update(self, sheet: str, updates: list[Update]) -> None:
        raise NotImplementedError()

    @abstractmethod
    def list_sheets(self) -> list[str]:
        raise NotImplementedError()


class AccessKey(ABC):
    @dataclass
    class TableName:
        name: str
        id: str

    @abstractmethod
    def list_tables(self, filter: str) -> list[TableName]:
        raise NotImplementedError()

    @abstractmethod
    def get_table(self, id: str) -> Table:
        raise NotImplementedError()
