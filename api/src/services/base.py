from typing import Optional, TypeVar, Generic, List
from datetime import datetime

T = TypeVar('T')

class BaseService(Generic[T]):
    def __init__(self):
        self.model = None

    async def get_by_id(self, id: str) -> Optional[T]:
        raise NotImplementedError

    async def get_connection(
        self,
        first: int = 20,
        after: Optional[str] = None,
        **filters
    ) -> tuple[List[T], bool, int]:
        """
        Returns a tuple of (items, has_next_page, total_count)
        """
        raise NotImplementedError

    def create_cursor(self, item: T) -> str:
        """
        Creates a cursor for pagination based on the item
        """
        if hasattr(item, 'id'):
            return str(item.id)
        raise NotImplementedError

    def decode_cursor(self, cursor: str) -> any:
        """
        Decodes a cursor into a value that can be used for filtering
        """
        try:
            return int(cursor)
        except ValueError:
            return cursor 