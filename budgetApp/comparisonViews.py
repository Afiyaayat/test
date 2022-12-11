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


def comparison(request):
    df = getBudgetCategory()
    json_records = df.reset_index().to_json(orient='records')
    category_data = []
    category_data = json.loads(json_records)

    # previous month
    previousMonth = datetime.today() - timedelta(days=30)
    context = {"title": "Budget", "category_data": category_data, "previousMonth": previousMonth.strftime("%Y-%m")}
    return render(request, 'comparison.html', context)


def getBudgetCategoryData(category, from_date):
    if(category == "ALL"):
        df_temp = pd.read_csv('https://raw.githubusercontent.com/sohelranacse/analysis-data/main/budget/budget.csv')
    else:
        df_temp = pd.read_csv(
            'https://raw.githubusercontent.com/sohelranacse/analysis-data/main/budget/budget.csv').query('category == "'+category+'"')

    df = pd.DataFrame(columns=['category', 'budget'])
    df['category'] = df_temp['category']

    count = 0
    for col_name in df_temp.columns:
        if col_name == from_date:
            df_temp = df_temp.rename(columns={from_date: 'mybudget'})
            df['budget'] = df_temp['mybudget']
            count = 1
            break

    if(count == 0):
        df['budget'] = df_temp['budget']

    return df


def getBudgetMainData(category, to_date, to_date_end, budget_df):
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

    # sum expense
    expense_data = df.groupby('category').sum()['expense'].reset_index()
    # concat with budget
    final_data = expense_data.merge(budget_df, how='outer', left_on=['category'], right_on=['category']).fillna(0)
    final_data.sort_values("category", inplace=True)
    return final_data


def concate_df(from_date_budget_df, to_date_budget_df):
    final_data = from_date_budget_df.merge(to_date_budget_df, how='outer', left_on=[
                                           'category'], right_on=['category']).fillna(0)
    final_data.sort_values("category", inplace=True)
    return final_data


def getExpenseDFbyMonthRange(category, from_date, from_date_end, to_date, to_date_end):
    # budget data
    from_date_budget_df = getBudgetCategoryData(category, from_date)
    to_date_budget_df = getBudgetCategoryData(category, to_date)

    # main data
    from_main_df = getBudgetMainData(category, from_date, from_date_end, from_date_budget_df)
    to_main_df = getBudgetMainData(category, to_date, to_date_end, to_date_budget_df)

    # concate df
    # ['category', 'budget_x', 'budget_y']
    budget_df = concate_df(from_date_budget_df, to_date_budget_df)
    # ['category', 'expense_x', 'budget_x', 'expense_y', 'budget_y']
    expense_df = concate_df(from_main_df, to_main_df)

    return {"budget_df": budget_df, "expense_df": expense_df}


def search_expense(request):
    category = request.GET['category']
    fDate = datetime.strptime(request.GET['from_date'], "%Y-%m-%d")
    tDate = datetime.strptime(request.GET['to_date'], "%Y-%m-%d")

    fDate_end = fDate + relativedelta(day=31)
    tDate_end = tDate + relativedelta(day=31)

    from_date = fDate.strftime("%Y-%m-%d")
    to_date = tDate.strftime("%Y-%m-%d")

    from_date_end = fDate_end.strftime("%Y-%m-%d")
    to_date_end = tDate_end.strftime("%Y-%m-%d")

    fromMonthYear = fDate.strftime("%B %Y")
    toMonthYear = tDate.strftime("%B %Y")

    # read data, peprocessing, distruct
    expense_data = getExpenseDFbyMonthRange(category, from_date, from_date_end, to_date, to_date_end)
    budget_df = expense_data['budget_df']
    expense_df = expense_data['expense_df']

    ############### budget graph start ###############
    budget_bar = get_budget_bar(budget_df, fromMonthYear, toMonthYear)
    budget_scatter = get_budget_scatter(budget_df, fromMonthYear, toMonthYear)
    ############### budget graph end ###############

    ############### budget graph start ###############
    expense_bar = get_expense_bar(expense_df, fromMonthYear, toMonthYear)
    expense_scatter = get_expense_scatter(expense_df, fromMonthYear, toMonthYear)
    ############### budget graph end ###############

    # make json
    expense_df.sort_values(by=['category'], inplace=True, ascending=False)
    json_records = expense_df.reset_index().to_json(orient='records')
    main_data = []
    main_data = json.loads(json_records)

    json_data = json.dumps({
        "budget_bar": budget_bar,
        "budget_scatter": budget_scatter,
        "expense_bar": expense_bar,
        "expense_scatter": expense_scatter,
        "main_data": main_data,
        "fromMonthYear": fromMonthYear,
        "toMonthYear": toMonthYear,
    })
    return HttpResponse(json_data, content_type="application/json")


def get_expense_bar(expense_df, fromMonthYear, toMonthYear):
    trace = {
        'x': list(expense_df["category"]),
        'y': list(expense_df["expense_x"]),
        'type': 'bar',
        'name': fromMonthYear,
        'marker': {
            'color': '#7163F1',
            'width': 1
        },
    }
    trace2 = {
        'x': list(expense_df["category"]),
        'y': list(expense_df["expense_y"]),
        'type': 'bar',
        'name': toMonthYear,
        'marker': {
            'color': '#FF0000',
            'width': 1
        },
    }
    traceLayout = {
        'title': {
            'text': fromMonthYear+' And '+toMonthYear,
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
        'barmode': 'group'
    }
    return {"trace": trace, "trace2": trace2, "traceLayout": traceLayout}


def get_expense_scatter(expense_df, fromMonthYear, toMonthYear):
    trace = {
        'x': list(expense_df["category"]),
        'y': list(expense_df["expense_x"]),
        'type': 'scatter',
        'name': fromMonthYear,
        'mode': 'lines+markers',
        'marker': {
            'color': '#7163F1',
            'width': 1
        },
    }
    trace2 = {
        'x': list(expense_df["category"]),
        'y': list(expense_df["expense_y"]),
        'type': 'scatter',
        'name': toMonthYear,
        'mode': 'lines+markers',
        'marker': {
            'color': '#FF0000',
            'width': 1
        },
    }
    traceLayout = {
        'title': {
            'text': fromMonthYear+' And '+toMonthYear,
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
        # 'barmode': 'group'
    }
    return {"trace": trace, "trace2": trace2, "traceLayout": traceLayout}


def get_budget_bar(budget_df, fromMonthYear, toMonthYear):
    trace = {
        'x': list(budget_df["category"]),
        'y': list(budget_df["budget_x"]),
        'type': 'bar',
        'name': fromMonthYear,
        'marker': {
            'color': '#7163F1',
            'width': 1
        },
    }
    trace2 = {
        'x': list(budget_df["category"]),
        'y': list(budget_df["budget_y"]),
        'type': 'bar',
        'name': toMonthYear,
        'marker': {
            'color': '#FF0000',
            'width': 1
        },
    }
    traceLayout = {
        'title': {
            'text': fromMonthYear+' And '+toMonthYear,
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
            'title': 'Budget',
            'color': '#888',
            'titlefont': {'size': 12},
            'automargin': 'true',
            'showline': 'true'
        },
        'height': '400',
        'barmode': 'group'
    }
    return {"trace": trace, "trace2": trace2, "traceLayout": traceLayout}


def get_budget_scatter(budget_df, fromMonthYear, toMonthYear):
    trace = {
        'x': list(budget_df["category"]),
        'y': list(budget_df["budget_x"]),
        'type': 'scatter',
        'name': fromMonthYear,
        'mode': 'lines+markers',
        'marker': {
            'color': '#7163F1',
            'width': 1
        },
    }
    trace2 = {
        'x': list(budget_df["category"]),
        'y': list(budget_df["budget_y"]),
        'type': 'scatter',
        'name': toMonthYear,
        'mode': 'lines+markers',
        'marker': {
            'color': '#FF0000',
            'width': 1
        },
    }
    traceLayout = {
        'title': {
            'text': fromMonthYear+' And '+toMonthYear,
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
            'title': 'Budget',
            'color': '#888',
            'titlefont': {'size': 12},
            'automargin': 'true',
            'showline': 'true'
        },
        'height': '400',
        # 'barmode': 'group'
    }
    return {"trace": trace, "trace2": trace2, "traceLayout": traceLayout}
