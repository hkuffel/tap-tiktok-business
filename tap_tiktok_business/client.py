"""REST client handling, including TapTiktokBusinessStream base class."""

import copy
import requests
from pathlib import Path
from typing import Any, cast, Dict, Optional, Union, List, Iterable

from memoization import cached
from singer_sdk.helpers.jsonpath import extract_jsonpath
from singer_sdk.streams import RESTStream

from tap_tiktok_business.auth import OAuthAuthenticator


SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")


class TapTiktokBusinessStream(RESTStream):
    """TapTiktokBusinessStream stream class."""

    records_jsonpath = "$[*]"
    url_base = "https://business-api.tiktok.com/open_api/v1.2/business"
    fields = None  # Account and Video streams will use this

    @property
    @cached
    def authenticator(self) -> OAuthAuthenticator:
        """Return a new authenticator object."""
        return OAuthAuthenticator(
            self,
            auth_endpoint="https://business-api.tiktok.com/open_api/oauth2/token/?business=tt_user",
        )

    @property
    def http_headers(self) -> dict:
        """Return the http headers needed."""
        headers = {
            "Content-Type": "application/json",
        }
        if "user_agent" in self.config:
            headers["User-Agent"] = self.config.get("user_agent")
        return headers

    def get_next_page_token(
        self, response: requests.Response, previous_token: Optional[Any]
    ) -> Optional[Any]:
        """Return a token for identifying next page or None if no more pages."""
        try:
            resp_json = response.json()
            if self.name != "accounts":
                if resp_json["data"]["has_more"]:
                    return resp_json["data"]["cursor"]
                else:
                    return None
        except KeyError:
            return None

    def get_url_params(
        self, context: Optional[dict], next_page_token: Optional[Any] = None
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization.
        params like business id and fields are actually added in the
        prepare_request_payload method due to the idiosyncrasies of the
        tiktok api.
        """
        params: Dict = super().get_url_params(context, next_page_token)
        if self.replication_key:
            params["sort"] = "asc"
            params["order_by"] = self.replication_key
        return params

    def request_records(self, context: Optional[dict]) -> Iterable[dict]:
        """Request records from REST endpoint(s), returning response records.

        If pagination is detected, pages will be recursed automatically.

        Args:
            context: Stream partition or context dictionary.

        Yields:
            An item for every record in the response.

        Raises:
            RuntimeError: If a loop in pagination is detected. That is, when two
                consecutive pagination tokens are identical.
        """
        next_page_token: Any = None
        finished = False
        decorated_request = self.request_decorator(self._request)

        while not finished:
            prepared_request = self.prepare_request(
                context, next_page_token=next_page_token
            )
            resp = decorated_request(prepared_request, context)

            # edited from the parent class to include context as an argument
            yield from self.parse_response(resp, context=context)
            previous_token = copy.deepcopy(next_page_token)
            next_page_token = self.get_next_page_token(
                response=resp, previous_token=previous_token
            )
            if next_page_token and next_page_token == previous_token:
                raise RuntimeError(
                    f"Loop detected in pagination. "
                    f"Pagination token {next_page_token} is identical to prior token."
                )
            # Cycle until get_next_page_token() no longer returns a value
            finished = not next_page_token

    def prepare_request_payload(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Optional[dict]:
        """Prepare the data payload for the REST API request.

        By default, no payload will be sent (return None).
        """
        payload: Dict = {}
        payload["business_id"] = context["business_id"]
        if self.fields:
            payload["fields"] = self.fields
        if next_page_token:
            payload["cursor"] = next_page_token
        return payload

    def parse_response(
        self, response: requests.Response, context: Optional[dict]
    ) -> Iterable[dict]:
        """Parse the response and return an iterator of result rows."""
        # TODO: Parse response body and return a set of records.
        yield from extract_jsonpath(self.records_jsonpath, input=response.json())
