import dash
from dash import dcc, html, callback, Output, Input
from datetime import date
from common.sidebar import get_sidebar
from functions.compute_views import compute_graph
from functions.query import get_data
import json

dash.register_page(__name__, path='/')

histogram = html.Section(
    id="histogram-container",
    className='card',
    children=[
        html.Div(
            className='card-content',
            children=[
                dcc.Graph(
                    id="histogram-graph",
                    #config={"displayModeBar": False},
                ),
            ]
        ),
        html.Footer(
            className='card-footer', children=[
                html.P(className='card-footer-item', id="histogram-title")
            ]
        ),
    ],
)

main_panel = html.Section(
    id="root",
    className="hero is-fullheight is-light is-flex",
    children=[
        html.Div(
            className="hero-body",
            children=[
                html.Meta(name="viewport", content="width=device-width, initial-scale=1"),
                html.Div(
                    className="hero-head",
                    children=[html.H1(children='Jira Work Log Data', className='title', style={'textAlign':'center'})]
                ),
                dcc.DatePickerRange(
                    id='jira-data-filter',
                    min_date_allowed=date(2019, 1, 1),
                    start_date=date.today().replace(day=1),
                    end_date=date.today()
                ),
                histogram,
                dcc.Store(id='worklogs'),
                dcc.Store(id='employees')
            ]
        )
    ],
    style = {
        'width': '100%',
        'z-index' : '0'
    }
    )

layout = html.Div(
    className='columns is-gapless is-flex',
    children=[
        html.Div(
            className='column is-flex is-one-fifth',
            children=[get_sidebar()]
        ),
        html.Div(
            className='column is-flex',
            children=[main_panel]
        )
    ],
)

@callback(
    Output('worklogs', 'data'),
    Output('employees', 'data'),

    Input('jira-data-filter', 'start_date'),
    Input('jira-data-filter', 'end_date')
)
def update_jira_data(start_date, end_date):
    return get_data(start_date,end_date)

@callback(
    Output('histogram-graph','figure'),
    Output('histogram-title','children'),
    Output('histogram-title','className'),

    Input('worklogs','data'),
    Input('employees','data'),
    Input('jira-data-filter', 'start_date'),
    Input('jira-data-filter', 'end_date'),
)
def update_graph(worklogs,employees, start_date, end_date):
    worklogs_json  = json.loads(worklogs)

    if not all(value == {} for value in worklogs_json.values()):
        title = f'Timesheet Data for the Period {start_date, end_date}'
        className = "card-footer-item"
    else:
        title = "No work logged in date period specified"
        className = "card-footer-item is-italic"

    return compute_graph(worklogs,employees), title, className