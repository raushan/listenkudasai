import os
import json
import random
import logging

from models import Video
from keys import SESSION_KEY
from utils import get_random_video, get_random_video_from_categories, Message

import webapp2
import jinja2
from webapp2_extras import sessions
from google.appengine.ext.webapp.util import run_wsgi_app

template_path = os.path.join(os.path.dirname(__file__), 'templates')
JINJA_ENV = jinja2.Environment(loader=jinja2.FileSystemLoader(template_path),
                               extensions=['jinja2.ext.autoescape'],
                               autoescape=True)


def get_template(template_name):
    return JINJA_ENV.get_template(template_name)


class BaseHandler(webapp2.RequestHandler):
    def dispatch(self):
        self.session_store = sessions.get_store(request=self.request)
        try:
            webapp2.RequestHandler.dispatch(self)
        finally:
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        return self.session_store.get_session()

    def flash(self, msg, error=True):
        key = "error_messages" if error else "success_messages"
        self.session.add_flash(msg, key=key)


class HomeHandler(BaseHandler):
    def get(self):
        context = {"messages": []}
        for error in self.session.get_flashes("error_messages"):
            context["messages"].append(Message("danger", error[0]))
        for error in self.session.get_flashes("success_messages"):
            context["messages"].append(Message("success", error[0]))
        self.response.write(get_template('index.html').render(context))


class VideoRetriever(webapp2.RequestHandler):
    def get(self):
        vid = get_random_video()
        if not vid:
            return self.response.out.write(json.dumps({'status': 'failure'}))
        embed_frame = vid.get_embed_frame()
        json_response = json.dumps({'video_html': embed_frame,
                                    'video_id': vid.key.id(),
                                    'status': 'success'})
        return self.response.write(json_response)


class SubmitHandler(BaseHandler):
    def post(self):
        video_url = self.request.get('urlinput')
        categories = list(set(self.request.get_all('ingenre')))
        for category in categories:
            if not Video.valid_categories.get(category.lower()):
                categories.remove(category)
        if not video_url or not categories:
            self.flash("Please fill in all required fields")
            return self.redirect("/")
        vid = Video(url=video_url,
                    categories=categories,
                    random=random.random(),
                    approved=False)
        vid.video_id = vid.get_video_id()
        if not vid.video_id:
            self.flash("Submission error. Possibly invalid youtube url")
        else:
            vid.put()
            self.flash("Your link has been submitted and is awaiting approval",
                       False)
        self.redirect("/")


class AdvancedSearchHandler(BaseHandler):
    def post(self):
        categories = self.request.get_all('list[]')
        if not categories:
            self.flash("Please choose a category")
            return self.redirect("/")
        vid = get_random_video_from_categories(categories)
        if not vid:
            return self.response.out.write(json.dumps({'status': 'failure'}))
        embed_frame = vid.get_embed_frame()
        json_response = json.dumps({'video_html': embed_frame,
                                    'categories': categories,
                                    'status': 'success'})
        return self.response.write(json_response)


class ReportHandler(BaseHandler):
    def post(self):
        video_id = self.request.get('video_id')
        vid = Video.get_by_id(int(video_id))
        if not vid:
            self.flash("Problem reporting video")
            return self.redirect("/")
        vid.problem_reported = True
        vid.put()
        self.flash("The video has been reported", False)
        self.redirect("/")


config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': SESSION_KEY
}

application = webapp2.WSGIApplication([('/', HomeHandler),
                                       ('/video', VideoRetriever),
                                       ('/submit', SubmitHandler),
                                       ('/advanced', AdvancedSearchHandler),
                                       ('/report', ReportHandler)
                                       ], config=config,
                                      debug=False)


def main():
    logging.getLogger().setLevel(logging.DEBUG)
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
