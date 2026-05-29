from django.test import TestCase, override_settings
from django.urls import reverse

from apps.spots.models import Region, SpotCategory, TouristSpot

from .forms import TravelPlanRequestForm
from .models import TravelPlanRequest, TravelPlanResult
from .views import (
    build_ai_prompt_preview,
    build_candidate_spots_snapshot,
    get_candidate_spots,
)


class TravelPlanRequestModelTests(TestCase):
    def setUp(self):
        self.region = Region.objects.create(name="宮崎市", prefecture="宮崎県")

    def test_str_returns_title_when_title_exists(self):
        request = TravelPlanRequest.objects.create(
            title="宮崎日帰り自然満喫プラン",
            region=self.region,
            days=TravelPlanRequest.Days.ONE_DAY,
            transportation=TravelPlanRequest.Transportation.CAR,
            traveler_type=TravelPlanRequest.TravelerType.COUPLE,
        )

        self.assertEqual(str(request), "宮崎日帰り自然満喫プラン")

    def test_ai_result_fields_do_not_exist_on_request(self):
        field_names = {field.name for field in TravelPlanRequest._meta.get_fields()}

        self.assertNotIn("generated_plan", field_names)
        self.assertNotIn("ai_provider", field_names)
        self.assertNotIn("ai_model_name", field_names)
        self.assertNotIn("ai_raw_response", field_names)
        self.assertNotIn("generated_at", field_names)


class TravelPlanResultModelTests(TestCase):
    def setUp(self):
        self.region = Region.objects.create(name="宮崎市", prefecture="宮崎県")
        self.plan_request = TravelPlanRequest.objects.create(
            region=self.region,
            days=TravelPlanRequest.Days.ONE_DAY,
            transportation=TravelPlanRequest.Transportation.CAR,
            traveler_type=TravelPlanRequest.TravelerType.SOLO,
        )

    def test_str_is_not_empty(self):
        result = TravelPlanResult.objects.create(
            request=self.plan_request,
            provider=TravelPlanResult.Provider.MOCK,
            generated_text="モック生成結果",
        )

        self.assertTrue(str(result))

    def test_multiple_results_can_belong_to_one_request(self):
        TravelPlanResult.objects.create(
            request=self.plan_request,
            provider=TravelPlanResult.Provider.MOCK,
            generated_text="1回目",
        )
        TravelPlanResult.objects.create(
            request=self.plan_request,
            provider=TravelPlanResult.Provider.OPENAI,
            generated_text="2回目",
        )

        self.assertEqual(self.plan_request.results.count(), 2)


class TravelPlanRequestFormTests(TestCase):
    def setUp(self):
        self.active_region = Region.objects.create(name="宮崎市", prefecture="宮崎県")
        self.inactive_region = Region.objects.create(
            name="非公開地域",
            prefecture="宮崎県",
            is_active=False,
        )
        self.active_category = SpotCategory.objects.create(name="自然", slug="nature")
        self.inactive_category = SpotCategory.objects.create(
            name="非公開カテゴリ",
            slug="inactive",
            is_active=False,
        )

    def test_only_active_regions_and_categories_are_available(self):
        form = TravelPlanRequestForm()

        self.assertIn(self.active_region, form.fields["region"].queryset)
        self.assertNotIn(self.inactive_region, form.fields["region"].queryset)
        self.assertIn(self.active_category, form.fields["categories"].queryset)
        self.assertNotIn(self.inactive_category, form.fields["categories"].queryset)

    def test_budget_min_must_be_less_than_or_equal_to_budget_max(self):
        form = TravelPlanRequestForm(
            data={
                "region": self.active_region.id,
                "days": TravelPlanRequest.Days.ONE_DAY,
                "transportation": TravelPlanRequest.Transportation.CAR,
                "budget_min": 10000,
                "budget_max": 5000,
                "traveler_type": TravelPlanRequest.TravelerType.SOLO,
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("予算下限", form.errors["__all__"][0])


class CandidateSpotTests(TestCase):
    def setUp(self):
        self.region = Region.objects.create(name="宮崎市", prefecture="宮崎県")
        self.other_region = Region.objects.create(name="高千穂町", prefecture="宮崎県")
        self.nature = SpotCategory.objects.create(name="自然", slug="nature")
        self.priority_spot = TouristSpot.objects.create(
            name="青島",
            slug="aoshima",
            region=self.region,
            category=self.nature,
            budget_min=0,
            budget_max=2000,
            is_family_friendly=True,
        )
        self.normal_spot = TouristSpot.objects.create(
            name="平和台公園",
            slug="heiwadai-park",
            region=self.region,
            category=self.nature,
            budget_min=0,
            budget_max=1000,
            is_family_friendly=False,
        )
        TouristSpot.objects.create(
            name="別地域スポット",
            slug="other-region",
            region=self.other_region,
            category=self.nature,
        )

    def test_family_friendly_is_priority_not_required_filter(self):
        plan_request = TravelPlanRequest.objects.create(
            region=self.region,
            days=TravelPlanRequest.Days.ONE_DAY,
            transportation=TravelPlanRequest.Transportation.CAR,
            traveler_type=TravelPlanRequest.TravelerType.FAMILY,
            is_family_friendly=True,
        )
        plan_request.categories.add(self.nature)

        spots = list(get_candidate_spots(plan_request))

        self.assertEqual(spots[0], self.priority_spot)
        self.assertIn(self.normal_spot, spots)


class PlanGenerationResultViewTests(TestCase):
    def setUp(self):
        self.region = Region.objects.create(name="宮崎市", prefecture="宮崎県")
        self.category = SpotCategory.objects.create(name="自然", slug="nature")
        self.spot = TouristSpot.objects.create(
            name="青島",
            slug="aoshima-mock",
            region=self.region,
            category=self.category,
            short_description="海沿いの景勝地",
        )
        self.plan_request = TravelPlanRequest.objects.create(
            title="モック生成テスト",
            region=self.region,
            days=TravelPlanRequest.Days.ONE_DAY,
            transportation=TravelPlanRequest.Transportation.CAR,
            traveler_type=TravelPlanRequest.TravelerType.SOLO,
        )
        self.plan_request.categories.add(self.category)
        snapshot = build_candidate_spots_snapshot([self.spot])
        self.plan_request.candidate_spots_snapshot = snapshot
        self.plan_request.ai_prompt_preview = build_ai_prompt_preview(
            self.plan_request,
            snapshot,
        )
        self.plan_request.save()

    def test_generate_plan_result_creates_result(self):
        response = self.client.post(
            reverse("plans:generate", kwargs={"pk": self.plan_request.pk})
        )

        result = TravelPlanResult.objects.get(request=self.plan_request)
        self.assertRedirects(
            response,
            reverse("plans:result", kwargs={"pk": result.pk}),
        )
        self.assertEqual(result.provider, TravelPlanResult.Provider.MOCK)
        self.assertEqual(result.model_name, "mock-localtrip-v1")
        self.assertIn("モック生成プラン", result.generated_text)

    def test_plan_result_view_returns_200(self):
        result = TravelPlanResult.objects.create(
            request=self.plan_request,
            provider=TravelPlanResult.Provider.MOCK,
            model_name="mock-localtrip-v1",
            prompt=self.plan_request.ai_prompt_preview,
            generated_text="モック生成結果",
        )

        response = self.client.get(reverse("plans:result", kwargs={"pk": result.pk}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "AI観光プラン生成結果")

    def test_plan_result_pdf_returns_pdf_response(self):
        result = TravelPlanResult.objects.create(
            request=self.plan_request,
            provider=TravelPlanResult.Provider.MOCK,
            model_name="mock-localtrip-v1",
            prompt=self.plan_request.ai_prompt_preview,
            generated_text="モック生成結果",
        )

        response = self.client.get(reverse("plans:result_pdf", kwargs={"pk": result.pk}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertIn(
            f'filename="localtrip-plan-result-{result.pk}.pdf"',
            response["Content-Disposition"],
        )
        self.assertTrue(response.content.startswith(b"%PDF"))

    def test_mock_result_is_saved_to_result_not_request(self):
        self.client.post(reverse("plans:generate", kwargs={"pk": self.plan_request.pk}))
        self.plan_request.refresh_from_db()

        self.assertEqual(self.plan_request.results.count(), 1)
        self.assertFalse(hasattr(self.plan_request, "generated_plan"))

    @override_settings(GEMINI_API_KEY="")
    def test_gemini_without_api_key_creates_failed_result(self):
        response = self.client.post(
            reverse("plans:generate", kwargs={"pk": self.plan_request.pk}),
            data={"provider": TravelPlanResult.Provider.GEMINI},
        )

        result = TravelPlanResult.objects.get(request=self.plan_request)
        self.assertRedirects(
            response,
            reverse("plans:result", kwargs={"pk": result.pk}),
        )
        self.assertEqual(result.provider, TravelPlanResult.Provider.GEMINI)
        self.assertEqual(result.status, TravelPlanResult.Status.FAILED)
        self.assertIn("Gemini APIキー", result.error_message)

    @override_settings(OPENAI_API_KEY="")
    def test_openai_without_api_key_creates_failed_result(self):
        response = self.client.post(
            reverse("plans:generate", kwargs={"pk": self.plan_request.pk}),
            data={"provider": TravelPlanResult.Provider.OPENAI},
        )

        result = TravelPlanResult.objects.get(request=self.plan_request)
        self.assertRedirects(
            response,
            reverse("plans:result", kwargs={"pk": result.pk}),
        )
        self.assertEqual(result.provider, TravelPlanResult.Provider.OPENAI)
        self.assertEqual(result.status, TravelPlanResult.Status.FAILED)
        self.assertIn("OpenAI APIキー", result.error_message)

    @override_settings(ANTHROPIC_API_KEY="")
    def test_claude_without_api_key_creates_failed_result(self):
        response = self.client.post(
            reverse("plans:generate", kwargs={"pk": self.plan_request.pk}),
            data={"provider": TravelPlanResult.Provider.ANTHROPIC},
        )

        result = TravelPlanResult.objects.get(request=self.plan_request)
        self.assertRedirects(
            response,
            reverse("plans:result", kwargs={"pk": result.pk}),
        )
        self.assertEqual(result.provider, TravelPlanResult.Provider.ANTHROPIC)
        self.assertEqual(result.status, TravelPlanResult.Status.FAILED)
        self.assertIn("Claude APIキー", result.error_message)
