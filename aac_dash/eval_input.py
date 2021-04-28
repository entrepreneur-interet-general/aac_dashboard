import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from flask_sqlalchemy import SQLAlchemy

app = dash.Dash()
app.server.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/test.db"
db = SQLAlchemy(app.server)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return "<User %r>" % self.username


app.layout = html.Div(
    [
        html.H4("username"),
        dcc.Input(id="username", placeholder="enter username", type="text"),
        html.H4("email"),
        dcc.Input(id="email", placeholder="enter email", type="email"),
        html.Button("add user", id="add-button"),
        html.Hr(),
        html.H3("users"),
        html.Div(id="users"),
    ]
)


@app.callback(
    Output("users", "children"),
    [Input("add-button", "n_clicks")],
    [State("username", "value"), State("email", "value")],
)
def add_and_show_users(n, username, email):
    if n is not None:
        # if button clicked, add user
        db.session.add(User(username=username, email=email))
        db.session.commit()

    # get all users in database
    users = db.session.query(User).all()
    return [
        html.Div(
            [
                html.Span([html.H5("Username: "), u.username]),
                html.Span([html.H5("Email: "), u.email]),
            ]
        )
        for u in users
    ]


if __name__ == "__main__":
    db.create_all()
    app.run_server()
