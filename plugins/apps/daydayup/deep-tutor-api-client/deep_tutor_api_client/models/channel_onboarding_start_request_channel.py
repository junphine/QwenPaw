from typing import Literal

ChannelOnboardingStartRequestChannel = Literal["feishu", "wecom"]

CHANNEL_ONBOARDING_START_REQUEST_CHANNEL_VALUES: set[ChannelOnboardingStartRequestChannel] = {
    "feishu",
    "wecom",
}


def check_channel_onboarding_start_request_channel(value: str) -> ChannelOnboardingStartRequestChannel:
    if value in CHANNEL_ONBOARDING_START_REQUEST_CHANNEL_VALUES:
        return value
    raise TypeError(f"Unexpected value {value!r}. Expected one of {CHANNEL_ONBOARDING_START_REQUEST_CHANNEL_VALUES!r}")
