from google.appengine.ext import ndb
import re


class Video(ndb.Model):
    url = ndb.StringProperty(required=True)
    reported = ndb.BooleanProperty()
    categories = ndb.StringProperty(repeated=True)
    tags = ndb.StringProperty(required=False, repeated=True)
    duration = ndb.IntegerProperty(required=False)
    problem_reported = ndb.BooleanProperty(required=False)
    approved = ndb.BooleanProperty()
    random = ndb.FloatProperty()
    video_id = ndb.StringProperty(required=False)

    valid_categories = {'music': 1,  'drama': 2, 'technology': 3,
                        'video games': 4, 'news': 5, 'anime': 6,
                        'lifestyle': 7, 'other': 8}

    def get_embed_frame(self):
        return '<iframe class="embed-responsive-item" src="https://www.youtube.com/embed/%s"></iframe>' % (self.get_video_id())

    def get_video_id(self):
        if self.video_id:
            return self.video_id
        r = re.compile(".*(?:youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=)([^#\&\?]*).*")
        result = r.findall(self.url)
        return result[0] if result else ""
