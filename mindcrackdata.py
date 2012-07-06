import psycopg2
from psycopg2 import extras


class MindCrackData(object):
    def __init__(self, connect_string):
        self.conn = psycopg2.connect(connect_string)
        self.cur = self.conn.cursor(cursor_factory=extras.RealDictCursor)
        psycopg2.extensions.register_type(psycopg2.extensions.UNICODE, self.cur)

    def add_video(self, video_id, title, duration, uploader, uploaded, description, thumbnail):
        self.cur.execute('SELECT video_id FROM videos WHERE video_id=\'{}\''.format(video_id))

        if self.cur.fetchone() == None:
            self.cur.execute('INSERT INTO videos VALUES (%s, %s, %s, %s, %s, %s, %s);',
                (video_id, title, duration, uploader.lower(), uploaded, description, thumbnail))

            self.conn.commit()
        else:
            self.update_video(video_id, title, duration, uploader, uploaded, description, thumbnail)

    def update_video(self, video_id, title, duration, uploader, uploaded, description, thumbnail):
        self.cur.execute('UPDATE videos SET \
            title=%s, \
            duration=%s, \
            uploaded=%s, \
            description=%s, \
            thumbnail=%s \
            WHERE video_id=%s', (title, duration, uploaded, description, thumbnail, video_id))

        self.conn.commit()

    def remove_video(self, video_id):
        self.cur.execute('DELETE FROM videos WHERE video_id=%s', (video_id, ))
        self.conn.commit()

    def add_mindcracker(self, username, name, url):
        self.cur.execute('INSERT INTO mindcrackers VALUES (%s, %s, %s);', (username.lower(), url.lower(), name,))
        self.conn.commit()

    def update_mindcracker(self, username, name, url):
        self.cur.execute('UPDATE mindcrackers SET \
            username=%s, \
            name=%s, \
            url=%s \
            WHERE username=%s', (username, name, url, username))

    def remove_mindcracker(self, username):
        self.cur.execute('DELETE FROM mindcrackers WHERE username=%s', (username, ))

    def mindcrackers(self):
        self.cur.execute('SELECT * FROM mindcrackers')

        return [m for m in self.cur]

    def videos(self, mindcrackers=None, num_videos=1, offset=0):
        if not mindcrackers:
            mindcrackers = tuple([m['username'] for m in self.mindcrackers()])

        self.cur.execute('SELECT * FROM videos, mindcrackers \
            WHERE videos.uploader IN %s \
            AND videos.uploader = mindcrackers.username \
            ORDER BY uploaded DESC LIMIT %s OFFSET %s',
            (mindcrackers, num_videos, offset))

        return [v for v in self.cur]
