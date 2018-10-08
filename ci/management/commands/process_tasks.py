from __future__ import unicode_literals, absolute_import
from django.core.management.base import BaseCommand
from ci import models
import os
import time

class Command(BaseCommand):
    help = 'Process tasks in the task queue.'
    def add_arguments(self, parser):
        parser.add_argument('--dryrun', default=False, action='store_true',
                help="Don't actually execute the task, just show what would be run. "
                    "This quits after looking at the current queue")
        parser.add_argument('--server', "-s", help="Only run tasks on this server")
        parser.add_argument('--one-task', action="store_true", help="Only run one task")
        parser.add_argument('--stop', action="store_true", help="Make the tasks runners stop")
        parser.add_argument('--clear-stop', action="store_true", help="Allow tasks runners to start")
        parser.add_argument('--sleep', type=int, default=3,
                help="Sleep for this amount when there are no jobs to run")

    def _do_next(self):
        try:
            t = models.Task.next_task()
            if t:
                self.stdout.write("Running: %s" % t)
                return t.run()
        except models.Task.DoesNotExist:
            self.stdout.write("Task does not exist")
        return False

    def _dry_run(self, one_task):
        task_list = models.Task.available_tasks()
        if one_task:
            self.stdout.write("DRYRUN: %s" % task_list.first())
        else:
            for t in task_list:
                self.stdout.write("DRYRUN: %s" % t)

    def _should_stop(self):
        return os.path.exists(self._stop_file)

    def _create_stop_file(self):
        if not self._should_stop():
            with open(self._stop_file, "w") as f:
                f.write("")

    def _rm_stop_file(self):
        if os.path.exists(self._stop_file):
            os.unlink(self._stop_file)

    def handle(self, *args, **options):
        self._server = options["server"]
        self._stop_file = os.path.join(os.path.realpath(os.path.dirname(__file__)), "stop_tasks")
        sleep = options["sleep"]

        if options["clear_stop"]:
            self._rm_stop_file()
            return
        if options["stop"]:
            self._create_stop_file()
            return

        if options["dryrun"]:
            self._dry_run(options["one_task"])
        elif options["one_task"]:
            self._do_next()
        else:
            while not self._should_stop():
                if not self._do_next():
                    if self._should_stop():
                        break
                    time.sleep(sleep)
