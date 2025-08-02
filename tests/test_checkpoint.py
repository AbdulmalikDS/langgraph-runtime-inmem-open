"""
Tests for the checkpoint module
"""

import pytest

from langgraph_runtime_inmem_open.checkpoint import (
    AsyncMemorySaver,
    BaseCheckpointSaver,
    CheckpointContext,
    DiskBackedMemorySaver,
    MemorySaver,
)


class TestBaseCheckpointSaver:
    """Test the abstract checkpoint saver interface"""

    def test_interface_abstract(self):
        """Test that BaseCheckpointSaver cannot be instantiated"""
        with pytest.raises(TypeError):
            BaseCheckpointSaver()


class TestMemorySaver:
    """Test the memory saver implementation"""

    def test_initialization(self):
        """Test memory saver initialization"""
        saver = MemorySaver()
        assert saver._checkpoints == {}
        assert saver._metadata == {}


class TestMemorySaverOperations:
    """Test the memory saver operations"""

    def setup_method(self):
        """Setup before each test"""
        self.saver = MemorySaver()

    def test_basic_operations(self):
        """Test basic memory saver operations"""
        # Test that the saver can be instantiated
        assert self.saver is not None
        assert hasattr(self.saver, "_checkpoints")
        assert hasattr(self.saver, "_metadata")

    def test_context_manager(self):
        """Test the memory saver as a context manager"""
        with self.saver as saver:
            # Test that we can use the saver in a context
            assert saver is not None


class TestCheckpointerIntegration:
    """Integration tests for checkpointer functionality"""

    def test_memory_saver_types(self):
        """Test different memory saver types"""
        # Test basic memory saver
        basic_saver = MemorySaver()
        assert basic_saver is not None

        # Test disk-backed memory saver
        disk_saver = DiskBackedMemorySaver()
        assert disk_saver is not None

        # Test async memory saver
        async_saver = AsyncMemorySaver()
        assert async_saver is not None

    def test_checkpoint_context(self):
        """Test checkpoint context functionality"""
        # Test that we can create a checkpoint context
        saver = MemorySaver()
        context = CheckpointContext(saver, "test_thread")
        assert context is not None
