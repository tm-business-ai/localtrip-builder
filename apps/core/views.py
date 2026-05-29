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
            "description": "Gemini、OpenAI、Claudeを切り替えられる生成機能を今後追加します。",
        },
        {
            "title": "Google Maps連携",
            "description": "移動ルート、地図リンク、周辺情報の連携を予定しています。",
        },
    ]
    return render(request, "core/home.html", {"cards": cards})
