# coding: utf-8
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone
import dateutil.parser
import json
import requests


def to_num_month(str_month):
    if str_month == "Jan":
        return "01"
    elif str_month == "Feb":
        return "02"
    elif str_month == "Mar":
        return "03"
    elif str_month == "Apr":
        return "04"
    elif str_month == "May":
        return "05"
    elif str_month == "Jun":
        return "06"
    elif str_month == "Jul":
        return "07"
    elif str_month == "Aug":
        return "08"
    elif str_month == "Sep":
        return "09"
    elif str_month == "Oct":
        return "10"
    elif str_month == "Nov":
        return "11"
    elif str_month == "Dec":
        return "12"

def utc_to_jst(timestamp_utc):
    datetime_utc = datetime.strptime(timestamp_utc + "+0000", "%Y-%m-%d %H:%M:%S%z")
    datetime_jst = datetime_utc.astimezone(timezone(timedelta(hours=+9)))
    return datetime_jst


rss_urls = [
    ["https://ch.nicovideo.jp/unkchanel/live?rss=2.0", "UNK"],
    ["https://www.youtube.com/feeds/videos.xml?channel_id=UCx1nAvtVDIsaGmCMSe8ofsQ", "jun"],
    ["https://www.youtube.com/feeds/videos.xml?channel_id=UCH-lygWpHodDff3iQurnWnQ", "kirinuki"],
    ["https://www.youtube.com/feeds/videos.xml?channel_id=UCddGctO9eY4-lKIwDj42p0Q", "kirinuki2"],
    ["https://www.youtube.com/feeds/videos.xml?channel_id=UCeWZN7rNRQaHCtMCdHEZFqw", "pizza"],
    ["https://www.youtube.com/feeds/videos.xml?channel_id=UCENoC6MLc4pL-vehJyzSWmg", "mokou"],
    ["https://www.youtube.com/feeds/videos.xml?channel_id=UCMJiPpN_09F0aWpQrgbc_qg", "kiyo"],
    ["https://www.youtube.com/feeds/videos.xml?channel_id=UCZMRuagdTBKmmrFtSMN48Xw", "ushizawa"],
]


result = {
    "UNK": {
        "videos": []
    },
    "jun": {
        "videos": []
    },
    "kirinuki": {
        "videos": []
    },
    "kirinuki2": {
        "videos": []
    },
    "pizza": {
        "videos": []
    },
    "mokou": {
        "videos": []
    },
    "kiyo": {
        "videos": []
    },
    "ushizawa": {
        "videos": []
    },
}


for loop, url in enumerate(rss_urls):
    res = requests.get(url[0])
    soup = BeautifulSoup(res.text, "lxml")

    if "nicovideo" in url[0]:
        videos = soup.find_all("item")
        if len(videos) > 8:
            length = 8
        else:
            length = len(videos)
        for i in range(length):
            #videoの情報を辞書型で用意し，最後にappendする
            video_dict = {
                "video_title": "",
                "video_link": "",
                "description": "",
                "thumbnail": "",
                "date": "",
            }
            video_dict["video_title"] = videos[i].find("title").text
            video_dict["video_link"] = str(videos[i])[str(videos[i]).find("link")+6 : str(videos[i]).find("description")-1].strip()
            video_dict["description"] = videos[i].find("description").text
            video_dict["thumbnail"] = videos[i].find("nicoch:live_thumbnail").text

            nicodate = videos[i].find("pubdate").text
            nicodate = nicodate.split(" ")
            nicodate = datetime(int(nicodate[3]), int(to_num_month(nicodate[2])), int(nicodate[1]), int(nicodate[4][:2]), int(nicodate[4][3:5]), int(nicodate[4][6:8]), tzinfo=timezone(timedelta(hours=9)))
            video_dict["date"] = nicodate.strftime("%Y-%m-%d %H:%M:%S")

            result[url[1]]["videos"].append(video_dict)

    else:   #tube
        videos = soup.find_all("entry")

        if len(videos) > 8:
            length = 8
        else:
            length = len(videos)

        for i in range(length):
            #videoの情報を辞書型で用意し，最後にappendする
            video_dict = {
                "video_title": "",
                "video_link": "",
                "description": "",
                "thumbnail": "",
                "date": "",
            }
            video_dict["video_title"] = videos[i].find("media:title").text
            video_dict["video_link"] = videos[i].find("link")["href"]
            if len(videos[i].find("media:description").text) > 120:
                video_dict["description"] = videos[i].find("media:description").text[:120] + "..."
            else:
                video_dict["description"] = videos[i].find("media:description").text
            video_dict["thumbnail"] = videos[i].find("media:thumbnail")["url"]

            tubedate = videos[i].find("published").text[:-6]
            tubedate = utc_to_jst(str(dateutil.parser.parse(tubedate)))
            video_dict["date"] = tubedate.strftime("%Y-%m-%d %H:%M:%S")

            result[url[1]]["videos"].append(video_dict)

#ファイルに書き出し
json_path = "C:\\Users\\JShimizu\\Documents\\feed.json"
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(result, f)


"""
print(result["jun"])
"""
