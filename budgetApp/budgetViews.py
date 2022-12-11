from django.shortcuts import render
from django.http import HttpResponse

# importing the required libraries
import pandas as pd
import json
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from io import BytesIO
from urllib.parse import quote

import warnings
warnings.filterwarnings('ignore')


def getBudgetCategory():
    df = pd.read_csv('https://raw.githubusercontent.com/sohelranacse/analysis-data/main/budget/budget.csv').category
    return df


def budget(request):
    df = getBudgetCategory()
    json_records = df.reset_index().to_json(orient='records')
    category_data = []
    category_data = json.loads(json_records)

    # previous month
    previousMonth = datetime.today() - timedelta(days=30)
    context = {"title": "Budget", "category_data": category_data, "previousMonth": previousMonth.strftime("%Y-%m")}
    return render(request, 'budget.html', context)


def getBudgetCategoryData(category, to_date):
    if(category == "ALL"):
        df_temp = pd.read_csv('https://raw.githubusercontent.com/sohelranacse/analysis-data/main/budget/budget.csv')
    else:
        df_temp = pd.read_csv(
            'https://raw.githubusercontent.com/sohelranacse/analysis-data/main/budget/budget.csv').query('category == "'+category+'"')

    df = pd.DataFrame(columns=['category', 'budget'])
    df['category'] = df_temp['category']

    count = 0
    for col_name in df_temp.columns:
        if col_name == to_date:
            df_temp = df_temp.rename(columns={to_date: 'mybudget'})
            df['budget'] = df_temp['mybudget']
            count = 1
            break

    if(count == 0):
        df['budget'] = df_temp['budget']

    return df


def getBudgetMainData(category, to_date, to_date_end):
    if(category == "ALL"):
        df = pd.read_csv('https://raw.githubusercontent.com/sohelranacse/analysis-data/main/budget/data.csv')
    else:
        df = pd.read_csv(
            'https://raw.githubusercontent.com/sohelranacse/analysis-data/main/budget/data.csv').query('Category == "'+category+'"')

    # peprocessing
    df = df.reset_index().fillna(0)
    df['date'] = pd.to_datetime(df['Date'])
    # drop
    columns_to_remove = ["Party", "Mode", "Cash In", "Balance"]
    df.drop(labels=columns_to_remove, axis=1, inplace=True)
    # rename
    df = df.rename(columns={"Time": "time", "Category": 'category', "Remark": 'remark', "Cash Out": 'expense'})

    # filter
    mask = (df['date'] >= to_date) & (df['date'] <= to_date_end)
    df = df.loc[mask]
    return df


def getCategoryWiseExpense(budget_df, main_df):
    # sum expense
    expense_data = main_df.groupby('category').sum()['expense'].reset_index()

    # concat with budget
    final_data = expense_data.merge(budget_df, how='outer', left_on=['category'], right_on=['category']).fillna(0)
    final_data.sort_values("category", inplace=True)
    return final_data


def getDateWiseExpense(budget_df, main_df):
    # sum expense
    expense_data = main_df.groupby('date').sum()['expense'].reset_index()
    final_data = pd.DataFrame(columns=['date', 'expense'])
    final_data['date'] = expense_data['date'].dt.strftime('%Y-%m-%d')
    final_data['expense'] = expense_data['expense']
    return final_data


def getExpenseDFbyMonthRange(category, to_date, to_date_end):
    budget_df = getBudgetCategoryData(category, to_date)
    main_df = getBudgetMainData(category, to_date, to_date_end)  # table data

    category_df = getCategoryWiseExpense(budget_df, main_df)  # table data and graph
    date_data = getDateWiseExpense(budget_df, main_df)  # graph

    return {"cat_data": category_df, "date_df": main_df, "date_data": date_data}


def search_month_wise_expense(request):
    category = request.GET['category']
    tDate = datetime.strptime(request.GET['to_date'], "%Y-%m-%d")
    tDate_end = tDate + relativedelta(day=31)
    to_date = tDate.strftime("%Y-%m-%d")
    to_date_end = tDate_end.strftime("%Y-%m-%d")
    monthYear = tDate.strftime("%B %Y")

    # read data, peprocessing, distruct
    expense_df = getExpenseDFbyMonthRange(category, to_date, to_date_end)
    expense_cat_df = expense_df['cat_data']  # sum data
    expense_date_df = expense_df['date_data']  # sum data
    expense_date_data = expense_df['date_df']  # All data - date duplicate

    ########### category wise expense report start ###########
    category_wise_bar = getCategoryWiseBar(expense_cat_df, monthYear)
    category_wise_scatter = getCategoryWiseScatter(expense_cat_df, monthYear)
    # make json
    expense_cat_df.sort_values(by=['category'], inplace=True, ascending=False)
    json_records = expense_cat_df.reset_index().to_json(orient='records')
    category_data = []
    category_data = json.loads(json_records)
    ########### category wise expense report end ###########

    ########### date wise expense report start ###########
    date_wise_bar = getDateWiseBar(expense_date_df, monthYear)
    date_wise_scatter = getDateWiseScatter(expense_date_df, monthYear)
    # make json
    expense_date_data.sort_values(by=['date'], inplace=True, ascending=False)
    json_records_date = expense_date_data.reset_index().to_json(orient='records')
    date_data = []
    date_data = json.loads(json_records_date)
    ########### date wise expense report end ###########

    json_data = json.dumps({
        "category_data": category_data,
        "category_wise_bar": category_wise_bar,
        "category_wise_scatter": category_wise_scatter,
        "date_data": date_data,
        "date_wise_bar": date_wise_bar,
        "date_wise_scatter": date_wise_scatter,
        "monthYear": monthYear,
    })
    return HttpResponse(json_data, content_type="application/json")


def getDateWiseBar(expense_date_df, monthYear):
    trace = {
        'x': list(expense_date_df["date"]),
        'y': list(expense_date_df["expense"]),
        'type': 'bar',
        'name': 'Expense',
        'marker': {
            'color': '#FF0000',
            'width': 1
        },
        # 'orientation': 'h'
    }
    traceLayout = {
        'title': {
            'text': monthYear,
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


def getDateWiseScatter(expense_date_df, monthYear):
    trace = {
        'x': list(expense_date_df["date"]),
        'y': list(expense_date_df["expense"]),
        'type': 'scatter',
        'name': 'Expense',
        'mode': 'lines+markers',
        'marker': {
            'color': '#FF0000',
            'width': 1
        },
    }
    traceLayout = {
        'title': {
            'text': monthYear,
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


def getCategoryWiseBar(expense_cat_df, monthYear):
    trace = {
        'x': list(expense_cat_df["category"]),
        'y': list(expense_cat_df["budget"]),
        'type': 'bar',
        'name': 'Budget',
        'marker': {
            'color': '#7163F1',
            'width': 1
        },
    }
    trace2 = {
        'x': list(expense_cat_df["category"]),
        'y': list(expense_cat_df["expense"]),
        'type': 'bar',
        'name': 'Expense',
        'marker': {
            'color': '#FF0000',
            'width': 1
        },
    }
    traceLayout = {
        'title': {
            'text': monthYear,
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
            'title': 'Budget/Expense',
            'color': '#888',
            'titlefont': {'size': 12},
            'automargin': 'true',
            'showline': 'true'
        },
        'height': '400',
        'barmode': 'group'
    }
    return {"trace": trace, "trace2": trace2, "traceLayout": traceLayout}


def getCategoryWiseScatter(expense_cat_df, monthYear):
    trace = {
        'x': list(expense_cat_df["category"]),
        'y': list(expense_cat_df["budget"]),
        'type': 'scatter',
        'name': 'Budget',
        'mode': 'lines+markers',
        'marker': {
            'color': '#7163F1',
            'width': 1
        },
    }
    trace2 = {
        'x': list(expense_cat_df["category"]),
        'y': list(expense_cat_df["expense"]),
        'type': 'scatter',
        'name': 'Expense',
        'mode': 'lines+markers',
        'marker': {
            'color': '#FF0000',
            'width': 1
        },
    }
    traceLayout = {
        'title': {
            'text': monthYear,
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
            'title': 'Budget/Expense',
            'color': '#888',
            'titlefont': {'size': 12},
            'automargin': 'true',
            'showline': 'true'
        },
        'height': '400',
        # 'barmode': 'stack'
    }
    return {"trace": trace, "trace2": trace2, "traceLayout": traceLayout}
