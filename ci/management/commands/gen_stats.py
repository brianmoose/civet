
# Copyright 2016 Battelle Energy Alliance, LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from django.core.management.base import BaseCommand
from ci import models
from ci import TimeUtils
from datetime import timedelta

class Command(BaseCommand):
    help = 'Dump the stats that John needs for his graphs'
    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=1,
            help='Specifies how many days in the past to start the search. Defaults to 1 day')

    def handle(self, *args, **options):
        days = options.get('days', 1)
        dt = TimeUtils.get_local_time() - timedelta(days=days)

        with open("num_tests.csv", "w") as f:
            f.write("date,repo,passed,failed,skipped\n")
            for s in models.JobTestStatistics.objects.filter(created__gte=dt).order_by('created').iterator():
                f.write("%s,%s,%s,%s,%s\n" % (s.created,
                    s.job.recipe.repository,
                    s.passed,
                    s.failed,
                    s.skipped,
                    ))

        with open("pr_stats.csv", "w") as f:
            f.write("created,repo,closed,last_modified\n")
            for pr in models.PullRequest.objects.filter(created__gte=dt).order_by('created', 'repository', 'number').iterator():
                f.write("%s,%s,%s,%s\n" % (pr.created, pr.repository, pr.closed, pr.last_modified))
