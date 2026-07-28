登録販売者 問題生成エンジン v2.1.2 フルパッケージ

このフォルダだけで動作する置き換え用の完全版です。

【配置手順】
1. GitHub Desktopで touhan-engine を開く
2. Pull origin を実行
3. Show in Explorer を開く
4. touhan-engine フォルダの中身をすべて削除する
   ※ touhan-engine フォルダ自体は削除しない
5. このZIPを展開し、展開後の中身5項目を touhan-engine 直下へコピーする
6. GitHub Desktopで Commit to main
7. Push origin

【必要ファイル】
- index.html
- app.bundle.js
- data/tkdb.json
- data/tokyo_master.json
- README.txt（説明用。動作には不要）

古い legacy-*.js、generator.js、validator.js、過去バージョンフォルダ等は不要です。


[v2.1.2]
- 通常・本番系の弱点補正を軽量化し、本番相当の題材分散を優先
- 同一成分・漢方・近接カテゴリの重複上限を強化


v2.1.2 修正:
- TKDB JSONの入れ子形式を自動検出
- questionMap欠落時はrecordsの知識IDから問題対応表を復元
- 形式エラー時に検出したトップレベルキーを表示
