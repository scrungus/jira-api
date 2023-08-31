from dash import html,Dash, page_container
import db.models as models
from db.db_connection import engine

models.Base.metadata.create_all(bind=engine)
# models.WorkLogChangeLog.__table__.drop(engine)
# models.WorkLog.__table__.drop(engine)
# models.Ticket.__table__.drop(engine)

app = Dash(__name__, use_pages=True)



app.layout = html.Div([page_container])



if __name__ == '__main__':
    app.run(debug=True)