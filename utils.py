import random
from models import Video
from google.appengine.ext import ndb


def get_max_random():
    return Video.query().order(-Video.random). \
        filter(Video.approved == True).get().random


def get_max_random_with_categories(categories):
    return Video.query().order(-Video.random). \
        filter(Video.approved == True, Video.categories.IN(categories)) \
        .get().random


def get_random_video():
    if not Video.query().get():
        return
    random_float = random.uniform(0, get_max_random())
    return Video.query() \
        .order(Video.random) \
        .filter(Video.approved == True, Video.random >= random_float).get()


def get_random_video_from_categories(categories):
    if not Video.query().filter(Video.categories.IN(categories)).get():
        return
    random_float = random.uniform(0, get_max_random_with_categories(categories))
    return Video.query(). \
        order(Video.random). \
        filter(Video.approved == True, Video.categories.IN(categories),
               Video.random >= random_float).get()


class Message():
    def __init__(self, variant, msg):
        self.variant = variant
        self.message = msg
