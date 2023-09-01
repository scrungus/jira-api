import dash
from dash import html, callback, Output, Input, dcc, State
from datetime import date
from common.sidebar import get_sidebar
import time
import os 

dash.register_page(__name__, path='/export')

if 'REDIS_URL' in os.environ:
    # Use Redis & Celery if REDIS_URL set as an env variable
    from celery import Celery
    print(os.environ['REDIS_URL'])
    celery_app = Celery(__name__, broker=os.environ['REDIS_URL'], backend=os.environ['REDIS_URL'])
    background_callback_manager = CeleryManager(celery_app)

main_panel = html.Section(
    id="root",
    className="hero is-fullheight is-light is-flex",
    children=[
        html.Meta(name="viewport", content="width=device-width, initial-scale=1"),
        html.Div(
            className='hero-head',
            children=[
                html.Div(
                    className="container",
                    children=[
                        html.Div(
                            className="title",
                            children=["Export Jira Data"],
                            style={'textAlign':'center'}
                        )
                    ]
                )
            ]
        ),
        html.Div(
            className='hero-body has-text-centered is-flex is-flex-direction-column',
            children=[
                html.Div(
                    className="container",
                    children=[
                        html.Section(
                            id="date-container",
                            className='card',
                            children=[
                                html.Header(
                                    className='card-header', children=[
                                        html.P(className="card-header-title", children=["Select a date range"])
                                    ]
                                ),
                                html.Div(
                                    className='card-content',
                                    children=[
                                        dcc.DatePickerRange(
                                            id='jira-data-filter',
                                            min_date_allowed=date(2019, 1, 1),
                                            start_date=date.today().replace(day=1),
                                            end_date=date.today()
                                        ),
                                    ]
                                ),
                            ],
                        ),
                    ]
                ),
                html.Div(
                    className="container",
                    children=[
                        html.Button(
                            id="export-button",
                            className="button is-danger",
                            n_clicks=0,
                            children=["Export"]
                        )
                    ]
                ),   
            ]
        ),
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
        ),
        html.P(id='placeholder')
    ],
)

@callback(
    Output('placeholder','children'),
    
    Input('export-button','n_clicks'),

    State('jira-data-filter','start_date'),
    State('jira-data-filter','end_date'),

    prevent_initial_call=True,
    background=True
)
def export_jira_data(n_clicks, start_date, end_date):
    time.sleep(2.0)
    print()
    print(f'you are exporting the range {start_date} - {end_date}')