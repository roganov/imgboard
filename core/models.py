from django.db import models
from django.db import transaction
from django.db.models import F

class Board(models.Model):
    slug = models.SlugField(unique=True)
    threads_per_page = models.PositiveSmallIntegerField(default=10)
    pages_num = models.PositiveSmallIntegerField(default=10)
    bumplimit = models.PositiveSmallIntegerField(default=500)
    description = models.TextField(blank=True)

    @property
    def max_threads(self):
        return self.threads_per_page * self.pages_num

    def __unicode__(self):
        return u"<Board: %s>" % self.slug

class BasePost(models.Model):
    name = models.CharField(max_length=100, blank=True)
    title = models.CharField(max_length=150, blank=True)
    raw_body = models.TextField()
    body = models.TextField()   # computed raw_body
    created_at = models.DateTimeField(auto_now_add=True)
    is_hidden = models.BooleanField(default=False)  # fake deletion

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        # TODO: function to actually compute the body
        self.body = self.raw_body
        super(BasePost, self).save(*args, **kwargs)

class ThreadsManager(models.Manager):
    @transaction.atomic
    def create(self, *args, **kwargs):
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
    board = models.ForeignKey(Board)
    is_pinned = models.BooleanField(default=False)
    is_closed = models.BooleanField(default=False,
                                    help_text="New posts cannot be submitted.")
    posts_count = models.IntegerField(default=0)  # denormalization

    bumped_at = models.DateTimeField(auto_now_add=True)  # denormalization

    objects = ThreadsManager.from_queryset(ThreadsQuerySet)()

    def __unicode__(self):
        return u"<Thread: {}>".format(self.pk)

class PostsManager(models.Manager):

    @transaction.atomic
    def create(self, *args, **kwargs):
        """Create a new post, bump the related thread,
           increment posts counter on the related thread. """
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

class Post(BasePost):
    thread = models.ForeignKey(Thread)

    objects = PostsManager()

    def __unicode__(self):
        return u"<Post: {}>".format(self.title or self.pk)
