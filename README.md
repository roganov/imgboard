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
- You can reference other posts using `>><id>` syntax

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

## Try out
The app is deployed on Heroku: https://mighty-eyrie-5540.herokuapp.com

First-time access is rather **slow** (as idle Heroku instances go down and start up on request), posting with images is slow as well because images are thumbnailed and transfered to AWS S3.

To login as moderator of the Programming board, go to /about/login/. The credentials are `moderator` and `password`. Go back to the Programming board and you'll see the Moderate button next to each post.

## Features I'm planning to implement
- Real-time fetching of new posts
- Introducing CAPCHA to prevent spamming
- For now, Django's LocMem cache backend is used on Heroku, needs to be moved to redis
- Full-text search