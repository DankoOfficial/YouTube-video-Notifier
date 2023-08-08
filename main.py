import requests, re, time, datetime, threading
from datetime import datetime
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem

videos = True # check for new videos
shorts = False # check for new shorts

target = '' # username of the youtuber
cooldown = 5 # cooldown in seconds, default is 5, checks for new videos every 5 seconds
webhook_url = '' # discord webhook url

def parse_recursive(data, left_string, right_string):
    pattern = re.compile(f'{re.escape(left_string)}(.*?){re.escape(right_string)}', re.DOTALL)
    return re.findall(pattern, data)

def userAgent():
    return UserAgent(software_names=SoftwareName.CHROME.value, operating_systems=OperatingSystem.LINUX.value).get_random_user_agent()

def log(text,sleep=None): 
    print(f"[{datetime.utcfromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')}] → {text}")
    if sleep: time.sleep(sleep)

try:
    past_video_ids = open('pastids.txt','r').read().splitlines()
except:
    r = requests.get(f'https://www.youtube.com/@{target}/videos',headers={"Accept": "text/html, application/xhtml+xml, application/xml;q=0.9, image/avif, image/webp, image/apng, */*;q=0.8, application/signed-exchange;v=b3;q=0.7","Accept-Encoding": "gzip, deflate, br","Accept-Language": "en-US, en;q=0.9","Cache-Control": "max-age=0","Cookie": "VISITOR_INFO1_LIVE=r75teNHhsJQ; YSC=U4TOG_zxDgw; GPS=1; PREF=tz=UTC","Sec-Ch-Ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", \"Google Chrome\";v=\"114\"","Sec-Ch-Ua-Arch": "\"x86\"","Sec-Ch-Ua-Bitness": "\"64\"","Sec-Ch-Ua-Full-Version": "\"114.0.5735.199\"","Sec-Ch-Ua-Full-Version-List": "\"Not.A/Brand\";v=\"8.0.0.0\", \"Chromium\";v=\"114.0.5735.199\", \"Google Chrome\";v=\"114.0.5735.199\"","Sec-Ch-Ua-Mobile": "?0","Sec-Ch-Ua-Model": "\"\"","Sec-Ch-Ua-Platform": "\"Windows\"","Sec-Ch-Ua-Platform-Version": "\"10.0.0\"","Sec-Ch-Ua-Wow64": "?0","Sec-Fetch-Dest": "document","Sec-Fetch-Mode": "navigate","Sec-Fetch-Site": "none","Sec-Fetch-User": "?1","Service-Worker-Navigation-Preload": "true","Upgrade-Insecure-Requests": "1","User-Agent": userAgent()})
    for _ in list(set(parse_recursive(r.text,'{"videoId":"','"'))):
        open('pastids.txt','a').write(f'{_}\n')
    past_video_ids = open('pastids.txt','r').read().splitlines()
    log(f'Loaded {len(past_video_ids)} past video ids')

# <Username> = Username of the youtuber
# <Video Name> = Name of the video
# <Video URL> = URL of the video

custom_message = '@everyone <Username> just uploaded <Video Name> at <Video URL> !'

def handle_videos(custom_message,past_video_ids):
    while True:
        r = requests.get(f'https://www.youtube.com/@{target}/videos',headers={"Accept": "text/html, application/xhtml+xml, application/xml;q=0.9, image/avif, image/webp, image/apng, */*;q=0.8, application/signed-exchange;v=b3;q=0.7","Accept-Encoding": "gzip, deflate, br","Accept-Language": "en-US, en;q=0.9","Cache-Control": "max-age=0","Cookie": "VISITOR_INFO1_LIVE=r75teNHhsJQ; YSC=U4TOG_zxDgw; GPS=1; PREF=tz=UTC","Sec-Ch-Ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", \"Google Chrome\";v=\"114\"","Sec-Ch-Ua-Arch": "\"x86\"","Sec-Ch-Ua-Bitness": "\"64\"","Sec-Ch-Ua-Full-Version": "\"114.0.5735.199\"","Sec-Ch-Ua-Full-Version-List": "\"Not.A/Brand\";v=\"8.0.0.0\", \"Chromium\";v=\"114.0.5735.199\", \"Google Chrome\";v=\"114.0.5735.199\"","Sec-Ch-Ua-Mobile": "?0","Sec-Ch-Ua-Model": "\"\"","Sec-Ch-Ua-Platform": "\"Windows\"","Sec-Ch-Ua-Platform-Version": "\"10.0.0\"","Sec-Ch-Ua-Wow64": "?0","Sec-Fetch-Dest": "document","Sec-Fetch-Mode": "navigate","Sec-Fetch-Site": "none","Sec-Fetch-User": "?1","Service-Worker-Navigation-Preload": "true","Upgrade-Insecure-Requests": "1","User-Agent": userAgent()})
        for _ in list(set(parse_recursive(r.text,'{"videoId":"','"')))[:5]:
            if _ not in past_video_ids:
                log(f'New Video Detected - https://www.youtube.com/watch?v={_}')
                open('pastids.txt','a').write(f'{_}\n')
                past_video_ids = open('pastids.txt','r').read().splitlines()
                temp = requests.get(f'https://www.youtube.com/watch?v={_}',headers={'User-Agent': userAgent(),'content-type': 'application/x-www-form-urlencoded','Accept-Language':'en-US,en;q=0.9'})
                author = temp.text.split('"author":"')[1].split('"')[0]
                title = temp.text.split('{"videoPrimaryInfoRenderer":{"title":{"runs":[{"text":"')[1].split('"')[0]
                author_pfp_url = temp.text.split('{"videoOwnerRenderer":{"thumbnail":{"thumbnails":[{"url":"')[1].split('"')[0]
                description = temp.text.split('"shortDescription":"')[1].split('"')[0].replace(r'\n','\n')
                thumbnail = temp.text.split('<link rel="image_src" href="')[1].split('"')[0]
                custom_message = custom_message.replace('<Username>',author).replace('<Video Name>',title).replace('<Video URL>',f'https://www.youtube.com/watch?v={_}')
                author_username = temp.text.split('href="http://www.youtube.com/@')[1].split('"')[0]
                requests.post(webhook_url,json={"content": custom_message, "embeds": [{"title": title, "description": f"{author} published a video on YouTube!\n\n**Description**\n{description}", "url": f"https://www.youtube.com/watch?v={_}", "color": 16517385, "timestamp": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z', "author": {"name": author, "url": f"https://www.youtube.com/{author_username}", "icon_url": author_pfp_url}, "image": {"url": thumbnail}, "footer": {"text": "YouTube", "icon_url": 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/YouTube_full-color_icon_%282017%29.svg/1024px-YouTube_full-color_icon_%282017%29.svg.png'}}], "username": 'Pingcord', "avatar_url": 'https://pngimg.com/uploads/at_sign/small/at_sign_PNG44.png', "attachments": []})
                custom_message = '@everyone <Username> just uploaded <Video Name> at <Video URL> !'
        log(f'Sleeping for {cooldown} seconds...')
        time.sleep(cooldown)

def handle_shorts(custom_message,past_video_ids):
    while True:
        r = requests.get(f'https://www.youtube.com/@{target}/shorts',headers={"Accept": "text/html, application/xhtml+xml, application/xml;q=0.9, image/avif, image/webp, image/apng, */*;q=0.8, application/signed-exchange;v=b3;q=0.7","Accept-Encoding": "gzip, deflate, br","Accept-Language": "en-US, en;q=0.9","Cache-Control": "max-age=0","Cookie": "VISITOR_INFO1_LIVE=r75teNHhsJQ; YSC=U4TOG_zxDgw; GPS=1; PREF=tz=UTC","Sec-Ch-Ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", \"Google Chrome\";v=\"114\"","Sec-Ch-Ua-Arch": "\"x86\"","Sec-Ch-Ua-Bitness": "\"64\"","Sec-Ch-Ua-Full-Version": "\"114.0.5735.199\"","Sec-Ch-Ua-Full-Version-List": "\"Not.A/Brand\";v=\"8.0.0.0\", \"Chromium\";v=\"114.0.5735.199\", \"Google Chrome\";v=\"114.0.5735.199\"","Sec-Ch-Ua-Mobile": "?0","Sec-Ch-Ua-Model": "\"\"","Sec-Ch-Ua-Platform": "\"Windows\"","Sec-Ch-Ua-Platform-Version": "\"10.0.0\"","Sec-Ch-Ua-Wow64": "?0","Sec-Fetch-Dest": "document","Sec-Fetch-Mode": "navigate","Sec-Fetch-Site": "none","Sec-Fetch-User": "?1","Service-Worker-Navigation-Preload": "true","Upgrade-Insecure-Requests": "1","User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"})
        for _ in list(set(parse_recursive(r.text,'{"videoId":"','"')))[:5]:
            if _ not in past_video_ids:
                log(f'New Short Detected - https://www.youtube.com/shorts/{_}')
                open('pastids.txt','a').write(f'{_}\n')
                past_video_ids = open('pastids.txt','r').read().splitlines()
                temp = requests.get(f'https://www.youtube.com/watch?v={_}',headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36','content-type': 'application/x-www-form-urlencoded','Accept-Language':'en-US,en;q=0.9'})
                author = temp.text.split('"author":"')[1].split('"')[0]
                title = temp.text.split('<title>')[1].split(' - YouTube')[0]
                author_pfp_url = temp.text.split('{"videoOwnerRenderer":{"thumbnail":{"thumbnails":[{"url":"')[1].split('"')[0]
                description = temp.text.split('"shortDescription":"')[1].split('"')[0].replace(r'\n','\n')
                thumbnail = temp.text.split('<link rel="image_src" href="')[1].split('"')[0]
                custom_message = custom_message.replace('<Username>',author).replace('<Video Name>',title).replace('<Video URL>',f'https://www.youtube.com/shorts/{_}')
                author_username = temp.text.split('href="http://www.youtube.com/@')[1].split('"')[0]
                requests.post(webhook_url,json={"content": custom_message, "embeds": [{"title": title, "description": f"{author} published a video on YouTube!\n\n**Description**\n{description}", "url": f"https://www.youtube.com/shorts/{_}", "color": 16517385, "timestamp": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z', "author": {"name": author, "url": f"https://www.youtube.com/{author_username}", "icon_url": author_pfp_url}, "image": {"url": thumbnail}, "footer": {"text": "YouTube", "icon_url": 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/YouTube_full-color_icon_%282017%29.svg/1024px-YouTube_full-color_icon_%282017%29.svg.png'}}], "username": 'Pingcord', "avatar_url": 'https://pngimg.com/uploads/at_sign/small/at_sign_PNG44.png', "attachments": []})
                custom_message = '@everyone <Username> just uploaded <Video Name> at <Video URL> !'
        log(f'Sleeping for {cooldown} seconds...')
        time.sleep(cooldown)

if videos:
    video_thread = threading.Thread(target=handle_videos, args=(custom_message,past_video_ids))
    video_thread.start()
    video_thread.join()

if shorts:
    shorts_thread = threading.Thread(target=handle_shorts, args=(custom_message,past_video_ids))
    shorts_thread.start()
    shorts_thread.join()
