from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from .models import Region, SpotCategory, TouristSpot


class RegionModelTests(TestCase):
    def test_str_returns_name(self):
        region = Region.objects.create(name="高千穂町", prefecture="宮崎県")

        self.assertEqual(str(region), "高千穂町")


class SpotCategoryModelTests(TestCase):
    def test_str_returns_name(self):
        category = SpotCategory.objects.create(name="自然", slug="nature")

        self.assertEqual(str(category), "自然")


class TouristSpotModelTests(TestCase):
    def setUp(self):
        self.region = Region.objects.create(name="宮崎市", prefecture="宮崎県")
        self.category = SpotCategory.objects.create(name="神社・仏閣", slug="shrines")

    def test_str_returns_name(self):
        spot = TouristSpot.objects.create(
            name="青島神社",
            slug="aoshima-shrine",
            region=self.region,
            category=self.category,
        )

        self.assertEqual(str(spot), "青島神社")

    def test_spot_belongs_to_region_and_category(self):
        spot = TouristSpot.objects.create(
            name="高千穂峡",
            slug="takachiho-gorge",
            region=self.region,
            category=self.category,
        )

        self.assertEqual(spot.region, self.region)
        self.assertEqual(spot.category, self.category)
        self.assertIn(spot, self.region.spots.all())
        self.assertIn(spot, self.category.spots.all())

    def test_default_values(self):
        spot = TouristSpot.objects.create(
            name="鵜戸神宮",
            slug="udo-jingu",
            region=self.region,
            category=self.category,
        )

        self.assertEqual(spot.estimated_stay_minutes, 60)
        self.assertTrue(spot.is_active)

    def test_get_google_maps_url_uses_existing_url(self):
        spot = TouristSpot.objects.create(
            name="青島",
            slug="aoshima",
            region=self.region,
            category=self.category,
            google_maps_url="https://maps.google.com/example",
        )

        self.assertEqual(spot.get_google_maps_url(), "https://maps.google.com/example")

    def test_get_google_maps_url_builds_url_without_api_key(self):
        spot = TouristSpot.objects.create(
            name="青島",
            slug="aoshima-generated-url",
            region=self.region,
            category=self.category,
            address="宮崎県宮崎市青島",
        )

        self.assertIn("https://www.google.com/maps/search/", spot.get_google_maps_url())
        self.assertIn("%E9%9D%92%E5%B3%B6", spot.get_google_maps_url())


class SeedDemoDataCommandTests(TestCase):
    def test_seed_demo_data_creates_demo_records(self):
        out = StringIO()

        call_command("seed_demo_data", stdout=out)

        self.assertGreaterEqual(Region.objects.count(), 4)
        self.assertGreaterEqual(SpotCategory.objects.count(), 9)
        self.assertGreaterEqual(TouristSpot.objects.count(), 12)
        self.assertTrue(Region.objects.filter(name="霧島周辺エリア").exists())
        self.assertTrue(SpotCategory.objects.filter(slug="souvenir").exists())
        self.assertTrue(TouristSpot.objects.filter(slug="demo-aoshima").exists())
        self.assertTrue(TouristSpot.objects.filter(slug="demo-kirishima-highland-view").exists())
        self.assertIn("デモデータ投入が完了しました", out.getvalue())

    def test_seed_demo_data_is_idempotent_by_slug(self):
        call_command("seed_demo_data", stdout=StringIO())
        first_spot_count = TouristSpot.objects.count()
        first_category_count = SpotCategory.objects.count()

        call_command("seed_demo_data", stdout=StringIO())

        self.assertEqual(TouristSpot.objects.count(), first_spot_count)
        self.assertEqual(SpotCategory.objects.count(), first_category_count)

    def test_seed_demo_data_does_not_store_api_keys_or_external_urls(self):
        call_command("seed_demo_data", stdout=StringIO())

        demo_spots = TouristSpot.objects.filter(slug__startswith="demo-")

        self.assertTrue(demo_spots.exists())
        self.assertFalse(demo_spots.exclude(official_url="").exists())
        self.assertFalse(demo_spots.exclude(google_maps_url="").exists())
        self.assertFalse(demo_spots.exclude(phone_number="").exists())
