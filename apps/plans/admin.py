from django.contrib import admin

from .models import TravelPlanRequest, TravelPlanResult


@admin.register(TravelPlanRequest)
class TravelPlanRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "region",
        "days",
        "transportation",
        "traveler_type",
        "created_at",
    )
    search_fields = ("title", "free_text", "ai_prompt_preview")
    list_filter = (
        "region",
        "days",
        "transportation",
        "traveler_type",
        "is_rainy_day",
        "is_family_friendly",
        "created_at",
    )
    filter_horizontal = ("categories",)
    readonly_fields = (
        "candidate_spots_snapshot",
        "ai_prompt_preview",
        "created_at",
        "updated_at",
    )
    fieldsets = (
        (
            "入力条件",
            {
                "fields": (
                    "title",
                    "region",
                    "days",
                    "transportation",
                    "categories",
                    "budget_min",
                    "budget_max",
                    "traveler_type",
                    "is_rainy_day",
                    "is_family_friendly",
                    "free_text",
                )
            },
        ),
        (
            "生成準備データ",
            {"fields": ("candidate_spots_snapshot", "ai_prompt_preview")},
        ),
        (
            "管理情報",
            {"fields": ("created_at", "updated_at")},
        ),
    )
    ordering = ("-created_at",)


@admin.register(TravelPlanResult)
class TravelPlanResultAdmin(admin.ModelAdmin):
    list_display = ("id", "request", "provider", "model_name", "status", "created_at")
    search_fields = ("request__title", "generated_text", "prompt", "error_message")
    list_filter = ("provider", "status", "created_at")
    readonly_fields = (
        "request",
        "provider",
        "model_name",
        "prompt",
        "generated_text",
        "raw_response",
        "status",
        "error_message",
        "created_at",
    )
    ordering = ("-created_at",)
