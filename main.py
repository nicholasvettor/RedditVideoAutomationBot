import os

import requests
from gtts import gTTS

SUFFIXES = {1: 'st', 2: 'nd', 3: 'rd'}


def ordinal(num):
    if 10 <= num % 100 <= 20:
        suffix = 'th'
    else:
        suffix = SUFFIXES.get(num % 10, 'th')
    return str(num) + suffix


class Post:
    def __init__(self, apidata, commentCount):
        data = apidata['data']
        self.title = data['title']
        self.image = data['url']
        self.permalink = "https://www.reddit.com" + data['permalink']

        res = requests.get(self.permalink + ".json?sort=top", headers={'User-agent': 'rubybot'})
        if res.status_code == 200:
            self.topComments = []
            comments = res.json()[1]['data']['children']
            r = commentCount
            i = 0
            while i < r:
                comment = comments[i]['data']['body']
                if not comment.startswith("Hi! This is our community moderation bot."):
                    self.topComments.append(comments[i]['data']['body'])
                else:
                    r += 1
                i += 1


def tts(words, saveloc):
    gTTS(text=words, lang='en', slow=False).save(saveloc)


subreddit = input("What Subreddit?\n>")
tp = input("Over what time period?\nhour\nday\nweek\nmonth\nyear\nall\n>")
url = f"https://www.reddit.com/r/{subreddit.replace(' ', '')}/top/.json?t={tp}"

response = requests.get(url, headers={'User-agent': 'rubybot'})

script = ""

if response.status_code == 200:
    print("successfully grabbed top posts!")
    postcount = int(input("How Many Posts?\n>"))
    commentcount = int(input("How Many Comments?\n>"))
    filepos = input("Where do you want to save related files?\n>")

    script += f"Today we'll be checking out a subreddit called R slash {subreddit}."
    os.makedirs(filepos)
    posts = response.json()['data']['children']
    for x in range(postcount):
        curpost = Post(posts[x], commentcount)
        print(curpost.title + f" (Original Post: {curpost.permalink})")
        print(curpost.image)
        print(curpost.topComments)
        # save Image to File
        img_data = requests.get(curpost.image).content
        with open(filepos + f'/post{str(x)}-image.jpg', 'wb') as handler:
            handler.write(img_data)

        tts(curpost.title, filepos + f'/post{str(x)}-title.mp3')
        i = 0
        for comment in curpost.topComments:
            tts(comment, filepos + f'/post{str(x)}-c{str(i)}.mp3')
            i += 1

        # Fullscript
        if postcount == 1:
            script += f"This redditor says {curpost.title}."
            comc = 0
            for com in curpost.topComments:
                script += f"The {ordinal(comc + 1)} comment says. {com}"
                comc += 1
        else:
            script += f"The {ordinal(x + 1)} post is titled {curpost.title}. {curpost.topComments[0]}."
    tts(script, filepos + f'/fullscript.mp3')
else:
    print(f"error {response.status_code} : {response.json()['message']}")