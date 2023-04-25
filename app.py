from abc import ABC

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from flask_script import Manager, Server
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from blueprints.course import course_blueprint
from scheduled.load_model import load_model
from scheduled.fetch_courses import fetch_courses
from scheduled.fine_tune_model import fine_tune_model
from blueprints.match import match_blueprint
from blueprints.feedback import feedback_blueprint
from apiflask import APIFlask

load_dotenv()

# Schedule fetch courses job to run every 24 hours at 03:00
scheduler = BackgroundScheduler(daemon=True)
trigger = CronTrigger(
    year="*", month="*", day="*", hour="3", minute="0", second="0"
)

scheduler.add_job(
    fetch_courses,
    trigger=trigger,
    name="fetch_courses",
)

scheduler.add_job(
    fine_tune_model,
    trigger=trigger,
    name="fine_tune_model",
)

scheduler.start()

app = APIFlask(__name__, spec_path='/openapi.yaml')
app.config['SPEC_FORMAT'] = 'yaml'
CORS(app)
app.register_blueprint(match_blueprint)
app.register_blueprint(course_blueprint)
app.register_blueprint(feedback_blueprint)

manager = Manager(app)


# On start load model and fetch courses
class CustomServer(Server, ABC):
    def __call__(self, app, *args, **kwargs):
        load_model()
        fetch_courses(first_run=True)
        return Server.__call__(self, app, *args, **kwargs)


manager.add_command('runserver', CustomServer())

if __name__ == "__main__":
    manager.run()
