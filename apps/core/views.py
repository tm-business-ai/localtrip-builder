from django.shortcuts import render


def home(request):
    cards = [
        {
            "title": "観光スポット管理",
            "description": "地域、カテゴリ、観光スポットをDjango Adminから管理できます。",
        },
        {
            "title": "旅行条件入力",
            "description": "旅行者の条件を入力し、AI生成前の候補スポットを確認できます。",
        },
        {
            "title": "AIプラン生成",
            "description": "Mock、Gemini、OpenAI、Claudeを切り替えて旅行プランを生成できます。",
        },
        {
            "title": "Google Maps連携",
            "description": "候補スポットの地図リンクとGoogle MapsルートURLを生成できます。",
        },
    ]
    return render(request, "core/home.html", {"cards": cards})
