<template>
    <div id="app">
        <div class="body">

            <h1 class="pageTitle">{{ pageTitle }}</h1>
            <article v-for="(list, index) in feed.items" :key="index">
                <figure>
                    <img :src="list.thumbnail" />
                </figure>
                <div class="text_content">
                    <p class="date">{{ list.date }}</p>
                    <h2><a @click="openPage(list.link)">
                        <font color="#2cb4ad" v-if="NewFeedindex>index">
                            {{ list.title }}
                        </font>
                        <font v-else>
                            {{ list.title }}
                        </font>
                    </a></h2>
                    <p class = "description">{{ list.description }}</p>
                    <a href="javascript:void(0)" class="btn" @click="add_watch_later(add_remove, list); return false;">{{ add_remove }}</a>
                </div>
            </article>
            <br />

        </div>

        <div class="sidebar">
            <ul>
                <li><a href="#" class="btn" @click="getAll">reload all</a></li>
                <li><a href="#" class="btn" @click="show_watch_later">watch later</a></li>
                <br />
                <li><a href="#" class="btn" @click="eachFeed('jun', 'jun channel')">jun channel</a></li>
                <li><a href="#" class="btn" @click="eachFeed('UNK', 'UNKちゃんねる')">UNKちゃんねる</a></li>
                <li><a href="#" class="btn" @click="eachFeed('kirinuki', '切り抜き')">切り抜き</a></li>
                <li><a href="#" class="btn" @click="eachFeed('kirinuki2', '切り抜き2')">切り抜き2</a></li>
                <li><a href="#" class="btn" @click="eachFeed('pizza', 'ピザラジ')">ピザラジ</a></li>
                <br />
                <li><a href="#" class="btn" @click="eachFeed('kiyo', 'キヨ')">キヨ</a></li>
                <li><a href="#" class="btn" @click="eachFeed('ushizawa', '牛沢')">牛沢</a></li>
                <li><a href="#" class="btn" @click="eachFeed('mokou', 'もこう')">もこう</a></li>
            </ul>
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
            newest: {},
            // ボタンのテキスト
            add_remove: "watch later",
            pageTitle: "",
            NewFeedindex: "",
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
            let h = self.getdoubleDigestNumer(D.getHours());
            let M = self.getdoubleDigestNumer(D.getMinutes());
            let S = self.getdoubleDigestNumer(D.getSeconds());

            let formatted = D.getFullYear() + "/" + month + "/" + date + " " + h + ":" + M + ":" + S;
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

        getAll() {
            let self = this;
            //初期化
            self.allFeed = {};
            //それぞれの名前とxmlへのurl
            const nicoList = [
                ["UNK", "https://ch.nicovideo.jp/unkchanel/live?rss=2.0"],
            ];

            const tubeList = [
                ["jun", "https://www.youtube.com/feeds/videos.xml?channel_id=UCx1nAvtVDIsaGmCMSe8ofsQ"],
                ["kirinuki", "https://www.youtube.com/feeds/videos.xml?channel_id=UCH-lygWpHodDff3iQurnWnQ"],
                ["kirinuki2", "https://www.youtube.com/feeds/videos.xml?channel_id=UCddGctO9eY4-lKIwDj42p0Q"],
                ["pizza", "https://www.youtube.com/feeds/videos.xml?channel_id=UCeWZN7rNRQaHCtMCdHEZFqw"],
                ["mokou", "https://www.youtube.com/feeds/videos.xml?channel_id=UCENoC6MLc4pL-vehJyzSWmg"],
                ["kiyo", "https://www.youtube.com/feeds/videos.xml?channel_id=UCMJiPpN_09F0aWpQrgbc_qg"],
                ["ushizawa", "https://www.youtube.com/feeds/videos.xml?channel_id=UCZMRuagdTBKmmrFtSMN48Xw"],
            ];

            const Parser = require('rss-parser');
            const nicoParser = new Parser({
                customFields: {
                    item: ["description", "nicoch:live_thumbnail"],
                }
            });
            for(let loop = 0; loop < nicoList.length; loop++){
                (async () => {
                    //パース
                    let parsed = await nicoParser.parseURL(nicoList[loop][1]);
                    //追加
                    self.allFeed[nicoList[loop][0]] = parsed;

                    // 日付・description・thumbnail 整える
                    for(let j = 0; j < self.allFeed[nicoList[loop][0]].items.length; j++) {
                        //日付表示を整える
                        self.setDate(self.allFeed[nicoList[loop][0]].items[j].isoDate, nicoList[loop][0], j);
                        //description追加
                        if (!("description" in self.allFeed[nicoList[loop][0]].items[j])) {
                            self.setDescription(nicoList[loop][0], j);
                        }
                        //thumbnail追加 nicoとtubeで場合分け
                        if (!("thumbnail" in self.allFeed[nicoList[loop][0]].items[j])) {
                            if ("nicoch:live_thumbnail" in self.allFeed[nicoList[loop][0]].items[j]) {
                                self.allFeed[nicoList[loop][0]].items[j]["thumbnail"] = self.allFeed[nicoList[loop][0]].items[j]["nicoch:live_thumbnail"];
                            } else {
                                self.allFeed[nicoList[loop][0]].items[j]["thumbnail"] = self.allFeed[nicoList[loop][0]].items[j]["media:group"]["media:thumbnail"][0]["$"]["url"];
                            }
                        }
                    }
                })();
            }

            const tubeParser = new Parser({
                customFields: {
                    item: ["media:group"],
                }
            });
            for(let loop = 0; loop < tubeList.length; loop++){
                (async () => {
                    //パース
                    let parsed = await tubeParser.parseURL(tubeList[loop][1]);
                    //追加
                    self.allFeed[tubeList[loop][0]] = parsed;

                    // 日付・description・thumbnail 整える
                    for(let j = 0; j < self.allFeed[tubeList[loop][0]].items.length; j++) {
                        //日付表示を整える
                        self.setDate(self.allFeed[tubeList[loop][0]].items[j].isoDate, tubeList[loop][0], j);
                        //description追加
                        if (!("description" in self.allFeed[tubeList[loop][0]].items[j])) {
                            self.setDescription(tubeList[loop][0], j);
                        }
                        //thumbnail追加 nicoとtubeで場合分け
                        if (!("thumbnail" in self.allFeed[tubeList[loop][0]].items[j])) {
                            if ("nicoch:live_thumbnail" in self.allFeed[tubeList[loop][0]].items[j]) {
                                self.allFeed[tubeList[loop][0]].items[j]["thumbnail"] = self.allFeed[tubeList[loop][0]].items[j]["nicoch:live_thumbnail"];
                            } else {
                                self.allFeed[tubeList[loop][0]].items[j]["thumbnail"] = self.allFeed[tubeList[loop][0]].items[j]["media:group"]["media:thumbnail"][0]["$"]["url"];
                            }
                        }
                    }
                })();
            }

            console.log('loaded');
            setTimeout(self.eachFeed, 1000, 'jun', 'jun channel');
        },


        eachFeed(channel, channelNickname) {
            let self = this;
            let newFeedindex = 0;

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
            self.NewFeedindex = newFeedindex;
            // newestを更新，localStorageにも変更を反映
            self.newest[channel] = self.allFeed[channel].items[0];
            localStorage.setItem('newestList', JSON.stringify(self.newest));

            self.feed = this.allFeed[channel];
            self.pageTitle = channelNickname;
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
    article figure img {
        margin-top: 20px;
        height: 150px;
        vertical-align: middle;
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
        color: #ccc;
    }

    .btn {
        display: inline-block;
        padding: 0.1em 0.4em;
        text-decoration: none;
        background: #555;
        color: #FFF;
        border-bottom: solid 4px #444;
        border-radius: 2px;
    }
    .btn:active {
        background: #444;
        color: #DDD;
    }

    .date {
        color: #888;
    }
    .description {
        color: #888;
    }
</style>
