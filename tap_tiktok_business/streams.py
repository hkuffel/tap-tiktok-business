"""Stream type classes for tap-tiktok-business."""

import copy
import json
from pathlib import Path
from typing import Any, Dict, Optional, Union, List, Iterable, cast

import requests
from singer_sdk import typing as th  # JSON Schema typing helpers

from tap_tiktok_business.client import TapTiktokBusinessStream

SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")


class AccountsStream(TapTiktokBusinessStream):
    """Business account data"""

    name = "accounts"
    path = "/get/"
    primary_keys = ["business_id"]
    replication_key = None
    schema_filepath = SCHEMAS_DIR / "accounts.schema.json"
    rest_method = "POST"
    fields = [
        "username",
        "display_name",
        "profile_image",
        "audience_countries",
        "audience_genders",
        "likes",
        "comments",
        "shares",
        "followers_count",
        "profile_views",
        "video_views",
        "audience_activity",
    ]

    @property
    def partitions(self) -> Optional[List[dict]]:
        return [
            {"business_id": business_id}
            for business_id in self.config.get("business_ids")
        ]

    def get_child_context(self, record: dict, context: Optional[dict]) -> dict:
        return {"business_id": context["business_id"]}


class VideosStream(TapTiktokBusinessStream):
    """Define custom stream."""

    name = "videos"
    path = "/videos/list/"
    parent_stream_type = AccountsStream
    primary_keys = ["item_id"]
    replication_key = "create_time"
    rest_method = "POST"
    fields = [
        "item_id",
        "create_time",
        "thumbnail_url",
        "share_url",
        "embed_url",
        "caption",
        "video_views",
        "likes",
        "comments",
        "shares",
        "reach",
        "video_duration",
        "full_video_watched_rate",
        "total_time_watched",
        "average_time_watched",
        "impression_sources",
        "audience_countries",
    ]
    schema_filepath = SCHEMAS_DIR / "videos.schema.json"

    def get_child_context(self, record: dict, context: Optional[dict]) -> dict:
        return {"business_id": context["business_id"], "video_id": record["item_id"]}

    def parse_response(
        self, response: requests.Response, context: Optional[dict]
    ) -> Iterable[dict]:
        resp_json = response.json()
        try:
            for row in resp_json["data"]["videos"]:
                row["business_id"] = context["business_id"]
                yield row
        except KeyError:
            self.logger.info("failed to parse response: {}".format(resp_json))


class CommentsStream(TapTiktokBusinessStream):
    """Define custom stream."""

    name = "comments"
    path = "/comments/list/"
    parent_stream_type = VideosStream
    primary_keys = ["comment_id"]
    replication_key = "create_time"
    rest_method = "POST"
    schema_filepath = SCHEMAS_DIR / "comments.schema.json"

    def prepare_request_payload(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Optional[dict]:
        """Prepare the data payload for the REST API request.

        By default, no payload will be sent (return None).
        """
        payload: Dict = {}
        payload["business_id"] = context["business_id"]
        payload["video_id"] = context["video_id"]
        if self.fields:
            payload["fields"] = self.fields
        if next_page_token:
            payload["cursor"] = next_page_token

        return payload

    def parse_response(
        self, response: requests.Response, context: Optional[dict]
    ) -> Iterable[dict]:
        resp_json = response.json()
        try:
            for row in resp_json["data"]["comments"]:
                row["business_id"] = context["business_id"]
                yield row
        except KeyError:
            self.logger.info("No comments found")
