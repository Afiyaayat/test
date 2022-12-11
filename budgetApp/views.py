from django.shortcuts import render
from django.http import HttpResponse

# importing the required libraries
import pandas as pd
import json
from datetime import datetime, timedelta
from io import BytesIO
from urllib.parse import quote

import warnings
warnings.filterwarnings('ignore')


def index(request):
    df = getBudgetCategory()
    json_records = df.reset_index().to_json(orient='records')
    category_data = []
    category_data = json.loads(json_records)
    context = {"title": "Home", "category_data": category_data}
    return render(request, 'index.html', context)


def getBudgetCategory():
    df = pd.read_csv('https://raw.githubusercontent.com/sohelranacse/analysis-data/main/budget/budget.csv').category
    return df


def getExpenseDFbyDateRange(category, from_date, to_date):
    if(category == "ALL"):
        df = pd.read_csv('https://raw.githubusercontent.com/sohelranacse/analysis-data/main/budget/data.csv')
    else:
        df = pd.read_csv(
            'https://raw.githubusercontent.com/sohelranacse/analysis-data/main/budget/data.csv').query('Category == "'+category+'"')

    # peprocessing
    df = df.reset_index().fillna(0)
    columns_to_remove = ['Party', 'Mode']
    df.drop(labels=columns_to_remove, axis=1, inplace=True)
    df['date'] = pd.to_datetime(df['Date'])

    # filter
    mask = (df['date'] >= from_date) & (df['date'] <= to_date)
    df = df.loc[mask]

    ########### DATE WISE START ###########
    # Serialize
    date_df = pd.DataFrame(columns=['Date', 'date', 'time', 'remark', 'categoy', 'expense'])
    date_df['Date'] = df['Date']
    date_df['date'] = df['date']
    date_df['time'] = df['Time']
    date_df['remark'] = df['Remark']
    date_df['category'] = df['Category']
    date_df['expense'] = df['Cash Out']

    # column summation
    date_expense = date_df.groupby('date').sum()['expense'].reset_index()
    date_data = pd.DataFrame(columns=['date', 'expense'])
    date_data['date'] = date_expense['date'].dt.strftime('%Y-%m-%d')
    date_data['expense'] = date_expense['expense']
    ########### DATE WISE END ###########

    ########### CATEGORY WISE START ###########
    # Serialize
    cat_df = pd.DataFrame(columns=['date', 'category', 'expense'])
    cat_df['date'] = df['date']
    cat_df['category'] = df['Category']
    cat_df['expense'] = df['Cash Out']

    # column summation
    cat_expense = cat_df.groupby('category').sum()['expense'].reset_index()
    cat_data = pd.DataFrame(columns=['category', 'expense'])
    cat_data['category'] = cat_expense['category']
    cat_data['expense'] = cat_expense['expense']
    ########### CATEGORY WISE END ###########

    return {"cat_data": cat_data, "date_df": date_df, "date_data": date_data}


def search_date_wise_expense(request):
    category = request.GET['category']
    from_date = request.GET['from_date']
    to_date = request.GET['to_date']

    # read data, peprocessing, distruct
    expense_df = getExpenseDFbyDateRange(category, from_date, to_date)
    expense_cat_df = expense_df['cat_data']  # sum data
    expense_date_df = expense_df['date_data']  # sum data
    expense_date_data = expense_df['date_df']  # All data - date duplicate

    ########### category wise expense report start ###########
    # category_df = getBudgetCategory()
    category_wise_bar = getCategoryWiseBar(expense_cat_df, from_date, to_date)
    # make json
    expense_cat_df.sort_values(by=['category'], inplace=True, ascending=False)
    json_records = expense_cat_df.reset_index().to_json(orient='records')
    category_data = []
    category_data = json.loads(json_records)
    ########### category wise expense report end ###########

    ########### date wise expense report start ###########
    date_wise_bar = getDateWiseBar(expense_date_df, from_date, to_date)
    # make json
    expense_date_data.sort_values(by=['date'], inplace=True, ascending=False)
    json_records_date = expense_date_data.reset_index().to_json(orient='records')
    date_data = []
    date_data = json.loads(json_records_date)
    ########### date wise expense report end ###########

    json_data = json.dumps({
        "category_data": category_data,
        "category_wise_bar": category_wise_bar,
        "date_data": date_data,
        "date_wise_bar": date_wise_bar,
    })
    return HttpResponse(json_data, content_type="application/json")


def getDateWiseBar(expense_date_df, from_date, to_date):
    trace = {
        'x': list(expense_date_df["date"]),
        'y': list(expense_date_df["expense"]),
        'type': 'bar',
        'name': 'Expense',
        'marker': {
            'color': '#7163F1',
            'width': 1
        },
        # 'orientation': 'h'
    }
    traceLayout = {
        'title': {
            'text': 'Date Wise Expense Report From '+from_date+' To '+to_date,
            'font': {
                'color': '#000',
                'size': 14
            }
        },
        'xaxis': {
            'title': '',
            'color': '#888',
            'titlefont': {'size': 12},
            'automargin': 'true',
            'showline': 'true'
        },
        'yaxis': {
            'title': 'Expense',
            'color': '#888',
            'titlefont': {'size': 12},
            'automargin': 'true',
            'showline': 'true'
        },
        'height': '400',
        'barmode': 'stack'
    }
    return {"trace": trace, "traceLayout": traceLayout}


def getCategoryWiseBar(expense_cat_df, from_date, to_date):
    trace = {
        'x': list(expense_cat_df["category"]),
        'y': list(expense_cat_df["expense"]),
        'type': 'bar',
        'name': 'Expense',
        'marker': {
            'color': '#7163F1',
            'width': 1
        },
        # 'orientation': 'h'
    }
    traceLayout = {
        'title': {
            'text': 'Category Wise Expense Report From '+from_date+' To '+to_date,
            'font': {
                'color': '#000',
                'size': 14
            }
        },
        'xaxis': {
            'title': '',
            'color': '#888',
            'titlefont': {'size': 12},
            'automargin': 'true',
            'showline': 'true'
        },
        'yaxis': {
            'title': 'Expense',
            'color': '#888',
            'titlefont': {'size': 12},
            'automargin': 'true',
            'showline': 'true'
        },
        'height': '400',
        'barmode': 'stack'
    }
    return {"trace": trace, "traceLayout": traceLayout}


def check_cookie_name(request):
    cookie = request.GET['cookie']
    success = 0
    if(cookie == "afiya"):
        success = 1

    json_data = json.dumps({
        "success": success,
    })
    return HttpResponse(json_data, content_type="application/json")
