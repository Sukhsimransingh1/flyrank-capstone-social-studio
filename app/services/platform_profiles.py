from dataclasses import dataclass


@dataclass(frozen=True)
class PlatformProfile:
    name: str
    max_length: int
    max_hashtags: int
    tone: str


PLATFORM_PROFILES = {
    "telegram": PlatformProfile(
        name="telegram",
        max_length=4096,
        max_hashtags=5,
        tone="conversational",
    ),
    "x": PlatformProfile(
        name="x",
        max_length=280,
        max_hashtags=3,
        tone="concise",
    ),
    "linkedin": PlatformProfile(
        name="linkedin",
        max_length=3000,
        max_hashtags=5,
        tone="professional",
    ),
}