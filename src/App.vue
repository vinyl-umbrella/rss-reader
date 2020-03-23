<template>
    <div id="app">
        <div class="sidebar">
            <ul>
                <li><a href="#" class="btn" @click="getAll" title="Ctrl + r">
                    reload all
                </a></li>
                <li><a href="#" class="btn" @click="show_watch_later">
                    watch later
                </a></li>
                <br />

                <div v-for="(channel, index) in feedList" :key="index">
                    <li><a href="#" class="btn" @click="eachFeed(channel[0])">
                        <span style="color:#00aaaa;" v-if="channelColorFlag[channel[0]] === 1">
                            {{ channel[0] }}
                        </span>
                        <span v-else>
                            {{ channel[0] }}
                        </span>
                    </a></li>
                    <br v-if="index===5"/>
                </div>

            </ul>
        </div>

        <div class="body">
            <h1 class="pageTitle"><a @click="openPage(feed.link)">
                {{ pageTitle }}
            </a></h1>
            <article v-for="(list, index) in feed.items" :key="index">
                <figure>
                    <img :src="list.thumbnail" />
                </figure>
                <div class="text_content">
                    <h2><a @click="openPage(list.link)">
                        <span style="color:#00aaaa;" v-if="NewFeedindex>index">
                            {{ list.title }}
                        </span>
                        <span v-else>
                            {{ list.title }}
                        </span>
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
        const fs = require('fs');
        const file_path = require('os').homedir() + '/Documents/.feedList.csv';
        const default_text = 'jun channel,https://www.youtube.com/feeds/videos.xml?channel_id=UCx1nAvtVDIsaGmCMSe8ofsQ\nUNKちゃんねる,https://ch.nicovideo.jp/unkchanel/live?rss=2.0\n切り抜き,https://www.youtube.com/feeds/videos.xml?channel_id=UCH-lygWpHodDff3iQurnWnQ\n';
        let temp = '';
        try {
            fs.statSync(file_path);
        } catch(err) {
            // 設定ファイルが存在しない場合
            if (err.code === 'ENOENT') {
                fs.writeFileSync(file_path, default_text);
            } else {
                console.log('file read error');
            }
        }
        temp = fs.readFileSync(file_path, 'utf-8');
        temp = temp.split('\n');
        if (temp[temp.length - 1].length === 0) {
            temp.pop();
        }
        for (let loop=0; loop<temp.length; loop++) {
            temp[loop] = temp[loop].split(',');
        }
        this.feedList = temp;

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
            //それぞれの名前とxmlへのurl
            feedList: [],
        }
    },

    methods: {
        getdoubleDigestNumer(num) {
            // 1桁の数を "0+n" にする
            return ("0" + num).slice(-2)
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
                self.channelColorFlag[channel] = 1;
            } else if (self.newest[channel].date === self.allFeed[channel].items[0].date) {
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

            for (let loop=0; loop<self.feedList.length; loop++) {
                if (self.feedList[loop][1].match(/nicovideo/)) {     //nicoliveの場合
                    (async () => {
                        //パース
                        let parsed = await nicoParser.parseURL(self.feedList[loop][1]);
                        parsed.items = parsed.items.slice(0, 8);
                        //追加
                        self.allFeed[self.feedList[loop][0]] = parsed;
                        self.allFeed[self.feedList[loop][0]]["channelNickname"] = self.feedList[loop][0];

                        // 日付・description・thumbnail 整える
                        for(let j = 0; j < self.allFeed[self.feedList[loop][0]].items.length; j++) {
                            //日付表示を整える
                            self.setDate(self.allFeed[self.feedList[loop][0]].items[j].isoDate, self.feedList[loop][0], j);
                            //description追加
                            if (!("description" in self.allFeed[self.feedList[loop][0]].items[j])) {
                                self.setDescription(self.feedList[loop][0], j);
                            }
                            //thumbnail追加
                            if (!("thumbnail" in self.allFeed[self.feedList[loop][0]].items[j])) {
                                self.allFeed[self.feedList[loop][0]].items[j]["thumbnail"] = self.allFeed[self.feedList[loop][0]].items[j]["nicoch:live_thumbnail"];
                            }
                        }
                        self.detectNew(self.feedList[loop][0]);
                    })();

                }else if (self.feedList[loop][1].match(/youtube.com/)) {     //tubeの場合
                    (async () => {
                        //パース
                        let parsed = await tubeParser.parseURL(self.feedList[loop][1]);
                        parsed.items = parsed.items.slice(0, 8);
                        //追加
                        self.allFeed[self.feedList[loop][0]] = parsed;
                        self.allFeed[self.feedList[loop][0]]["channelNickname"] = self.feedList[loop][0];

                        // 日付・description・thumbnail 整える
                        for(let j = 0; j < self.allFeed[self.feedList[loop][0]].items.length; j++) {
                            //日付表示を整える
                            self.setDate(self.allFeed[self.feedList[loop][0]].items[j].isoDate, self.feedList[loop][0], j);
                            //description追加
                            if (!("description" in self.allFeed[self.feedList[loop][0]].items[j])) {
                                self.setDescription(self.feedList[loop][0], j);
                            }
                            //thumbnail追加
                            if (!("thumbnail" in self.allFeed[self.feedList[loop][0]].items[j])) {
                                self.allFeed[self.feedList[loop][0]].items[j]["thumbnail"] = self.allFeed[self.feedList[loop][0]].items[j]["media:group"]["media:thumbnail"][0]["$"]["url"];
                            }
                        }
                        self.detectNew(self.feedList[loop][0]);
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
                channel = self.feedList[0][0];
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
