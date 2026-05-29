from django.db import models


class Region(models.Model):
    name = models.CharField("地域名", max_length=100)
    prefecture = models.CharField("都道府県", max_length=50)
    city = models.CharField("市区町村", max_length=100, blank=True)
    description = models.TextField("説明", blank=True)
    display_order = models.PositiveIntegerField("表示順", default=0)
    is_active = models.BooleanField("有効", default=True)
    created_at = models.DateTimeField("作成日時", auto_now_add=True)
    updated_at = models.DateTimeField("更新日時", auto_now=True)

    class Meta:
        verbose_name = "地域"
        verbose_name_plural = "地域"
        ordering = ["display_order", "name"]

    def __str__(self):
        return self.name

class SpotCategory(models.Model):
    name = models.CharField("カテゴリ名", max_length=100, unique=True)
    slug = models.SlugField(
        "スラッグ",
        max_length=120,
        unique=True,
        help_text="URLや内部識別に使う半角英数字、ハイフン、アンダースコアを入力してください。",
    )
    description = models.TextField("説明", blank=True)
    display_order = models.PositiveIntegerField("表示順", default=0)
    is_active = models.BooleanField("有効", default=True)
    created_at = models.DateTimeField("作成日時", auto_now_add=True)
    updated_at = models.DateTimeField("更新日時", auto_now=True)

    class Meta:
        verbose_name = "観光カテゴリ"
        verbose_name_plural = "観光カテゴリ"
        ordering = ["display_order", "name"]

    def __str__(self):
        return self.name

class TouristSpot(models.Model):
    name = models.CharField("スポット名", max_length=150)
    slug = models.SlugField(
        "スラッグ",
        max_length=180,
        unique=True,
        help_text="URLや内部識別に使う半角英数字、ハイフン、アンダースコアを入力してください。",
    )
    region = models.ForeignKey(
        Region,
        verbose_name="地域",
        on_delete=models.PROTECT,
        related_name="spots",
    )
    category = models.ForeignKey(
        SpotCategory,
        verbose_name="カテゴリ",
        on_delete=models.PROTECT,
        related_name="spots",
    )
    short_description = models.CharField(
        "短い説明",
        max_length=255,
        blank=True,
        help_text="一覧表示やAIへの短い説明に使います。",
    )
    description = models.TextField("詳細説明", blank=True)
    address = models.CharField("住所", max_length=255, blank=True)
    latitude = models.DecimalField(
        "緯度",
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )
    longitude = models.DecimalField(
        "経度",
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )
    estimated_stay_minutes = models.PositiveIntegerField(
        "滞在目安時間",
        default=60,
        help_text="観光スポットでの滞在目安時間を分単位で入力してください。",
    )
    opening_hours = models.CharField("営業時間", max_length=255, blank=True)
    closed_days = models.CharField("定休日", max_length=255, blank=True)
    budget_min = models.PositiveIntegerField("予算下限", null=True, blank=True)
    budget_max = models.PositiveIntegerField("予算上限", null=True, blank=True)
    official_url = models.URLField("公式URL", blank=True)
    google_maps_url = models.URLField("Google Maps URL", blank=True)
    phone_number = models.CharField("電話番号", max_length=50, blank=True)
    recommended_season = models.CharField("おすすめ時期", max_length=100, blank=True)
    tags = models.CharField("タグ", max_length=255, blank=True)
    is_rainy_day_friendly = models.BooleanField("雨の日向け", default=False)
    is_family_friendly = models.BooleanField("子連れ向け", default=False)
    is_active = models.BooleanField("有効", default=True)
    created_at = models.DateTimeField("作成日時", auto_now_add=True)
    updated_at = models.DateTimeField("更新日時", auto_now=True)

    class Meta:
        verbose_name = "観光スポット"
        verbose_name_plural = "観光スポット"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_google_maps_url(self):
        from apps.maps.services import get_spot_google_maps_url

        return get_spot_google_maps_url(self)
