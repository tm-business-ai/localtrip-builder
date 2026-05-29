from django.db.models import Case, IntegerField, Q, Value, When
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.ai_providers.services import generate_travel_plan_with_ai
from apps.maps.services import build_google_maps_directions_url, get_spot_google_maps_url
from apps.spots.models import TouristSpot

from .forms import TravelPlanRequestForm
from .models import TravelPlanRequest, TravelPlanResult
from .pdf import build_travel_plan_result_pdf


AVAILABLE_AI_PROVIDERS = [
    {"value": TravelPlanResult.Provider.MOCK, "label": "Mock"},
    {"value": TravelPlanResult.Provider.GEMINI, "label": "Gemini"},
    {"value": TravelPlanResult.Provider.OPENAI, "label": "OpenAI / ChatGPT"},
    {"value": TravelPlanResult.Provider.ANTHROPIC, "label": "Claude"},
]


def get_candidate_spots(plan_request):
    spots = TouristSpot.objects.select_related("region", "category").filter(
        is_active=True,
        region=plan_request.region,
        category__is_active=True,
        region__is_active=True,
    )

    selected_categories = plan_request.categories.all()
    if selected_categories.exists():
        spots = spots.filter(category__in=selected_categories)

    if plan_request.budget_min is not None:
        spots = spots.filter(
            Q(budget_max__isnull=True) | Q(budget_max__gte=plan_request.budget_min)
        )

    if plan_request.budget_max is not None:
        spots = spots.filter(
            Q(budget_min__isnull=True) | Q(budget_min__lte=plan_request.budget_max)
        )

    priority_cases = []
    if plan_request.is_rainy_day:
        priority_cases.append(When(is_rainy_day_friendly=True, then=Value(0)))
    if plan_request.is_family_friendly:
        priority_cases.append(When(is_family_friendly=True, then=Value(0)))

    if priority_cases:
        spots = spots.annotate(
            priority=Case(
                *priority_cases,
                default=Value(1),
                output_field=IntegerField(),
            )
        )
        return spots.order_by("priority", "name")

    return spots.order_by("name")


def build_candidate_spots_snapshot(spots):
    return [
        {
            "id": spot.id,
            "name": spot.name,
            "region": spot.region.name,
            "category": spot.category.name,
            "short_description": spot.short_description,
            "address": spot.address,
            "google_maps_url": get_spot_google_maps_url(spot),
            "latitude": str(spot.latitude) if spot.latitude is not None else "",
            "longitude": str(spot.longitude) if spot.longitude is not None else "",
            "estimated_stay_minutes": spot.estimated_stay_minutes,
            "opening_hours": spot.opening_hours,
            "closed_days": spot.closed_days,
            "budget_min": spot.budget_min,
            "budget_max": spot.budget_max,
            "recommended_season": spot.recommended_season,
            "tags": spot.tags,
            "is_rainy_day_friendly": spot.is_rainy_day_friendly,
            "is_family_friendly": spot.is_family_friendly,
        }
        for spot in spots
    ]


def build_ai_prompt_preview(plan_request, candidate_spots):
    category_names = [category.name for category in plan_request.categories.all()]
    category_text = "、".join(category_names) if category_names else "指定なし"
    budget_min = plan_request.budget_min if plan_request.budget_min is not None else "指定なし"
    budget_max = plan_request.budget_max if plan_request.budget_max is not None else "指定なし"

    lines = [
        "以下の旅行条件と候補スポットをもとに、地方観光プランを作成してください。",
        "",
        "【旅行条件】",
        f"プラン名: {plan_request.title or '未設定'}",
        f"地域: {plan_request.region.name}",
        f"旅行日数: {plan_request.get_days_display()}",
        f"移動手段: {plan_request.get_transportation_display()}",
        f"カテゴリ: {category_text}",
        f"予算: {budget_min}円 - {budget_max}円",
        f"旅行者タイプ: {plan_request.get_traveler_type_display()}",
        f"雨の日想定: {'はい' if plan_request.is_rainy_day else 'いいえ'}",
        f"子連れ優先: {'はい' if plan_request.is_family_friendly else 'いいえ'}",
        f"補足条件: {plan_request.free_text or 'なし'}",
        "",
        "【候補スポット】",
    ]

    if candidate_spots:
        for index, spot in enumerate(candidate_spots, start=1):
            lines.append(
                f"{index}. {spot['name']} / {spot['category']} / 滞在目安{spot['estimated_stay_minutes']}分 / {spot['short_description'] or '説明なし'}"
            )
    else:
        lines.append("条件に合う候補スポットはありません。")

    lines.extend(
        [
            "",
            "※このプロンプトは外部AI APIへ送信せず、現時点ではMockAIProviderでダミー生成します。",
        ]
    )
    return "\n".join(lines)


def plan_request_create(request):
    if request.method == "POST":
        form = TravelPlanRequestForm(request.POST)
        if form.is_valid():
            plan_request = form.save()
            candidate_spots = list(get_candidate_spots(plan_request))
            snapshot = build_candidate_spots_snapshot(candidate_spots)
            plan_request.candidate_spots_snapshot = snapshot
            plan_request.ai_prompt_preview = build_ai_prompt_preview(plan_request, snapshot)
            plan_request.save(
                update_fields=[
                    "candidate_spots_snapshot",
                    "ai_prompt_preview",
                    "updated_at",
                ]
            )
            return redirect("plans:preview", pk=plan_request.pk)
    else:
        form = TravelPlanRequestForm()

    return render(request, "plans/plan_form.html", {"form": form})


def plan_request_preview(request, pk):
    plan_request = get_object_or_404(TravelPlanRequest, pk=pk)
    latest_result = plan_request.results.first()
    return render(
        request,
        "plans/plan_preview.html",
        {
            "plan_request": plan_request,
            "candidate_spots": plan_request.candidate_spots_snapshot,
            "latest_result": latest_result,
            "available_ai_providers": AVAILABLE_AI_PROVIDERS,
            "directions_url": build_google_maps_directions_url(
                plan_request.candidate_spots_snapshot
            ),
        },
    )


@require_POST
def generate_plan_result(request, pk):
    plan_request = get_object_or_404(TravelPlanRequest, pk=pk)
    provider_name = request.POST.get("provider", TravelPlanResult.Provider.MOCK)
    allowed_provider_values = {provider["value"] for provider in AVAILABLE_AI_PROVIDERS}
    if provider_name not in allowed_provider_values:
        provider_name = TravelPlanResult.Provider.MOCK

    try:
        ai_response = generate_travel_plan_with_ai(
            plan_request,
            provider_name=provider_name,
        )
        result = TravelPlanResult.objects.create(
            request=plan_request,
            provider=ai_response.provider,
            model_name=ai_response.model_name,
            prompt=plan_request.ai_prompt_preview,
            generated_text=ai_response.content,
            raw_response=ai_response.raw_response,
            status=TravelPlanResult.Status.SUCCESS,
        )
    except Exception as exc:
        result = TravelPlanResult.objects.create(
            request=plan_request,
            provider=provider_name,
            prompt=plan_request.ai_prompt_preview,
            generated_text="生成に失敗しました。",
            status=TravelPlanResult.Status.FAILED,
            error_message=str(exc),
        )

    return redirect("plans:result", pk=result.pk)


def plan_result(request, pk):
    result = get_object_or_404(
        TravelPlanResult.objects.select_related("request", "request__region"),
        pk=pk,
    )
    return render(
        request,
        "plans/plan_result.html",
        {
            "result": result,
            "plan_request": result.request,
            "candidate_spots": result.request.candidate_spots_snapshot,
            "directions_url": build_google_maps_directions_url(
                result.request.candidate_spots_snapshot
            ),
        },
    )


def plan_result_pdf(request, pk):
    result = get_object_or_404(
        TravelPlanResult.objects.select_related("request", "request__region"),
        pk=pk,
    )
    pdf_bytes = build_travel_plan_result_pdf(result)
    filename = f"localtrip-plan-result-{result.pk}.pdf"
    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


def plan_request_latest_result(request, pk):
    plan_request = get_object_or_404(TravelPlanRequest, pk=pk)
    latest_result = plan_request.results.first()
    if latest_result is None:
        return redirect("plans:preview", pk=plan_request.pk)
    return redirect("plans:result", pk=latest_result.pk)
