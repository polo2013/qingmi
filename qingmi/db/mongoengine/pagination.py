# coding: utf-8
from flask import abort, request, url_for, render_template
from flask_mongoengine.pagination import Pagination as _Pagination
from qingmi.utils import success

class Pagination(_Pagination):

    def __init__(self, iterable, page=None, per_page=None,
                    endpoint=None, **kwargs):
        if page < 1:
            page = 1
        page = page or max(1, request.args.get('page', 1, int))
        per_page = per_page or max(1, min(100,
                    request.args.get('per_page', 10, int)))
        super(Pagination, self).__init__(iterable, page, per_page)
        self.endpoint = endpoint if endpoint else request.endpoint
        self.kwargs = kwargs

    @property
    def has_pages(self):
        return self.pages > 1

    @property
    def next_link(self):
        if self.has_next:
            return self.get_link(self.next_num)
        return ''

    def get_link(self, page):
        return url_for(self.endpoint, page=page, per_page=self.per_page,
                        **self.kwargs)

    def iter_links(self, pages=5, next=False, last=True,
                   first_page='«', prev_page='<',
                   last_page='»', next_page='>'):
        if last:
            yield first_page, self.get_link(1) if self.page > 1 else None
        if next:
            yield prev_page, self.get_link(self.prev_num) if self.has_prev else None

        start = max(1, self.page - (pages - 1) / 2)
        end = min(self.pages + 1, start + pages)
        start = max(1, end - pages)
        for i in range(start, end):
            yield i, self.get_link(i)

        if next:
            yield next_page, self.get_link(self.next_num) if self.has_next else None
        if last:
            yield last_page, self.get_link(self.pages) if self.page < self.pages else None

    def json(self, tojson=lambda x: x.json, **kwargs):
        return success(
            items=[tojson(x) for x in self.items],
            next=self.next_link, **kwargs)
