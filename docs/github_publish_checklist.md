# GitHub公開前チェックリスト

LocalTrip Builder をGitHubやポートフォリオで公開する前の確認リストです。

## 秘密情報

- [ ] `.env` がGit管理対象に含まれていない
- [ ] `.env.*` がGit管理対象に含まれていない
- [ ] `.env.example` にはダミー値だけが入っている
- [ ] `SECRET_KEY` の実値をREADMEやdocsに書いていない
- [ ] Gemini / OpenAI / Claude / Google Maps の実APIキーを書いていない
- [ ] 本番DBパスワードや本番接続情報を書いていない

## 生成物・ローカルファイル

- [ ] `__pycache__/` や `*.pyc` がGit管理対象に含まれていない
- [ ] `db.sqlite3` や `*.sqlite3` がGit管理対象に含まれていない
- [ ] `logs/` や `*.log` がGit管理対象に含まれていない
- [ ] `media/`、`uploads/` がGit管理対象に含まれていない
- [ ] PDF出力物などの生成ファイルをGit管理対象に含めていない
- [ ] ローカルPCの絶対パスをREADMEやdocsに残していない

## アプリ動作

- [ ] `python manage.py check` が通る
- [ ] `python -m compileall apps config` が通る
- [ ] PostgreSQL起動後に `python manage.py migrate` が通る
- [ ] `python manage.py seed_demo_data` が通る
- [ ] `python manage.py test` が通る、または未実行理由をREADMEや作業メモに残している

## 外部API

- [ ] トップページ表示だけで外部APIを呼び出さない
- [ ] プレビュー画面表示だけで外部AI APIを呼び出さない
- [ ] PDF生成で外部APIを呼び出さない
- [ ] デモデータ投入で外部APIを呼び出さない
- [ ] Geocoding APIは管理者の明示アクション時だけ呼び出す

## ドキュメント

- [ ] READMEに概要、機能、セットアップ、環境変数、デモ手順がある
- [ ] `docs/demo_scenario.md` にデモの流れがある
- [ ] `docs/product_overview.md` にポートフォリオ説明文がある
- [ ] 実績を誇張した表現になっていない
- [ ] デモデータがサンプルであることを明記している

## 公開時の注意

- [ ] GitHubへpushする前に `git status` で不要ファイルを確認する
- [ ] 実APIキーを入れた `.env` を誤って追加していないか確認する
- [ ] スクリーンショットやPDFに個人情報・APIキー・ローカルパスが写っていないか確認する
