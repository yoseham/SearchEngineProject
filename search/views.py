from django.shortcuts import render
from django.views.generic.base import View
from search.models import *
from django.http import HttpResponse
from elasticsearch import Elasticsearch
from datetime import datetime
import json
import redis
# Create your views here.
es = Elasticsearch(hosts=["localhost"])
redis_cli = redis.StrictRedis()
class SearchSuggest(View):
    def get(self,request):
        key_words = request.GET.get('s','')
        current_type = request.GET.get('s_type', '')
        if current_type == "article":
            re_datas = []
            if key_words:
                """fuzzy模糊搜索, fuzziness 编辑距离, prefix_length前面不变化的前缀长度"""
                s = JobboleArticleType.search()
                s = s.suggest('article_suggest',key_words,completion={
                    "field":"suggest",
                    "fuzzy":{
                        "fuzziness":2
                    },
                    "size":10
                })
                suggestions = s.execute()
                for match in suggestions.suggest.article_suggest[0].options:
                    source = match._source
                    re_datas.append(("".join(source['title'])).replace('Jobbloe',''))
                a=HttpResponse(json.dumps(re_datas), content_type="application/json")
                return HttpResponse(json.dumps(re_datas[:10]),content_type="application/json")

        if current_type == "television":
            re_datas = []
            if key_words:
                # 豆瓣
                s = DoubanMovieType.search()
                s = s.suggest('movie_suggest', key_words, completion={
                    "field": "suggest",
                    "fuzzy": {
                        "fuzziness": 2
                    },
                    "size": 5
                })
                suggestions = s.execute()
                for match in suggestions.suggest.movie_suggest[0].options:
                    source = match._source
                    re_datas.append(source['movie_name'])
                #美剧TV
                s = MeiJuTVType.search()
                s = s.suggest('movie_suggest', key_words, completion={
                    "field": "suggest",
                    "fuzzy": {
                        "fuzziness": 1
                    },
                    "size": 5
                })
                suggestions = s.execute()
                for match in suggestions.suggest.movie_suggest[0].options:
                    source = match._source
                    re_datas.append(source['tv_name'])
                # 电影天堂
                s = DygodMovieType.search()
                s = s.suggest('movie_suggest', key_words, completion={
                    "field": "suggest",
                    "fuzzy": {
                        "fuzziness": 1
                    },
                    "size": 10
                })
                suggestions = s.execute()
                for match in suggestions.suggest.movie_suggest[0].options:
                    source = match._source
                    re_datas.append(source['movie_name'])
                return HttpResponse(json.dumps(re_datas[:10]), content_type="application/json")

        if current_type == "job":
            re_datas = []
            if key_words:
                #
                s = MoocType.search()
                s = s.suggest('course_suggest', key_words, completion={
                    "field": "suggest",
                    "fuzzy": {
                        "fuzziness": 1
                    },
                    "size": 10
                })
                suggestions = s.execute()
                for match in suggestions.suggest.course_suggest[0].options:
                    source = match._source
                    re_datas.append(source['course_name'])

                #

                return HttpResponse(json.dumps(re_datas[:10]), content_type="application/json")

        if current_type == "metrial":
            re_datas = []
            if key_words:
                #
                s = PPTType.search()
                s = s.suggest('ppt_suggest', key_words, completion={
                    "field": "suggest",
                    "fuzzy": {
                        "fuzziness": 1
                    },
                    "size": 5
                })
                suggestions = s.execute()
                for match in suggestions.suggest.ppt_suggest[0].options:
                    source = match._source
                    re_datas.append(source['title'])

                #
                s = BaotuVideoType.search()
                s = s.suggest('video_suggest', key_words, completion={
                    "field": "suggest",
                    "fuzzy": {
                        "fuzziness": 1
                    },
                    "size": 5
                })
                suggestions = s.execute()
                for match in suggestions.suggest.video_suggest[0].options:
                    source = match._source
                    re_datas.append(source['video_name'])

                return HttpResponse(json.dumps(re_datas[:10]), content_type="application/json")

        if current_type == "images":
            re_datas = []
            if key_words:
                #
                s = UnsplashImageType.search()
                s = s.suggest('image_suggest', key_words, completion={
                    "field": "suggest",
                    "fuzzy": {
                        "fuzziness": 8
                    },
                    "size": 10
                })
                suggestions = s.execute()
                for match in suggestions.suggest.image_suggest[0].options:
                    source = match._source
                    re_datas.append(source['image_name'])
                #
                return HttpResponse(json.dumps(re_datas[:10]), content_type="application/json")


class SearchView(View):
    def get(self,request):
        key_words=request.GET.get('q','')
        s_type=request.GET.get('s_type','')
        hit_list=[]
        total_num=0
        page_nums=0
        page = request.GET.get('p','1')
        start_time=datetime.now()
        try:
            page = int(page)
        except:
            page = 1
        # jobbole_count = redis_cli.get("jobbole_count")
        # ppt_count = redis_cli.get("ppt_count")
        # baotu_count = redis_cli.get("baotu_count")
        # douban_count = redis_cli.get("douban_count")
        # meijutt_count = redis_cli.get("meijutt_count")
        # mooc_count = redis_cli.get("mooc_count")
        # dygod_count = redis_cli.get("dygod_count")
        if s_type == 'article':
            jobbole_response = es.search(
                index='jobbole',
                body={
                    'query':{
                        'multi_match':{
                            'query':key_words,
                            'fields':['title','tags','content']

                        }
                    },
                    'from':(page-1)*10,
                    'size':10,
                    'highlight':{
                        'pre_tags': ['<span class="keyWord">'],
                        'post_tags': ['</span>'],
                        'fields':{
                            'title':{},
                            'tags':{},
                            'content':{}
                        }
                    }
                }
            )
            total_num=jobbole_response['hits']['total']
            for hit in jobbole_response['hits']['hits']:
                hit_dict={}
                if 'highlight'in hit.keys() and 'title' in hit['highlight']:
                    hit_dict['title']=("".join(hit['highlight']['title']).replace('Jobbloe',''))
                else:
                    hit_dict['title']=hit['_source']['title']
                if 'highlight'in hit.keys() and 'content' in hit['highlight']:
                    hit_dict['content']="".join(hit['highlight']['content'])[:250]
                else:
                    hit_dict['content'] = hit['_source']['content'][:250]
                if 'highlight'in hit.keys() and 'tags' in hit['highlight']:
                    hit_dict['tags']=" ".join(hit['highlight']['tags'])
                else:
                    hit_dict['tags'] = " ".join(hit['_source']['tags'])

                hit_dict['create_date']=hit['_source']['create_date']
                hit_dict['image_url']=hit['_source']['image_url']
                hit_dict['url']=hit['_source']['url']
                hit_dict['score']=hit['_score']
                hit_dict['source_site']='伯乐在线'
                hit_list.append(hit_dict)
            if total_num % 10 != 0:
                page_nums = int(total_num / 10) + 1
            else:
                page_nums = int(total_num / 10)

        elif s_type == 'images':
            image_response = es.search(
                index='unsplash',
                body={
                    'query':{
                        'multi_match':{
                            'query':key_words,
                            'fields':['image_name']

                        }
                    },
                    'from':(page-1)*20,
                    'size':20,
                }
            )
            total_num = image_response['hits']['total']
            for hit in image_response['hits']['hits']:
                hit_dict = {}
                hit_dict['image_url'] = hit['_source']['image_url']
                hit_list.append(hit_dict)
            if total_num % 10 != 0:
                page_nums = int(total_num / 10) + 1
            else:
                page_nums = int(total_num / 10)

        elif s_type == 'job':
            job_response = es.search(
                index='mooc',
                body={
                    'query':{
                        'multi_match':{
                            'query':key_words,
                            'fields':['course_name','tags','introduction']

                        }
                    },
                    'from':(page-1)*10,
                    'size':10,
                    'highlight':{
                        'pre_tags': ['<span class="keyWord">'],
                        'post_tags': ['</span>'],
                        'fields':{
                            'course_name':{},
                            'tags':{},
                            'introduction':{}
                        }
                    }
                }
            )
            total_num=job_response['hits']['total']
            for hit in job_response['hits']['hits']:
                hit_dict={}
                if 'highlight'in hit.keys() and 'course_name' in hit['highlight']:
                    hit_dict['title']="".join(hit['highlight']['course_name'])
                else:
                    hit_dict['title']=hit['_source']['course_name']
                if 'highlight'in hit.keys() and 'introduction' in hit['highlight']:
                    hit_dict['content']="".join(hit['highlight']['introduction'])[:250]
                else:
                    hit_dict['content'] = hit['_source']['introduction'][:250]
                if 'highlight'in hit.keys() and 'tags' in hit['highlight']:
                    hit_dict['tags']=" ".join(hit['highlight']['tags'])
                else:
                    hit_dict['tags'] = " ".join(hit['_source']['tags'])

                hit_dict['course_type']=hit['_source']['course_type']
                hit_dict['image_url']=hit['_source']['image_url']
                hit_dict['url']=hit['_source']['course_url']
                hit_dict['score']=hit['_score']
                hit_dict['source_site']='慕课网'
                hit_list.append(hit_dict)
            if total_num % 10 != 0:
                page_nums = int(total_num / 10) + 1
            else:
                page_nums = int(total_num / 10)

        elif s_type == 'television':

            douban_response = es.search(
                index='douban',
                body={
                    'query':{
                        'multi_match':{
                            'query':key_words,
                            'fields':['movie_name','tags','quote']

                        }
                    },
                    'from':(page-1)*10,
                    'size':10,
                    'highlight':{
                        'pre_tags': ['<span class="keyWord">'],
                        'post_tags': ['</span>'],
                        'fields':{
                            'movie_name':{},
                            'quote':{},
                            'tags':{}
                        }
                    }
                }
            )
            total_num=douban_response['hits']['total']

            for hit in douban_response['hits']['hits']:
                hit_dict={}
                if 'highlight'in hit.keys() and 'movie_name' in hit['highlight']:
                    hit_dict['title']="".join(hit['highlight']['movie_name'])
                else:
                    hit_dict['title']=hit['_source']['movie_name']
                if 'highlight'in hit.keys() and 'quote' in hit['highlight']:
                    hit_dict['content']="".join(hit['highlight']['quote'])
                else:
                    hit_dict['content'] = hit['_source'].get('quote')
                if 'highlight'in hit.keys() and 'tags' in hit['highlight']:
                    hit_dict['tags']=" ".join(hit['highlight']['tags'])
                else:
                    hit_dict['tags'] = " ".join(hit['_source']['tags'])

                hit_dict['movie_score']=hit['_source']['score']
                hit_dict['image_url']=hit['_source']['image_url']
                hit_dict['url']=hit['_source']['movie_url']
                hit_dict['score']=hit['_score']
                hit_dict['source_site']='豆瓣'
                hit_list.append(hit_dict)

            dygod_response = es.search(
                index='dygod',
                body={
                    'query': {
                        'multi_match': {
                            'query': key_words,
                            'fields': ['movie_name', 'tags', 'abstract']

                        }
                    },
                    'from': (page-1)*5,
                    'size': 5,
                    'highlight': {
                        'pre_tags': ['<span class="keyWord">'],
                        'post_tags': ['</span>'],
                        'fields': {
                            'movie_name': {},
                            'abstract': {},
                            'tags':{}
                        }
                    }
                }
            )
            total_num += dygod_response['hits']['total']

            for hit in dygod_response['hits']['hits']:
                hit_dict = {}
                if 'highlight'in hit.keys() and 'movie_name' in hit['highlight']:
                    hit_dict['title'] = "".join(hit['highlight']['movie_name'])
                else:
                    hit_dict['title'] = hit['_source']['movie_name']
                if 'highlight'in hit.keys() and 'abstract' in hit['highlight']:
                    hit_dict['content'] = "".join(hit['highlight']['abstract'])[:250]
                else:
                    hit_dict['content'] = hit['_source']['abstract'][:250]
                if 'highlight'in hit.keys() and 'tags' in hit['highlight']:
                    hit_dict['tags']=" ".join(hit['highlight']['tags'])
                else:
                    hit_dict['tags'] = " ".join(hit['_source']['tags'])

                hit_dict['movie_score'] = "暂无"
                hit_dict['image_url'] = hit['_source']['image_url']
                hit_dict['url'] = hit['_source']['movie_url']
                hit_dict['score'] = hit['_score']
                hit_dict['source_site'] = '电影天堂'
                hit_list.append(hit_dict)

            meijutt_response = es.search(
                index='meijutt',
                body={
                    'query': {
                        'multi_match': {
                            'query': key_words,
                            'fields': ['tv_name', 'tags', 'abstract']

                        }
                    },
                    'from': (page-1)*5,
                    'size': 5,
                    'highlight': {
                        'pre_tags': ['<span class="keyWord">'],
                        'post_tags': ['</span>'],
                        'fields': {
                            'tv_name': {},
                            'abstract': {},
                            'tags':{}
                        }
                    }
                }
            )
            total_num += meijutt_response['hits']['total']

            for hit in meijutt_response['hits']['hits']:
                hit_dict = {}
                if 'highlight'in hit.keys() and 'tv_name' in hit['highlight']:
                    hit_dict['title'] = "".join(hit['highlight']['tv_name'])
                else:
                    hit_dict['title'] = hit['_source']['tv_name']
                if 'highlight'in hit.keys() and 'abstract' in hit['highlight']:
                    hit_dict['content'] = "".join(hit['highlight']['abstract'])[:250]
                else:
                    hit_dict['content'] = hit['_source']['abstract'][:250]
                if 'highlight'in hit.keys() and 'tags' in hit['highlight']:
                    hit_dict['tags']="".join(hit['highlight']['tags'])
                else:
                    hit_dict['tags'] = hit['_source']['tags']

                hit_dict['movie_score'] = "暂无"
                hit_dict['image_url'] = hit['_source']['image_url']
                hit_dict['url'] = hit['_source']['tv_url']
                hit_dict['score'] = hit['_score']
                hit_dict['source_site'] = '美剧天堂'
                hit_list.append(hit_dict)
            if total_num % 10 != 0:
                page_nums = int(total_num / 10) + 1
            else:
                page_nums = int(total_num / 10)


        if s_type == 'metrial':
            ppt_response = es.search(
                index='1ppt',
                body={
                    'query': {
                        'multi_match': {
                            'query': key_words,
                            'fields': ['title', 'tags', 'content']

                        }
                    },
                    'from': (page-1)*5,
                    'size': 5,
                    'highlight': {
                        'pre_tags': ['<span class="keyWord">'],
                        'post_tags': ['</span>'],
                        'fields': {
                            'title': {},
                            'content': {},
                            'tags': {}
                        }
                    }
                }
            )
            total_num = ppt_response['hits']['total']

            for hit in ppt_response['hits']['hits']:
                hit_dict = {}
                if 'highlight' in hit.keys() and 'title' in hit['highlight']:
                    hit_dict['title'] = "".join(hit['highlight']['title'])
                else:
                    hit_dict['title'] = hit['_source']['title']
                if 'highlight' in hit.keys() and 'content' in hit['highlight']:
                    hit_dict['content'] = "".join(hit['highlight']['content'])
                else:
                    hit_dict['content'] = hit['_source']['content']
                if 'highlight' in hit.keys() and 'tags' in hit['highlight']:
                    hit_dict['tags'] = " ".join(hit['highlight']['tags'])
                else:
                    hit_dict['tags'] = " ".join(hit['_source']['tags'])

                hit_dict['image_url'] = hit['_source']['image_url']
                hit_dict['url'] = hit['_source']['ppt_url']
                hit_dict['score'] = hit['_score']
                hit_dict['source_site'] = '第一PPT'
                hit_list.append(hit_dict)

            video_response = es.search(
                index='baotu',
                body={
                    'query': {
                        'multi_match': {
                            'query': key_words,
                            'fields': ['video_name']

                        }
                    },
                    'from': (page-1)*5,
                    'size': 5,
                    'highlight': {
                        'pre_tags': ['<span class="keyWord">'],
                        'post_tags': ['</span>'],
                        'fields': {
                            'video_name':{}
                        }
                    }
                }
            )
            total_num += video_response['hits']['total']

            for hit in video_response['hits']['hits']:
                hit_dict = {}
                if 'highlight' in hit.keys() and 'video_name' in hit['highlight']:
                    hit_dict['title'] = "".join(hit['highlight']['video_name'])
                else:
                    hit_dict['title'] = hit['_source']['video_name']
                hit_dict['tags'] = "视频"
                hit_dict['content'] = "包图网视频素材"
                hit_dict['image_url'] = hit['_source']['image_url']
                hit_dict['url'] = hit['_source']['video_url']
                hit_dict['score'] = hit['_score']
                hit_dict['source_site'] = '包图网'
                hit_list.append(hit_dict)
            if total_num % 10 > 0:
                page_nums = int(total_num/10)+1
            else:
                page_nums = int(total_num / 10)



        end_time = datetime.now()
        last_seconds = (end_time - start_time).total_seconds()
        return render(request,'result.html',{'page':page,
                                             'page_nums':page_nums,
                                             'all_hits':hit_list,
                                             'key_words':key_words,
                                             'total_nums':total_num,
                                             's_type':s_type,
                                             'last_seconds':last_seconds})



