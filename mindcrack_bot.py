import json
import logging
import datetime
import os
import sys
import urllib2

import praw
import gevent

from datetime import timedelta

from gevent import monkey
monkey.patch_socket()
monkey.patch_ssl()

video_filters = [
    'uhc', 'ultra hard core', 'ultra hardcore'
]

mindcrackers = {
    'adlingtont': 'Adlington',
    'bdoubleo100': 'BdoubleO',
    'arkasmc': 'Arkas',
    'ethoslab': 'EthosLab',
    'jsano19': 'Jsano',
    'kurtjmac': 'Kurtjmac',
    'millbeeful': 'MillBee',
    'nebris88': 'Nebris',
    'pauseunpause': 'PauseUnpause',
    'vintagebeef': 'VintageBeef',
    'shreeyamnet': 'Shreeyam',
    'imanderzel': 'AnderZEL',
    'w92baj': 'Baj',
    'docm77': 'DocM',
    'guudeboulderfist': 'Guude',
    'justd3fy': 'JustDefy',
    'supermcgamer': 'MCGamer',
    'mhykol': 'Mhykol',
    'pakratt13': 'Pakratt',
    'pyropuncher': 'PyroPuncher',
    'thejims': 'TheJims',
    'zisteau': 'Zisteau',
    'mindcracknetwork': 'MindCrackNetwork'
}


def get_HMS(time):
    hms = str(timedelta(seconds=time))
    parts = hms.split(':')

    if parts[0] == '0':
        return ':'.join(parts[1:])
    else:
        return hms


def process_video(data):
    return dict(
        video_id=data['id'],
        title=data['title'],
        uploader=data['uploader'],
        uploaded=datetime.datetime.strptime(data['uploaded'], "%Y-%m-%dT%H:%M:%S.%fZ"),
        duration=data['duration']
    )


def get_uploads(username, number_videos=2, offset=1):
    # print('Getting ' + str(number_videos) + ' uploads for ' + username)

    feed_url = 'https://gdata.youtube.com/feeds/api/users/{username}/uploads?v=2&alt=jsonc&start-index={offset}&max-results={number_videos}'.format(username=username, offset=offset, number_videos=number_videos)

    feed = json.loads(urllib2.urlopen(feed_url).read())

    if feed['data']['totalItems'] > 0:
        return [process_video(item) for item in feed['data']['items']]
    else:
        return []


def videos(number_videos=3):
    jobs = [gevent.spawn(get_uploads, username, number_videos=number_videos)
            for username, _ in mindcrackers.iteritems()]
    gevent.joinall(jobs)

    videos = []
    for job in jobs:
        videos = videos + job.value

    return videos


def video_filter(title):
    """Check the title of a video against a list of blacklisted phrases.

    We may wish to exclude certain videos from being posted by this bot. This
    function checks against a list of blacklisted phrases (video_filters) in
    the title of the video. It is case insensitive.

    Returns:
    true if the video is allowed
    false if the video is disallowed

    """
    for s in video_filters:
        if s.lower() in title.lower():
            return False

    return True


def main():
    cfg_dir = sys.argv[1]
    cfg = json.load(open(os.path.join(cfg_dir, 'config.json')))

    if cfg['logging_level'] == 'DEBUG':
        logging_level = logging.DEBUG
    else:
        logging_level = logging.WARNING

    logging.basicConfig(format='%(asctime)s %(message)s',
        filename=os.path.join(cfg['logging_dir'], 'mindcrackredditbot.log'),
        level=logging_level)
    logging.info('Started')

    # Find out when the last video check was completed.
    with open(os.path.join(cfg['logging_dir'], 'timestamp.log'), 'r+') as t:
        timestamp = datetime.datetime.strptime(t.read(), '%Y-%m-%d %H:%M:%S.%f')
        logging.info('Last check at %s', timestamp)

        # Go back to the beginning of the file to avoid IOError: [Errno 0]
        t.seek(0, 0)

        # Update timestamp log to show that check for new videos is being done now.
        now = str(datetime.datetime.utcnow())
        t.write(now)

    # Connect to reddit as the bot.
    r = praw.Reddit(user_agent='Mindcrack YouTube video fetcher bot, by /u/bighuggies')
    r.login(cfg['username'], cfg['password'])

    for video in videos(number_videos=cfg['num_videos']):
        if video['uploaded'] > timestamp:
            if video_filter(video['title']):
                logging.info('Submitting video %s with id: %s',
                    video['title'], video['video_id'])

                submission_title = '[' + mindcrackers[video['uploader']] + '] ' + video['title'] + ' (' + get_HMS(video['duration']) + ')'
                video_url = 'http://www.youtube.com/watch?v=' + video['video_id']

                try:
                    r.submit(cfg['subreddit'], submission_title, url=video_url)
                except:
                    logging.warning('Submission to reddit failed')
            else:
                logging.info('Skipping video %s with timestamp %s (filtered)',
                    video['title'], video['uploaded'])
        else:
            logging.info('Skipping video %s with timestamp %s (too old)',
                video['title'], video['uploaded'])

    logging.info('Videos checked at %s', now)
    logging.info('Finished')


if __name__ == '__main__':
    main()
