# Imageboard
Imageboard is a system of anonymous forums with the ability to attach an image to each post (hence the name).

## Features
- Each board has threads, each thread has posts
- Each board (forum) has limited number of threads, creation of new threads removes old ones
- New posts bump the parent thread unless the total number of posts exceed a certain number
- The posts are formatted with slightly customized markdown, code hightlighting is   supported as well
- New boards are created in the admin page
- Superuser can create moderators for each board
- Moderators can pin, close or delete threads, delete posts and ban the poster (by ip)
- Pinned threads occupy the top position and never get purged
- Referencing other posts using `>><id>` syntax
- New posts are showed instantly, no need to reload (requires additional setup)

## Installation
CPython 2.7.* is required
```sh
git clone this_repo
cd imgboard
virtualenv .env
source .env/bin/activate
pip install -r requirements/local.txt
DJANGO_SETTINGS_MODULE=imgboard.settings.local ./manage.py migrate
DJANGO_SETTINGS_MODULE=imgboard.settings.local ./manage.py runserver
```
Running tests:
```sh
pip install -r requirements/testing.txt
DJANGO_SETTINGS_MODULE=imgboard.settings.testing ./manage.py test
```

## Live updates
Implemented via Redis pub/sub and gevent.

To use locally:
- install redis (`apt-get install redis-server` on Ubuntu)
- start redis `$ redis-server`
- configure `REDIS_CONF` in settings/local.py (or leave as is)
- run `pip install -r requirements/live_updates.txt`
- set `ENABLE_LIVE_UPDATES = true;` in static/src/js/common.js
- run `./manage.py runliveupdates` to start gevent
- open two pages with same thread, submit a new post, the post should be displayed on second pages instantly

## Try out
The app is deployed on Heroku: https://mighty-eyrie-5540.herokuapp.com

First-time access is rather **slow** (as idle Heroku instances go down and start up on request), posting with images is slow as well because images are thumbnailed and transfered to AWS S3.

To login as moderator of the Programming board, go to /about/login/. The credentials are `moderator` and `password`. Go back to the Programming board and you'll see the Moderate button next to each post.

## Features I'm planning to implement
- For now, Django's LocMem cache backend is used on Heroku, needs to be moved to redis
- Full-text search
- Catalog on all threads on a give boards