from uuid import uuid4

from app.publishers.base import PublishResult, PublisherAdapter


class MockPublisherAdapter(PublisherAdapter):
    """
    Deterministic publisher used for development and testing.

    No external platform API is called.
    """

    platform = "mock"

    def publish(
        self,
        content: str,
    ) -> PublishResult:
        if not content.strip():
            return PublishResult(
                success=False,
                error="Content cannot be empty.",
            )

        external_id = f"mock_{uuid4()}"

        return PublishResult(
            success=True,
            external_id=external_id,
        )