from django.contrib import admin
from django.urls import path
from budgetApp import views
from budgetApp import budgetViews
from budgetApp import comparisonViews
from django.conf.urls import url

urlpatterns = [
    path('admin/', admin.site.urls),

    # my code
    url('^$', views.index, name='index'),
    url('check_cookie_name', views.check_cookie_name, name='check_cookie_name'),
    url('search_date_wise_expense', views.search_date_wise_expense, name='search_date_wise_expense'),

    url('budget', budgetViews.budget, name='budget'),
    url('search_month_wise_expense', budgetViews.search_month_wise_expense, name='search_month_wise_expense'),

    url('comparison', comparisonViews.comparison, name='comparison'),
    url('search_expense', comparisonViews.search_expense, name='search_expense'),
]
