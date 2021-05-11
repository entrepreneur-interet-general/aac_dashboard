# -*- coding: utf-8 -*-
import base64
import io
import os
import json
import requests
from pandas.io.json import json_normalize
import numpy as np
import pandas as pd
import sqlalchemy as sa
from dash import Dash
import dash
import dash_auth
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_table
import plotly.graph_objects as go
import plotly.express as px
from random import randint
import flask
from sqlalchemy import insert
from sqlalchemy import MetaData


###################################################################################
###################################################################################
#################################### APP SETUP ####################################
###################################################################################
###################################################################################

# Keep this out of source code repository - save in a file or a database

external_stylesheets = [
    dbc.themes.LUX
]  # Other themes available. Check out https://bootswatch.com/lux/

app = Dash(__name__, external_stylesheets=external_stylesheets)

VALID_USERNAME_PASSWORD_PAIRS = {"username": "password"}  # Keep this in a separate file
auth = dash_auth.BasicAuth(app, VALID_USERNAME_PASSWORD_PAIRS)

server = app.server

app.config.suppress_callback_exceptions = True

### API setup

api_token = YourPrivateToken
api_id_demarche = NumberOfYourDémarche

api_url = "https://www.demarches-simplifiees.fr/api/v2/graphql"

api_headers = {"Content-Type": "application/json", "Authorization": f"{api_token}"}


###################################################################################
###################################################################################
################################## AUTHENTICATION #################################
###################################################################################
###################################################################################


########### DataFrames

from plotly.subplots import make_subplots

PAGE_SIZE = 15

eng = sa.create_engine("postgresql://.....")  # your database DSN

dfquestions = pd.read_sql("""SELECT "questions" FROM public."fieldmap";""", eng)
dfjury = pd.read_sql("""SELECT * FROM public."jury";""", eng)


###################################################################################
###################################################################################
################################# LAYOUT ELEMENTS #################################
###################################################################################
###################################################################################

### Titles

title = dbc.Row(
    [
        dbc.Col(
            [
                html.Br(),
                html.Br(),
                html.H1(
                    children="Evaluation des candidatures EIG 5",
                    style={"textAlign": "center"},
                ),
                html.Br(),
                html.Br(),
                html.Br(),
            ],
            width=9,
        )
    ],
    justify="center",
)


evaltitle = dbc.Card(
    dbc.CardBody(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H3(
                                children="Evaluation", style={"textAlign": "center"}
                            ),
                        ],
                        width=9,
                    )
                ],
                justify="center",
            )
        ]
    ),
    color="light",
)

tabletitle = dbc.Card(
    dbc.CardBody(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H3(
                                children="Aperçu des candidatures et de leur évaluation",
                                style={"textAlign": "center"},
                            )
                        ],
                        width=9,
                    )
                ],
                justify="center",
            )
        ]
    ),
    color="light",
)


eytitle = dbc.Card(
    dbc.CardBody(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H3(
                                children="Classification des candidatures par EY",
                                style={"textAlign": "center"},
                            )
                        ],
                        width=9,
                    )
                ],
                justify="center",
            )
        ]
    ),
    color="light",
)

statstitle = dbc.Card(
    dbc.CardBody(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H3(
                                children="Statistiques et Graphiques",
                                style={"textAlign": "center"},
                            )
                        ],
                        width=9,
                    )
                ],
                justify="center",
            )
        ]
    ),
    color="light",
)


### First row: Job filters + dropdown of jury

jury = dbc.Form(
    [
        dbc.FormGroup(
            [
                dbc.Col(
                    [
                        dbc.Label(
                            "Je suis :",
                            html_for="jury-dropdown",
                            color="info",
                            style={"margin-left": "15px", "font-size": "large"},
                        ),
                        dbc.FormText(
                            "Si votre nom ne figure pas dans le menu, contactez Raphaëlle qui vous ajoutera",
                            style={"font-style": "italic", "margin-left": "15px"},
                            color="secondary",
                        ),
                        html.Br(),
                        dcc.Dropdown(
                            id="jury-dropdown",
                            options=[
                                {"label": i, "value": i}
                                for i in dfjury.jury_name.unique()
                            ],
                            style={"margin-right": "10px", "margin-left": "10px"},
                            placeholder="Sélectionnez votre nom",
                            persistence=True,
                        ),
                        html.Br(),
                        dbc.Alert(
                            "Afin d'éviter toute erreur, veillez à bien renseigner ces deux champs !",
                            dismissable="True",
                            color="warning",
                        ),
                        dbc.Alert(
                            "Pour évaluer une autre candidature, veuillez rafraîchir la page",
                            dismissable="True",
                            color="info",
                        ),
                    ]
                )
            ]
        )
    ]
)


jobfilters = dbc.Form(
    [
        dbc.FormGroup(
            [
                dbc.Label(
                    "Je souhaite évaluer une candidature...",
                    html_for="jobs-row",
                    color="info",
                    style={"margin-left": "15px", "font-size": "large"},
                ),
                dbc.FormText(
                    "Sélectionnez un métier",
                    style={"font-style": "italic", "margin-left": "15px"},
                    color="secondary",
                ),
                html.Br(),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dcc.RadioItems(
                                    id="jobs-row",
                                    options=[
                                        {
                                            "label": "Data scientist",
                                            "value": "Data scientist",
                                        },
                                        {
                                            "label": "Développeur / développeuse",
                                            "value": "Développeur / développeuse",
                                        },
                                        {"label": "Designer", "value": "Designer"},
                                        {
                                            "label": "Data engineer",
                                            "value": "Data engineer",
                                        },
                                        {"label": "Juriste", "value": "Juriste"},
                                        {
                                            "label": "Géomaticien / géomaticienne",
                                            "value": "Géomaticien / géomaticienne",
                                        },
                                        {"label": "Autre", "value": "Autre"},
                                    ],
                                    inputStyle={
                                        "margin-right": "10px",
                                        "margin-left": "10px",
                                    },
                                    labelStyle={"display": "inline-block"},
                                    persistence=True,
                                ),
                                html.Br(),
                                dbc.Button(
                                    "Evaluer une candidature",
                                    id="pick-evaluation",
                                    color="info",
                                    n_clicks=0,
                                    style={
                                        "margin-right": "10px",
                                        "margin-left": "10px",
                                    },
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        )
    ]
)


toprow = dbc.Card(
    dbc.CardBody(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            jury,
                        ],
                    ),
                    dbc.Col(
                        [
                            jobfilters,
                        ],
                    ),
                ],
                justify="center",
            )
        ]
    ),
    color="info",
    outline=True,
)


second_row = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [
                                        html.H5(
                                            "Candidature à évaluer",
                                            className="card-title",
                                        ),
                                        html.P(
                                            """
                                            Voici une des candidatures qui restent à évaluer. 
                                            Vous pouvez aussi choisir de sélectionner un autre profil si vous le 
                                            souhaitez en rafraîchissant la page et en cliquant à nouveau sur le 
                                            bouton "Evaluer une candidature".
                                            """
                                        ),
                                        html.Br(),
                                    ],
                                ),
                            ],
                            color="light",
                        ),
                    ],
                    width=6,
                ),
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [
                                        html.H5(
                                            children="Votre évaluation",
                                            className="card-title",
                                        ),
                                        dcc.Markdown(
                                            """
                                            Pour compléter votre évaluation de la candidature, veuillez remplir chacun des champs ci-dessous.

                                            """
                                        ),
                                        html.Br(),
                                        html.Br(),
                                    ],
                                ),
                            ],
                            color="light",
                        ),
                    ],
                    width=6,
                ),
            ]
        ),
        html.Br(),
    ]
)


third_row = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        html.Div(
                                                            id="candidate_id",
                                                            style={
                                                                "margin-left": "15px",
                                                                "margin-left": "15px",
                                                                "font-size": "small",
                                                            },
                                                        ),
                                                    ],
                                                    width={"size": 3, "offset": 1},
                                                ),
                                                dbc.Col(
                                                    [
                                                        dbc.Button(
                                                            "Obtenir le CV",
                                                            id="cv-button",
                                                            color="info",
                                                            n_clicks=0,
                                                        )
                                                    ],
                                                    width={"size": 3},
                                                ),
                                                dbc.Col(
                                                    [
                                                        html.Div(
                                                            id="cv-url",
                                                        )
                                                    ],
                                                    width={"size": 5},
                                                ),
                                            ],
                                            align="center",
                                        ),
                                    ],
                                ),
                            ],
                            color="light",
                        ),
                        html.Br(),
                        html.Div(id="candidate-placeholder"),
                    ],
                    width=6,
                ),
                dbc.Col(
                    [
                        dbc.Form(
                            [
                                dbc.FormGroup(
                                    [
                                        dcc.Markdown(
                                            "**Compétences techniques** *(compétences métier et clarté dans la communication, degré d'expérience...)*"
                                        ),
                                        dbc.InputGroup(
                                            [
                                                dbc.InputGroupAddon(
                                                    "Compétences techniques",
                                                    addon_type="prepend",
                                                ),
                                                dbc.Textarea(
                                                    id="competences-techniques-appreciation"
                                                ),
                                            ],
                                            className="mb-3",
                                            id="competences-tech",
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        dbc.Label(
                                                            "Score (1 = non qualifié, 5 = expert) :"
                                                        )
                                                    ],
                                                    align="left",
                                                ),
                                                dbc.Col(
                                                    [
                                                        dcc.RadioItems(
                                                            id="competences-techniques-score",
                                                            options=[
                                                                {
                                                                    "label": "1",
                                                                    "value": "1",
                                                                },
                                                                {
                                                                    "label": "2",
                                                                    "value": "2",
                                                                },
                                                                {
                                                                    "label": "3",
                                                                    "value": "3",
                                                                },
                                                                {
                                                                    "label": "4",
                                                                    "value": "4",
                                                                },
                                                                {
                                                                    "label": "5",
                                                                    "value": "5",
                                                                },
                                                            ],
                                                            inputStyle={
                                                                "margin-right": "10px",
                                                                "margin-left": "10px",
                                                            },
                                                            labelStyle={
                                                                "display": "inline-block"
                                                            },
                                                        )
                                                    ]
                                                ),
                                                html.Br(),
                                            ]
                                        ),
                                    ],
                                ),
                                dbc.FormGroup(
                                    [
                                        dcc.Markdown(
                                            "**Capacité à travailler en équipe-projet au sein d’un environnement administratif** *(mener un projet de bout en bout, travailler en équipe interdisciplinaire, s'adapter à la culture de l'administration d'accueil...)*"
                                        ),
                                        dbc.InputGroup(
                                            [
                                                dbc.InputGroupAddon(
                                                    "Travail d'équipe",
                                                    addon_type="prepend",
                                                ),
                                                dbc.Textarea(
                                                    id="travail-equipe-appreciation"
                                                ),
                                            ],
                                            className="mb-3",
                                            id="travail-equipe",
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        dbc.Label(
                                                            "Score (1 = non qualifié, 5 = expert) :"
                                                        )
                                                    ],
                                                    align="left",
                                                ),
                                                dbc.Col(
                                                    [
                                                        dcc.RadioItems(
                                                            id="travail-equipe-score",
                                                            options=[
                                                                {
                                                                    "label": "1",
                                                                    "value": "1",
                                                                },
                                                                {
                                                                    "label": "2",
                                                                    "value": "2",
                                                                },
                                                                {
                                                                    "label": "3",
                                                                    "value": "3",
                                                                },
                                                                {
                                                                    "label": "4",
                                                                    "value": "4",
                                                                },
                                                                {
                                                                    "label": "5",
                                                                    "value": "5",
                                                                },
                                                            ],
                                                            inputStyle={
                                                                "margin-right": "10px",
                                                                "margin-left": "10px",
                                                            },
                                                            labelStyle={
                                                                "display": "inline-block"
                                                            },
                                                        )
                                                    ]
                                                ),
                                            ]
                                        ),
                                        html.Br(),
                                    ]
                                ),
                                dbc.FormGroup(
                                    [
                                        dcc.Markdown(
                                            "**Esprit EIG ** *(engagement pour l'intérêt général, motivation, apport souhaité auprès de la communauté...)*"
                                        ),
                                        dbc.InputGroup(
                                            [
                                                dbc.InputGroupAddon(
                                                    "Esprit EIG", addon_type="prepend"
                                                ),
                                                dbc.Textarea(
                                                    id="esprit-eig-appreciation"
                                                ),
                                            ],
                                            className="mb-3",
                                            id="esprit-eig",
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        dbc.Label(
                                                            "Score (1 = non qualifié, 5 = expert) :"
                                                        )
                                                    ],
                                                    align="left",
                                                ),
                                                dbc.Col(
                                                    [
                                                        dcc.RadioItems(
                                                            id="esprit-eig-score",
                                                            options=[
                                                                {
                                                                    "label": "1",
                                                                    "value": "1",
                                                                },
                                                                {
                                                                    "label": "2",
                                                                    "value": "2",
                                                                },
                                                                {
                                                                    "label": "3",
                                                                    "value": "3",
                                                                },
                                                                {
                                                                    "label": "4",
                                                                    "value": "4",
                                                                },
                                                                {
                                                                    "label": "5",
                                                                    "value": "5",
                                                                },
                                                            ],
                                                            inputStyle={
                                                                "margin-right": "10px",
                                                                "margin-left": "10px",
                                                            },
                                                            labelStyle={
                                                                "display": "inline-block"
                                                            },
                                                        )
                                                    ]
                                                ),
                                            ]
                                        ),
                                        html.Br(),
                                    ]
                                ),
                                dbc.FormGroup(
                                    [
                                        dcc.Markdown(
                                            "**Impression générale** *(Points forts et points faibles de la candidature)*"
                                        ),
                                        dbc.InputGroup(
                                            [
                                                dbc.InputGroupAddon(
                                                    "Impression générale",
                                                    addon_type="prepend",
                                                ),
                                                dbc.Textarea(id="impression-generale"),
                                            ],
                                            className="mb-3",
                                            id="impression",
                                        ),
                                        html.Br(),
                                        dcc.Markdown("**Votre verdict: **"),
                                        dcc.RadioItems(
                                            id="next-steps",
                                            options=[
                                                {
                                                    "label": "Coup de coeur",
                                                    "value": "Coup de coeur",
                                                },
                                                {
                                                    "label": "Avis neutre",
                                                    "value": "Avis neutre",
                                                },
                                                {
                                                    "label": "Avis défavorable",
                                                    "value": "Avis défavorable",
                                                },
                                            ],
                                            inputStyle={
                                                "margin-right": "10px",
                                                "margin-left": "10px",
                                            },
                                            labelStyle={"display": "inline-block"},
                                        ),
                                        html.Br(),
                                    ]
                                ),
                                html.Br(),
                                dbc.Button(
                                    "Enregistrer mon évaluation",
                                    id="save-eval",
                                    n_clicks=0,
                                    color="info",
                                ),
                                html.Div(id="placeholder", children=[]),
                                # dcc.Interval(id='interval', interval=1000),
                            ]
                        ),
                    ],
                    width=6,
                ),
            ],
        ),
    ],
)


###################################################################################
###################################################################################
############################### BUILDING THE TABS #################################
###################################################################################
###################################################################################


tab1_content = dbc.Card(
    dbc.CardBody(
        [
            evaltitle,
            html.Br(),
            dbc.Row(
                [
                    dbc.Col(
                        toprow,
                        width={"size": 8, "offset": 2},
                    ),
                ],
            ),
            html.Br(),
            second_row,
            html.Br(),
            third_row,
        ],
    )
)

tab2_content = dbc.Card(
    dbc.CardBody(
        [
            tabletitle,
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dcc.Interval(
                                id="interval_pg", interval=86400000 * 7, n_intervals=0
                            ),
                            html.Div(id="sql-db"),
                        ],
                        width=12,
                    ),
                ],
                justify="center",
            ),
        ]
    ),
    className="mt-3",
)

tab2ey_content = dbc.Card(
    dbc.CardBody(
        [
            eytitle,
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dcc.Interval(
                                id="interval_pg2", interval=86400000 * 7, n_intervals=0
                            ),
                            html.Div(id="ey-table"),
                        ],
                        width=12,
                    ),
                ],
                justify="center",
            ),
        ]
    ),
    className="mt-3",
)

tab3_content = dbc.Card(
    dbc.CardBody(
        [
            statstitle,
            dcc.Graph(id="piechart"),
            # fig.update_layout(margin=dict(t=10, b=10, r=10, l=10))
        ]
    ),
    className="mt-3",
)

tabs = dbc.Tabs(
    [
        dbc.Tab(tab1_content, label="Evaluation"),
        dbc.Tab(tab2_content, label="Aperçu des candidatures et de leur évaluation"),
        dbc.Tab(tab2ey_content, label="Classification des candidatures par EY"),
        dbc.Tab(tab3_content, label="Statistiques & Graphiques"),
    ]
)


### Final layout

app.layout = html.Div([title, tabs])

###################################################################################
###################################################################################
#################################### CALLBACKS ####################################
###################################################################################
###################################################################################


### Callback: Get a priority random new candidate when pressing the button


@app.callback(
    [Output("candidate-placeholder", "children"), Output("candidate_id", "children")],
    Input("pick-evaluation", "n_clicks"),
    State("jury-dropdown", "value"),
    State("jobs-row", "value"),
    prevent_initial_call=False,
)
def write_evaluation(nclicks, jury, job):
    """Callback to write into SQL from the evaluation module"""
    no_output = dbc.Col(
        [html.Br(), dbc.Alert("Veuillez sélectionner une candidature", color="warning")]
    )
    output = dbc.Col([html.Br(), dbc.Alert("!!!", color="success")])
    no_candidate_id = ""
    input_triggered = dash.callback_context.triggered[0]["prop_id"].split(".")[0]
    if nclicks < 1:
        return no_output, no_candidate_id
    else:
        myquery = """SELECT * FROM public.applications WHERE "Q2hhbXAtMTY4MDI3Ng" = %s AND eval_count < 2 AND "jury_name" NOT LIKE %s AND "ey_classification" = 'VIVIER DE PROFILS A POTENTIEL' ORDER BY RANDOM() LIMIT 1;"""
        df_apps = pd.read_sql(myquery, con=eng, params=(job, jury))
        candidate_id = df_apps["dossier_id"]
        dff_apps = df_apps.drop(
            columns=["index", "app_id", "dossier_id", "eval_count", "jury_name"]
        )
        dff_apps = dff_apps.rename(index={0: "Réponses"})
        dff_apps = dff_apps.transpose()
        dff_apps = dff_apps["Réponses"].reset_index(drop=True)
        table_applis = pd.concat([dfquestions, dff_apps], axis=1)
        table2 = dbc.Table.from_dataframe(
            table_applis,
            style={"whiteSpace": "normal", "height": "auto"},
            size="sm",
            striped=False,
            bordered=True,
            hover=True,
        )

        table = (
            dash_table.DataTable(
                id="candidate-dossier-table",
                columns=[{"name": i, "id": i} for i in table_applis.columns],
                data=table_applis.to_dict("records"),
                # style_as_list_view=True,
                style_header={
                    "backgroundColor": "white",
                    "fontWeight": "bold",
                    "font-size": "large",
                },
                style_table={"overflowX": "auto"},
                style_cell={
                    "padding-left": "10px",
                    "padding-right": "10px",
                    "padding-top": "10px",
                    "padding-bottom": "10px",
                    "textAlign": "left",
                    "font-family": "Nunito Sans",
                    "whiteSpace": "normal",
                    "height": "auto",
                },
            ),
        )

        return table, candidate_id


### Callback: call API to get CV
@app.callback(
    Output("cv-url", "children"),
    Input("cv-button", "n_clicks"),
    State("candidate_id", "children"),
)
def get_cv(nclicks, dossier_id):
    no_output = html.Div(
        "⬅️ Cliquez pour obtenir le CV",
        style={"margin-left": "15px", "margin-right": "15px", "font-size": "small"},
    )

    input_triggered = dash.callback_context.triggered[0]["prop_id"].split(".")[0]
    if nclicks < 1:
        return no_output
    else:
        q1 = """
        query{
        dossier(number: %s) {
            champs{
            ...on PieceJustificativeChamp {
                file {
                url
                }
            }
            }
        }
        }
        """ % (
            int(dossier_id[0])
        )
        api_json = {"query": q1}
        r = requests.post(url=api_url, json=api_json, headers=api_headers)
        data = r.json()
        cvdata = data["data"]["dossier"]["champs"][8]
        cvdf = pd.json_normalize(cvdata)
        cv_url = cvdf.iloc[0]["file.url"]
        return html.A(
            children="🔹 Lien vers le CV 🔹",
            href=cv_url,
            style={"margin-left": "15px", "margin-left": "15px", "font-size": "medium"},
            target="_blank",
        )


### Callback: Write Evaluations into SQL db


@app.callback(
    Output("placeholder", "children"),
    Input("save-eval", "n_clicks"),
    State("candidate_id", "children"),
    State("jury-dropdown", "value"),
    State("competences-techniques-appreciation", "value"),
    State("competences-techniques-score", "value"),
    State("travail-equipe-appreciation", "value"),
    State("travail-equipe-score", "value"),
    State("esprit-eig-appreciation", "value"),
    State("esprit-eig-score", "value"),
    State("impression-generale", "value"),
    State("next-steps", "value"),
    prevent_initial_call=False,
)
def write_evaluation(
    nclicks,
    candidate,
    juryname,
    competencestechniquesappreciation,
    competencestechniquesscore,
    travailequipeappreciation,
    travailequipescore,
    espriteigappreciation,
    espriteigscore,
    impressiongenerale,
    nextsteps,
):
    """Callback to write into SQL from the evaluation module"""
    no_output = dbc.Col(
        [
            html.Br(),
            dbc.Alert(
                "Attention, votre évaluation n'est pas enregistrée !", color="warning"
            ),
        ]
    )
    output = dbc.Col(
        [
            html.Br(),
            dbc.Alert(
                "Evaluation enregistrée. Veuillez rafraîchir la page et sélectionner une nouvelle candidature",
                color="success",
            ),
        ]
    )
    existing_output = dbc.Col(
        [
            html.Br(),
            dbc.Alert("Votre évaluation a déjà été enregistrée !", color="warning"),
        ]
    )

    # If click is triggered
    input_triggered = dash.callback_context.triggered[0]["prop_id"].split(".")[0]
    if nclicks < 1:
        return no_output

    elif nclicks == 1:
        df_eval = pd.read_sql("SELECT * FROM public.evaluations ORDER BY id DESC;", eng)
        if df_eval.empty:
            id = 100
        else:
            id = df_eval["id"][0]
            id = int(id) + 1

        # Insert into the evaluations table
        insert_statement = (
            "INSERT INTO public.evaluations VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        )
        reg_eval = ""
        metadata = MetaData(eng)
        metadata.reflect()
        evaluations = metadata.tables["evaluations"]
        with eng.begin() as conn:
            conn.execute(
                insert_statement,
                (
                    id,
                    candidate[0],
                    juryname,
                    competencestechniquesappreciation,
                    competencestechniquesscore,
                    travailequipeappreciation,
                    travailequipescore,
                    espriteigappreciation,
                    espriteigscore,
                    impressiongenerale,
                    nextsteps,
                ),
            )

        # insert the name of jury and number of evaluations so far for this candidate in the applications table
        eval_count_query = pd.read_sql(
            "SELECT eval_count FROM public.applications WHERE dossier_id = %s",
            eng,
            params={candidate[0]},
        )
        eval_count = int(eval_count_query.iloc[0])
        eval_count = eval_count + 1
        reg_eval = "UPDATE public.applications SET eval_count= %s ,jury_name= %s WHERE dossier_id = (%s)"
        metadata = MetaData(eng)
        metadata.reflect()
        applications = metadata.tables["applications"]
        with eng.begin() as conn:
            conn.execute(reg_eval, (eval_count, juryname, candidate[0]))

        return output
    else:
        return existing_output


### Callback: Tab 2 Table


@app.callback(Output("sql-db", "children"), [Input("interval_pg", "n_intervals")])
def populate_datatable(n_intervals):
    df_overview = pd.read_sql(
        """SELECT * FROM public.evaluations a FULL JOIN ( SELECT "Q2hhbXAtMTY4MTE5OA", "Q2hhbXAtMTY4MTEzNA", "Q2hhbXAtMTY4MTEzMw", "Q2hhbXAtMTY4MTIwMQ", "Q2hhbXAtMTY4MDI3Ng", "Q2hhbXAtMTY4MDQ1OA", "dossier_id", "eval_count" FROM public.applications ) b on a.dossier_id = b.dossier_id""",
        eng,
    )
    # rename columns for readibility
    df_overview.rename(
        columns={
            "dossier_id": "Dossier N°",
            "jury_name": "Evaluateur/Evaluatrice",
            "competences-techniques-appreciation": "Compétences techniques: appréciation",
            "competences-techniques-score": "Compétences techniques: score",
            "travail-equipe-appreciation": "Travail en équipe: appréciation",
            "travail-equipe-score": "Travail en équipe: score",
            "esprit-eig-appreciation": "Esprit EIG: appréciation",
            "esprit-eig-score": "Esprit EIG: score",
            "impression-generale": "Impression Générale",
            "next-steps": "Verdict !",
            "Q2hhbXAtMTY4MTE5OA": "Civilité",
            "Q2hhbXAtMTY4MTEzNA": "Prénom",
            "Q2hhbXAtMTY4MTEzMw": "Nom",
            "Q2hhbXAtMTY4MTIwMQ": "E-mail",
            "Q2hhbXAtMTY4MDI3Ng": "Métier",
            "Q2hhbXAtMTY4MDQ1OA": "Statut de la candidature",
            "eval_count": "Nombre d'évaluations",
        },
        inplace=True,
    )
    # Average score
    df_overview["Average"] = df_overview[
        [
            "Compétences techniques: score",
            "Travail en équipe: score",
            "Esprit EIG: score",
        ]
    ].mean(axis=1)
    # Trying out emoji for coup de coeur
    df_overview["Moyenne"] = df_overview["Average"].apply(
        lambda x: "⭐⭐⭐⭐⭐"
        if x == 5
        else (
            "⭐⭐⭐⭐"
            if x >= 4
            else ("⭐⭐⭐" if x >= 3 else ("⭐⭐" if x >= 2 else ("⭐" if x >= 0 else "")))
        )
    )
    df_overview = df_overview[
        [
            "Dossier N°",
            "Civilité",
            "Prénom",
            "Nom",
            "E-mail",
            "Métier",
            "Nombre d'évaluations",
            "Evaluateur/Evaluatrice",
            "Impression Générale",
            "Moyenne",
            "Verdict !",
            "Compétences techniques: appréciation",
            "Compétences techniques: score",
            "Travail en équipe: appréciation",
            "Travail en équipe: score",
            "Esprit EIG: appréciation",
            "Esprit EIG: score",
            "Statut de la candidature",
        ]
    ]
    # remove duplicate column
    df_overview = df_overview.loc[:, ~df_overview.columns.duplicated()]
    df_overview = df_overview.sort_values(
        by=["Moyenne", "Dossier N°"], ascending=False, na_position="last"
    )
    # populate tab 2 with the table
    return [
        dash_table.DataTable(
            id="data-table",
            columns=[{"name": i, "id": i} for i in df_overview.columns],
            data=df_overview.to_dict("records"),
            style_as_list_view=True,
            style_header={
                "backgroundColor": "white",
                "fontWeight": "bold",
                "font-size": "medium",
                "padding-left": "20px",
                "padding-right": "20px",
                "padding-top": "10px",
                "padding-bottom": "10px",
            },
            style_table={"overflowX": "auto"},
            style_cell={
                "textAlign": "left",
                "font-family": "Nunito Sans",
                "width": "180px",
                "minWidth": "180px",
                "maxWidth": "300px",
                "whiteSpace": "no-wrap",
                "overflow": "hidden",
                "height": "auto",
            },
            style_data_conditional=[
                {
                    "if": {"filter_query": '{Verdict !} contains "coeur"'},
                    "backgroundColor": "#dbf2e3",
                    #'color': 'white'
                },
                {
                    "if": {"filter_query": '{Verdict !} contains "défavorable"'},
                    "backgroundColor": "#f7dddc",
                },
            ],
            filter_action="native",
            sort_action="native",
            sort_mode="multi",
        ),
    ]

# TODO: refactor code!


### Callback: Tab 2-bis:  EY Table


@app.callback(Output("ey-table", "children"), [Input("interval_pg2", "n_intervals")])
def populate_datatable(n_intervals):
    df_ey = pd.read_sql("""SELECT * FROM public.classification_ey """, eng)
    df_ey = df_ey.sort_values(by=["total"], ascending=False, na_position="last")
    # populate tab 2 with the table
    return [
        dash_table.DataTable(
            id="ey-data-table",
            columns=[{"name": i, "id": i} for i in df_ey.columns],
            data=df_ey.to_dict("records"),
            tooltip_data=[
                {
                    column: {"value": str(value), "type": "markdown"}
                    for column, value in row.items()
                }
                for row in df_ey.to_dict("records")
            ],
            tooltip_duration=None,
            style_as_list_view=True,
            style_cell={
                "textAlign": "left",
                "font-family": "Nunito Sans",
                "width": "150px",
                "minWidth": "180px",
                "maxWidth": "400px",
                "whiteSpace": "no-wrap",
                "overflow": "hidden",
                "textOverflow": "ellipsis",
            },
            style_header={
                "backgroundColor": "white",
                "fontWeight": "bold",
                "font-size": "medium",
                "padding-left": "20px",
                "padding-right": "20px",
                "padding-top": "10px",
                "padding-bottom": "10px",
            },
            style_table={"overflowX": "auto"},
            style_cell_conditional=[
                {
                    "if": {
                        "column_id": "ey_classification",
                    },
                    "display": "None",
                }
            ],
            style_data_conditional=[
                {
                    "if": {"filter_query": '{ey_classification} contains "POTENTIEL"'},
                    "backgroundColor": "#dbf2e3",
                },
                {
                    "if": {"filter_query": '{ey_classification} contains "NON RETENU"'},
                    "backgroundColor": "#f7dddc",
                },
            ],
            filter_action="native",
            sort_action="native",
            sort_mode="multi",
        ),
    ]


### Callback: Tab 3 Charts
@app.callback(Output("piechart", "figure"), [Input("interval_pg", "n_intervals")])
def create_charts(n_intervals):
    df_overview = pd.read_sql(
        """SELECT * FROM public.evaluations a FULL JOIN ( SELECT "Q2hhbXAtMTY4MTE5OA", "Q2hhbXAtMTY4MTEzNA", "Q2hhbXAtMTY4MTEzMw", "Q2hhbXAtMTY4MTIwMQ", "Q2hhbXAtMTY4MDI3Ng", "Q2hhbXAtMTY4MDQ1OA", "dossier_id", "eval_count" FROM public.applications ) b on a.dossier_id = b.dossier_id""",
        eng,
    )
    # rename columns for readibility
    df_overview.rename(
        columns={
            "dossier_id": "Dossier N°",
            "jury_name": "Evaluateur/Evaluatrice",
            "competences-techniques-appreciation": "Compétences techniques: appréciation",
            "competences-techniques-score": "Compétences techniques: score",
            "travail-equipe-appreciation": "Travail en équipe: appréciation",
            "travail-equipe-score": "Travail en équipe: score",
            "esprit-eig-appreciation": "Esprit EIG: appréciation",
            "esprit-eig-score": "Esprit EIG: score",
            "impression-generale": "Impression Générale",
            "next-steps": "Verdict !",
            "Q2hhbXAtMTY4MTE5OA": "Civilité",
            "Q2hhbXAtMTY4MTEzNA": "Prénom",
            "Q2hhbXAtMTY4MTEzMw": "Nom",
            "Q2hhbXAtMTY4MTIwMQ": "E-mail",
            "Q2hhbXAtMTY4MDI3Ng": "Métier",
            "Q2hhbXAtMTY4MDQ1OA": "Statut de la candidature",
            "eval_count": "Nombre d'évaluations",
        },
        inplace=True,
    )
    # Average score
    df_overview["Average"] = df_overview[
        [
            "Compétences techniques: score",
            "Travail en équipe: score",
            "Esprit EIG: score",
        ]
    ].mean(axis=1)
    # Trying out emoji for coup de coeur
    df_overview["Moyenne"] = df_overview["Average"].apply(
        lambda x: "⭐⭐⭐⭐⭐"
        if x == 5
        else (
            "⭐⭐⭐⭐"
            if x >= 4
            else ("⭐⭐⭐" if x >= 3 else ("⭐⭐" if x >= 2 else ("⭐" if x >= 0 else "")))
        )
    )
    df_overview = df_overview[
        [
            "Dossier N°",
            "Civilité",
            "Prénom",
            "Nom",
            "E-mail",
            "Métier",
            "Nombre d'évaluations",
            "Evaluateur/Evaluatrice",
            "Impression Générale",
            "Moyenne",
            "Verdict !",
            "Compétences techniques: appréciation",
            "Compétences techniques: score",
            "Travail en équipe: appréciation",
            "Travail en équipe: score",
            "Esprit EIG: appréciation",
            "Esprit EIG: score",
            "Statut de la candidature",
            "Average",
        ]
    ]
    # remove duplicate column
    df_overview = df_overview.loc[:, ~df_overview.columns.duplicated()]
    df_overview = df_overview.sort_values(
        by=["Moyenne", "Dossier N°"], ascending=False, na_position="last"
    )
    histo_metiers = px.histogram(
        df_overview,
        x="Métier",
        color="Civilité",
        color_discrete_map={
            "Monsieur": "#b0e0e6",
            "Madame": "#bc8f8f",
            "Je préfère ne pas répondre": "#008080",
        },
        title="Civilité des candidats par métier",
    )

    return histo_metiers  # pie_chart


# TODO: Add charts of skills


# Run the Dash app
if __name__ == "__main__":
    app.server.run(debug=True, threaded=True)
