from django.contrib import admin
from .models import Author, Book, MetaData, WannaBook, Series, Tag, Rating, Translator, CommentAnnotation, CommentReview, Review, Collection, LoaningRecord, BookRating, Annotation, Photo
import logging
SEARCH_VAR = 'q'


class SeriesAdmin(admin.ModelAdmin):
    pass


admin.site.register(Series, SeriesAdmin)


class TagAdmin(admin.ModelAdmin):
    pass


admin.site.register(Tag, TagAdmin)


class RatingAdmin(admin.ModelAdmin):
    pass


admin.site.register(Rating, RatingAdmin)


class TranslatorAdmin(admin.ModelAdmin):
    pass


admin.site.register(Translator, TranslatorAdmin)


class CommentReviewAdmin(admin.ModelAdmin):
    pass


admin.site.register(CommentReview, CommentReviewAdmin)


class ReviewAdmin(admin.ModelAdmin):
    pass


admin.site.register(Review, ReviewAdmin)


class CollectionAdmin(admin.ModelAdmin):
    pass


admin.site.register(Collection, CollectionAdmin)


class BookRatingAdmin(admin.ModelAdmin):
    pass


admin.site.register(BookRating, BookRatingAdmin)


class AnnotationAdmin(admin.ModelAdmin):
    pass


admin.site.register(Annotation, AnnotationAdmin)


class PhotoAdmin(admin.ModelAdmin):
    pass


admin.site.register(Photo, PhotoAdmin)


class MetaDataInline(admin.TabularInline):
    model = MetaData
    extra = 0


class BookAdmin(admin.ModelAdmin):
    filter_horizontal = ('author', 'translator')
    list_display = ('title', 'amount', 'remaining', 'shelf_time', 'image', 'summary_short', 'was_published_recently',)
    list_display_links = ('title',)
    search_fields = ['title',]
    ordering = ('-shelf_time',)
    date_hierarchy = 'shelf_time'
    #inlines = [MetaDataInline ]

    def get_queryset(self, request):
        if '' == request.GET.get(SEARCH_VAR, ''):
            return super(BookAdmin, self).get_queryset(request).all()
        return super(BookAdmin, self).get_queryset(request)


admin.site.register(Book, BookAdmin)


class AuthorAdmin(admin.ModelAdmin):
    search_fields = ('name',)


admin.site.register(Author, AuthorAdmin)


class WannaBookAdmin(admin.ModelAdmin):
    pass


admin.site.register(WannaBook, WannaBookAdmin)


class MetaDataAdmin(admin.ModelAdmin):
    raw_id_fields = ('book',)
    list_display = ('book', 'serial_number_long', 'available_str', 'owner', 'status', 'status_str', 'applicant',
                    'borrow_date_time', 'should_return_date_time_addition', )
    list_editable = ('book', 'serial_number')
    list_display_links = ('book',)
    search_fields = ('serial_number', 'book__title',)
    list_editable = ['status']
    ordering = ('-serial_number',)

    actions = ['batch_borrow', 'batch_give_back', 'batch_postpone', 'batch_apply']
    #


    def batch_borrow(self, request, queryset):
        for q in queryset:
            try:
                q.borrow()
            except ValueError as e:
                self.message_user(request, "%s（%s）借阅失败（请检查书籍是否已借走）." % (q.book.title,q.serial_number))
                logging.exception(e)
    batch_borrow.short_description = '批量借阅'

    def batch_give_back(self, request, queryset):
        for q in queryset:
            try:
                q.give_back()
            except ValueError as e:
                self.message_user(request, "%s（%s）归还失败（请检查书籍是否已归还）." % (q.book.title,q.serial_number))
                logging.exception(e)
    batch_give_back.short_description = '批量归还'

    def batch_postpone(self, request, queryset):
        for q in queryset:
            try:
                q.postpone()
            except ValueError as e:
                self.message_user(request, "%s（%s）延期失败（请检查书籍是否达延期上限）." % (q.book.title,q.serial_number))
                logging.exception(e)
    batch_postpone.short_description = '批量延期15天'

    def batch_apply(self, request, queryset):
        for q in queryset:
            try:
                q.apply(3)
            except ValueError as e:
                self.message_user(request, "%s（%s）申请失败（请检查是否达借阅、申请上限）." % (q.book.title,q.serial_number))
                logging.exception(e)
    batch_apply.short_description = '申请'


admin.site.register(MetaData, MetaDataAdmin)


class LoaningRecordAdmin(admin.ModelAdmin):
    list_display = ('book__title', 'borrower', 'datetime',)
    search_fields = ('book__title',)


admin.site.register(LoaningRecord, LoaningRecordAdmin)


# class BorrowRecordAdmin:
#     list_display = ('book__title', 'borrower', 'datetime',)
#     search_fields = ('book__title',)
#
#
# admin.site.register(BorrowRecord, BorrowRecordAdmin)

#
# class BorrowingAndReturningStatChartsAdmin(admin.ModelAdmin):
#     data_charts = {
#         "borrow": {'title': '借阅统计', "x-field": "date", "y-field": ('borrow_count',)},
#         "return": {'title': '还书统计', "x-field": "date", "y-field": ('return_count',)}
#     }
#
#
# admin.site.register(BorrowReturnStat, BorrowingAndReturningStatChartsAdmin)
