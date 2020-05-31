from rest_framework.pagination import PageNumberPagination


class SignRecordPagination(PageNumberPagination):
    # 每页显示
    page_size = 2
    # URL中每页显示条数的参数
    page_size_query_param = 'page_size'
    # 页码参数
    page_query_param = 'page_num'
    # 每页显示条数的最大限制
    max_page_size = 50
