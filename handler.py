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

from datetime import datetime
import os

from google.appengine.api import apiproxy_stub_map
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
import simplejson as json

stub = apiproxy_stub_map.apiproxy.GetStub('taskqueue')

def is_dev():
  return os.environ['SERVER_SOFTWARE'].startswith('Development')
  

class TaskListHandler(webapp.RequestHandler):
  """ Returns a list of task json which may be fetched by wget to execute
  tasks locally.
  
  @see http://appengine-cookbook.appspot.com/recipe/automatically-run-tasks-from-task-queue-on-development-sdk/
  """
  def get(self):
    if not is_dev():
      self.response.out.write("This URL is only valid in a development environment.")
    else:
      #get all the tasks for all the queues
      tasks = []
      for queue in stub.GetQueues():
        queue_tasks = stub.GetTasks(queue['name'])
        map(lambda t: t.setdefault('queue_name', queue['name']), queue_tasks)
        tasks.extend(queue_tasks)
      
      #keep only tasks that need to be executed
      now = datetime.now()
      fn = lambda t: datetime.strptime(t['eta'],'%Y/%m/%d %H:%M:%S') < now
      tasks = filter(fn, tasks)
      
      self.response.headers['Content-Type'] = 'application/json'
      self.response.out.write(json.dumps(tasks))


class TaskFlushHandler(webapp.RequestHandler):
  """Flushes all tasks from a queue."""
  def get(self, queue_name):
    if not is_dev():
      self.response.out.write("This URL is only valid in a development environment.")
    else:
      stub.FlushQueue(queue_name)
      self.response.headers['Content-Type'] = 'text/plain'
      self.response.out.write('cleared queue %s' % queue_name)


urls = [('/devtaskrunner/list', TaskListHandler),
        ('/devtaskrunner/flush/(.*)', TaskFlushHandler),]
application = webapp.WSGIApplication(urls, debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()

