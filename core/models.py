import uuid

from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from django.db import transaction
from django.db.models import F, Prefetch
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse

from .utils import get_thumbnail
from misc.markup import parse


class BoardManager(models.Manager):
    # TODO: make this a Bord method rather than Manager
    def threads_page(self, page_num, board):
        """Returns EVALUATED threads list."""
        entries = board.thread_set.visible().order()
        paginator = Paginator(entries, board.threads_per_page)
        # ensure that page in [1, num_pages]
        page_num = max(min(page_num, paginator.num_pages), 1)
        page = paginator.page(page_num)
        threads = page.object_list

        # This is a dumb implementation of greatest-n-per-category pattern
        # done by simply fetching all the posts and then truncating
        # TODO: dig into a better implementation
        threads = threads.prefetch_related(Prefetch('post_set',
                                           queryset=Post.objects.present()))

        threads = list(threads)
        for t in threads:
            # TODO: 4 is hard-coded, better to add the option to the Board table
            t.latest_posts = list(t.post_set.all())[-4:]
            t.posts_set = None
        page.object_list = threads
        return page

class Board(models.Model):
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    threads_per_page = models.PositiveSmallIntegerField(default=10)
    pages_num = models.PositiveSmallIntegerField(default=10)
    bumplimit = models.PositiveSmallIntegerField(default=500)
    moderators = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)

    objects = BoardManager()

    def __unicode__(self):
        return u"<Board: %s>" % self.slug

    def get_absolute_url(self):
        return reverse('board', kwargs={'slug': self.slug})

    @property
    def max_threads(self):
        return self.threads_per_page * self.pages_num

    def moderated_by(self, user):
        return user.is_authenticated() and self.moderators.filter(pk=user.pk).exists()


def image_upload_path(instance, filename):
    if '.' in filename:
        extension = filename.split('.')[-1]
    else:
        extension = ''
    return "images/{}.{}".format(uuid.uuid4(), extension)

class BasePost(models.Model):
    name = models.CharField(max_length=100, blank=True)
    title = models.CharField(max_length=150, blank=True)
    raw_body = models.TextField(validators=[
        RegexValidator(regex=r'^\s*$', message='The body may not be empty.', inverse_match=True)
    ])
    body = models.TextField()   # computed raw_body
    ip = models.GenericIPAddressField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_hidden = models.BooleanField(default=False)  # fake deletion

    image = models.ImageField(upload_to=image_upload_path, null=True)
    thumbnail = models.ImageField(upload_to='thumbs/', null=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.body = replies_to_links(parse(self.raw_body), board=self.board)

        if not self.pk and self.image:
            thumb = get_thumbnail(self.image)
            self.image.save(self.image.name, self.image, save=False)
            img_name = self.image.name.split('/')[-1]
            self.thumbnail.save(img_name, thumb, save=False)

        super(BasePost, self).save(*args, **kwargs)

class ThreadsManager(models.Manager):
    @transaction.atomic
    def create(self, *args, **kwargs):
        """Create new thread and mark the oldest (by `bumped_at`) as hidden."""
        thread = Thread(*args, **kwargs)
        thread.save()

        # TODO: there may be a better way to mark the oldest thread as hidden
        board = thread.board
        to_hide = board.thread_set.visible().order()[board.max_threads:]
        Thread.objects.filter(id__in=to_hide).update(is_hidden=True)
        return thread

class ThreadsQuerySet(models.QuerySet):
    def visible(self):
        return self.filter(is_hidden=False)

    def order(self):
        return self.order_by('-is_pinned', '-bumped_at')


class Thread(BasePost):
    board = models.ForeignKey(Board, db_index=False)
    is_pinned = models.BooleanField(default=False)
    is_closed = models.BooleanField(default=False,
                                    help_text="New posts cannot be submitted.")
    posts_count = models.IntegerField(default=0)  # denormalization

    bumped_at = models.DateTimeField(auto_now_add=True)  # denormalization

    objects = ThreadsManager.from_queryset(ThreadsQuerySet)()

    class Meta:
        index_together = ['board', 'is_pinned', 'bumped_at']

    def __unicode__(self):
        return u"<Thread: {}>".format(self.pk)

    def get_absolute_url(self):
        return reverse('thread', kwargs={'slug': self.board.slug,
                                         'thread_id': self.pk})

class PostsManager(models.Manager):

    @transaction.atomic
    def create(self, *args, **kwargs):
        """Create a new post, bump the related thread,
           increment posts counter on the related thread."""
        post = Post(*args, **kwargs)
        post.save()
        thread = Thread.objects.select_for_update().select_related('board').get(pk=post.thread_id)
        board = thread.board
        if thread.is_pinned or thread.posts_count < board.bumplimit:
            thread.bumped_at = post.created_at
        thread.posts_count = F('posts_count') + 1
        thread.save()
        post.thread = thread
        return post

    def new_posts(self, latest_id, thread_id, board_slug):
        return self.filter(thread_id=thread_id, thread__board__slug=board_slug,
                           id__gt=latest_id).present()

class PostsQuerySet(models.QuerySet):
    def present(self):
        # ordering by id since it corresponds the order of posting
        return self.filter(is_hidden=False).order_by('pk')

class Post(BasePost):
    thread = models.ForeignKey(Thread)

    objects = PostsManager.from_queryset(PostsQuerySet)()

    @property
    def board(self):
        return self.thread.board

    def __unicode__(self):
        return u"<Post: {}>".format(self.title or self.pk)


# FIXME: refactor this shit
# avoiding circular imports
from .post_markup import replies_to_links