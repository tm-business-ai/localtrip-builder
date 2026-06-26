# GitHub公開前チェックリスト

- [x] APIキー、秘密鍵、トークン、パスワードをソースコードやREADMEに直接含めていない
- [x] `.env` をGit管理していない
- [x] `.env.example` は実値ではなくダミー値のみになっている
- [x] READMEを公開向けに整備済み
- [x] スクリーンショット保存先 `docs/screenshots/` をREADMEに反映済み
- [x] セットアップ手順を記載済み
- [x] テスト実行方法を記載済み
- [x] `db.sqlite3`、`*.sqlite3`、`__pycache__`、`.pytest_cache`、`venv`、`.venv`、`node_modules`、`staticfiles`、`media`、一時ファイルをGit管理対象外にしている
- [x] `DEBUG=True` と `SECRET_KEY` の扱いをREADMEに記載済み
- [x] 最終テスト実行結果を確認済み
- [x] スクリーンショットを保存済み
- [x] `git diff --check` 実行済み
- [x] GitHubへpush済み
