# rss-reader

## How to install
```
npm install --production
npm run electron:build
```

## How to add feeds
src/App.jsのコードを編集
- getAllのfeedListに名前とリンクを追加
- サイドバーのボタンを追加

## 今後追加したい機能
- サイドバーをv-forで回す
    - jsonは順不同であるため困難?
- すべてのfeedを時系列順で並べるページ
- アプリアイコン作成(win, mac, linux)
- 任意のfeedを追加する機能
    - ボタンの追加とgetAllの中にxmlのリンクを追加により任意のfeedを追加することができる(もっと楽に追加したい)
- windowサイズの記憶

## License
MIT
