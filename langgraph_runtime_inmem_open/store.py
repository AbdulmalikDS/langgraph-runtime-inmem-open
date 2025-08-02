"""
Store implementations for the open-source langgraph-runtime-inmem alternative
"""

import json
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Union


class BaseStore(ABC):
    """
    Abstract base class for stores.

    This defines the interface that all store implementations must follow.
    """

    @abstractmethod
    def get(
        self,
        namespace: Tuple[str, ...],
        key: str,
        *,
        refresh_ttl: Optional[bool] = None,
    ) -> Optional[Dict[str, Any]]:
        """Retrieve a single item"""

    @abstractmethod
    def put(
        self,
        namespace: Tuple[str, ...],
        key: str,
        value: Dict[str, Any],
        index: Union[bool, List[str], None] = None,
        *,
        ttl: Optional[float] = None,
    ) -> None:
        """Store or update an item"""

    @abstractmethod
    def delete(self, namespace: Tuple[str, ...], key: str) -> None:
        """Delete an item"""

    @abstractmethod
    def search(
        self,
        namespace_prefix: Tuple[str, ...],
        /,
        *,
        query: Optional[str] = None,
        filter: Optional[Dict[str, Any]] = None,
        limit: int = 10,
        offset: int = 0,
        refresh_ttl: Optional[bool] = None,
    ) -> List[Dict[str, Any]]:
        """Search for items within a namespace prefix"""

    @abstractmethod
    def list_namespaces(
        self,
        *,
        prefix: Optional[Tuple[str, ...]] = None,
        suffix: Optional[Tuple[str, ...]] = None,
        max_depth: Optional[int] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Tuple[str, ...]]:
        """List and filter namespaces in the store"""


class InMemoryStore(BaseStore):
    """
    In-memory dictionary-backed store with optional vector search.

    This is a simple in-memory implementation that stores data in Python dictionaries.
    Data is lost when the process exits.
    """

    def __init__(self, **kwargs):
        """
        Initialize the in-memory store.

        Args:
            **kwargs: Additional configuration options (currently unused)
        """
        self._data = {}
        self._namespaces = set()
        self._ttl_data = {}  # Store TTL information
        self._index_config = kwargs.get("index", None)

    def get(
        self,
        namespace: Tuple[str, ...],
        key: str,
        *,
        refresh_ttl: Optional[bool] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve a single item.

        Args:
            namespace: Hierarchical path for the item
            key: Unique identifier within the namespace
            refresh_ttl: Whether to refresh TTL (ignored in this implementation)

        Returns:
            The retrieved item or None if not found
        """
        ns_key = self._make_key(namespace, key)
        return self._data.get(ns_key)

    def put(
        self,
        namespace: Tuple[str, ...],
        key: str,
        value: Dict[str, Any],
        index: Union[bool, List[str], None] = None,
        *,
        ttl: Optional[float] = None,
    ) -> None:
        """
        Store or update an item in the store.

        Args:
            namespace: Hierarchical path for the item
            key: Unique identifier within the namespace
            value: Dictionary containing the item's data
            index: Controls indexing (ignored in this implementation)
            ttl: Time to live in minutes (ignored in this implementation)
        """
        ns_key = self._make_key(namespace, key)
        self._data[ns_key] = value
        self._namespaces.add(namespace)

        if ttl is not None:
            self._ttl_data[ns_key] = time.time() + (ttl * 60)

    def delete(self, namespace: Tuple[str, ...], key: str) -> None:
        """
        Delete an item.

        Args:
            namespace: Hierarchical path for the item
            key: Unique identifier within the namespace
        """
        ns_key = self._make_key(namespace, key)
        self._data.pop(ns_key, None)
        self._ttl_data.pop(ns_key, None)

    def search(
        self,
        namespace_prefix: Tuple[str, ...],
        /,
        *,
        query: Optional[str] = None,
        filter: Optional[Dict[str, Any]] = None,
        limit: int = 10,
        offset: int = 0,
        refresh_ttl: Optional[bool] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for items within a namespace prefix.

        Args:
            namespace_prefix: The namespace prefix to search within
            query: Search query (ignored in this implementation)
            filter: Filter criteria for the search
            limit: Maximum number of results to return
            offset: Number of results to skip
            refresh_ttl: Whether to refresh TTL (ignored in this implementation)

        Returns:
            List of matching items
        """
        results = []
        prefix_str = self._make_key(namespace_prefix, "")

        for ns_key, value in self._data.items():
            if ns_key.startswith(prefix_str):
                if filter is None or self._matches_filter(value, filter):
                    results.append(value)

        # Apply offset and limit
        results = results[offset : offset + limit]
        return results

    def list_namespaces(
        self,
        *,
        prefix: Optional[Tuple[str, ...]] = None,
        suffix: Optional[Tuple[str, ...]] = None,
        max_depth: Optional[int] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Tuple[str, ...]]:
        """
        List and filter namespaces in the store.

        Args:
            prefix: Filter namespaces that start with this prefix
            suffix: Filter namespaces that end with this suffix
            max_depth: Maximum depth of namespaces to return
            limit: Maximum number of namespaces to return
            offset: Number of namespaces to skip

        Returns:
            List of namespace tuples
        """
        namespaces = list(self._namespaces)

        # Apply filters
        if prefix is not None:
            namespaces = [ns for ns in namespaces if ns[: len(prefix)] == prefix]

        if suffix is not None:
            namespaces = [ns for ns in namespaces if ns[-len(suffix) :] == suffix]

        if max_depth is not None:
            namespaces = [ns for ns in namespaces if len(ns) <= max_depth]

        # Apply offset and limit
        namespaces = namespaces[offset : offset + limit]
        return namespaces

    def _make_key(self, namespace: Tuple[str, ...], key: str) -> str:
        """Create a key from namespace and key"""
        return f"{':'.join(namespace)}:{key}"

    def _matches_filter(
        self, value: Dict[str, Any], filter_dict: Dict[str, Any]
    ) -> bool:
        """Check if a value matches the filter criteria"""
        for filter_key, filter_value in filter_dict.items():
            if filter_key not in value or value[filter_key] != filter_value:
                return False
        return True


class DiskBackedInMemStore(InMemoryStore):
    """
    Disk-backed in-memory store with persistence.

    This extends InMemoryStore to provide disk persistence across process restarts.
    """

    def __init__(self, persist_path: Optional[str] = None, **kwargs):
        """
        Initialize the disk-backed store.

        Args:
            persist_path: Path to the persistence file
            **kwargs: Additional configuration options
        """
        super().__init__(**kwargs)
        self.persist_path = persist_path
        if persist_path:
            self._load_from_disk()

    def _load_from_disk(self):
        """Load data from disk if available"""
        try:
            with open(self.persist_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._data = data.get("data", {})
                self._namespaces = set(data.get("namespaces", []))
                self._ttl_data = data.get("ttl_data", {})
        except (FileNotFoundError, json.JSONDecodeError):
            # File doesn't exist or is invalid, start with empty state
            pass

    def _save_to_disk(self):
        """Save data to disk"""
        if self.persist_path:
            data = {
                "data": self._data,
                "namespaces": list(self._namespaces),
                "ttl_data": self._ttl_data,
            }
            with open(self.persist_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

    def put(
        self,
        namespace: Tuple[str, ...],
        key: str,
        value: Dict[str, Any],
        index: Union[bool, List[str], None] = None,
        *,
        ttl: Optional[float] = None,
    ) -> None:
        """Store an item and persist to disk"""
        super().put(namespace, key, value, index, ttl=ttl)
        self._save_to_disk()

    def delete(self, namespace: Tuple[str, ...], key: str) -> None:
        """Delete an item and update disk"""
        super().delete(namespace, key)
        self._save_to_disk()


def Store(*args, **kwargs):
    """
    Factory function to create a store instance.

    This provides a convenient way to create store instances with different
    configurations.

    Args:
        *args: Positional arguments passed to the store constructor
        **kwargs: Keyword arguments passed to the store constructor

    Returns:
        A store instance
    """
    return InMemoryStore(*args, **kwargs)
