from django.core.management.base import BaseCommand

from apps.spots.models import Region, SpotCategory, TouristSpot


REGIONS = [
    {
        "lookup": {"name": "宮崎市", "prefecture": "宮崎県"},
        "defaults": {
            "city": "宮崎市",
            "description": "宮崎市周辺の海沿い・市街地観光を想定したデモ用地域です。",
            "display_order": 10,
            "is_active": True,
        },
    },
    {
        "lookup": {"name": "高千穂エリア", "prefecture": "宮崎県"},
        "defaults": {
            "city": "西臼杵郡高千穂町",
            "description": "自然景観や神話ゆかりの観光を想定したデモ用地域です。",
            "display_order": 20,
            "is_active": True,
        },
    },
    {
        "lookup": {"name": "日南海岸エリア", "prefecture": "宮崎県"},
        "defaults": {
            "city": "日南市",
            "description": "海岸沿いのドライブ観光を想定したデモ用地域です。",
            "display_order": 30,
            "is_active": True,
        },
    },
    {
        "lookup": {"name": "霧島周辺エリア", "prefecture": "宮崎県"},
        "defaults": {
            "city": "小林市・えびの市周辺",
            "description": "高原、温泉、ドライブ観光を想定したデモ用地域です。",
            "display_order": 40,
            "is_active": True,
        },
    },
]

CATEGORIES = [
    {
        "name": "自然",
        "slug": "nature",
        "description": "景勝地、海、山、渓谷などのデモ用カテゴリです。",
        "display_order": 10,
    },
    {
        "name": "神社・仏閣",
        "slug": "shrines-temples",
        "description": "神社や寺社観光のデモ用カテゴリです。",
        "display_order": 20,
    },
    {
        "name": "グルメ",
        "slug": "gourmet",
        "description": "飲食店や食べ歩きスポットのデモ用カテゴリです。",
        "display_order": 30,
    },
    {
        "name": "歴史",
        "slug": "history",
        "description": "城下町、史跡、文化施設などのデモ用カテゴリです。",
        "display_order": 40,
    },
    {
        "name": "温泉",
        "slug": "hot-spring",
        "description": "温泉や休憩施設のデモ用カテゴリです。",
        "display_order": 50,
    },
    {
        "name": "体験",
        "slug": "experience",
        "description": "ものづくり、アクティビティ、地域体験のデモ用カテゴリです。",
        "display_order": 60,
    },
    {
        "name": "カフェ",
        "slug": "cafe",
        "description": "休憩や軽食に使うデモ用カテゴリです。",
        "display_order": 70,
    },
    {
        "name": "お土産",
        "slug": "souvenir",
        "description": "買い物や地域産品の立ち寄りを想定したデモ用カテゴリです。",
        "display_order": 80,
    },
    {
        "name": "絶景",
        "slug": "scenic-view",
        "description": "写真映えや眺望スポットを想定したデモ用カテゴリです。",
        "display_order": 90,
    },
    {
        "name": "雨の日",
        "slug": "rainy-day",
        "description": "屋内や天候に左右されにくいスポットを想定したデモ用カテゴリです。",
        "display_order": 100,
    },
]

SPOTS = [
    {
        "name": "青島デモスポット",
        "slug": "demo-aoshima",
        "region": "宮崎市",
        "category": "nature",
        "short_description": "海沿いの景色を楽しむデモ用スポットです。",
        "description": "南国らしい雰囲気と海岸散策を組み合わせた観光プランの説明に使いやすいサンプルです。",
        "address": "宮崎県宮崎市青島",
        "estimated_stay_minutes": 60,
        "opening_hours": "デモ用サンプル: 終日",
        "closed_days": "デモ用サンプル: なし",
        "budget_min": 0,
        "budget_max": 1000,
        "recommended_season": "春, 夏, 秋",
        "tags": "海,散策,写真映え,家族旅行",
        "is_rainy_day_friendly": False,
        "is_family_friendly": True,
    },
    {
        "name": "宮崎ローカル市場デモ",
        "slug": "demo-miyazaki-local-market",
        "region": "宮崎市",
        "category": "gourmet",
        "short_description": "地元グルメを楽しむ想定のデモ用スポットです。",
        "description": "実在店舗情報に依存しない、グルメ立ち寄り候補のサンプルです。",
        "address": "宮崎県宮崎市中心部",
        "estimated_stay_minutes": 75,
        "opening_hours": "デモ用サンプル: 10:00-18:00",
        "closed_days": "デモ用サンプル: 不定休",
        "budget_min": 1000,
        "budget_max": 3000,
        "recommended_season": "通年",
        "tags": "グルメ,雨の日,買い物",
        "is_rainy_day_friendly": True,
        "is_family_friendly": True,
    },
    {
        "name": "平和台公園デモ散策",
        "slug": "demo-heiwadai-park",
        "region": "宮崎市",
        "category": "nature",
        "short_description": "市街地から立ち寄りやすい公園散策のデモ用スポットです。",
        "description": "短時間の散策候補として使える、ゆったりした旅程向けのサンプルです。",
        "address": "宮崎県宮崎市下北方町",
        "estimated_stay_minutes": 45,
        "opening_hours": "デモ用サンプル: 終日",
        "closed_days": "デモ用サンプル: なし",
        "budget_min": 0,
        "budget_max": 1000,
        "recommended_season": "通年",
        "tags": "公園,散策,短時間",
        "is_rainy_day_friendly": False,
        "is_family_friendly": True,
    },
    {
        "name": "高千穂峡デモビュー",
        "slug": "demo-takachiho-gorge",
        "region": "高千穂エリア",
        "category": "nature",
        "short_description": "渓谷景観を楽しむデモ用スポットです。",
        "description": "自然景観を中心にしたAI観光プラン生成の候補として使うサンプルです。",
        "address": "宮崎県西臼杵郡高千穂町",
        "estimated_stay_minutes": 90,
        "opening_hours": "デモ用サンプル: 9:00-17:00",
        "closed_days": "デモ用サンプル: 荒天時注意",
        "budget_min": 0,
        "budget_max": 3000,
        "recommended_season": "春, 秋",
        "tags": "絶景,自然,写真映え",
        "is_rainy_day_friendly": False,
        "is_family_friendly": True,
    },
    {
        "name": "天岩戸エリアデモ",
        "slug": "demo-amano-iwato-area",
        "region": "高千穂エリア",
        "category": "shrines-temples",
        "short_description": "神話ゆかりの立ち寄り先を想定したデモ用スポットです。",
        "description": "文化・歴史寄りの旅行条件で候補に出しやすいサンプルです。",
        "address": "宮崎県西臼杵郡高千穂町岩戸",
        "estimated_stay_minutes": 60,
        "opening_hours": "デモ用サンプル: 8:30-17:00",
        "closed_days": "デモ用サンプル: なし",
        "budget_min": 0,
        "budget_max": 1000,
        "recommended_season": "通年",
        "tags": "神話,神社,歴史",
        "is_rainy_day_friendly": False,
        "is_family_friendly": True,
    },
    {
        "name": "高千穂ものづくり体験デモ",
        "slug": "demo-takachiho-craft",
        "region": "高千穂エリア",
        "category": "experience",
        "short_description": "屋内体験を想定したデモ用スポットです。",
        "description": "雨の日や家族旅行を想定した候補として使いやすいサンプルです。",
        "address": "宮崎県西臼杵郡高千穂町中心部",
        "estimated_stay_minutes": 90,
        "opening_hours": "デモ用サンプル: 10:00-16:00",
        "closed_days": "デモ用サンプル: 水曜日",
        "budget_min": 2000,
        "budget_max": 5000,
        "recommended_season": "通年",
        "tags": "体験,雨の日,家族旅行",
        "is_rainy_day_friendly": True,
        "is_family_friendly": True,
    },
    {
        "name": "高千穂屋内ミュージアムデモ",
        "slug": "demo-takachiho-indoor-museum",
        "region": "高千穂エリア",
        "category": "rainy-day",
        "short_description": "雨の日でも立ち寄りやすい屋内展示を想定したデモ用スポットです。",
        "description": "天候に左右されにくい候補をAIプランに含めるためのサンプルです。",
        "address": "宮崎県西臼杵郡高千穂町中心部",
        "estimated_stay_minutes": 60,
        "opening_hours": "デモ用サンプル: 10:00-17:00",
        "closed_days": "デモ用サンプル: 木曜日",
        "budget_min": 500,
        "budget_max": 1500,
        "recommended_season": "通年",
        "tags": "雨の日,屋内,文化",
        "is_rainy_day_friendly": True,
        "is_family_friendly": True,
    },
    {
        "name": "鵜戸神宮デモ参拝",
        "slug": "demo-udo-jingu",
        "region": "日南海岸エリア",
        "category": "shrines-temples",
        "short_description": "海沿いの参拝スポットを想定したデモ用スポットです。",
        "description": "日南海岸ドライブの立ち寄り先として使いやすいサンプルです。",
        "address": "宮崎県日南市宮浦",
        "estimated_stay_minutes": 60,
        "opening_hours": "デモ用サンプル: 8:00-17:00",
        "closed_days": "デモ用サンプル: なし",
        "budget_min": 0,
        "budget_max": 1000,
        "recommended_season": "通年",
        "tags": "神社,海,ドライブ",
        "is_rainy_day_friendly": False,
        "is_family_friendly": True,
    },
    {
        "name": "飫肥城下町デモ散策",
        "slug": "demo-obi-castle-town",
        "region": "日南海岸エリア",
        "category": "history",
        "short_description": "城下町散策を想定したデモ用スポットです。",
        "description": "歴史・街歩きテーマのプランで使えるサンプルです。",
        "address": "宮崎県日南市飫肥",
        "estimated_stay_minutes": 120,
        "opening_hours": "デモ用サンプル: 9:00-17:00",
        "closed_days": "デモ用サンプル: 年末年始",
        "budget_min": 500,
        "budget_max": 2500,
        "recommended_season": "春, 秋, 冬",
        "tags": "歴史,街歩き,グルメ",
        "is_rainy_day_friendly": False,
        "is_family_friendly": True,
    },
    {
        "name": "日南海岸ビューポイントデモ",
        "slug": "demo-nichinan-coast-viewpoint",
        "region": "日南海岸エリア",
        "category": "nature",
        "short_description": "海岸ドライブの休憩地点を想定したデモ用スポットです。",
        "description": "移動ルートの途中に挟む短時間スポットとして使えるサンプルです。",
        "address": "宮崎県日南市海岸沿い",
        "estimated_stay_minutes": 30,
        "opening_hours": "デモ用サンプル: 終日",
        "closed_days": "デモ用サンプル: なし",
        "budget_min": 0,
        "budget_max": 1000,
        "recommended_season": "通年",
        "tags": "海,ドライブ,短時間",
        "is_rainy_day_friendly": False,
        "is_family_friendly": True,
    },
    {
        "name": "日南リラックス温泉デモ",
        "slug": "demo-nichinan-relax-hot-spring",
        "region": "日南海岸エリア",
        "category": "hot-spring",
        "short_description": "旅の最後に休憩する想定のデモ用温泉スポットです。",
        "description": "雨の日やゆったりした旅程で使える屋内寄りのサンプルです。",
        "address": "宮崎県日南市",
        "estimated_stay_minutes": 90,
        "opening_hours": "デモ用サンプル: 11:00-21:00",
        "closed_days": "デモ用サンプル: 火曜日",
        "budget_min": 800,
        "budget_max": 2500,
        "recommended_season": "通年",
        "tags": "温泉,雨の日,休憩",
        "is_rainy_day_friendly": True,
        "is_family_friendly": True,
    },
    {
        "name": "霧島高原ビューデモ",
        "slug": "demo-kirishima-highland-view",
        "region": "霧島周辺エリア",
        "category": "scenic-view",
        "short_description": "高原ドライブと眺望を想定したデモ用スポットです。",
        "description": "霧島周辺エリアの自然・絶景テーマで使うサンプルです。",
        "address": "宮崎県小林市周辺",
        "estimated_stay_minutes": 45,
        "opening_hours": "デモ用サンプル: 終日",
        "closed_days": "デモ用サンプル: 荒天時注意",
        "budget_min": 0,
        "budget_max": 1000,
        "recommended_season": "春, 夏, 秋",
        "tags": "高原,絶景,ドライブ",
        "is_rainy_day_friendly": False,
        "is_family_friendly": True,
    },
    {
        "name": "霧島リラックス温泉デモ",
        "slug": "demo-kirishima-relax-hot-spring",
        "region": "霧島周辺エリア",
        "category": "hot-spring",
        "short_description": "温泉休憩を想定したデモ用スポットです。",
        "description": "旅程後半の休憩や雨の日候補として使いやすいサンプルです。",
        "address": "宮崎県えびの市周辺",
        "estimated_stay_minutes": 90,
        "opening_hours": "デモ用サンプル: 11:00-20:00",
        "closed_days": "デモ用サンプル: 水曜日",
        "budget_min": 800,
        "budget_max": 2500,
        "recommended_season": "通年",
        "tags": "温泉,雨の日,休憩",
        "is_rainy_day_friendly": True,
        "is_family_friendly": True,
    },
    {
        "name": "霧島クラフトカフェデモ",
        "slug": "demo-kirishima-craft-cafe",
        "region": "霧島周辺エリア",
        "category": "cafe",
        "short_description": "カフェ休憩と地域クラフトを想定したデモ用スポットです。",
        "description": "移動の合間に立ち寄る休憩候補として使うサンプルです。",
        "address": "宮崎県小林市中心部",
        "estimated_stay_minutes": 60,
        "opening_hours": "デモ用サンプル: 10:00-18:00",
        "closed_days": "デモ用サンプル: 月曜日",
        "budget_min": 1000,
        "budget_max": 2500,
        "recommended_season": "通年",
        "tags": "カフェ,休憩,お土産",
        "is_rainy_day_friendly": True,
        "is_family_friendly": True,
    },
    {
        "name": "宮崎お土産セレクトデモ",
        "slug": "demo-miyazaki-souvenir-select",
        "region": "宮崎市",
        "category": "souvenir",
        "short_description": "旅の最後の買い物を想定したデモ用スポットです。",
        "description": "PDF出力やデモ説明で、土産購入を旅程に含めるためのサンプルです。",
        "address": "宮崎県宮崎市中心部",
        "estimated_stay_minutes": 45,
        "opening_hours": "デモ用サンプル: 10:00-19:00",
        "closed_days": "デモ用サンプル: 不定休",
        "budget_min": 500,
        "budget_max": 5000,
        "recommended_season": "通年",
        "tags": "お土産,買い物,雨の日",
        "is_rainy_day_friendly": True,
        "is_family_friendly": True,
    },
]


class Command(BaseCommand):
    help = "LocalTrip Builderのデモ用地域・カテゴリ・観光スポットを投入します。外部APIは呼び出しません。"

    def handle(self, *args, **options):
        regions = self._seed_regions()
        categories = self._seed_categories()
        created_count, updated_count = self._seed_spots(regions, categories)

        self.stdout.write(
            self.style.SUCCESS(
                "デモデータ投入が完了しました。"
                f" 地域: {len(regions)}件, カテゴリ: {len(categories)}件, "
                f"観光スポット: 作成{created_count}件 / 更新{updated_count}件"
            )
        )
        self.stdout.write(
            "営業時間・料金・定休日はデモ用サンプルです。実運用前に正確な情報へ更新してください。"
        )

    def _seed_regions(self):
        regions = {}
        for data in REGIONS:
            region = Region.objects.filter(**data["lookup"]).order_by("id").first()
            if region is None:
                region = Region.objects.create(**data["lookup"], **data["defaults"])
            else:
                for field, value in data["defaults"].items():
                    setattr(region, field, value)
                region.save()
            regions[region.name] = region
        return regions

    def _seed_categories(self):
        categories = {}
        for data in CATEGORIES:
            category, _ = SpotCategory.objects.update_or_create(
                slug=data["slug"],
                defaults={
                    "name": data["name"],
                    "description": data["description"],
                    "display_order": data["display_order"],
                    "is_active": True,
                },
            )
            categories[category.slug] = category
        return categories

    def _seed_spots(self, regions, categories):
        created_count = 0
        updated_count = 0
        for data in SPOTS:
            spot_data = data.copy()
            region_name = spot_data.pop("region")
            category_slug = spot_data.pop("category")
            slug = spot_data.pop("slug")

            _, created = TouristSpot.objects.update_or_create(
                slug=slug,
                defaults={
                    **spot_data,
                    "region": regions[region_name],
                    "category": categories[category_slug],
                    "official_url": "",
                    "google_maps_url": "",
                    "phone_number": "",
                    "is_active": True,
                },
            )
            if created:
                created_count += 1
            else:
                updated_count += 1
        return created_count, updated_count
