import dash
from dash import html
from common.sidebar import get_sidebar

dash.register_page(__name__, path='/export')

main_panel = html.Section(
    id="root",
    className="hero is-fullheight is-light is-flex",
    children=[
        html.H1('export!')
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