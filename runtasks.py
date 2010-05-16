#!/usr/bin/env python
#
# Copyright 2010 Blue Shift Software Laboratory, Inc.
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

import cookielib
from optparse import OptionParser
import urllib2

import simplejson as json

DEFAULT_BASE_URL = 'http://localhost:8080'
DEFAULT_INTERVAL = 20
TASK_LIST_URL = '/devtaskrunner/list'
TASK_FLUSH_URL = '/devtaskrunner/flush/%s'
ADMIN_LOGIN_URL = '/_ah/login?email=test@example.com&admin=True&action=Login&continue=/'


class DevTaskRunner(object):
  def __init__(self, base_url):
    self.base_url = base_url
    self.queues = set()
    self._get_admin_cookie()

  def _get_admin_cookie(self):
    """Logging in as admin will give us a cookie to bypass security"""
    cj = cookielib.LWPCookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    urllib2.install_opener(opener)
    urllib2.urlopen( urllib2.Request(self.base_url + ADMIN_LOGIN_URL) )
  
  def run(self):
    result = urllib2.urlopen(self.base_url + TASK_LIST_URL).read()
    tasks = json.loads(result)
    did_find_tasks = (len(tasks) > 1)
    
    if did_find_tasks:
      for task in tasks:
        url = "%s%s" % (self.base_url, task['url'])
        body = task['body']
        headers = dict([(pair[0], pair[1]) for pair in task['headers']])
        print "Running %s (%s)" % (task['name'], url)
        req = urllib2.Request(url, body, headers)
        urllib2.urlopen(req)
        self.queues.add(task['queue_name'])
    return did_find_tasks
  
  def clean_up(self):
    for queue_name in self.queues:
      url_path = TASK_FLUSH_URL % queue_name
      urllib2.urlopen(self.base_url + url_path).read()
    self.queues.clear()


def parseargs():
    parser = OptionParser(usage='%prog [OPTIONS] [queue-name]')
    parser.add_option('--base-url', dest='base_url', default=DEFAULT_BASE_URL,
                      help="Dev server url. default: %s" % DEFAULT_BASE_URL)
    parser.add_option('-r', '--repeat', dest='do_repeat', action="store_true", 
                      default=False,
                      help="Periodically check for new tasks automatically")
    parser.add_option('--interval', dest='interval', type="int", 
                      default=DEFAULT_INTERVAL,
                      help=("How long to pause between checks (secs).  "
                            "default: %s" % DEFAULT_INTERVAL))
    options, args = parser.parse_args()
    return options, args 

def run_tasks(base_url):
  print "Running Tasks"
  task_runner = DevTaskRunner(base_url)
  task_runner.run()
  task_runner.clean_up()
  print "Done Running Tasks"

def run_tasks_auto(base_url, interval):
  from time import sleep
  print "Running Tasks (interval %s secs; hit ctrl-c to exit)" % interval
  task_runner = DevTaskRunner(base_url)
  while True:
    did_find_tasks = task_runner.run()
    task_runner.clean_up()
    if not did_find_tasks:
      try:
        sleep(interval)
      except KeyboardInterrupt:
        print "Done Running Tasks"
        exit(0)

def main():
  options, args = parseargs()
  if options.do_repeat:
    run_tasks_auto(options.base_url, options.interval)
  else:
    run_tasks(options.base_url)


if __name__ == "__main__":
  main()
