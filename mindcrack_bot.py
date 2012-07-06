import json
import logging
import datetime
import os
import sys

import reddit

import util
from mindcrackdata import MindCrackData


mindcrackers = [
    ('adlingtont', 'Adlington'),
    ('bdoubleo100', 'BdoubleO'),
    ('arkasmc', 'Arkas'),
    ('ethoslab', 'EthosLab'),
    ('jsano19', 'Jsano'),
    ('kurtjmac', 'Kurtjmac'),
    ('millbeeful', 'MillBee'),
    ('nebris88', 'Nebris'),
    ('pauseunpause', 'PauseUnpause'),
    ('vintagebeef', 'VintageBeef'),
    ('shreeyamnet', 'Shreeyam'),
    ('imanderzel', 'AnderZEL'),
    ('w92baj', 'Baj'),
    ('docm77', 'DocM'),
    ('guudeboulderfist', 'Guude'),
    ('justd3fy', 'JustDefy'),
    ('supermcgamer', 'MCGamer'),
    ('mhykol', 'Mhykol'),
    ('pakratt13', 'Pakratt'),
    ('pyropuncher', 'PyroPuncher'),
    ('thejims', 'TheJims'),
    ('zisteau', 'Zisteau'),
    ('mindcracknetwork', 'MindCrackNetwork')
]


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

        # Go back to the beginning of the file to avoid IOError: [Errno 0] Error
        t.seek(0, 0)

        # Update timestamp log to show that check for new videos is being done now.
        now = str(datetime.datetime.utcnow())
        t.write(now)

    # Connect to reddit as the bot.
    r = reddit.Reddit(user_agent='Mindcrack YouTube video fetcher bot, biiighuggies@gmail.com')
    r.login(cfg['username'], cfg['password'])

    # Connect to the MindCrack video database
    db = MindCrackData(cfg['database'])

    for video in db.videos(num_videos=cfg['num_videos']):
        if video['uploaded'] > timestamp:
            logging.info('Submitting video %s with id: %s',
                video['title'], video['video_id'])

            submission_title = '[' + video['name'].strip() + '] ' + video['title'] + ' (' + util.get_HMS(video['duration']) + ')'
            video_url = 'http://www.youtube.com/watch?v=' + video['video_id']

            try:
                r.submit(cfg['subreddit'], submission_title, url=video_url)
            except:
                logging.warning('Submission to reddit failed')
        else:
            logging.info('Skipping video %s with timestamp %s (too old)',
                video['title'], video['uploaded'])

    logging.info('Videos checked at %s', now)
    logging.info('Finished')


if __name__ == '__main__':
    main()
