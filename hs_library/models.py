from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from django.utils.html import format_html
import logging
from django.db.models import Q
from time import gmtime, strftime
from django.conf import settings
import functools

app_name = 'hs_library'


class Series(models.Model):
    title = models.CharField(max_length=200, verbose_name='系列')

    def __str__(self):
        return str(self.title)

    class Meta:
        verbose_name = '系列'
        verbose_name_plural = '系列管理'


class Tag(models.Model):
    name = models.CharField(max_length=200, verbose_name='标签')

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = '标签'
        verbose_name_plural = '标签管理'

RATING_CHOICES = (
    ('5', '力荐'),
    ('4', '推荐'),
    ('3', '还行'),
    ('2', '较差'),
    ('1', '很差'),
)


class Rating(models.Model):
    max = models.IntegerField(verbose_name='最大分数')
    value = models.IntegerField(verbose_name='平均分数')
    min = models.IntegerField(verbose_name='最小分数')

    def __str__(self):
        return str(self.value)

    class Meta:
        verbose_name = '评分'
        verbose_name_plural = '评分管理'


class Translator(models.Model):
    name = models.CharField(max_length=50, verbose_name='译者名')
    introduction = models.CharField(max_length=200, verbose_name='译者简介', default='')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '译者'
        verbose_name_plural = '译者管理'

    def introduction_short(self):
        if len(str(self.introduction)) > 10:
            return '{}...'.format(str(self.introduction)[0:10])
        else:
            return str(self.introduction)


class Author(models.Model):
    name = models.CharField(max_length=50, verbose_name='作者名')
    introduction = models.CharField(max_length=2000, verbose_name='作者简介', default='')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '作者'
        verbose_name_plural = '作者管理'

    def introduction_short(self):
        if len(str(self.introduction)) > 10:
            return '{}...'.format(str(self.introduction)[0:10])
        else:
            return str(self.introduction)


class BookRating(models.Model):
    average = models.DecimalField(max_digits=2, decimal_places=1, verbose_name='总评分')
    max = models.IntegerField(verbose_name='最高分')
    min = models.IntegerField(verbose_name='最低分')
    numRaters = models.BigIntegerField(verbose_name='评分数')

    def __str__(self):
        return str(self.average)

    class Meta:
        verbose_name = '书籍评分'
        verbose_name_plural = '书籍评分管理'

def get_sentinel_author():
    return Author.objects.get_or_create(name='deleted')


def get_sentienl_own():
    user = User.objects.all()[0]
    if not user:
        logger = logging.getLogger(__name__)
        logger.info('create user missing bookmanager password 123456')
        user = User.objects.create_user(username='missing book manager', email='1035381759@qq.com', password=123456)
    return user


BINDING_CHOICES = (
    ('平装', '平装'),
    ('精装', '精装'),
)


def book_image_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return '%s%s%s_%s' % ('uploads/', strftime("%Y/%m/%d/", gmtime()), str(instance.title), filename)



class Book(models.Model):
    isbn10 = models.IntegerField(unique=True, verbose_name='isbn10')
    isbn13 = models.IntegerField(unique=True, verbose_name='isbn13')
    title = models.CharField(max_length=200, verbose_name='书名')
    origin_title = models.CharField(blank=True, max_length=200, verbose_name='原名', default='')
    alt_title = models.CharField(blank=True, max_length=200, verbose_name='别名', default='')
    subtitle = models.CharField(blank=True, max_length=200, verbose_name='副标题', default='')
    author = models.ManyToManyField(Author, related_name='book_set', verbose_name='作者')
    translator = models.ManyToManyField(Translator, related_name='book_set', blank=True, verbose_name='译者')
    publisher = models.CharField(max_length=200, verbose_name='出版商')
    pubdate = models.DateField(verbose_name='出版日期')
    rating = models.OneToOneField(BookRating, related_name='book', verbose_name='总评分', on_delete=models.PROTECT)
    #rating = models.DecimalField(max_digits=2, decimal_places=1, verbose_name='总评')
    #总评是收集该书有关的收藏、评论评分，综合计算得出
    tags = models.ManyToManyField(Tag, related_name='book_set', verbose_name='标签')
    binding = models.CharField(max_length=20, choices=BINDING_CHOICES, verbose_name='装订')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='价格')
    series = models.ForeignKey(Series, related_name='book_set', blank=True, null=True, on_delete=models.PROTECT, verbose_name='系列')
    pages = models.BigIntegerField(verbose_name='页数')
    author_intro = models.CharField(max_length=2000, verbose_name='作者简介', default='')
    summary = models.CharField(max_length=2000, verbose_name='简介', default='')
    catalog = models.CharField(blank=True, max_length=2000, verbose_name='目录', default='')
    ebook_url = models.URLField(blank=True, max_length=200, verbose_name='电子书url', default='')
    ebook_price = models.DecimalField(blank=True, max_digits=10, decimal_places=2, verbose_name='电子书价格', default=0)

    shelf_time = models.DateTimeField('上架时间', default=timezone.now)
    like = models.BigIntegerField(primary_key=False, verbose_name='点赞数', default=0)
    image = models.ImageField(max_length=50, default='uploads/unnamed', upload_to=book_image_path,
                              verbose_name='封面')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '上架书籍'
        verbose_name_plural = '上架书籍管理'

    def was_published_recently(self):
        now = timezone.now()
        return now - timedelta(days=15) <= self.shelf_time <= now
    was_published_recently.admin_order_field = 'shelf_time'
    was_published_recently.boolean = True
    was_published_recently.short_description = '近期上架'

    def summary_short(self):
        if len(str(self.summary)) > 10:
            return '{}...'.format(str(self.summary)[0:10])
        else:
            return str(self.summary)
    summary_short.short_description = '简介'

    def amount(self):
        return self.metadata_set.count()

    amount.short_description = '总数'

    def remaining(self):
        return self.metadata_set.filter(status=MetaData.STATUS_ON_SHELF()).count()
    remaining.short_description = '剩余'


class Review(models.Model):
    book = models.ForeignKey(Book, related_name='review_set', on_delete=models.PROTECT, verbose_name='书籍')
    title = models.CharField(max_length=20, verbose_name='评论标题')
    summary = models.CharField(max_length=200, default='暂时没有评论呢，快来添加吧', verbose_name='评论')
    author = models.ForeignKey(User, related_name='comment_set', on_delete=models.PROTECT, verbose_name='评论人')
    published = models.DateTimeField(verbose_name='发布时间')
    updated = models.DateTimeField(verbose_name='更新时间')
    rating = models.OneToOneField(Rating, related_name='comment_set', on_delete=models.PROTECT, verbose_name='评分')
    votes = models.BigIntegerField(default=0, verbose_name='赞')
    useless = models.BigIntegerField(default=0, verbose_name='踩')

    def __str__(self):
        return str(self.title)

    class Meta:
        verbose_name = '评论'
        verbose_name_plural = '评论管理'


class CommentReview(models.Model):
    reply = models.CharField(max_length=200, verbose_name='回复内容')
    respondent = models.ForeignKey(User, related_name='comment_review_set', on_delete=models.PROTECT, verbose_name='回复人')
    comment = models.ForeignKey(Review, related_name='comment_review_set', on_delete=models.PROTECT, verbose_name='回复')

    def __str__(self):
        return str(self.reply)

    class Meta:
        verbose_name = '回复'
        verbose_name_plural = '回复管理'


class Photo(models.Model):
    photo = models.URLField(blank=True, max_length=200, verbose_name='照片', default='')

class Annotation(models.Model):
    book = models.ForeignKey(Book, related_name='annotation_set', on_delete=models.PROTECT, verbose_name='书本')
    author_user = models.ForeignKey(User, related_name='annotation_set', on_delete=models.PROTECT, verbose_name='用户')
    chapter = models.CharField(max_length=200, verbose_name='章节')
    page_no = models.IntegerField(verbose_name='页数')
    privacy = models.IntegerField(verbose_name='隐私级别')
    abstract = models.CharField(max_length=2000, verbose_name='摘要')
    content = models.CharField(max_length=5000, verbose_name='正文')
    abstract_photo = models.ForeignKey(Photo, blank=True, related_name='annotation_abstract_photo_set', on_delete=models.PROTECT,
                                       verbose_name='摘要图片')
    photos = models.ManyToManyField(Photo, blank=True, related_name='annotation_photos_set', verbose_name='图片')
    hasmath = models.BooleanField(verbose_name='')
    time = models.TimeField(verbose_name='时间')

    def __str__(self):
        return str(self.chapter)

    def last_photo(self):
        return 0

    def comments_count(self):
        return Annotation.comment_annotation_set.count()

    class Meta:
        verbose_name = '笔记'
        verbose_name_plural = '笔记管理'

class CommentAnnotation(models.Model):
    reply = models.CharField(max_length=200, verbose_name='回复内容')
    respondent = models.ForeignKey(User, related_name='comment_annotation_set', on_delete=models.PROTECT, verbose_name='回复人')
    comment = models.ForeignKey(Annotation, related_name='comment_annotation_set', on_delete=models.PROTECT, verbose_name='回复')

    def __str__(self):
        return str(self.reply)

    class Meta:
        verbose_name = '回复'
        verbose_name_plural = '回复管理'


BORROW_CHOICES = (
    (0, '已借走'),
    (1, '已申请'),
    (2, '可借阅'),
    (3, '超期未归还'),
    (4, '预留状态'),

)

def postpone_recording(debug):
    def wrapper(func):
        @functools.wraps(func)
        def sub_wrapper(*args, **kwargs):
            metadata_obj = args[0]
            lr = PostPoneRecord()
            lr.book, lr.borrower, lr.datetime = \
                metadata_obj.book, metadata_obj.owner, timezone.now()

            if debug or not metadata_obj.internal_status_code_check(func.__name__):
                print(lr.book, lr.borrower, lr.datetime)
            else:
                lr.save()
            return func(*args, **kwargs)
        return sub_wrapper
    return wrapper

def borrow_recording(debug):
    def wrapper(func):
        @functools.wraps(func)
        def sub_wrapper(*args, **kwargs):
            date = timezone.now().date()
            metadata_obj = args[0]
            lr = BorrowRecord()
            lr.book, lr.borrower, lr.datetime = \
                metadata_obj.book, metadata_obj.owner, timezone.now()
            last = BorrowReturnStat.objects.filter(date=date)
            last = None if not last else last[0]
            if last:
                new = last
            else:
                new = BorrowReturnStat()
            new.date, new.borrow_count, new.return_count = date, 1 if not last or last.borrow_count == 0 else last.borrow_count + 1, 0 if not last else last.return_count

            if debug or not metadata_obj.internal_status_code_check(func.__name__):
                print(lr.book, lr.borrower, lr.datetime)
            else:
                lr.save()
                new.save()
            return func(*args, **kwargs)
        return sub_wrapper
    return wrapper

def loan_recording(debug):
    def wrapper(func):
        @functools.wraps(func)
        def sub_wrapper(*args, **kwargs):
            date = timezone.now().date()
            metadata_obj = args[0]
            lr = LoaningRecord()
            lr.book, lr.borrower, lr.datetime = \
                metadata_obj.book, metadata_obj.owner, timezone.now()

            last = BorrowReturnStat.objects.filter(date=date)
            last = None if not last else last[0]
            if last:
                new = last
            else:
                new = BorrowReturnStat()
            new.date, new.return_count, new.borrow_count = date, 1 if not last or last.return_count == 0 else last.return_count + 1, 0 if not last else last.borrow_count

            if debug or not metadata_obj.internal_status_code_check(func.__name__):
                print(lr.book, lr.borrower, lr.datetime)
            else:
                new.save()
                new.save()
            return func(*args, **kwargs)
        return sub_wrapper
    return wrapper


class MetaData(models.Model):
    book = models.ForeignKey(Book, related_name='metadata_set', on_delete=models.PROTECT, verbose_name='书籍')
    serial_number = models.BigIntegerField(unique=True, primary_key=False, verbose_name='序列号', )
    status = models.IntegerField(choices=BORROW_CHOICES, default=2, primary_key=False, verbose_name='借阅状态')
    owner = models.ForeignKey(User, default=1, related_name='metadata_owner_set', null=True, blank=True, on_delete=models.SET(get_sentienl_own),
                              verbose_name='所有者')
    applicant = models.ForeignKey(User, null=True, blank=True, related_name='metadata_applicant_set', on_delete=models.PROTECT, verbose_name='申请人')
    borrow_date_time = models.DateTimeField(null=True, blank=True, verbose_name='借阅时间')
    should_return_date_time = models.DateTimeField(null=True, blank=True, verbose_name='归还时间')

    def __str__(self):
        return str(self.book.title)

    class Meta:
        verbose_name = '上架单本'
        verbose_name_plural = '上架单本管理'


    def get_status(self):
        return self.status

    @classmethod
    def STATUS_BORROWED(cls):
        return BORROW_CHOICES[0][0]

    @classmethod
    def STATUS_APPLY(cls):
        return BORROW_CHOICES[1][0]

    @classmethod
    def STATUS_ON_SHELF(cls):
        return BORROW_CHOICES[2][0]

    @classmethod
    def STATUS_EXCEED_TIME_LIMIT(cls):
        return BORROW_CHOICES[3][0]

    def available(self):
        return self.STATUS_APPLY() == self.status

    def applicable(self):
        return self.STATUS_ON_SHELF() == self.status

    def returnable(self):
        return self.STATUS_BORROWED() == self.status \
               or self.STATUS_EXCEED_TIME_LIMIT() == self.status

    def can_postpone(self):
        return self.STATUS_BORROWED() == self.status

    def available_str(self):
        if self.available():
            return format_html('<p><span style="color: {};"</span>{}</p>', 'green', '是')
        else:
            return format_html('<p><span style="color: {};"</span>{}</p>', 'red', '否')
    available_str.short_description = '可借阅'

    def status_str(self):
        if self.applicable():
            return format_html('<p><span style="color: {};"</span>{}</p>', 'blue', '未申请')
        elif self.available():
            return format_html('<p><span style="color: {};"</span>{}</p>', 'green', '已申请')
        elif self.returnable():
            return format_html('<p><span style="color: {};"</span>{}</p>', 'red', '已借出')
        else:
            return self.str(self.status)
    status_str.short_description = '借阅状态'

    def serial_number_long(self):
        return '%08d' % self.serial_number
    serial_number_long.short_description = '序列号'

    def delay_days(self):
        if self.should_return_date_time == (self.borrow_date_time + timedelta(60)):
            return ''
        else:

            return '(延期' + str((self.should_return_date_time - (self.borrow_date_time + timedelta(60))).days) + '天)'

    def should_return_date_time_addition(self):
        if self.should_return_date_time is None:
            return '-'
        return str(self.should_return_date_time) + self.delay_days()
    should_return_date_time_addition.short_description = '应还日期'

    def internal_status_code_check(self, name):
        check_methods = {
            'apply': self.applicable,
            'borrow': self.available,
            'give_back': self.returnable,
            'postpone': self.can_postpone,
        }
        return check_methods[name]()

    def borrow_apply_limit_check(self, applicant_id):
        return MetaData.objects.filter(Q(applicant__id=applicant_id)).count() \
               + MetaData.objects.filter(Q(owner__id=applicant_id)).count() \
               < settings.BORROW_APPLY_LIMIT

    def point_check(self):
        return True

    def apply(self, applicant_id):
        if self.internal_status_code_check(self.apply.__name__)\
                and self.borrow_apply_limit_check(applicant_id) and self.point_check():
            self.status = self.STATUS_APPLY()
            self.applicant = User.objects.get(pk=applicant_id)
            self.save()
        else:
            raise ValueError('apply err')

        #TODO增加借阅记录

    @borrow_recording(settings.DEBUG)
    def borrow(self):
        if not self.internal_status_code_check(self.borrow.__name__):
            raise ValueError('borrow err')
        self.owner = self.applicant
        self.status = self.STATUS_BORROWED()
        self.borrow_date_time = timezone.now()
        self.should_return_date_time = self.borrow_date_time+timedelta(days=60)
        self.save()

    @loan_recording(settings.DEBUG)
    def give_back(self):
        if not self.internal_status_code_check(self.give_back.__name__):#TODO不能借阅提示管理员
            raise ValueError('give_back err')
        self.owner = User.objects.get(pk=1)
        self.applicant = None
        self.status = self.STATUS_ON_SHELF()
        self.borrow_date_time = None
        self.should_return_date_time = None
        self.save()

    @postpone_recording(settings.DEBUG)
    def postpone(self):
        if not self.internal_status_code_check(self.postpone.__name__):
            raise ValueError('postpone err')
        self.should_return_date_time += timedelta(days=15)
        self.save()

    def get_borrower(self):
        if self.applicant is None:
            return 'someone'
        return self.applicant.username

#每次查询自动更新状态
    class AutoCalOverdueStatusManager(models.Manager):
        def get_queryset(self):
            qs = super().get_queryset()
            for q in qs:
                if q.should_return_date_time:
                    if timezone.now() > q.should_return_date_time:
                        q.status = BORROW_CHOICES[3][0]
                        q.save()
            return qs

    objects = AutoCalOverdueStatusManager()


STATUS_CHOICES = (
    ('reading', '在读'),
    ('read', '读过'),
    ('wish', '想读'),
)


class Collection(models.Model):
    book = models.ForeignKey(Book, related_name='collection_set', on_delete=models.PROTECT, verbose_name='藏书')
    comment = models.CharField(max_length=200, default='暂时没有评论呢，快来添加吧', verbose_name='评论')
    rating = models.ForeignKey(Rating, related_name='collection_set', on_delete=models.PROTECT, verbose_name='评分')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, verbose_name='状态')
    tags = models.ManyToManyField(Tag, related_name='collection_set', verbose_name='标签')
    updated = models.DateTimeField(default=timezone.now, verbose_name='更新时间')
    collector = models.ForeignKey(User, related_name='collection_set', on_delete=models.PROTECT, verbose_name='推荐人')

    def __str__(self):
        return str(self.book.title)

    class Meta:
        verbose_name = '收藏'
        verbose_name_plural = '收藏管理'


class WannaBook(models.Model):
    title = models.CharField(max_length=50, verbose_name='书名')
    author = models.CharField(max_length=50, verbose_name='作者')
    describe = models.CharField(max_length=200, verbose_name='描述')
    recommender = models.ForeignKey(User, related_name='wannabook_set', on_delete=models.PROTECT, verbose_name='推荐人')
    likes = models.BigIntegerField(primary_key=False, verbose_name='点赞数')

    def __str__(self):
        return str(self.title)

    class Meta:
        verbose_name = '想看书籍'
        verbose_name_plural = '想看书籍管理'


class FavoriteBookWeeklyStatistic(models.Model):
    book = models.ForeignKey(Book, related_name='favorite_book_weekly_statistic_set', on_delete=models.PROTECT, verbose_name='书籍')
    book_weekly_likes = models.BigIntegerField(primary_key=False, verbose_name='本周点赞数', default=0)
    book_weekly_likes_save = models.BigIntegerField(primary_key=False, verbose_name='上周点赞数', default=0)


class FavoriteBookMonthlyStatistic(models.Model):
    book = models.ForeignKey(Book, related_name='favorite_book_monthly_statistic_set', on_delete=models.PROTECT, verbose_name='书籍')
    book_monthly_likes = models.BigIntegerField(primary_key=False, verbose_name='本月点赞数', default=0)
    book_monthly_likes_save = models.BigIntegerField(primary_key=False, verbose_name='上月点赞数', default=0)


class FavoriteBookAnnuallyStatistic(models.Model):
    book = models.ForeignKey(Book, related_name='favorite_book_annually_statistic_set', on_delete=models.PROTECT, verbose_name='书籍')
    book_annually_likes = models.BigIntegerField(primary_key=False, verbose_name='本年点赞数', default=0)
    book_annually_likes_save = models.BigIntegerField(primary_key=False, verbose_name='上年点赞数', default=0)


class MostWantBookWeeklyStatistic(models.Model):
    wanna_book = models.ForeignKey(WannaBook, related_name='most_want_book_weekly_statistic_set', on_delete=models.PROTECT, verbose_name='书籍')
    wanna_book_weekly_likes = models.BigIntegerField(primary_key=False, verbose_name='本周点赞数', default=0)
    wanna_book_weekly_likes_save = models.BigIntegerField(primary_key=False, verbose_name='上周点赞数', default=0)


class MostWantBookMonthlyStatistic(models.Model):
    wanna_book = models.ForeignKey(WannaBook, related_name='most_want_book_monthly_statistic_set', on_delete=models.PROTECT, verbose_name='书籍')
    wanna_book_monthly_likes = models.BigIntegerField(primary_key=False, verbose_name='本周点赞数', default=0)
    wanna_book_monthly_likes_save = models.BigIntegerField(primary_key=False, verbose_name='上周点赞数', default=0)


class MostWantBookAnnuallyStatistic(models.Model):
    wanna_book = models.ForeignKey(WannaBook, related_name='most_want_book_annuallystatistic_set', on_delete=models.PROTECT, verbose_name='书籍')
    wanna_book_annually_likes = models.BigIntegerField(primary_key=False, verbose_name='本周点赞数', default=0)
    wanna_book_annually_likes_save = models.BigIntegerField(primary_key=False, verbose_name='上周点赞数', default=0)


class HighRatingBookWeeklyStatistic(models.Model):
    book = models.ForeignKey(Book, related_name='high_rating_book_weekly_statistic_set', on_delete=models.PROTECT, verbose_name='书籍')
    weekly_avg_rating = models.DecimalField(max_digits=2, decimal_places=1, verbose_name='本周评分')
    weekly_rating_count = models.BigIntegerField(verbose_name='本周评分数')


class HighRatingBookMonthlyStatistic(models.Model):
    book = models.ForeignKey(Book, related_name='high_rating_book_monthly_statistic_set', on_delete=models.PROTECT, verbose_name='书籍')
    monthly_avg_rating = models.DecimalField(max_digits=2, decimal_places=1, verbose_name='本月评分')
    monthly_rating_count = models.BigIntegerField(verbose_name='本月评分数')


class HighRatingBookAnnuallyStatistic(models.Model):
    book = models.ForeignKey(Book, related_name='high_rating_book_annually_statistic_set', on_delete=models.PROTECT, verbose_name='书籍')
    annually_avg_rating = models.DecimalField(max_digits=12, decimal_places=10, verbose_name='本年评分')
    annually_rating_count = models.BigIntegerField(verbose_name='本年评分数')


class MostCommentedBookWeeklyStatistic(models.Model):
    book = models.ForeignKey(Book, related_name='most_commented_book_weekly_statistic_set', on_delete=models.PROTECT, verbose_name='书籍')
    weekly_comment_count = models.BigIntegerField(verbose_name='本周评论数')


class MostCommentedBookMonthlyStatistic(models.Model):
    book = models.ForeignKey(Book, related_name='most_commented_book_monthly_statistic_set', on_delete=models.PROTECT, verbose_name='书籍')
    monthly_comment_count = models.BigIntegerField(verbose_name='本月评论数')


class MostCommentedBookAnnuallyStatistic(models.Model):
    book = models.ForeignKey(Book, related_name='most_commented_book_annually_statistic_set', on_delete=models.PROTECT, verbose_name='书籍')
    annually_comment_count = models.BigIntegerField(verbose_name='本年评论数')


# class Record(models.Model):
#     book = models.ForeignKey(Book, on_delete=models.PROTECT, verbose_name='单本')
#     borrower = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='借阅人')
#     datetime = models.DateTimeField(verbose_name='借还日期', default=timezone.now)

#
class BorrowRecord(models.Model):
    book = models.ForeignKey(Book, related_name='borrow_record', on_delete=models.PROTECT, verbose_name='单本')
    borrower = models.ForeignKey(User, related_name='borrow_record', on_delete=models.PROTECT, verbose_name='借阅人')
    datetime = models.DateTimeField(verbose_name='借还日期', default=timezone.now)

    class Meta:
        verbose_name = '借书记录'
        verbose_name_plural = '借书记录'

class PostPoneRecord(models.Model):
    book = models.ForeignKey(Book, related_name='postpone_record', on_delete=models.PROTECT, verbose_name='单本')
    borrower = models.ForeignKey(User, related_name='postpone_record', on_delete=models.PROTECT, verbose_name='借阅人')
    datetime = models.DateTimeField(verbose_name='借还日期', default=timezone.now)

    class Meta:
        verbose_name = '延期记录'
        verbose_name_plural = '延期记录'

class LoaningRecord(models.Model):
    book = models.ForeignKey(Book, related_name='loaning_record', on_delete=models.PROTECT, verbose_name='单本')
    borrower = models.ForeignKey(User, related_name='loaning_record', on_delete=models.PROTECT, verbose_name='借阅人')
    datetime = models.DateTimeField(verbose_name='借还日期', default=timezone.now)
    comment = models.OneToOneField(Review, blank=True, null=True, on_delete=models.SET_NULL, verbose_name='评论')

    def book__title(self):
        return str(self.book.title)

    class Meta:
        verbose_name = '还书记录'
        verbose_name_plural = '还书记录'


class BorrowReturnStat(models.Model):
    date = models.DateField(verbose_name='日期', default=timezone.now)
    borrow_count = models.BigIntegerField(default=0, primary_key=False)
    return_count = models.BigIntegerField(default=0, primary_key=False)

    class Meta:
        verbose_name = '借阅统计'
        verbose_name_plural = '借阅统计'
