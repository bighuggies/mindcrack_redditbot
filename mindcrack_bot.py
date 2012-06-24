import reddit
import sqlite3 as sqlite
import util
import json


def main():
    cfg = json.load(open('config.json'))

    r = reddit.Reddit(user_agent='Mindcrack YouTube video fetcher bot')
    r.login(cfg['username'], cfg['password'])

    conn = sqlite.connect('videos.db')
    cur = conn.cursor()

    cur.execute('CREATE TABLE IF NOT EXISTS videos(video_id text PRIMARY KEY, title text, uploader text, duration integer)')
    cur.execute('CREATE TABLE IF NOT EXISTS mindcrackers(username text PRIMARY KEY, name text)')

    mindcrackers = [m for m in cur.execute('SELECT * FROM mindcrackers')]

    for m in mindcrackers:
        print(m[0])

        for video in util.youtube_feed(m[0], number_videos=5):
            cur.execute('SELECT * FROM videos WHERE video_id=?', (video['video_id'],))

            if cur.fetchone() == None:
                submission_title = '[' + m[1].strip() + '] ' + video['title'] + ' (' + util.get_HMS(video['duration']) + ')'
                video_url = 'http://www.youtube.com/watch?v=' + video['video_id']

                print(submission_title)

                r.submit(cfg['subreddit'], submission_title, url=video_url)

                cur.execute('INSERT INTO videos VALUES (?, ?, ?, ?)', (video['video_id'], video['title'], video['uploader'], video['duration']))
                conn.commit()

    cur.close()
    conn.close()


if __name__ == '__main__':
    main()
