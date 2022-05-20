"""Tests standard tap features using the built-in SDK tests library."""

import datetime
import os

from singer_sdk.helpers._util import read_json_file
from singer_sdk.testing import get_standard_tap_tests

from tap_tiktok_business.tap import TapTiktokBusiness

CONFIG_PATH = ".secrets/config.json"

if os.getenv("CI"):  # true when running a GitHub Actions workflow
    SAMPLE_CONFIG = {
        "client_id": os.getenv("TAP_TIKTOK_CLIENT_ID"),
        "client_secret": os.getenv("TAP_TIKTOK_CLIENT_SECRET"),
        "access_token": os.getenv("TAP_TIKTOK_ACCESS_TOKEN"),
        "refresh_token": os.getenv("TAP_TIKTOK_REFRESH_TOKEN"),
        "business_ids": os.getenv("TAP_TIKTOK_BUSINESS_ID").split(", "),
        "start_date": "2022-04-01T00:00:00Z",
    }
else:
    SAMPLE_CONFIG = read_json_file(CONFIG_PATH)


# Run standard built-in tap tests from the SDK:
def test_standard_tap_tests():
    """Run standard tap tests from the SDK."""
    tests = get_standard_tap_tests(TapTiktokBusiness, config=SAMPLE_CONFIG)
    for test in tests:
        test()


# TODO: Create additional tests as appropriate for your tap.
