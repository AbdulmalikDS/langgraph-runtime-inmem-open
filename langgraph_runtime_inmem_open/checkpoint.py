"""
Checkpoint implementations for the open-source langgraph-runtime-inmem alternative
"""

import json
import time
from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Any, Dict, Optional


class BaseCheckpointSaver(ABC):
    """
    Abstract base class for checkpoint savers.

    This defines the interface that all checkpoint implementations must follow.
    """

    @abstractmethod
    def get(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """Get a checkpoint for a thread"""

    @abstractmethod
    def put(self, thread_id: str, checkpoint: Dict[str, Any]) -> None:
        """Save a checkpoint for a thread"""

    @abstractmethod
    def delete(self, thread_id: str) -> None:
        """Delete a checkpoint for a thread"""


class MemorySaver(BaseCheckpointSaver):
    """
    An in-memory checkpoint saver.

    This checkpoint saver stores checkpoints in memory using a dictionary.
    Checkpoints are lost when the process exits.
    """

    def __init__(self):
        """Initialize the memory saver"""
        self._checkpoints = {}
        self._metadata = {}  # Store metadata like timestamps

    def __enter__(self):
        """Enter context manager"""
        return CheckpointContext(self, "default")

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager"""

    def get(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a checkpoint for a thread.

        Args:
            thread_id: The thread identifier

        Returns:
            The checkpoint data or None if not found
        """
        return self._checkpoints.get(thread_id)

    def put(self, thread_id: str, checkpoint: Dict[str, Any]) -> None:
        """
        Save a checkpoint for a thread.

        Args:
            thread_id: The thread identifier
            checkpoint: The checkpoint data to save
        """
        self._checkpoints[thread_id] = checkpoint
        self._metadata[thread_id] = {
            "timestamp": time.time(),
            "size": len(str(checkpoint)),
        }

    def delete(self, thread_id: str) -> None:
        """
        Delete a checkpoint for a thread.

        Args:
            thread_id: The thread identifier
        """
        self._checkpoints.pop(thread_id, None)
        self._metadata.pop(thread_id, None)

    def list_threads(self) -> list[str]:
        """
        List all thread IDs that have checkpoints.

        Returns:
            List of thread IDs
        """
        return list(self._checkpoints.keys())

    def get_metadata(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a thread.

        Args:
            thread_id: The thread identifier

        Returns:
            Metadata dictionary or None if not found
        """
        return self._metadata.get(thread_id)

    def clear_all(self) -> None:
        """Clear all checkpoints and metadata"""
        self._checkpoints.clear()
        self._metadata.clear()

    def __len__(self) -> int:
        """Return the number of checkpoints"""
        return len(self._checkpoints)

    def __contains__(self, thread_id: str) -> bool:
        """Check if a thread has a checkpoint"""
        return thread_id in self._checkpoints


class DiskBackedMemorySaver(MemorySaver):
    """
    A disk-backed memory saver that persists checkpoints to disk.

    This extends the MemorySaver to provide persistence across process restarts.
    """

    def __init__(self, persist_path: Optional[str] = None):
        """
        Initialize the disk-backed memory saver.

        Args:
            persist_path: Path to the persistence file
        """
        super().__init__()
        self.persist_path = persist_path
        if persist_path:
            self._load_from_disk()

    def _load_from_disk(self):
        """Load checkpoints from disk if available"""
        try:
            with open(self.persist_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._checkpoints = data.get("checkpoints", {})
                self._metadata = data.get("metadata", {})
        except (FileNotFoundError, json.JSONDecodeError):
            # File doesn't exist or is invalid, start with empty state
            pass

    def _save_to_disk(self):
        """Save checkpoints to disk"""
        if self.persist_path:
            data = {
                "checkpoints": self._checkpoints,
                "metadata": self._metadata,
            }
            with open(self.persist_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

    def put(self, thread_id: str, checkpoint: Dict[str, Any]) -> None:
        """Save a checkpoint and persist to disk"""
        super().put(thread_id, checkpoint)
        self._save_to_disk()

    def delete(self, thread_id: str) -> None:
        """Delete a checkpoint and update disk"""
        super().delete(thread_id)
        self._save_to_disk()

    def clear_all(self) -> None:
        """Clear all checkpoints and update disk"""
        super().clear_all()
        self._save_to_disk()


class CheckpointContext:
    """
    Context manager for checkpoint operations.

    This provides a convenient way to work with checkpoints in a context.
    """

    def __init__(self, saver: BaseCheckpointSaver, thread_id: str):
        """
        Initialize the checkpoint context.

        Args:
            saver: The checkpoint saver to use
            thread_id: The thread identifier
        """
        self.saver = saver
        self.thread_id = thread_id

    def __enter__(self):
        """Enter the context"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context"""

    def save(self, checkpoint: Dict[str, Any]) -> None:
        """Save a checkpoint"""
        self.saver.put(self.thread_id, checkpoint)

    def load(self) -> Optional[Dict[str, Any]]:
        """Load a checkpoint"""
        return self.saver.get(self.thread_id)


@contextmanager
def checkpoint_context(saver: BaseCheckpointSaver, thread_id: str):
    """
    Context manager for checkpoint operations.

    Args:
        saver: The checkpoint saver to use
        thread_id: The thread identifier

    Yields:
        A CheckpointContext object
    """
    context = CheckpointContext(saver, thread_id)
    try:
        yield context
    finally:
        # Context cleanup if needed
        pass


class AsyncMemorySaver(MemorySaver):
    """
    Async version of the memory saver.

    This provides async versions of the checkpoint operations.
    """

    async def aget(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """Async version of get"""
        return self.get(thread_id)

    async def aput(self, thread_id: str, checkpoint: Dict[str, Any]) -> None:
        """Async version of put"""
        self.put(thread_id, checkpoint)

    async def adelete(self, thread_id: str) -> None:
        """Async version of delete"""
        self.delete(thread_id)

    async def alist_threads(self) -> list[str]:
        """Async version of list_threads"""
        return self.list_threads()

    async def aclear_all(self) -> None:
        """Async version of clear_all"""
        self.clear_all()
