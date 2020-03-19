<template>
    <div id="app">
        <div class="sidebar">
            <ul>
                <li><a href="#" class="btn" @click="getAll">
                    reload all
                </a></li>
                <li><a href="#" class="btn" @click="show_watch_later">
                    watch later
                </a></li>
                <br />
                <li><a href="#" class="btn" @click="eachFeed('jun')">
                    <font color="#00aaaa" v-if="channelColorFlag['jun'] === 1">
                        jun channel
                    </font>
                    <font v-else>
                        jun channel
                    </font>
                </a></li>
                <li><a href="#" class="btn" @click="eachFeed('UNK')">
                    <font color="#00aaaa" v-if="channelColorFlag['UNK'] === 1">
                        UNKちゃんねる
                    </font>
                    <font v-else>
                        UNKちゃんねる
                    </font>
                </a></li>
                <li><a href="#" class="btn" @click="eachFeed('kirinuki')">
                    <font color="#00aaaa" v-if="channelColorFlag['kirinuki'] === 1">
                        切り抜き
                    </font>
                    <font v-else>
                        切り抜き
                    </font>
                </a></li>
                <li><a href="#" class="btn" @click="eachFeed('kirinuki2')">
                    <font color="#00aaaa" v-if="channelColorFlag['kirinuki2'] === 1">
                        切り抜き2
                    </font>
                    <font v-else>
                        切り抜き2
                    </font>
                </a></li>
                <li><a href="#" class="btn" @click="eachFeed('pizza')">
                    <font color="#00aaaa" v-if="channelColorFlag['pizza'] === 1">
                        ピザラジ
                    </font>
                    <font v-else>
                        ピザラジ
                    </font>
                </a></li>
                <li><a href="#" class="btn" @click="eachFeed('hokanko')">
                    <font color="#00aaaa" v-if="channelColorFlag['hokanko'] === 1">
                        録画保管庫
                    </font>
                    <font v-else>
                        録画保管庫
                    </font>
                </a></li>

                <br />
                <li><a href="#" class="btn" @click="eachFeed('kiyo')">
                    <font color="#00aaaa" v-if="channelColorFlag['kiyo'] === 1">
                        キヨ
                    </font>
                    <font v-else>
                        キヨ
                    </font>
                </a></li>
                <li><a href="#" class="btn" @click="eachFeed('ushizawa')">
                    <font color="#00aaaa" v-if="channelColorFlag['ushizawa'] === 1">
                        牛沢
                    </font>
                    <font v-else>
                        牛沢
                    </font>
                </a></li>
                <li><a href="#" class="btn" @click="eachFeed('mokou')">
                    <font color="#00aaaa" v-if="channelColorFlag['mokou'] === 1">
                        もこう
                    </font>
                    <font v-else>
                        もこう
                    </font>
                </a></li>
                <li><a href="#" class="btn" @click="eachFeed('mokou_kirinuki')">
                    <font color="#00aaaa" v-if="channelColorFlag['mokou_kirinuki'] === 1">
                        もこう切り抜き
                    </font>
                    <font v-else>
                        もこう切り抜き
                    </font>
                </a></li>

            </ul>
        </div>

        <div class="body">
            <h1 class="pageTitle">{{ pageTitle }}</h1>
            <article v-for="(list, index) in feed.items" :key="index">
                <figure>
                    <img :src="list.thumbnail" />
                </figure>
                <div class="text_content">
                    <h2><a @click="openPage(list.link)">
                        <font color="#00aaaa" v-if="NewFeedindex>index">
                            {{ list.title }}
                        </font>
                        <font v-else>
                            {{ list.title }}
                        </font>
                    </a></h2>
                    <p class = "description">{{ list.description }}</p>
                    <span class="date">{{ list.date }}</span>
                    <a href="javascript:void(0)" class="btn" @click="add_watch_later(add_remove, list); return false;">{{ add_remove }}</a>
                </div>
            </article>
            <br />
        </div>

    </div>
</template>

<script>
const { shell } = require('electron');

export default {
    created: function() {
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
            },
            // それぞれのチャンネルの最新のfeedのリスト
            newest: {},
            // ボタンのテキスト
            add_remove: "watch later",
            pageTitle: "",
            // 何番目のfeedが最新か示す値
            NewFeedindex: "",
            channelColorFlag: {},
        }
    },
    methods: {
        getdoubleDigestNumer(number) {
            // 1桁の数を "0+n" にする
            return ("0" + number).slice(-2)
        },

        setDate(iso, channel, loop) {
            // isoDateから表示形式を変更
            let self = this;
            let D = new Date(iso);
            let month = self.getdoubleDigestNumer(D.getMonth() + 1);
            let date = self.getdoubleDigestNumer(D.getDate());
            let H = self.getdoubleDigestNumer(D.getHours());
            let M = self.getdoubleDigestNumer(D.getMinutes());

            let formatted = month + "/" + date + " " + H + ":" + M;
            self.allFeed[channel].items[loop]["date"] = formatted;
        },

        setDescription(channel, loop) {
            // tubeのみ
            let self = this;
            let desc = self.allFeed[channel].items[loop]["media:group"]["media:description"][0];
            if (desc.length > 100){
                desc = desc.substr(0, 100) + "...";
            }
            self.allFeed[channel].items[loop]["description"] = desc;
        },

        detectNew(channel) {
            let self = this;
            if (!(self.newest[channel])) {
                console.log('none');
                self.channelColorFlag[channel] = 1;
            }else if (self.newest[channel].date === self.allFeed[channel].items[0].date){
                // 新着なし
                self.channelColorFlag[channel] = 0;
            } else {
                // 新着あり
                self.channelColorFlag[channel] = 1;
                let notif = new Notification(self.allFeed[channel].channelNickname, {
                    body: self.allFeed[channel].items[0].title,
                    timeout: 4000,
                });
                notif.onclick = () => {
                  self.add_watch_later("watch later", self.allFeed[channel].items[0]);
                }
            }
        },

        getAll() {
            let self = this;
            //初期化
            self.allFeed = {};
            //それぞれの名前とxmlへのurl
            const feedList = [
                ["UNK", "https://ch.nicovideo.jp/unkchanel/live?rss=2.0", "UNKちゃんねる"],
                ["jun", "https://www.youtube.com/feeds/videos.xml?channel_id=UCx1nAvtVDIsaGmCMSe8ofsQ", "jun channel"],
                ["kirinuki", "https://www.youtube.com/feeds/videos.xml?channel_id=UCH-lygWpHodDff3iQurnWnQ", "切り抜き"],
                ["kirinuki2", "https://www.youtube.com/feeds/videos.xml?channel_id=UCddGctO9eY4-lKIwDj42p0Q", "切り抜き2"],
                ["pizza", "https://www.youtube.com/feeds/videos.xml?channel_id=UCeWZN7rNRQaHCtMCdHEZFqw", "ピザラジ"],
                ["hokanko", "https://www.youtube.com/feeds/videos.xml?channel_id=UC4vLrf83XQ9zpGx6XqDgk3g", "録画保管庫"],
                ["kiyo", "https://www.youtube.com/feeds/videos.xml?channel_id=UCMJiPpN_09F0aWpQrgbc_qg", "キヨ"],
                ["ushizawa", "https://www.youtube.com/feeds/videos.xml?channel_id=UCZMRuagdTBKmmrFtSMN48Xw", "牛沢"],
                ["mokou", "https://www.youtube.com/feeds/videos.xml?channel_id=UCENoC6MLc4pL-vehJyzSWmg", "もこう"],
                ["mokou_kirinuki", "https://www.youtube.com/feeds/videos.xml?channel_id=UC66kipgL5DTVPFg7mzWdBCw", "もこう切り抜き"],
            ];

            const Parser = require('rss-parser');
            const nicoParser = new Parser({
                customFields: {
                    item: ["description", "nicoch:live_thumbnail"],
                }
            });
            const tubeParser = new Parser({
                customFields: {
                    item: ["media:group"],
                }
            });

            for (let loop=0; loop<feedList.length; loop++) {
                if (feedList[loop][1].match(/nicovideo/)) {     //nicoliveの場合
                    (async () => {
                        //パース
                        let parsed = await nicoParser.parseURL(feedList[loop][1]);
                        //追加
                        self.allFeed[feedList[loop][0]] = parsed;
                        self.allFeed[feedList[loop][0]]["channelNickname"] = feedList[loop][2];

                        // 日付・description・thumbnail 整える
                        for(let j = 0; j < self.allFeed[feedList[loop][0]].items.length; j++) {
                            //日付表示を整える
                            self.setDate(self.allFeed[feedList[loop][0]].items[j].isoDate, feedList[loop][0], j);
                            //description追加
                            if (!("description" in self.allFeed[feedList[loop][0]].items[j])) {
                                self.setDescription(feedList[loop][0], j);
                            }
                            //thumbnail追加
                            if (!("thumbnail" in self.allFeed[feedList[loop][0]].items[j])) {
                                self.allFeed[feedList[loop][0]].items[j]["thumbnail"] = self.allFeed[feedList[loop][0]].items[j]["nicoch:live_thumbnail"];
                            }
                        }
                        self.detectNew(feedList[loop][0]);
                    })();

                }else if (feedList[loop][1].match(/youtube.com/)) {     //tubeの場合
                    (async () => {
                        //パース
                        let parsed = await tubeParser.parseURL(feedList[loop][1]);
                        //追加
                        self.allFeed[feedList[loop][0]] = parsed;
                        self.allFeed[feedList[loop][0]]["channelNickname"] = feedList[loop][2];

                        // 日付・description・thumbnail 整える
                        for(let j = 0; j < self.allFeed[feedList[loop][0]].items.length; j++) {
                            //日付表示を整える
                            self.setDate(self.allFeed[feedList[loop][0]].items[j].isoDate, feedList[loop][0], j);
                            //description追加
                            if (!("description" in self.allFeed[feedList[loop][0]].items[j])) {
                                self.setDescription(feedList[loop][0], j);
                            }
                            //thumbnail追加 nicoとtubeで場合分け
                            if (!("thumbnail" in self.allFeed[feedList[loop][0]].items[j])) {
                                self.allFeed[feedList[loop][0]].items[j]["thumbnail"] = self.allFeed[feedList[loop][0]].items[j]["media:group"]["media:thumbnail"][0]["$"]["url"];
                            }
                        }
                        self.detectNew(feedList[loop][0]);
                    })();

                }
            }

            console.log('loaded');
            setTimeout(self.eachFeed, 1500, 'default');
        },


        eachFeed(channel) {
            let self = this;
            let newFeedindex = 0;
            if (channel === 'default') {
                channel = 'jun';
                for (;newFeedindex < self.allFeed[channel].items.length; newFeedindex++){
                    if (!(self.newest[channel])) {
                        continue;
                    }
                    // 新着feed検知
                    if (self.newest[channel].date === self.allFeed[channel].items[newFeedindex].date){
                        break;
                    }
                }
                self.NewFeedindex = newFeedindex;

            } else {
                for (;newFeedindex < self.allFeed[channel].items.length; newFeedindex++){
                    // localStorageにそのチャンネルが存在しない
                    if (!(self.newest[channel])) {
                        continue;
                    }
                    // 新着feed検知
                    if (self.newest[channel].date === self.allFeed[channel].items[newFeedindex].date){
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
            }

            self.feed = this.allFeed[channel];
            self.pageTitle = self.allFeed[channel].channelNickname;
            self.add_remove = "watch later";
        },

        //リンクをブラウザで開く
        openPage(url) {
            shell.openExternal(url);
        },

        //変数listに任意の動画のjsonを追加
        add_watch_later(add_or_remove, list) {
            let self = this;
            let notExist = new Boolean(true);
            if (add_or_remove === "watch later"){
                //すでにlaterに存在するか判断
                for(let i=0; i < self.later.items.length; i++) {
                    if (self.later.items[i] === list) {
                        notExist = false;
                    }
                }
                //存在しないなら追加，localStorageにも変更を反映
                if (notExist){
                    self.later.items.push(list);
                    localStorage.setItem('watch_later_list', JSON.stringify(self.later));
                }
            } else {
                //laterから削除，localStorageにも変更を反映
                for(let i=0; i<self.later.items.length; i++){
                    if (self.later.items[i] === list) {
                        self.later.items.splice(i, 1);
                        localStorage.setItem('watch_later_list', JSON.stringify(self.later));
                    }
                }
            }
        },

        show_watch_later() {
            let self = this;
            self.add_remove = "remove";
            self.feed = this.later;
            self.pageTitle = "watch later"
        }
    }
}

</script>

<style>
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

    article {
        display: flex;
        margin-bottom: 10px;
        padding-bottom: 10px;
        border-radius: 4px;
        box-sizing: border-box;
        box-shadow: 0 0 5px #777;
        background-color: #333;
    }
    article figure {
        margin-block-start: 30px;
        margin-block-end: 15px;
        margin-inline-start: 40px;
        margin-inline-end: 30px;
    }
    article figure img {
        height: 150px;
        vertical-align: middle;
    }

    h1 {
        margin-block-start: 15px;
        margin-block-end: 15px;
    }
    h2 {
        margin-block-end: 5px;
    }
    p.description {
        margin-block-start: 5px;
    }
    .text_content a.btn {
        margin-left: 150px;
    }

    .sidebar {
        height: 100vh;
        width: 200px;
        position: fixed;
        top: 0;
        left: 0;
        background-color: #333;
        color: #ccc;
        border-right: solid 1px #777;
    }

    .body {
        position: relative;
        margin-left: 200px;
        margin-right: 2px;
        background-color: #555;
    }

    .pageTitle {
        text-align: center;
        color: #ddd;
        background: #333;
        padding: 0.4em;
        border-top: solid 3px black;
        border-bottom: solid 3px black;
        border-radius: 5px;
    }

    .text_content {
        margin-right: 10px;
        color: #ccc;
    }

    .btn {
        display: inline-block;
        padding: 0.1em 0.5em;
        margin-bottom: 2px;
        background: #555;
        color: #FFF;
        border-bottom: solid 4px #444;
        border-radius: 2px;
    }
    .btn:active {
        background: #444;
        color: #DDD;
    }

    li a.btn {
        transition: font-size 300ms;
    }
    li a.btn:hover {
        text-decoration: none;
        font-size: 115%;
    }

    .date {
        color: #999;
    }
    .description {
        color: #888;
        padding-bottom: 20px;
    }
</style>
