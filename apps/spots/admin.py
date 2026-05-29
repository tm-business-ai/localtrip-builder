from django.contrib import admin, messages
from django.utils.html import format_html

from apps.maps.geocoding import (
    GoogleGeocodingClient,
    GoogleGeocodingError,
    GoogleMapsConfigurationError,
)
from apps.maps.services import get_spot_google_maps_url
from .models import Region, SpotCategory, TouristSpot


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ("name", "prefecture", "city", "display_order", "is_active")
    search_fields = ("name", "prefecture", "city")
    list_filter = ("prefecture", "is_active")
    ordering = ("display_order", "name")


@admin.register(SpotCategory)
class SpotCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "display_order", "is_active")
    search_fields = ("name", "slug")
    list_filter = ("is_active",)
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("display_order", "name")


@admin.register(TouristSpot)
class TouristSpotAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "region",
        "category",
        "address",
        "estimated_stay_minutes",
        "google_maps_link",
        "is_rainy_day_friendly",
        "is_family_friendly",
        "is_active",
    )
    search_fields = ("name", "short_description", "description", "address", "tags")
    list_filter = (
        "region",
        "category",
        "is_rainy_day_friendly",
        "is_family_friendly",
        "is_active",
    )
    prepopulated_fields = {"slug": ("name",)}
    actions = ("geocode_selected_spots",)
    fieldsets = (
        (
            "基本情報",
            {
                "fields": (
                    "name",
                    "slug",
                    "region",
                    "category",
                    "short_description",
                    "description",
                )
            },
        ),
        (
            "場所情報",
            {
                "fields": (
                    "address",
                    "latitude",
                    "longitude",
                )
            },
        ),
        (
            "営業・料金情報",
            {
                "fields": (
                    "estimated_stay_minutes",
                    "opening_hours",
                    "closed_days",
                    "budget_min",
                    "budget_max",
                )
            },
        ),
        (
            "URL・連絡先",
            {
                "fields": (
                    "official_url",
                    "google_maps_url",
                    "phone_number",
                )
            },
        ),
        (
            "AIプラン生成用の補足情報",
            {
                "fields": (
                    "recommended_season",
                    "tags",
                    "is_rainy_day_friendly",
                    "is_family_friendly",
                )
            },
        ),
        (
            "公開設定",
            {
                "fields": ("is_active",),
            },
        ),
    )
    ordering = ("name",)

    @admin.display(description="Google Maps")
    def google_maps_link(self, obj):
        url = get_spot_google_maps_url(obj)
        if not url:
            return "-"
        return format_html('<a href="{}" target="_blank" rel="noopener">地図を開く</a>', url)

    @admin.action(description="選択した観光スポットの住所から緯度経度を取得")
    def geocode_selected_spots(self, request, queryset):
        client = GoogleGeocodingClient()
        success_count = 0
        failed_messages = []

        for spot in queryset:
            if not spot.address:
                failed_messages.append(f"{spot.name}: 住所が未入力です。")
                continue

            try:
                result = client.geocode(spot.address)
            except (GoogleMapsConfigurationError, GoogleGeocodingError, Exception) as exc:
                failed_messages.append(f"{spot.name}: {exc}")
                continue

            spot.latitude = result["latitude"]
            spot.longitude = result["longitude"]
            if not spot.google_maps_url:
                spot.google_maps_url = get_spot_google_maps_url(spot)
            spot.save(update_fields=["latitude", "longitude", "google_maps_url", "updated_at"])
            success_count += 1

        if success_count:
            self.message_user(
                request,
                f"{success_count}件の観光スポットで緯度経度を更新しました。",
                messages.SUCCESS,
            )

        for failed_message in failed_messages[:10]:
            self.message_user(request, failed_message, messages.WARNING)

        if len(failed_messages) > 10:
            self.message_user(
                request,
                f"他 {len(failed_messages) - 10} 件のエラーがあります。",
                messages.WARNING,
            )
