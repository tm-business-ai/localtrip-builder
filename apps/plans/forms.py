from django import forms

from apps.spots.models import Region, SpotCategory

from .models import TravelPlanRequest


class TravelPlanRequestForm(forms.ModelForm):
    class Meta:
        model = TravelPlanRequest
        fields = [
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
        ]
        labels = {
            "title": "プラン名",
            "region": "旅行したい地域",
            "days": "旅行日数",
            "transportation": "主な移動手段",
            "categories": "興味のあるカテゴリ",
            "budget_min": "予算下限",
            "budget_max": "予算上限",
            "traveler_type": "旅行者タイプ",
            "is_rainy_day": "雨の日を想定する",
            "is_family_friendly": "子連れ向けを優先する",
            "free_text": "希望・補足条件",
        }
        help_texts = {
            "title": "任意です。例：宮崎日帰り自然満喫プラン",
            "categories": "複数選択できます。未選択の場合は全カテゴリを候補にします。",
            "free_text": "行きたい場所、避けたい条件、旅の雰囲気などを入力してください。",
        }
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "例：宮崎日帰り自然満喫プラン"}),
            "region": forms.Select(attrs={"class": "form-control"}),
            "days": forms.Select(attrs={"class": "form-control"}),
            "transportation": forms.Select(attrs={"class": "form-control"}),
            "categories": forms.CheckboxSelectMultiple(attrs={"class": "checkbox-list"}),
            "budget_min": forms.NumberInput(attrs={"class": "form-control", "min": "0", "placeholder": "例：3000"}),
            "budget_max": forms.NumberInput(attrs={"class": "form-control", "min": "0", "placeholder": "例：15000"}),
            "traveler_type": forms.Select(attrs={"class": "form-control"}),
            "is_rainy_day": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_family_friendly": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "free_text": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "例：写真映えする場所を中心に、移動は車で無理のない行程にしたい。",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["region"].queryset = Region.objects.filter(is_active=True)
        self.fields["categories"].queryset = SpotCategory.objects.filter(is_active=True)

    def clean(self):
        cleaned_data = super().clean()
        budget_min = cleaned_data.get("budget_min")
        budget_max = cleaned_data.get("budget_max")

        if budget_min is not None and budget_max is not None and budget_min > budget_max:
            raise forms.ValidationError("予算下限は予算上限以下の金額で入力してください。")

        return cleaned_data
