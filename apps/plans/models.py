from django.db import models

from apps.spots.models import Region, SpotCategory


class TravelPlanRequest(models.Model):
    class Days(models.TextChoices):
        HALF_DAY = "half_day", "半日"
        ONE_DAY = "one_day", "1日"
        TWO_DAYS = "two_days", "1泊2日"
        THREE_DAYS = "three_days", "2泊3日"

    class Transportation(models.TextChoices):
        CAR = "car", "車"
        WALK = "walk", "徒歩"
        PUBLIC_TRANSPORT = "public_transport", "公共交通機関"
        BICYCLE = "bicycle", "自転車"

    class TravelerType(models.TextChoices):
        SOLO = "solo", "一人旅"
        COUPLE = "couple", "カップル"
        FAMILY = "family", "家族旅行"
        SENIOR = "senior", "シニア"
        FRIENDS = "friends", "友人同士"
        BUSINESS = "business", "出張ついで"

    title = models.CharField("プラン名", max_length=150, blank=True)
    region = models.ForeignKey(
        Region,
        verbose_name="地域",
        on_delete=models.PROTECT,
        related_name="plan_requests",
    )
    days = models.CharField("旅行日数", max_length=20, choices=Days.choices)
    transportation = models.CharField("移動手段", max_length=20, choices=Transportation.choices)
    categories = models.ManyToManyField(
        SpotCategory,
        verbose_name="興味のあるカテゴリ",
        blank=True,
        related_name="plan_requests",
    )
    budget_min = models.PositiveIntegerField("予算下限", null=True, blank=True)
    budget_max = models.PositiveIntegerField("予算上限", null=True, blank=True)
    traveler_type = models.CharField("旅行者タイプ", max_length=30, choices=TravelerType.choices)
    is_rainy_day = models.BooleanField("雨の日を想定", default=False)
    is_family_friendly = models.BooleanField("子連れ向けを優先", default=False)
    free_text = models.TextField(
        "自由入力",
        blank=True,
        help_text="旅行者の希望や補足条件を入力してください。",
    )
    candidate_spots_snapshot = models.JSONField(
        "候補スポットスナップショット",
        default=list,
        blank=True,
        help_text="プラン作成時点の候補スポット情報を保存します。",
    )
    ai_prompt_preview = models.TextField(
        "AIプロンプト下書き",
        blank=True,
        help_text="AIに渡す予定のプロンプト下書きです。",
    )
    created_at = models.DateTimeField("作成日時", auto_now_add=True)
    updated_at = models.DateTimeField("更新日時", auto_now=True)

    class Meta:
        verbose_name = "旅行プラン作成依頼"
        verbose_name_plural = "旅行プラン作成依頼"
        ordering = ["-created_at"]

    def __str__(self):
        if self.title:
            return self.title
        return f"{self.region}の旅行プラン依頼"


class TravelPlanResult(models.Model):
    class Provider(models.TextChoices):
        MOCK = "mock", "Mock"
        GEMINI = "gemini", "Gemini"
        OPENAI = "openai", "OpenAI / ChatGPT"
        ANTHROPIC = "anthropic", "Claude"

    class Status(models.TextChoices):
        SUCCESS = "success", "成功"
        FAILED = "failed", "失敗"

    request = models.ForeignKey(
        TravelPlanRequest,
        verbose_name="旅行プラン作成依頼",
        on_delete=models.CASCADE,
        related_name="results",
    )
    provider = models.CharField("AIプロバイダー", max_length=30, choices=Provider.choices)
    model_name = models.CharField("モデル名", max_length=100, blank=True)
    prompt = models.TextField("使用したプロンプト", blank=True)
    generated_text = models.TextField("生成テキスト")
    raw_response = models.JSONField("AIレスポンス原文", null=True, blank=True)
    status = models.CharField("ステータス", max_length=20, choices=Status.choices, default=Status.SUCCESS)
    error_message = models.TextField("エラーメッセージ", blank=True)
    created_at = models.DateTimeField("作成日時", auto_now_add=True)

    class Meta:
        verbose_name = "AI生成プラン"
        verbose_name_plural = "AI生成プラン"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.request} - {self.provider} - {self.created_at}"
