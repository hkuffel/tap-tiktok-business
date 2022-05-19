"""tap-tiktok-business tap class."""

from typing import List

from singer_sdk import Tap, Stream
from singer_sdk import typing as th  # JSON schema typing helpers

from tap_tiktok_business.streams import (
    TapTiktokBusinessStream,
    AccountsStream,
    VideosStream,
    CommentsStream,
)

STREAM_TYPES = [AccountsStream, VideosStream, CommentsStream]


class TapTiktokBusiness(Tap):
    """Tiktok Business tap class."""

    name = "tap_tiktok_business"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "client_id",
            th.StringType,
            required=True,
            description="Client ID for the TikTok Business API",
        ),
        th.Property(
            "client_secret",
            th.StringType,
            required=True,
            description="Client secret for the TikTok Business API",
        ),
        th.Property(
            "access_token",
            th.StringType,
            required=True,
            description="The token to authenticate against the API service",
        ),
        th.Property(
            "refresh_token",
            th.StringType,
            required=True,
            description="The token to generate a new access token",
        ),
        th.Property(
            "business_ids",
            th.ArrayType(th.StringType),
            required=True,
            description="unique ids for each TikTok business account to be queried",
        ),
        th.Property(
            "start_date",
            th.DateTimeType,
            description="The earliest record date to sync",
        ),
    ).to_dict()

    def discover_streams(self) -> List[Stream]:
        """Return a list of discovered streams."""
        return [stream_class(tap=self) for stream_class in STREAM_TYPES]
