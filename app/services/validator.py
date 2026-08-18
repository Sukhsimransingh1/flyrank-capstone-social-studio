import re

from app.services.platform_profiles import (
    PLATFORM_PROFILES,
    PlatformProfile,
)


def count_hashtags(content: str) -> int:
    return len(re.findall(r"(?<!\w)#\w+", content))


def validate_variant(
    content: str,
    platform: str,
) -> list[str]:
    profile: PlatformProfile | None = PLATFORM_PROFILES.get(platform)

    if profile is None:
        return [f"Unsupported platform: {platform}"]

    errors: list[str] = []

    if len(content) > profile.max_length:
        errors.append(
            f"Content length {len(content)} exceeds "
            f"{platform} limit of {profile.max_length}."
        )

    hashtag_count = count_hashtags(content)

    if hashtag_count > profile.max_hashtags:
        errors.append(
            f"Hashtag count {hashtag_count} exceeds "
            f"{platform} limit of {profile.max_hashtags}."
        )

    return errors