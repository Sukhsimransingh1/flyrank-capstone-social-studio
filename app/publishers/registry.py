from app.publishers.base import PublisherAdapter
from app.publishers.mock import MockPublisherAdapter


class PublisherRegistry:
    """
    Resolves a platform name to its publisher adapter.
    """

    def __init__(self) -> None:
        self._publishers: dict[str, PublisherAdapter] = {}

        self.register(MockPublisherAdapter())

    def register(self, publisher: PublisherAdapter) -> None:
        self._publishers[publisher.platform] = publisher

    def get(self, platform: str) -> PublisherAdapter:
        try:
            return self._publishers[platform]
        except KeyError:
            raise ValueError(
                f"Unsupported publishing platform: {platform}"
            )


publisher_registry = PublisherRegistry()