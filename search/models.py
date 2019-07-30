from django.db import models

# Create your models here.
from datetime import datetime
from elasticsearch_dsl import Document,Date,Nested,Boolean,analyzer,\
    Completion,Keyword,Text,Integer
from elasticsearch_dsl.connections import connections

connections.create_connection(hosts=["localhost"])


class JobboleArticleType(Document):
    suggest = Completion(analyzer="ik_max_word")
    title = Text(analyzer="ik_max_word")
    create_date = Date()
    url = Keyword()
    image_url = Keyword()
    image_path = Keyword()
    vote_num = Integer()
    comment_num = Integer()
    book_num = Integer()
    tags = Text(analyzer="ik_max_word")
    content = Text(analyzer="ik_max_word")

    class Index:
        name = "jobbole"
    class Meta:
        doc_type = "article"


class DoubanMovieType(Document):
    suggest = Completion(analyzer="ik_max_word")
    movie_name = Text(analyzer="ik_max_word")
    movie_url = Keyword()
    image_url = Keyword()
    year = Integer()
    country = Text()
    quote = Text()
    score= Text()
    ranking=Integer()
    comment_num = Integer()
    tags = Text(analyzer="ik_max_word")


    class Index:
        name = "douban"
    class Meta:
        doc_type = "movie"


class PPTType(Document):
    suggest = Completion(analyzer="ik_max_word")
    tags = Text(analyzer="ik_max_word")
    title = Text(analyzer="ik_max_word")
    image_url = Keyword()
    content = Text(analyzer="ik_max_word")
    ppt_url = Keyword()

    class Index:
        name = "1ppt"
    class Meta:
        doc_type = "ppt"


class BaotuVideoType(Document):
    suggest = Completion(analyzer="ik_max_word")
    video_name = Text(analyzer="ik_max_word")
    image_url = Keyword()
    video_url = Keyword()

    class Index:
        name = "baotu"
    class Meta:
        doc_type = "video"


class MeiJuTVType(Document):
    suggest = Completion(analyzer="ik_max_word")
    tv_name = Text(analyzer="ik_max_word")
    tv_url = Keyword()
    image_url = Keyword()
    tags=Text(analyzer="ik_max_word")
    abstract=Text(analyzer="ik_max_word")

    class Index:
        name = "meijutt"
    class Meta:
        doc_type = "tv"


class MoocType(Document):
    suggest=Completion(analyzer="ik_max_word")
    course_name=Text(analyzer="ik_max_word")
    course_type=Text(analyzer="ik_max_word")
    course_url = Keyword()
    student = Integer()
    image_url = Keyword()
    introduction=Text(analyzer="ik_max_word")
    tags=Text(analyzer="ik_max_word")

    class Index:
        name = "mooc"
    class Meta:
        doc_type = "course"


class DygodMovieType(Document):
    suggest = Completion(analyzer="ik_max_word")
    movie_name=Text(analyzer="ik_max_word")
    translated_name=Text(analyzer="ik_max_word")
    movie_url = Keyword()
    image_url = Keyword()
    tags=Text(analyzer="ik_max_word")
    abstract=Text(analyzer="ik_max_word")

    class Index:
        name = "dygod"
    class Meta:
        doc_type = "movie"

class UnsplashImageType(Document):
    suggest = Completion(analyzer='ik_max_word')
    image_name = Text(analyzer='ik_max_word')
    image_url = Keyword()
    class Index:
        name = 'unsplash'
    class Meta:
        doc_type = 'image'
#

if __name__ == "__main__":
    JobboleArticleType.init()
    DoubanMovieType.init()
    MoocType.init()
    MeiJuTVType.init()
    BaotuVideoType.init()
    PPTType.init()
    DygodMovieType.init()