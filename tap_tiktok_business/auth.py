"Custom implementation of Meltano SDK OAuth authenticator class"

from datetime import datetime
import requests
from pathlib import Path
from typing import Any, cast, Dict, Optional, Union, List, Iterable

from singer import utils

from singer_sdk.helpers._util import utc_now
from singer_sdk.streams import Stream as RESTStreamBase
from singer_sdk.authenticators import APIAuthenticatorBase, SingletonMeta


class OAuthAuthenticator(APIAuthenticatorBase, metaclass=SingletonMeta):
    """API Authenticator for OAuth 2.0 flows."""

    def __init__(
        self,
        stream: RESTStreamBase,
        auth_endpoint: Optional[str] = None,
    ) -> None:
        """Create a new authenticator.

        Args:
            stream: The stream instance to use with this authenticator.
        """
        super().__init__(stream=stream)
        self._auth_endpoint = auth_endpoint
        self._default_expiration = 86400

        # Initialize internal tracking attributes
        self.access_token: Optional[str] = self.config.get("access_token")
        self.refresh_token: Optional[str] = self.config.get("refresh_token")
        self.last_refreshed: Optional[datetime] = None
        self.expires_in: Optional[int] = None

    @property
    def auth_headers(self) -> dict:
        """Return a dictionary of auth headers to be applied.

        These will be merged with any `http_headers` specified in the stream.

        Returns:
            HTTP headers for authentication.
        """
        if not self.is_token_valid():
            self.logger.info("Token is not valid, refreshing.")
            self.update_access_token()
        result = super().auth_headers
        result["Access-Token"] = f"{self.access_token}"
        return result

    @property
    def auth_endpoint(self) -> str:
        """Get the authorization endpoint.

        Returns:
            The API authorization endpoint if it is set.

        Raises:
            ValueError: If the endpoint is not set.
        """
        if not self._auth_endpoint:
            raise ValueError("Authorization endpoint not set.")
        return self._auth_endpoint

    @property
    def oauth_request_payload(self) -> dict:
        """Get request body.

        Returns:
            A plain (OAuth) or encrypted (JWT) request body.
        """
        return self.oauth_request_body

    @property
    def oauth_request_body(self) -> dict:
        """Get formatted body of the OAuth authorization request."""
        return {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token",
            "refresh_token": self.config["refresh_token"],
        }

    @property
    def client_id(self) -> Optional[str]:
        """Get client ID string to be used in authentication.

        Returns:
            Optional client secret from stream config if it has been set.
        """
        if self.config:
            return self.config.get("client_id")
        return None

    @property
    def client_secret(self) -> Optional[str]:
        """Get client secret to be used in authentication.

        Returns:
            Optional client secret from stream config if it has been set.
        """
        if self.config:
            return self.config.get("client_secret")
        return None

    def is_token_valid(self) -> bool:
        """Check if token is valid.

        Returns:
            True if the token is valid (fresh).
        """
        if self.last_refreshed is None or self.expires_in is None:
            return False
        if self.expires_in > (utils.now() - self.last_refreshed).total_seconds():
            return True
        return False

    # Authentication and refresh
    def update_access_token(self) -> None:
        """Update `access_token` along with: `last_refreshed` and `expires_in`.

        Raises:
            RuntimeError: When OAuth login fails.
        """
        request_time = utc_now()
        auth_request_payload = self.oauth_request_payload
        token_response = requests.post(
            url=self.auth_endpoint,
            json=auth_request_payload,
            headers={"Content-Type": "application/json"},
        )
        try:
            token_response.raise_for_status()
            self.logger.info("OAuth authorization attempt was successful.")
        except Exception as ex:
            raise RuntimeError(
                f"Failed OAuth login, response was '{token_response.json()}'. {ex}"
            )
        token_json = token_response.json()
        self.access_token = token_json["access_token"]
        self.expires_in = token_json.get("expires", self._default_expiration)
        self.refresh_expires_in = token_json.get("refresh_expires")
        if self.expires_in is None:
            self.logger.debug(
                "No expires_in receied in OAuth response and no "
                "default_expiration set. Token will be treated as if it never "
                "expires."
            )
        self.last_refreshed = request_time
