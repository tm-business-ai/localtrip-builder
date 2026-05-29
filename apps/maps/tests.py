from decimal import Decimal
from unittest.mock import Mock, patch

import requests
from django.test import SimpleTestCase, override_settings

from .geocoding import (
    GoogleGeocodingClient,
    GoogleGeocodingError,
    GoogleMapsConfigurationError,
)
from .services import (
    build_google_maps_directions_url,
    build_google_maps_lat_lng_url,
    build_google_maps_place_url,
    build_google_maps_search_url,
)


class GoogleMapsUrlTests(SimpleTestCase):
    def test_build_search_url_does_not_require_api_key(self):
        url = build_google_maps_search_url("宮崎市 青島")

        self.assertEqual(
            url,
            "https://www.google.com/maps/search/?api=1&query=%E5%AE%AE%E5%B4%8E%E5%B8%82+%E9%9D%92%E5%B3%B6",
        )

    def test_build_lat_lng_url(self):
        url = build_google_maps_lat_lng_url(Decimal("31.805500"), Decimal("131.475000"))

        self.assertIn("31.805500%2C131.475000", url)

    def test_build_place_url_joins_name_and_address(self):
        url = build_google_maps_place_url("青島", "宮崎県宮崎市")

        self.assertIn("%E9%9D%92%E5%B3%B6+%E5%AE%AE%E5%B4%8E%E7%9C%8C", url)

    def test_build_directions_url_requires_two_or_more_spots(self):
        url = build_google_maps_directions_url(
            [{"name": "青島", "address": "宮崎県宮崎市"}]
        )

        self.assertEqual(url, "")

    def test_build_directions_url_from_spot_dicts_without_api_key(self):
        url = build_google_maps_directions_url(
            [
                {"name": "青島", "address": "宮崎県宮崎市青島"},
                {"name": "宮崎神宮", "address": "宮崎県宮崎市神宮"},
            ]
        )

        self.assertIn("https://www.google.com/maps/dir/?api=1", url)
        self.assertIn("origin=%E9%9D%92%E5%B3%B6", url)
        self.assertIn("destination=%E5%AE%AE%E5%B4%8E%E7%A5%9E%E5%AE%AE", url)
        self.assertIn("travelmode=driving", url)

    def test_build_directions_url_uses_waypoints(self):
        url = build_google_maps_directions_url(
            [
                {"name": "A", "address": "宮崎県"},
                {"name": "B", "address": "宮崎県"},
                {"name": "C", "address": "宮崎県"},
            ],
            travelmode="walking",
        )

        self.assertIn("waypoints=B+", url)
        self.assertIn("travelmode=walking", url)

    def test_build_directions_url_prefers_lat_lng(self):
        url = build_google_maps_directions_url(
            [
                {"name": "A", "latitude": "31.805500", "longitude": "131.475000"},
                {"name": "B", "latitude": "31.915000", "longitude": "131.420000"},
            ]
        )

        self.assertIn("origin=31.805500%2C131.475000", url)
        self.assertIn("destination=31.915000%2C131.420000", url)


class GoogleGeocodingClientTests(SimpleTestCase):
    @override_settings(GOOGLE_MAPS_API_KEY="", GOOGLE_MAPS_GEOCODING_ENDPOINT="https://example.test/geocode")
    def test_geocoding_requires_api_key(self):
        client = GoogleGeocodingClient()

        with self.assertRaisesMessage(GoogleMapsConfigurationError, "Google Maps APIキー"):
            client.geocode("宮崎県宮崎市青島")

    @override_settings(
        GOOGLE_MAPS_API_KEY="dummy-google-maps-api-key",
        GOOGLE_MAPS_GEOCODING_ENDPOINT="https://example.test/geocode",
    )
    def test_geocoding_rejects_dummy_api_key(self):
        client = GoogleGeocodingClient()

        with self.assertRaisesMessage(GoogleMapsConfigurationError, "Google Maps APIキー"):
            client.geocode("宮崎県宮崎市青島")

    @override_settings(
        GOOGLE_MAPS_API_KEY="test-google-maps-api-key",
        GOOGLE_MAPS_GEOCODING_ENDPOINT="https://example.test/geocode",
    )
    @patch("apps.maps.geocoding.requests.get")
    def test_geocoding_uses_requests_without_real_api_call(self, requests_get):
        response = Mock()
        response.json.return_value = {
            "status": "OK",
            "results": [
                {
                    "formatted_address": "宮崎県宮崎市青島",
                    "place_id": "place123",
                    "geometry": {
                        "location": {
                            "lat": 31.8055,
                            "lng": 131.475,
                        }
                    },
                }
            ],
        }
        requests_get.return_value = response

        result = GoogleGeocodingClient().geocode("宮崎県宮崎市青島")

        self.assertEqual(result["latitude"], Decimal("31.8055"))
        self.assertEqual(result["longitude"], Decimal("131.475"))
        requests_get.assert_called_once()
        _, kwargs = requests_get.call_args
        self.assertEqual(kwargs["params"]["address"], "宮崎県宮崎市青島")
        self.assertEqual(kwargs["params"]["key"], "test-google-maps-api-key")

    @override_settings(
        GOOGLE_MAPS_API_KEY="test-google-maps-api-key",
        GOOGLE_MAPS_GEOCODING_ENDPOINT="https://example.test/geocode",
    )
    @patch("apps.maps.geocoding.requests.get")
    def test_geocoding_non_ok_status_raises(self, requests_get):
        response = Mock()
        response.json.return_value = {"status": "ZERO_RESULTS", "results": []}
        requests_get.return_value = response

        with self.assertRaises(GoogleGeocodingError):
            GoogleGeocodingClient().geocode("存在しない住所")

    @override_settings(
        GOOGLE_MAPS_API_KEY="test-google-maps-api-key",
        GOOGLE_MAPS_GEOCODING_ENDPOINT="https://example.test/geocode",
    )
    @patch("apps.maps.geocoding.requests.get")
    def test_geocoding_request_error_does_not_expose_api_key(self, requests_get):
        requests_get.side_effect = requests.RequestException(
            "network error with secret test-google-maps-api-key"
        )

        with self.assertRaises(GoogleGeocodingError) as context:
            GoogleGeocodingClient().geocode("宮崎県宮崎市青島")

        self.assertNotIn("test-google-maps-api-key", str(context.exception))
