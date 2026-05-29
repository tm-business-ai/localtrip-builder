from decimal import Decimal

import requests
from django.conf import settings


class GoogleMapsConfigurationError(ValueError):
    pass


class GoogleGeocodingError(ValueError):
    pass


def _has_valid_api_key(api_key: str) -> bool:
    if not api_key:
        return False
    return not api_key.startswith("dummy-")


class GoogleGeocodingClient:
    def __init__(self, api_key=None, endpoint=None, timeout=10):
        self.api_key = api_key if api_key is not None else settings.GOOGLE_MAPS_API_KEY
        self.endpoint = endpoint or settings.GOOGLE_MAPS_GEOCODING_ENDPOINT
        self.timeout = timeout

    def geocode(self, address: str) -> dict:
        if not _has_valid_api_key(self.api_key):
            raise GoogleMapsConfigurationError(
                "Google Maps APIキーが設定されていません。GOOGLE_MAPS_API_KEY を .env に設定してください。"
            )
        if not address or not address.strip():
            raise GoogleGeocodingError("Geocoding APIに送信する住所が空です。")

        try:
            response = requests.get(
                self.endpoint,
                params={
                    "address": address,
                    "key": self.api_key,
                    "language": "ja",
                },
                timeout=self.timeout,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            raise GoogleGeocodingError(
                "Google Geocoding APIへの接続に失敗しました。"
            ) from exc
        payload = response.json()
        status = payload.get("status")

        if status != "OK":
            raise GoogleGeocodingError(f"Google Geocoding API error: {status}")

        results = payload.get("results") or []
        if not results:
            raise GoogleGeocodingError("Google Geocoding APIから結果が返されませんでした。")

        first_result = results[0]
        location = first_result.get("geometry", {}).get("location", {})
        lat = location.get("lat")
        lng = location.get("lng")
        if lat is None or lng is None:
            raise GoogleGeocodingError("Google Geocoding APIの応答に緯度経度がありません。")

        return {
            "latitude": Decimal(str(lat)),
            "longitude": Decimal(str(lng)),
            "formatted_address": first_result.get("formatted_address", ""),
            "place_id": first_result.get("place_id", ""),
            "raw_response": payload,
        }
