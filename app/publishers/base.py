from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class PublishResult:
    success: bool
    external_id: str | None = None
    error: str | None = None


class PublisherAdapter(ABC):
    """
    Base interface for all social-platform publishers.

    Each platform adapter must implement publish().
    """

    platform: str

    @abstractmethod
    def publish(
        self,
        content: str,
    ) -> PublishResult:
        """
        Publish content to the target platform.
        """
        raise NotImplementedError