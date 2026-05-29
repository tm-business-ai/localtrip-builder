# LocalTrip Builder

地方観光プラン作成アプリ

## 概要

LocalTrip Builder は、旅行者の希望条件に合わせて、登録済みの地域・観光スポット情報から候補を抽出し、生成AIで地方観光プランを作成する Django 製Webアプリです。

観光スポット管理、旅行条件入力、候補スポット抽出、AIプロバイダー切り替え、Google Maps URL生成、PDF出力までを一通り確認できるポートフォリオ向けの業務アプリサンプルとして構成しています。

## 主な機能

- Django Admin による地域・観光カテゴリ・観光スポット管理
- 旅行条件入力フォーム
- 条件に応じた候補スポット抽出
- AIに渡すプロンプト下書き生成
- Mock / Gemini / OpenAI / Claude のAIプロバイダー切り替え
- AI生成結果を `TravelPlanResult` として保存
- Google Maps検索URL・ルートURL生成
- 管理者操作によるGeocoding API連携の土台
- AI観光プラン生成結果のPDFダウンロード
- デモデータ投入コマンド

## 想定利用シーン

- 地方自治体・観光協会向けの観光プラン作成支援
- 宿泊施設・旅行代理店向けの周辺観光提案
- 地域事業者向けのモデルコース作成
- 生成AI API連携を含むDjango業務アプリのポートフォリオ提示

## 使用技術

- Python
- Django
- PostgreSQL
- Docker Compose
- HTML / CSS
- python-dotenv
- psycopg
- requests / httpx
- google-genai
- OpenAI Python SDK
- Anthropic Python SDK
- ReportLab

## 画面・機能の流れ

1. Django Admin で地域、観光カテゴリ、観光スポットを登録します。
2. `/plans/new/` から旅行条件を入力します。
3. 登録済みスポットから候補スポットを抽出します。
4. プレビュー画面で候補スポット、Google Mapsリンク、ルートURL、AIプロンプト下書きを確認します。
5. Mock / Gemini / OpenAI / Claude から1つを選択してプランを生成します。
6. 生成結果画面でAI観光プラン、入力条件、候補スポット、使用プロンプトを確認します。
7. 必要に応じてPDFをダウンロードします。

## セットアップ手順

仮想環境を作成し、依存関係をインストールします。

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

`.env.example` をコピーして `.env` を作成します。

```bash
copy .env.example .env
```

PostgreSQLを起動します。

```bash
docker compose up -d
```

マイグレーションを適用します。

```bash
python manage.py migrate
```

開発サーバーを起動します。

```bash
python manage.py runserver
```

トップページ:

```text
http://127.0.0.1:8000/
```

管理画面を確認する場合は、管理ユーザーを作成してください。

```bash
python manage.py createsuperuser
```

管理画面:

```text
http://127.0.0.1:8000/admin/
```

## 環境変数の設定

`.env.example` にはダミー値のみを記載しています。実際のAPIキーや本番用パスワードは `.env` に設定し、GitHubへ公開しないでください。

主な環境変数:

- `SECRET_KEY`
- `DEBUG`
- `ALLOWED_HOSTS`
- `DATABASE_NAME`
- `DATABASE_USER`
- `DATABASE_PASSWORD`
- `DATABASE_HOST`
- `DATABASE_PORT`
- `GOOGLE_MAPS_API_KEY`
- `GEMINI_API_KEY`
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`

ローカルでMock生成だけを試す場合、AI APIキーは未設定またはダミー値のままでも動作確認できます。

## デモデータ投入

ポートフォリオや商品デモ用に、宮崎県内の地域・観光カテゴリ・観光スポットのサンプルデータを投入できます。

```bash
python manage.py seed_demo_data
```

デモデータの目安:

- 地域: 4件以上
- 観光カテゴリ: 9件以上
- 観光スポット: 12件以上

このコマンドは外部APIを呼び出しません。Gemini / OpenAI / Claude / Google Maps API / Geocoding API への通信も行いません。

営業時間、料金、定休日、緯度経度、説明文はデモ用サンプルです。実運用前には正確な情報へ更新してください。

詳しいデモ手順は [docs/demo_scenario.md](docs/demo_scenario.md) を参照してください。

## AI API連携について

AIプロバイダーは共通インターフェースで切り替えられる構成です。

- `Mock`: 外部APIを呼ばないテスト用プロバイダー
- `Gemini`: Gemini API
- `OpenAI`: OpenAI / ChatGPT API
- `Claude`: Anthropic Claude API

Gemini / OpenAI / Claude は、プレビュー画面で対象プロバイダーを選択し、生成ボタンを押したPOST時だけ呼び出します。トップページ、入力画面、プレビュー画面の表示、テスト、デモデータ投入、PDF生成では外部AI APIを呼び出しません。

APIキーが未設定またはダミー値の場合、画面全体を落とさず、`TravelPlanResult` に失敗結果として保存します。

## Google Maps連携について

候補スポットのGoogle MapsリンクとルートURLは、APIキー不要のURL生成で実装しています。画面表示やPDF出力だけではGoogle Maps APIを呼び出しません。

住所から緯度経度を取得するGeocoding APIクライアントも用意していますが、自動実行はしません。Django Adminで管理者が明示的にアクションを実行した場合だけ呼び出す設計です。

## PDF出力について

AI観光プラン生成結果画面からPDFをダウンロードできます。

PDFには以下を出力します。

- AI観光プラン生成結果
- 入力条件
- 候補スポット一覧
- Google Mapsリンク
- Google MapsルートURL
- 注意事項

PDFはサーバーに保存せず、その場でPDFレスポンスとして返します。PDF生成時にAI APIやGoogle Maps APIは呼び出しません。

## セキュリティ注意事項

- APIキー、DBパスワード、Djangoの `SECRET_KEY` は `.env` に保存し、GitHubへ公開しないでください。
- `.env`、`.env.*`、DBファイル、ログ、アップロードファイル、生成PDFは `.gitignore` に含めています。
- `.env.example` にはダミー値だけを記載してください。
- `DEBUG=True` はローカル開発用です。本番では `DEBUG=False` にしてください。
- 管理画面 `/admin/` は管理者のみが利用する前提です。
- 旅行条件やAIプロンプトには、氏名、電話番号、メールアドレス、住所、予約番号などの個人情報を入力しないでください。

## デモシナリオ

デモの進め方は [docs/demo_scenario.md](docs/demo_scenario.md) にまとめています。

ポートフォリオや提案文に使う説明文は [docs/product_overview.md](docs/product_overview.md) を参照してください。

GitHub公開前の確認事項は [docs/github_publish_checklist.md](docs/github_publish_checklist.md) にまとめています。

## 今後の拡張予定

- AIプロンプト品質の改善
- 旅程の時間割・移動時間の自動整形
- Google Mapsルート表示の詳細化
- PDFレイアウトの改善
- Django Adminの入力補助・データ管理改善
- 本番デプロイ向け設定の整理

## 注意事項

このリポジトリはポートフォリオ・学習・提案用のサンプル実装です。デモデータは実在情報の正確性を保証するものではありません。実運用では、観光情報、営業時間、料金、定休日、地図情報、API利用規約、個人情報保護方針を確認したうえで利用してください。
