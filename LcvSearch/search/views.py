from django.shortcuts import render
from django.views.generic.base import View
from search.models import ArticleType



class SearchSuggest(View):
    def get(self, request):
        key_words = request.GET.get('s', '')
        re_datas = []
        if key_words:
            s = ArticleType.search()
            s.suggest()


