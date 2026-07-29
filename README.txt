登録販売者 問題生成エンジン v2.2.0 フルパッケージ

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



[v2.2.0]
- 章 → 手引き項目（officialTopicId）→ テーマグループ → topicId の3層分散を実装
- 同じ章内でも手引き項目・薬効群・成分/個別題材が偏らないよう、使用回数の少ない候補を優先
- 生成JSONへ official_topic_id / theme_group_ids / topic_ids を出力
- 候補不足時は従来どおり同一元問題・ほぼ同文を禁止したまま制限を緩和し、必要問題数の完成を優先

[v2.1.3]
- 通常・本番系の弱点補正を軽量化し、本番相当の題材分散を優先
- 同一成分・漢方・近接カテゴリの重複上限を強化


v2.1.3 修正:
- TKDB JSONの入れ子形式を自動検出
- questionMap欠落時はrecordsの知識IDから問題対応表を復元
- 形式エラー時に検出したトップレベルキーを表示


【v2.1.3】
題材分散ルールで章別必要数を確保できない場合、同一元問題・ほぼ同文の重複だけを禁止したまま、近接カテゴリー・成分上限を段階的に緩和して必要数を満たします。東京都2021〜2025の問題DBだけで生成を完了できるようにする修正であり、他県問題の追加は不要です。
