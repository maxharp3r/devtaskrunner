About
=====

This package makes it possible to automatically run background tasks
in App Engine.  This package is compatible with any App Engine framework; it 
requires modification to app.yaml to wire up a couple of URLs.

There are other packages that run tasks in dev mode, but they are written for
Django (http://appengine-cookbook.appspot.com/recipe/automatically-run-tasks-from-task-queue-on-development-sdk/)
or they require screen scraping and related dependencies
(http://www.gae123.com/articles/gaet/run-tasks.html).  Please check out those
projects if they sound better suited to your needs.


Dependencies
============

simplejson (http://pypi.python.org/pypi/simplejson/2.1.1)  To install:

    easy_install simplejson


To Install
==========

Drop this package somewhere in your app, then add handlers to app.yaml:

    - url: /devtaskrunner/.*
      script: path/to/handler.py


To Run Tasks
============

Note: the development server must be running to execute tasks.

To run all of the currently queued tasks:

    python path/to/devtaskrunner/runtasks.py

To periodically check and run all of the queued tasks:

    python path/to/devtaskrunner/runtasks.py -r

You can configure things like the url of your dev server, and how often the
process should check for new tasks.  For more command-line options, run:

    python path/to/devtaskrunner/runtasks.py -h


License
=======

Apache 2.0.  See the included file called LICENSE for information.


Thanks
======

http://appengine-cookbook.appspot.com/recipe/automatically-run-tasks-from-task-queue-on-development-sdk/

http://www.gae123.com/articles/gaet/run-tasks.html


