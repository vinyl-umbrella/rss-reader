# rss-reader

## sample image
<img src="./img/sample.png" width="480px">


## Features
- [x] 通知機能
    - 動画が投稿または生放送が始まってから10分以内に通知
    - 通知をクリックするとwatch laterリストに保存
- [x] 任意のfeedの登録
- [x] 新しく投稿があったチャンネルのハイライト機能
- [x] 後で見ようと思った投稿の記憶機能
- [x] リンクを既定のブラウザで開く


## How to Add Feed
- feedを管理するファイルの場所
    - windowsの場合
        - `:%homepath%\\Documents\\.feedList.csv`
    - macの場合
        - `$HOME/Documents/.feedList.csv`
- フォーマット
    - チャンネルのタイトル,feedのurl
        - youtubeの場合: `https://www.youtube.com/feeds/videos.xml?channel_id=?????`
        - ニコニコの場合: `https://ch.nicovideo.jp/?????/live?rss=2.0`


## How to Install
```
npm install
npm run electron:build
```
dist_electron内にあるインストーラを実行

<!--
## 今後追加したい機能
- すべてのfeedを時系列順で並べるページ
- アプリアイコン作成(mac, linux)
- windowサイズの記憶
-->

## License
MIT
