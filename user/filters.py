from django_filters import rest_framework as filters
from .models import SignRecord


class SignRecordFilter(filters.FilterSet):
    sign_time = filters.DateFromToRangeFilter()

    class Meta:
        model = SignRecord
        fields = ['sign_time']
