from tastypie.resources import ModelResource, Resource
from tastypie import fields
from tastypie.authentication import BasicAuthentication
from ..models import Book, WannaBook, MetaData, Author, Translator, Tag, Series, LoaningRecord, Rating, Review, BookRating, Annotation, Photo
import jieba
import heapq
import json
from django.db.models import Q
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.conf.urls import url
from tastypie.utils import trailing_slash
from .dingtalk_api.default_dingtalk_client import DefaultDingTalkClient
from .dingtalk_api.request.o_api_get_token_request import OApiGetTokenRequest
from .dingtalk_api.request.o_api_sns_getuserinfo_bycode_request import OApiSnsGetuserinfoBycodeRequest
from .dingtalk_api.request.o_api_user_get_request import OApiUserGetRequest
from library.settings import DingTalk_args as dd



SEARCH_VAR = 'q'

class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        fields = ['username']
        allowed_methods = ['get']
        resource_name = 'user'
        authentication = BasicAuthentication()

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/login%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('login'), name="api_login"),

        ]

    def login(self, request, **kwargs):
        try:
            gettoken_client = DefaultDingTalkClient(server_url=dd['gettokenUrl'])
            req = OApiGetTokenRequest()
            req.corp_id = dd['corpId']
            req.corp_secret = dd['corpSecret']
            req.set_http_method('GET')
            rsp = json.loads(gettoken_client.execute(request=req))
            access_token = rsp['access_token']
            user_get_client = DefaultDingTalkClient(server_url=dd['userGetUrl'])
            req = OApiUserGetRequest()
            req.tmp_auth_code = request.GET.get('code', '')
            req.set_http_method('GET')
            rsp = json.loads(user_get_client.execute(request=req, session=access_token))
            username = 'ding-' + rsp['userid']
            user = User.objects.filter(username=username)
            if not user:
                User.objects.create_user(username=username, password='default')
            return self.get_response(request, user, self._meta.resource_name + 's')
        except Exception as e:
            if 'errcode' in rsp.keys():
                if rsp['errcode'] == 0:
                    return self.create_response(request, {'internal_err': str(e)})
                else:
                    return self.create_response(request, rsp)
            else:
                return self.create_response(request, {'internal_err': str(e)})

class AuthorResource(ModelResource):
    class Meta:
        queryset = Author.objects.all()
        allowed_methods = ['get']
        resource_name = 'author'
    # def dehydrate(self, bundle):
    #     if bundle.request.GET:
    #         return {key: bundle.data[key] for key in bundle.data.keys() & bundle.request.GET.dict().keys()}
    #     else:
    #         return bundle
class TagResource(ModelResource):
    class Meta:
        queryset = Tag.objects.all()
        allowed_methods = ['get']
        resource_name = 'tag'

    def dehydrate(self, bundle):
        bundle.data['count'] = bundle.obj.book_set.count()
        bundle.data['name'] = str(bundle.obj)
        # if bundle.request.GET:
        #     return {key: bundle.data[key] for key in bundle.data.keys() & bundle.request.GET.dict().keys()}
        # else:
        #     return bundle
        # return bundle
    # print('tags.obj:', bundle.obj.tags.all()[0])
    # print('tags:', bundle.data['tags'])
    # print('tag0:', bundle.data['tags'][0])

    # for t in bundle.obj.tags.all():
    #     tags.append({'count': t.book_set.count(), 'name': str(t)})
    # bundle.data['tags'] = tags

class RatingResource(ModelResource):
    class Meta:
        queryset = Rating.objects.all()
        allowed_methods = ['get']
        resource_name = 'rating'


class TranslatorResource(ModelResource):
    class Meta:
        queryset = Translator.objects.all()
        allowed_methods = ['get']
        resource_name = 'translator'
    # def dehydrate(self, bundle):
    #     if bundle.request.GET:
    #         return {key: bundle.data[key] for key in bundle.data.keys() & bundle.request.GET.dict().keys()}
    #     else:
    #         return bundle

class SeriesResource(ModelResource):
    class Meta:
        queryset = Series.objects.all()
        allowed_methods = ['get']
        resource_name = 'series'

    # def dehydrate(self, bundle):
    #     if bundle.request.GET:
    #         return {key: bundle.data[key] for key in bundle.data.keys() & bundle.request.GET.dict().keys()}
    #     else:
    #         return bundle


class BookRatingResource(ModelResource):
    class Meta:
        queryset = BookRating.objects.all()
        allowed_methods = ['get']
        resource_name = 'bookrating'


class BookResource(ModelResource):
    author = fields.ToManyField(AuthorResource, 'author', full=True)
    translator = fields.ToManyField(TranslatorResource, 'translator', full=True)
    tags = fields.ToManyField(TagResource, 'tags', full=True)
    series = fields.ToOneField(SeriesResource, 'series', full=True)
    rating = fields.ToOneField(BookRatingResource, 'rating', full=True)


    class Meta:
        queryset = Book.objects.all()
        allowed_methods = ['get']
        resource_name = 'book'
    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/search%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('get_search'), name="api_get_search"),
            url(r"^(?P<resource_name>%s)/new%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view('get_new'), name="api_get_new"),
        ]

    def get_search_query_set(self, request, **kwargs):
        if '' == request.GET.get(SEARCH_VAR, ''):
            return self._meta.queryset
        else:
            obj = self._meta.queryset.filter(title__icontains=request.GET.get(SEARCH_VAR, None))
            if not obj:
                seg_list = jieba.cut(request.GET.get(SEARCH_VAR, None), cut_all=False)
                keywords = heapq.nsmallest(3, seg_list, key=lambda s: -len(s))
                k1, *k2 = keywords
                query = Q(title__icontains=k1)
                for k in k2:
                    query = query | Q(title__icontains=k)
                obj = self._meta.queryset.filter(query)
            return obj

    def get_new_query_set(self, request, **kwargs):
        now = timezone.now()
        return self._meta.queryset.filter(Q(shelf_time__gte=now) & Q(shelf_time__lte=now-timedelta(days=15)))

    def get_response(self, request, qs, name):
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)
        paginator = self._meta.paginator_class(request.GET, qs,
                                               resource_uri=self.get_resource_uri(), limit=self._meta.limit,
                                               max_limit=self._meta.max_limit,
                                               collection_name=self._meta.collection_name)

        to_be_serialized = paginator.page()

        bundles = [self.build_bundle(obj=result, request=request) for result in to_be_serialized['objects']]
        to_be_serialized[name] = [self.full_dehydrate(bundle) for bundle in bundles]
        del to_be_serialized['objects']
        to_be_serialized = self.alter_list_data_to_serialize(request, to_be_serialized)
        return self.create_response(request, to_be_serialized)

    def get_search(self, request, **kwargs):
        return self.get_response(request, self.get_search_query_set(request, **kwargs), self._meta.resource_name+'s')

    def get_new(self, request, **kwargs):
        return self.get_response(request, self.get_new_query_set(request, **kwargs), self._meta.resource_name+'s')

    def base_urls(self):
        return [
            url(r"^(?P<resource_name>%s)%s$" % (self._meta.resource_name, trailing_slash),
                self.wrap_view('dispatch_list'), name="api_dispatch_list"),
            url(r"^(?P<resource_name>%s)/schema%s$" % (self._meta.resource_name, trailing_slash),
                self.wrap_view('get_schema'), name="api_get_schema"),
            url(r"^(?P<resource_name>%s)/set/(?P<%s_list>.*?)%s$" % (self._meta.resource_name, self._meta.detail_uri_name, trailing_slash), self.wrap_view('get_multiple'),
                name="api_get_multiple"),
            url(r"^(?P<resource_name>%s)/(?P<%s>(0|[1-9][0-9]*))%s$" % (self._meta.resource_name, self._meta.detail_uri_name, trailing_slash), self.wrap_view('dispatch_detail'),
                name="api_dispatch_detail"),
        ]
    def dehydrate_id(self, bundle):
        return str(bundle.data['id'])

    def dehydrate_isbn10(self, bundle):
        return str(bundle.data['isbn10'])

    def dehydrate_isbn13(self, bundle):
        return str(bundle.data['isbn13'])

    def dehydrate_author(self, bundle):
        ret = []
        if bundle.data['author']:
            for a in bundle.data['author']:
                print(bundle.data)
                print('author', a)
                ret.append(a.data['name'])
        return ret

    def dehydrate_translator(self, bundle):
        ret = []
        for t in bundle.data['translator']:
            ret.append(t.data['name'])
        return ret

    def dehydrate_pages(self, bundle):
        return str(bundle.data['pages'])


    def dehydrate(self, bundle):
        bundle.data['amount'] = bundle.obj.amount()
        bundle.data['remaining'] = bundle.obj.remaining()
        bundle.data['url'] = bundle.data['resource_uri']
        bundle.data['alt'] = bundle.data['resource_uri']
        fls = {key: '' for key in bundle.request.GET.get('fields', '').split(',') if key}
        if fls:
            return {key: bundle.data[key] for key in bundle.data.keys() & fls.keys()}
        else:
            return bundle


class ReviewResource(ModelResource):
    book = fields.ToOneField(BookResource, 'book', full=True)
    author = fields.ToOneField(UserResource, 'author', full=True)
    rating = fields.ToOneField(RatingResource, 'rating', full=True)
    comments = fields.IntegerField(readonly=True)
    class Meta:
        queryset = Review.objects.all()
        allowed_methods = ['get']
        resource_name = 'review'

    def prepend_urls(self):
        print(r"^(?P<resource_name>book)/(?P<pk>(0|[1-9][0-9]*))/%ss%s$" % (self._meta.resource_name, trailing_slash()))
        return [
            url(r"^(?P<resource_name>book)/(?P<pk>(0|[1-9][0-9]*))/%ss%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_reviews'), name="api_reviews"),
        ]

    def get_reviews(self, request, *args, **kwargs):
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)
        sqs = Book.objects.filter(pk=kwargs['pk']).review_set.all()
        paginator = self._meta.paginator_class(request.GET, sqs,
                                               resource_uri=self.get_resource_uri(), limit=self._meta.limit,
                                               max_limit=self._meta.max_limit,
                                               collection_name=self._meta.collection_name)

        to_be_serialized = paginator.page()

        bundles = [self.build_bundle(obj=result, request=request) for result in to_be_serialized['objects']]
        to_be_serialized['reviews'] = [self.full_dehydrate(bundle) for bundle in bundles]
        del to_be_serialized['objects']
        to_be_serialized = self.alter_list_data_to_serialize(request, to_be_serialized)
        return self.create_response(request, to_be_serialized)

    def dehydrate_comments(self, bundle):
        return bundle.obj.comment_review_set.count()

    def dehydrate(self, bundle):
        bundle.data['alt'] = bundle.data['resource_uri']
        return bundle


class PhotoResource(ModelResource):
    class Meta:
        queryset = Photo.objects.all()
        allowed_methods = ['get']
        resource_name = 'photo'


class BookAnnotationResource(ModelResource):
    book = fields.ToOneField(BookResource, 'book', full=True)
    author_user = fields.ToOneField(UserResource, 'author_user', full=True)
    abstract_photo = fields.ToOneField(PhotoResource, 'abstract_photo', full=True)
    photos = fields.ManyToManyField(PhotoResource, 'photos',full=True)
    comments_count = fields.IntegerField(readonly=True)

    class Meta:
        queryset = Annotation.objects.all()
        allowed_methods = ['get']
        resource_name = 'annotation'

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>book)/(?P<pk>(0|[1-9][0-9]*))/%ss%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_annotations'), name="api_annotations"),
        ]

    def get_annotations(self, request, *args, **kwargs):
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)
        sqs = Book.objects.filter(pk=kwargs['pk']).annotation_set.all()
        paginator = self._meta.paginator_class(request.GET, sqs,
                                               resource_uri=self.get_resource_uri(), limit=self._meta.limit,
                                               max_limit=self._meta.max_limit,
                                               collection_name=self._meta.collection_name)

        to_be_serialized = paginator.page()

        bundles = [self.build_bundle(obj=result, request=request) for result in to_be_serialized['objects']]
        to_be_serialized['annotations'] = [self.full_dehydrate(bundle) for bundle in bundles]
        to_be_serialized['total'] = to_be_serialized['meta']['total_count']
        to_be_serialized['start'] = to_be_serialized['meta']['offset']
        to_be_serialized['count'] = to_be_serialized['meta']['limit']
        del to_be_serialized['objects']
        to_be_serialized = self.alter_list_data_to_serialize(request, to_be_serialized)

        print(to_be_serialized)
        return self.create_response(request, to_be_serialized)

    def dehydrate_comments_count(self, bundle):
        return bundle.obj.comment_annotation_set.count()


class MetaDataResource(ModelResource):
    book = fields.ToOneField(BookResource, 'book')
    owner = fields.ToOneField(UserResource, 'owner')

    # def get_object_list(self, request):
    #     code = request.GET.get('code', None)
    #     if code is None:
    #         return MetaData.objects.filter(id=-1)
    #     else:
    #         auth = Auth(
    #             code=code,
    #             appid='dingoaakxvbgbuaei0kfs5',
    #             appsecret='F88HpmLQEpEm50-_7JcTi4fC-EjECOgKfpdVKYa4QQHDS-Z_tFIp7zqKL4u_YD8p',
    #             access_token_url='https://oapi.dingtalk.com/sns/gettoken?appid=%s&appsecret=%s',
    #             persistent_code_url='https://oapi.dingtalk.com/sns/get_persistent_code?access_token=%s',
    #             sns_token_url='https://oapi.dingtalk.com/sns/get_sns_token?access_token=%s',
    #             user_info_url='https://oapi.dingtalk.com/sns/getuserinfo?sns_token=%s'
    #         )
    #         info = auth.get_user_info()
    #         print(info)
    #         username = info['user_info']['dingId']
    #         password = username
    #         if User.objects.filter(username=username):
    #             """User already exists"""
    #             pass
    #         else:
    #             User(username=username, password=password).save()
    #
    #         return Book.objects.filter()
    #
    #         return Book.objects.all()
    class Meta:
        queryset = MetaData.objects.all()
        allowed_methods = ['get', 'post']
        resource_name = 'metadata'
    # def dehydrate(self, bundle):
    #     if bundle.request.GET:
    #         return {key: bundle.data[key] for key in bundle.data.keys() & bundle.request.GET.dict().values()}
    #     else:
    #         return bundle

class WannaBookResource(ModelResource):
    def get_object_list(self, request):
        uid = request.GET.get('uid', '')

        print(request)
        if '' == uid:
            return WannaBook.objects.all()
        else:
            return WannaBook.objects.filter(recommender=uid)

    class Meta:
        queryset = WannaBook.objects.all()
        allowed_methods = ['get']
        resource_name = 'wannabook'
    # def dehydrate(self, bundle):
    #     if bundle.request.GET:
    #         return {key: bundle.data[key] for key in bundle.data.keys() & bundle.request.GET.dict().keys()}
    #     else:
    #         return bundle

# class SearchBookResource(ModelResource):
#     author = fields.ToManyField(AuthorResource, 'author', full=True)
#     translator = fields.ToManyField(TranslatorResource, 'translator', full=True)
#     tags = fields.ToManyField(TagResource, 'tags', full=True)
#     series = fields.ToOneField(SeriesResource, 'series', full=True)
#     rating = fields.ToOneField(BookRatingResource, 'rating', full=True)
#
#     class Meta:
#         allowed_methods = ['get',]
#         resource_name = 'book'
#         queryset = Book.objects.all()
#
#
#     def dehydrate(self, bundle):
#         #bundle.data['books'] = bundle.data['objects']
#         # bundle.data['count'] = bundle.data['meta']['limit']
#         # bundle.data['total'] = bundle.data['meta']['total_count']
#         bundle.data['start'] = 123456
#         #del bundle.data['objects']
#
#         fls = {key: '' for key in bundle.request.GET.get('fields', '').split(',') if key}
#         if fls:
#             return {key: bundle.data[key] for key in bundle.data.keys() & fls.keys()}
#         else:
#             return bundle


class SearchWannaBookResource(ModelResource):
    def get_object_list(self, request):
        if '' == request.GET.get(SEARCH_VAR, ''):
            return super(SearchWannaBookResource, self).get_object_list(request)
        else:
            obj = WannaBook.objects.filter(title__icontains=request.GET.get(SEARCH_VAR, None))
            if not obj:
                seg_list = jieba.cut(request.GET.get(SEARCH_VAR, ''), cut_all=False)
                keywords = heapq.nsmallest(3, seg_list, key=lambda s: -len(s))
                k1, *k2 = keywords
                query = Q(title__icontains=k1)
                for k in k2:
                    query = query | Q(title__icontains=k)
                obj = WannaBook.objects.filter(query)
            return obj

    class Meta:
        allowed_methods = ['get',]
        resource_name = 'searchwannabook'
        queryset = WannaBook.objects.all()
    def dehydrate(self, bundle):
        bundle.data['books'] = bundle.data['objects']
        bundle.data['count'] = bundle.data['meta']['limit']
        bundle.data['total'] = bundle.data['meta']['total_count']
        bundle.data['start'] = bundle.data['offset']
        del bundle.data['objects']
        return bundle

# class NewBookResource(ModelResource):
#
#     class Meta:
#         allowed_methods = ['get']
#         resource_name = 'new'
#         now = timezone.now()
#         query = Q(shelf_time__gte=now) & Q(shelf_time__lte=now-timedelta(days=15))
#         queryset = Book.objects.filter(query)


##待借阅
class AppliedBookResource(ModelResource):
    def get_object_list(self, request):
        uid = request.GET.get('uid', '')
        if '' == uid:
            return MetaData.objects.filter(status=MetaData.STATUS_APPLY())
        else:
            return MetaData.objects.filter(owner=uid, status=MetaData.STATUS_APPLY())

    class Meta:
        allowed_methods = ['get',]
        resource_name = 'appliedbook'
        queryset = MetaData.objects.all()
        

##待归还
class UnReturnedBookResource(ModelResource):
    def get_object_list(self, request):
        uid = request.GET.get('uid', '')
        if '' == uid:
            return MetaData.objects.filter(status=MetaData.STATUS_BORROWED())
        else:
            return MetaData.objects.filter(
                Q(owner=uid) &
                Q(status=MetaData.STATUS_BORROWED())
            )

    class Meta:
        allowed_methods = ['get',]
        resource_name = 'unreturnedbook'
        queryset = MetaData.objects.all()


##全部图书
class FinishedBookResource(ModelResource):
    book = fields.ToOneField(BookResource, 'book', full=True)
    borrower = fields.ToOneField(UserResource, 'borrower', full=True)

    def get_object_list(self, request):
        uid = request.GET.get('uid', '')
        if '' == uid:
            return LoaningRecord.objects.all()
        else:
            return LoaningRecord.objects.filter(Q(borrower__id=uid))

    class Meta:
        allowed_methods = ['get',]
        resource_name = 'finishedbook'
        queryset = LoaningRecord.objects.all()


#待评价
#评价的话，需要添加一条comment，并外键关联
class UncommentedBookResource(ModelResource):
    book = fields.ToOneField(BookResource, 'book', full=True)
    borrower = fields.ToOneField(UserResource, 'borrower', full=True)

    def get_object_list(self, request):
        uid = request.GET.get('uid', '')
        if '' == uid:
            return LoaningRecord.objects.filter(Q(comment__isnull=True))
        else:
            query = Q(borrower__id=uid) & \
                    Q(comment__isnull=True)
            return LoaningRecord.objects.filter(query)

    class Meta:
        allowed_methods = ['get',]
        resource_name = 'uncommentedbook'
        queryset = LoaningRecord.objects.all()


class LoanHistoryResource(ModelResource):
    borrower = fields.ToOneField(UserResource, 'borrower', full=True)
    
    def get_object_list(self, request):
        bid = request.GET.get('bid', '')

        if '' == bid:
            return LoaningRecord.objects.all()
        else:
            return LoaningRecord.objects.filter(book__id=bid)

    class Meta:
        allowed_methods = ['get',]
        resource_name = 'loanhistory'
        queryset = LoaningRecord.objects.all()


