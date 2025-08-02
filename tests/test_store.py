"""
Tests for the store module
"""

import pytest

from langgraph_runtime_inmem_open.store import (
    BaseStore,
    InMemoryStore,
)


class TestBaseStore:
    """Test the abstract store interface"""

    def test_interface_abstract(self):
        """Test that BaseStore cannot be instantiated"""
        with pytest.raises(TypeError):
            BaseStore()


class TestStoreInitialization:
    """Test the store initialization"""

    def test_default_initialization(self):
        """Test default initialization"""
        store = InMemoryStore()
        assert store._data == {}
        assert store._namespaces == set()
        assert store._ttl_data == {}

    def test_custom_initialization(self):
        """Test custom initialization"""
        store = InMemoryStore(index=True)
        assert store._index_config is True


class TestInMemoryStore:
    """Test the synchronous in-memory store"""

    def setup_method(self):
        """Setup before each test"""
        self.store = InMemoryStore()

    def test_initialization(self):
        """Test store initialization"""
        assert self.store._data == {}
        assert self.store._namespaces == set()
        assert self.store._ttl_data == {}

    def test_put_and_get(self):
        """Test basic put and get operations"""
        namespace = ("test", "namespace")
        key = "key1"
        value = {"data": "value1"}

        # Put a value
        self.store.put(namespace, key, value)

        # Get the value
        result = self.store.get(namespace, key)
        assert result == value

    def test_get_nonexistent_key(self):
        """Test getting a key that doesn't exist"""
        namespace = ("test", "namespace")
        result = self.store.get(namespace, "nonexistent")
        assert result is None

    def test_put_overwrite(self):
        """Test overwriting an existing key"""
        namespace = ("test", "namespace")
        key = "key1"

        # Set initial value
        self.store.put(namespace, key, {"data": "old_value"})

        # Overwrite with new value
        self.store.put(namespace, key, {"data": "new_value"})

        # Verify new value
        result = self.store.get(namespace, key)
        assert result == {"data": "new_value"}

    def test_delete(self):
        """Test deleting a key"""
        namespace = ("test", "namespace")
        key = "key1"
        value = {"data": "value1"}

        # Put a value
        self.store.put(namespace, key, value)

        # Verify it exists
        assert self.store.get(namespace, key) == value

        # Delete the key
        self.store.delete(namespace, key)

        # Verify it's gone
        assert self.store.get(namespace, key) is None

    def test_delete_nonexistent_key(self):
        """Test deleting a key that doesn't exist"""
        namespace = ("test", "namespace")
        # Should not raise an exception
        self.store.delete(namespace, "nonexistent")

    def test_search(self):
        """Test searching for items"""
        namespace = ("test", "namespace")

        # Add some data
        self.store.put(namespace, "key1", {"data": "value1", "type": "test"})
        self.store.put(namespace, "key2", {"data": "value2", "type": "test"})

        # Search for items
        results = self.store.search(namespace, filter={"type": "test"})
        assert len(results) == 2

        # Search with specific criteria
        results = self.store.search(namespace, filter={"data": "value1"})
        assert len(results) == 1
        assert results[0]["data"] == "value1"

    def test_list_namespaces(self):
        """Test listing namespaces"""
        # Add data to different namespaces
        self.store.put(("ns1",), "key1", {"data": "value1"})
        self.store.put(("ns2",), "key1", {"data": "value2"})

        # List namespaces
        namespaces = self.store.list_namespaces()
        assert ("ns1",) in namespaces
        assert ("ns2",) in namespaces


class TestStoreIntegration:
    """Integration tests for store functionality"""

    def test_store_methods(self):
        """Test that store has the required methods"""
        store = InMemoryStore()
        required_methods = ["get", "put", "delete", "search", "list_namespaces"]

        for method in required_methods:
            assert hasattr(store, method)

    def test_namespace_operations(self):
        """Test namespace-based operations"""
        store = InMemoryStore()

        # Test different namespaces
        ns1 = ("user", "123")
        ns2 = ("user", "456")

        # Add data to different namespaces
        store.put(ns1, "key1", {"data": "value1"})
        store.put(ns2, "key1", {"data": "value2"})

        # Verify data is isolated by namespace
        assert store.get(ns1, "key1") == {"data": "value1"}
        assert store.get(ns2, "key1") == {"data": "value2"}

        # List namespaces
        namespaces = store.list_namespaces()
        assert ns1 in namespaces
        assert ns2 in namespaces
