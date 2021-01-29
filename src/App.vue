<template>
    <div id="app">
        <div class="sidebar">
            <ul>
                <li><a href="#" class="btn" @click="showAll">
                    All Items
                </a></li>
                <li><a href="#" class="btn" @click="showWatchLater">
                    watch later
                </a></li>
                <br />
                <div v-for="(channel, index) in feedList" :key="index">
                    <br v-show="blankLine.indexOf(index) >= 0"/>
                    <li><a href="#" class="btn" @click="eachFeed(channel[0])">
                        <span style="color:#00aaaa;" v-if="channelColorFlag[channel[0]] === 1">
                            {{ channel[0] }}
                        </span>
                        <span v-else>
                            {{ channel[0] }}
                        </span>
                    </a></li>
                </div>

            </ul>
        </div>

        <div class="body">
            <h1 class="pageTitle">
                <a @click="openPage(feed.link)" v-if="feed.link">
                    {{ feed.channelNickname }}
                </a>
                <div v-else>
                    {{feed.channelNickname}}
                </div>
            </h1>
            <article v-for="(list, index) in feed.items" :key="index">
                <figure v-if="list.thumbnail">
                    <img :src="list.thumbnail"/>
                </figure>
                <div v-else>
                    <span style="padding:10px;"> </span>
                </div>
                <div class="text_content">
                    <h2><a @click="openPage(list.link)">
                        <span style="color:#00aaaa;" v-if="NewFeedindex>index">
                            {{ list.title }}
                        </span>
                        <span v-else>
                            {{ list.title }}
                        </span>
                    </a></h2>
                    <p class = "description" v-show="list.description">
                        {{ list.description | shortenDescription }}
                    </p>
                    <span class="date" v-show="list.isoDate">
                        {{ list.isoDate | formatDate }}
                    </span>
                    <a href="javascript:void(0)" class="btn" @click="removeWatchLater(list); return false;" v-if="feed.channelNickname === 'watch later'">
                        <span>remove</span>
                    </a>
                    <a href="javascript:void(0)" class="btn" @click="addWatchLater(list); return false;" v-else>
                        <span>watch later</span>
                    </a>
                </div>
            </article>
        </div>

    </div>
</template>

<script>

export default {
    created: function() {
        const fs = require('fs');
        const filePath = require('os').homedir() + '/Documents/.feedList.csv';
        const defaultText = 'jun channel,http://www.youtube.com/feeds/videos.xml?channel_id=UCx1nAvtVDIsaGmCMSe8ofsQ\nUNKちゃんねる,http://ch.nicovideo.jp/unkchanel/live?rss=2.0\n';
        let feedArray = '';
        try {
            fs.statSync(filePath);
        } catch(err) {
            // 設定ファイルが存在しない場合
            if (err.code === 'ENOENT') {
                fs.writeFileSync(filePath, defaultText);
            } else {
                console.log('file read error');
            }
        }
        feedArray = fs.readFileSync(filePath, 'utf-8');
        feedArray = feedArray.split('\n');
        let blank = [];

        feedArray.forEach(function(v, i){
            if(v === ''){
                blank.push(i-blank.length);
            }
        })
        this.blankLine = blank;

        feedArray = feedArray.filter(n => n !== '');

        feedArray.forEach(function(v, i){
            feedArray[i] = feedArray[i].split(',')
        });
        this.feedList = feedArray;

        // localStorageに watch_later_list が存在すれば取ってくる
        if (localStorage.getItem('watch_later_list')) {
            this.later = JSON.parse(localStorage.getItem('watch_later_list'));
        }
        // localStorageに newestList が存在すれば取ってくる
        if (localStorage.getItem('newestList')) {
            this.newest = JSON.parse(localStorage.getItem('newestList'));
        }

        this.getAll();
        // 5分ごとにfeedを更新
        setInterval(this.getAll, 300000);
    },

    data(){
        return {
            // すべてのfeedをjson形式で格納
            allFeed: {},
            // 各ページのfeed
            feed: {},
            // watch later のリスト
            later: {
                "items": [],
                "channelNickname": "watch later",
            },
            // それぞれのチャンネルの最新のfeedのリスト
            newest: {},
            // 何番目のfeedが最新か示す値
            NewFeedindex: "",
            channelColorFlag: {},
            //それぞれの名前とxmlへのurl
            feedList: [],
            blankLine: [],
        }
    },

    filters: {
        formatDate(isoDate) {
            function getDoubleDigestNumber(num) {
                // 1桁の数を "0+n" にする
                return ("0" + num).slice(-2)
            }

            // format
            let now = new Date();
            let iso = new Date(isoDate);
            let month = getDoubleDigestNumber(iso.getMonth() + 1);
            let date = getDoubleDigestNumber(iso.getDate());
            let H = getDoubleDigestNumber(iso.getHours());
            let M = getDoubleDigestNumber(iso.getMinutes());


            if ((now - iso) / 3600000 < 1) {
                // 1時間以内
                return month + "/" + date + " " + H + ":" + M + "　" + Math.floor((now - iso) / 60000) + "分前";
            } else if ((now - iso) / 3600000 < 24) {
                // 24時間以内
                return month + "/" + date + " " + H + ":" + M + "　" + Math.floor((now - iso) / 3600000) + "時間前";
            } else {
                return month + "/" + date + " " + H + ":" + M + "　" + Math.floor((now - iso) / 86400000) + "日前";
            }
        },
        shortenDescription(description) {
            if (description.length > 100) {
                return description = description.substring(0, 100) + "...";
            } else {
                return description
            }
        },
    },

    methods: {
        showAll() {
            let self = this;
            let test = {
                "items": [],
                "channelNickname": "All Items",
            };
            self.feedList.forEach(function(ch){
                self.allFeed[ch[0]].items.forEach(function(v){
                    test.items.push(v);
                })
            })
            test.items.sort(function(a,b){
                if (a.isoDate>b.isoDate) return -1;
                if (a.isoDate<b.isoDate) return 1;
                return 0
            });
            test.items = test.items.slice(0, 15);
            self.feed = test;
            self.NewFeedindex = 0;
        },

        detectNew(channel) {
            let self = this;
            if (!(self.newest[channel])) {
                // 初期値
                self.channelColorFlag[channel] = 1;
            } else if (self.newest[channel].isoDate >= self.allFeed[channel].items[0].isoDate) {
                // 新着なし
                self.channelColorFlag[channel] = 0;
            } else {
                // 新着あり
                self.channelColorFlag[channel] = 1;
                let notif = new Notification(channel, {
                    body: self.allFeed[channel].items[0].title,
                    timeout: 4000,
                });
                notif.onclick = () => {
                  self.addWatchLater(self.allFeed[channel].items[0]);
                }
            }
        },

        getAll() {
            let self = this;
            //初期化
            self.allFeed = {};

            const Parser = require('rss-parser');
            const nicoParser = new Parser({
                customFields: {
                    item: ["description", "nicoch:live_thumbnail"],
                }
            });
            // const nicoComuParser = new Parser({
            //     customFields: {
            //         item: ["description"],
            //     }
            // })
            const tubeParser = new Parser({
                customFields: {
                    item: ["media:group"],
                }
            });
            const otherParser = new Parser({
                customFields: {
                    item: ["description"],
                }
            });

            self.feedList.forEach(function(v){
                if (v[1].match(/ch.nicovideo/)) {     //nicoliveの場合
                    (async () => {
                        //パース
                        let parsed = await nicoParser.parseURL(v[1]);
                        parsed.items = parsed.items.slice(0, 8);
                        //追加
                        self.allFeed[v[0]] = parsed;
                        self.allFeed[v[0]]["channelNickname"] = v[0];

                        self.allFeed[v[0]].items.forEach(function(item) {
                            //thumbnail追加
                            item["thumbnail"] = item["nicoch:live_thumbnail"];
                        })
                        self.detectNew(v[0]);
                    })();

                // } else if (v[1].match(/com.nicovideo/)) {     //コミュ放送
                //     (async () => {
                //         //パース
                //         let parsed = await nicoComuParser.parseURL(v[1]);
                //         console.log(parsed);
                //         parsed.items = parsed.items.slice(0, 8);
                //         //追加
                //         self.allFeed[v[0]] = parsed;
                //         self.allFeed[v[0]]["channelNickname"] = v[0];

                //         // self.allFeed[v[0]].items.forEach(function(item) {
                //         //     //thumbnail追加
                //         //     item["thumbnail"] = item["nicoch:live_thumbnail"];
                //         // })
                //         self.detectNew(v[0]);
                //     })();
                } else if (v[1].match(/youtube.com/)) {     //tubeの場合
                    (async () => {
                        //パース
                        let parsed = await tubeParser.parseURL(v[1]);
                        parsed.items = parsed.items.slice(0, 8);
                        //追加
                        self.allFeed[v[0]] = parsed;
                        self.allFeed[v[0]]["channelNickname"] = v[0];

                        self.allFeed[v[0]].items.forEach(function(item) {
                            item.description = item["media:group"]["media:description"][0];
                            //thumbnail追加
                            if (item["media:group"]["media:thumbnail"][0]["$"]["url"].match(/hqdefault.jpg/)) {
                                item["media:group"]["media:thumbnail"][0]["$"]["url"] = item["media:group"]["media:thumbnail"][0]["$"]["url"].replace(/hqdefault.jpg/, 'mqdefault.jpg');
                            }
                            item["thumbnail"] = item["media:group"]["media:thumbnail"][0]["$"]["url"];
                        })
                        self.detectNew(v[0]);
                    })();
                } else {        //other feed
                    (async () => {
                        //パース
                        let parsed = await otherParser.parseURL(v[1]);
                        parsed.items = parsed.items.slice(0, 8);
                        //追加
                        self.allFeed[v[0]] = parsed;
                        self.allFeed[v[0]]["channelNickname"] = v[0];

                        self.detectNew(v[0]);
                    })();

                }
            })

            setTimeout(self.showAll, 1500);
        },


        eachFeed(channel) {
            let self = this;
            let newFeedindex = 0;
            if (self.feed.channelNickname !== 'All Items' && self.feed.channelNickname !== 'watch later') {
                self.channelColorFlag[self.feed.channelNickname] = 0
            }

            for (;newFeedindex < self.allFeed[channel].items.length; newFeedindex++){
                // localStorageにそのチャンネルが存在しない
                if (!(self.newest[channel])) {
                    continue;
                }
                // 新着feed検知
                if (self.newest[channel].isoDate >= self.allFeed[channel].items[newFeedindex].isoDate){
                    break;
                }
            }
            if (newFeedindex === 0) {
                self.channelColorFlag[channel] = 0;
            }
            self.NewFeedindex = newFeedindex;
            // newestを更新，localStorageにも変更を反映
            self.newest[channel] = self.allFeed[channel].items[0];
            localStorage.setItem('newestList', JSON.stringify(self.newest));

            self.feed = self.allFeed[channel];
        },

        //リンクをブラウザで開く
        openPage(url) {
            require('electron').shell.openExternal(url);
        },

        //変数listに任意の動画のjsonを追加
        addWatchLater(list) {
            let self = this;
            let notExist = new Boolean(true);
            //すでにlaterに存在するか判断
            self.later.items.forEach(function(v){
                if (v === list) {
                    notExist = false;
                }
            })
            //存在しないなら追加，localStorageにも変更を反映
            if (notExist){
                self.later.items.push(list);
                localStorage.setItem('watch_later_list', JSON.stringify(self.later));
            }
        },

        removeWatchLater(list) {
            let self = this;
            //laterから削除，localStorageにも変更を反映
            self.later.items.forEach(function(v, i){
                if (v === list) {
                    self.later.items.splice(i, 1);
                    localStorage.setItem('watch_later_list', JSON.stringify(self.later));
                }
            });
        },

        showWatchLater() {
            this.feed = this.later;
        }
    }
}

</script>

<style>
    .sidebar {
        height: 100vh;
        width: 200px;
        position: fixed;
        top: 0;
        left: 0;
        background-color: #333;
        color: #ccc;
    }

    .body {
        position: relative;
        margin-left: 200px;
        margin-right: 2px;
        background-color: #555;
        word-break:break-all;
    }

    .btn {
        display: inline-block;
        padding: 0.1em 0.5em;
        margin-bottom: 2px;
        background: #555;
        color: #fff;
        border-bottom: solid 4px #444;
        border-radius: 2px;
    }
    .btn:active {
        background: #444;
        color: #ddd;
    }

    ul {
        list-style: none;
        padding-left: 15px;
    }
    ul li {
        padding-top: 5px;
    }

    a {
        text-decoration: none;
    }
    a:hover {
        text-decoration: underline;
    }

    li a.btn {
        transition: font-size 300ms;
    }
    li a.btn:hover {
        text-decoration: none;
        font-size: 115%;
    }

    .pageTitle {
        text-align: center;
        color: #ddd;
        background: #333;
        padding: 0.4em;
        border-top: solid 2px black;
        border-bottom: solid 2px black;
        border-radius: 5px;
        margin-block-start: 0px;
        margin-block-end: 15px;
    }

    article {
        display: flex;
        margin-bottom: 10px;
        padding-bottom: 5px;
        border-radius: 4px;
        box-shadow: 0 0 5px #777;
        background-color: #333;
    }
    article figure {
        margin-block-start: 28px;
        margin-inline-start: 25px;
        margin-inline-end: 20px;
        min-width: 200px;
        text-align: center;
    }
    article figure img {
        max-height: 120px;
        max-width: 200px;
    }

    .text_content {
        margin-right: 10px;
    }

    .text_content h2 {
        margin-block-end: 5px;
        color: #ccc;
    }
    .description {
        margin-block-start: 0px;
        color: #888;
        padding-bottom: 10px;
    }
    .date {
        color: #999;
    }
    .text_content .btn {
        float: right;
    }
</style>
