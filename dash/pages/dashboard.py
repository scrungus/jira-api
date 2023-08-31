import dash
from dash import dcc, html, callback, Output, Input
from datetime import date
from common.sidebar import get_sidebar
from functions.compute_views import compute_graph
from functions.query import get_data

dash.register_page(__name__, path='/')

main_panel = html.Section(
    id="root",
    className="hero is-fullheight is-light is-flex",
    children=[
        html.Meta(name="viewport", content="width=device-width, initial-scale=1"),
        html.H1(children='Jira Work Log Data', className='title', style={'textAlign':'center'}),
        dcc.DatePickerRange(
            id='jira-data-filter',
            min_date_allowed=date(2019, 1, 1),
            start_date=date.today().replace(day=1),
            end_date=date.today()
        ),
        dcc.Graph(id='graph-content'),
        dcc.Store(id='worklogs'),
        dcc.Store(id='employees')
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
            className='column is-flex is-one-fifth is-align-items-stretch',
            children=[get_sidebar()]
        ),
        html.Div(
            className='column is-flex is-align-items-stretch',
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
    Output('graph-content','figure'),

    Input('worklogs','data'),
    Input('employees','data')
)
def update_graph(worklogs,employees):
    return compute_graph(worklogs,employees)