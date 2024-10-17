from celery.loaders import get_loader_cls
from django import db

class CustomLoader(get_loader_cls("app")):
    def on_task_init(self, task_id, task):
        """Called before every task."""
        for conn in db.connections.all():
            conn.close_if_unusable_or_obsolete()
        super(get_loader_cls("app"), self).on_task_init(task_id, task)