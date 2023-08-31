from dash import html

sidebar = html.Div(
    className="hero",
    children=[
        html.Div(
            className="box is-dark",
            children=[
                html.Aside(
                    className="menu is-dark",
                    children=[
                        html.Div(
                            children=[
                                html.P(
                                className='menu-label',
                                children=['Views']   
                                ),
                                html.Ul(
                                    className='menu-list',
                                    children=[
                                        html.Li(html.A('Dashboard', href='/')),
                                        html.Li(html.A('Export', href='/export'))
                                    ]
                                )
                            ]
                        )
                    ],
                )
            ],
        )
    ],
    style = {
                'width': '100%',
                'z-index' : '500'
            }
)

def get_sidebar():
    return sidebar