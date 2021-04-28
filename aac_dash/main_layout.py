import pandas as pd
import base64
import io
import sqlite3
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_table
import plotly.graph_objects as go 
import plotly.express as px


external_stylesheets = [dbc.themes.LUX]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

###########
from plotly.subplots import make_subplots

#df = pd.read_csv('/Users/raph/Documents/Etalab/AAC_AAP/aac_dashboard/data/raw/applications.csv')
PAGE_SIZE=15

conn = sqlite3.connect('./data/sql/raw_data.sqlite')
c = conn.cursor()

df2 = pd.read_sql("SELECT Email, Civilité, Nom, Prénom FROM application_tab_0", conn)


### Filters
jobfilters = dbc.Form(
    [
        dbc.FormGroup(
            [
                dbc.Label("Je souhaite évaluer une candidature de...", html_for="example-radios-row", width=2),
                dbc.FormText(
                    "Sélectionnez un ou plusieurs profils",
                    style = {"margin-left": "20px"},
                    color="secondary",
                ),
                html.Br(),
                dbc.Col(
                    dcc.Checklist(
                        id="example-radios-row",
                        options=[
                            {"label": "Data Scientist", "value": 1},
                            {"label": "Dev", "value": 2},
                            {"label": "Designer", "value": 3},
                        ],
                        inputStyle={"margin-right": "10px", "margin-left": "10px"},
                        labelStyle={'display': 'inline-block'},
                    ),
                    width=10,
                ),
               
            ],
    row=False,   
)
])



####### Hierarchical treemaps
df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/sales_success.csv')
levels = ['salesperson', 'county', 'region'] # levels used for the hierarchical chart
color_columns = ['sales', 'calls']
value_column = 'calls'

def build_hierarchical_dataframe(df, levels, value_column, color_columns=None):
    """
    Build a hierarchy of levels for Sunburst or Treemap charts.

    Levels are given starting from the bottom to the top of the hierarchy,
    ie the last level corresponds to the root.
    """
    df_all_trees = pd.DataFrame(columns=['id', 'parent', 'value', 'color'])
    for i, level in enumerate(levels):
        df_tree = pd.DataFrame(columns=['id', 'parent', 'value', 'color'])
        dfg = df.groupby(levels[i:]).sum()
        dfg = dfg.reset_index()
        df_tree['id'] = dfg[level].copy()
        if i < len(levels) - 1:
            df_tree['parent'] = dfg[levels[i+1]].copy()
        else:
            df_tree['parent'] = 'total'
        df_tree['value'] = dfg[value_column]
        df_tree['color'] = dfg[color_columns[0]] / dfg[color_columns[1]]
        df_all_trees = df_all_trees.append(df_tree, ignore_index=True)
    total = pd.Series(dict(id='total', parent='',
                              value=df[value_column].sum(),
                              color=df[color_columns[0]].sum() / df[color_columns[1]].sum()))
    df_all_trees = df_all_trees.append(total, ignore_index=True)
    return df_all_trees

df_all_trees = build_hierarchical_dataframe(df, levels, value_column, color_columns)
average_score = df['sales'].sum() / df['calls'].sum()

fig = make_subplots(1, 2, specs=[[{"type": "domain"}, {"type": "domain"}]],)

fig.add_trace(go.Treemap(
    labels=df_all_trees['id'],
    parents=df_all_trees['parent'],
    values=df_all_trees['value'],
    branchvalues='total',
    marker=dict(
        colors=df_all_trees['color'],
        colorscale='RdBu',
        cmid=average_score),
    hovertemplate='<b>%{label} </b> <br> Sales: %{value}<br> Success rate: %{color:.2f}',
    name=''
    ), 1, 1)

fig.add_trace(go.Treemap(
    labels=df_all_trees['id'],
    parents=df_all_trees['parent'],
    values=df_all_trees['value'],
    branchvalues='total',
    marker=dict(
        colors=df_all_trees['color'],
        colorscale='RdBu',
        cmid=average_score),
    hovertemplate='<b>%{label} </b> <br> Sales: %{value}<br> Success rate: %{color:.2f}',
    maxdepth=2
    ), 1, 2)

fig.update_layout(margin=dict(t=10, b=10, r=10, l=10))

#### Setting up the modal
evaluation = dbc.Row(
    [
    dbc.Col([
        
        dbc.Table.from_dataframe(df2, striped=True, bordered=True, hover=True),
        ], align = 'left', width = 3),

    dbc.Col([
        html.H3(
            children='Evaluation'
            ),
        
        dcc.Markdown(
            '''
            Pour compléter votre évaluation de la candidature, veuillez remplir chacun des champs ci-dessous.

            La grille d'évaluation complète est disponible **ici**, n'hésitez pas à la consulter !'''
        ),

        html.Br(),

        html.Div(id="the_alert", children=[]),

        dcc.Markdown(
            "**Compétences techniques** *(compétences métier et clarté dans la communication, degré d'expérience...)*"
        ),

        dbc.InputGroup(
            [
                dbc.InputGroupAddon("Compétences techniques", addon_type="prepend"),
                dbc.Textarea(),
            ],
            className="mb-3",
            id="competences-techniques-appreciation"
        ),
        
        dbc.Row([
            dbc.Col([
                dbc.Label(  
                    "Score (1 = non qualifié, 5 = expert) :"
                )], align='left'),
            
            dbc.Col([
                dcc.RadioItems(
                    id = 'competences-techniques-score',
                    options=[
                        {'label': '1', 'value': '1'},
                        {'label': '2', 'value': '2'},
                        {'label': '3', 'value': '3'},
                        {'label': '4', 'value': '4'},
                        {'label': '5', 'value': '5'}
                    ],
                    inputStyle={"margin-right": "10px", "margin-left": "10px"},
                    labelStyle={'display': 'inline-block'}
                )]),
        ]),
        
        dcc.Markdown(
            "**Capacité à travailler en équipe-projet au sein d’un environnement administratif** *(mener un projet de bout en bout, travailler en équipe interdisciplinaire, s'adapter à la culture de l'administration d'accueil...)*"
        ),

        dbc.InputGroup(
            [
                dbc.InputGroupAddon("Travail d'équipe", addon_type="prepend"),
                dbc.Textarea(),
            ],
            className="mb-3",
            id="travail-equipe-appreciation"
        ),

        dbc.Row([
            dbc.Col([
                dbc.Label(  
                    "Score (1 = non qualifié, 5 = expert) :"
                )], align='left'),
            
            dbc.Col([
                dcc.RadioItems(
                    id = 'travail-equipe-score',
                    options=[
                        {'label': '1', 'value': '1'},
                        {'label': '2', 'value': '2'},
                        {'label': '3', 'value': '3'},
                        {'label': '4', 'value': '4'},
                        {'label': '5', 'value': '5'}
                    ],
                    inputStyle={"margin-right": "10px", "margin-left": "10px"},
                    labelStyle={'display': 'inline-block'}
                )]),
        ]),
        
        dcc.Markdown(
            "**Esprit EIG ** *(engagement pour l'intérêt général, motivation, apport souhaité auprès de la communauté...)*"
        ),

        dbc.InputGroup(
            [
                dbc.InputGroupAddon("Esprit EIG", addon_type="prepend"),
                dbc.Textarea(),
            ],
            className="mb-3",
            id="esprit-eig-appreciation"
        ),
        
        dbc.Row([
            dbc.Col([
                dbc.Label(  
                    "Score (1 = non qualifié, 5 = expert) :"
                )], align='left'),
            
            dbc.Col([
                dcc.RadioItems(
                    id = 'esprit-eig-score',
                    options=[
                        {'label': '1', 'value': '1'},
                        {'label': '2', 'value': '2'},
                        {'label': '3', 'value': '3'},
                        {'label': '4', 'value': '4'},
                        {'label': '5', 'value': '5'}
                    ],
                    inputStyle={"margin-right": "10px", "margin-left": "10px"},
                    labelStyle={'display': 'inline-block'}
                )]),
        ]),
        
        dcc.Markdown(
            "**Impression générale** *(Points forts et points faibles de la candidature)*"
        ),

        dbc.InputGroup(
            [
                dbc.InputGroupAddon("Impression générale", addon_type="prepend"),
                dbc.Textarea(),
            ],
            className="mb-3",
        ),
        
        dcc.Markdown(
            "**Coup de coeur ?** *(Cochez cette case si cette candidature vous impressionne)*"
        ),
        
        dcc.Checklist(
            id="coup-de-coeur", 
            options=[
                {'label': 'Coup de coeur', 'value': '1'}
            ],
            inputStyle={"margin-right": "10px", "margin-left": "10px"}
            ),
        
        dcc.Markdown(
            "**Priorisation de la candidature :**"
        ),

        dcc.RadioItems(
            id = 'priorite-candidature',
            options=[
                {'label': 'Profils prioritaires', 'value': '1'},
                {'label': 'Profils satisfaisants', 'value': '2'},
                {'label': 'Profils non recommandés', 'value': '3'}
            ],
            inputStyle={"margin-right": "10px", "margin-left": "10px"},
            labelStyle={'display': 'inline-block'}
            ),
        
        dcc.Markdown(
            "**Statut de la candidature :** "
        ),

        dcc.RadioItems(
            id = 'statut-candidature',
            options=[
                {'label': 'Admissible au jury', 'value': '1'},
                {'label': 'En cours de discussion', 'value': '2'},
                {'label': 'Non retenu', 'value': '3'}
            ],
            inputStyle={"margin-right": "10px", "margin-left": "10px"},
            labelStyle={'display': 'inline-block'}
            ),
        
        dcc.Markdown(
            "**Communication / Echanges en cours :**"
        ),

        dcc.RadioItems(
            id = 'communication-candidature',
            options=[
                {'label': 'Invitation aux jurys envoyée', 'value': '1'},
                {'label': 'Mail de refus envoyé', 'value': '2'},
                {'label': 'Réponse à faire', 'value': '3'}
            ],
            inputStyle={"margin-right": "10px", "margin-left": "10px"},
            labelStyle={'display': 'inline-block'}
            ) 
    ], align = 'right')
    ])

modal = html.Div(
    [
        dbc.Button("Evaluer", id="open"),

        dbc.Modal([
            dbc.ModalHeader("Evaluation de la candidature"),
            dbc.ModalBody(
                evaluation
            ),
            dbc.ModalFooter(
                dbc.Button("Fermer", id="close", className="ml-auto")
            ),

        ],
            id="modal",
            is_open=False,    # True, False
            size="xl",        # "sm", "lg", "xl"
            backdrop=False,    # True, False or Static for modal to not be closed by clicking on backdrop
            scrollable=True,  # False or True if modal has a lot of text
            centered=True,    # True, False
            fade=True         # True, False
        ),
    ]
)


### Testing here the alert feature:
alert = dbc.Alert("Attention, vos changements n'ont pas été enregistrés !", color="danger", dismissable = True)

#############


app.layout = html.Div([
    dbc.Card(
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.H1(children='Evaluation des candidatures EIG 5',
                    style = {'textAlign' : 'center'}
                )], width=9)
            ], justify='center')
        ]), color = 'light'),
            
    html.Br(),
    jobfilters,
    html.Br(),  
    dbc.Card(
        dbc.CardBody([
            dbc.Row([
                
                dbc.Col([
                    html.H5(
                        "Candidature de .......", 
                        className="card-title"
                        ),
                    html.P("Draws fields from SQL for a given candidate"),
                    dbc.Button(
                        "Sélectionner une autre candidature",
                        id = "next-candidate",
                        color="primary"
                        ),
                        modal,
                ], width=5, align='left'),
                # dbc.Col([
                #     html.H3(
                #         children='Evaluation'
                #         ),
                    
                #     dcc.Markdown(
                #         '''
                #         Pour compléter votre évaluation de la candidature, veuillez remplir chacun des champs ci-dessous.

                #         La grille d'évaluation complète est disponible **ici**, n'hésitez pas à la consulter !'''
                #     ),

                #     html.Br(),

                #     #html.Div(id="the_alert", children=[]),

                #     dcc.Markdown(
                #         "**Compétences techniques** *(compétences métier et clarté dans la communication, degré d'expérience...)*"
                #     ),

                #     dbc.InputGroup(
                #         [
                #             dbc.InputGroupAddon("Compétences techniques", addon_type="prepend"),
                #             dbc.Textarea(),
                #         ],
                #         className="mb-3",
                #         id="competences-techniques-appreciation"
                #     ),
                    
                #     dbc.Row([
                #         dbc.Col([
                #             dbc.Label(  
                #                 "Score (1 = non qualifié, 5 = expert) :"
                #             )], align='left'),
                        
                #         dbc.Col([
                #             dcc.RadioItems(
                #                 id = 'competences-techniques-score',
                #                 options=[
                #                     {'label': '1', 'value': '1'},
                #                     {'label': '2', 'value': '2'},
                #                     {'label': '3', 'value': '3'},
                #                     {'label': '4', 'value': '4'},
                #                     {'label': '5', 'value': '5'}
                #                 ],
                #                 inputStyle={"margin-right": "10px", "margin-left": "10px"},
                #                 labelStyle={'display': 'inline-block'}
                #             )]),
                #     ]),
                    
                #     dcc.Markdown(
                #         "**Capacité à travailler en équipe-projet au sein d’un environnement administratif** *(mener un projet de bout en bout, travailler en équipe interdisciplinaire, s'adapter à la culture de l'administration d'accueil...)*"
                #     ),

                #     dbc.InputGroup(
                #         [
                #             dbc.InputGroupAddon("Travail d'équipe", addon_type="prepend"),
                #             dbc.Textarea(),
                #         ],
                #         className="mb-3",
                #         id="travail-equipe-appreciation"
                #     ),

                #     dbc.Row([
                #         dbc.Col([
                #             dbc.Label(  
                #                 "Score (1 = non qualifié, 5 = expert) :"
                #             )], align='left'),
                        
                #         dbc.Col([
                #             dcc.RadioItems(
                #                 id = 'travail-equipe-score',
                #                 options=[
                #                     {'label': '1', 'value': '1'},
                #                     {'label': '2', 'value': '2'},
                #                     {'label': '3', 'value': '3'},
                #                     {'label': '4', 'value': '4'},
                #                     {'label': '5', 'value': '5'}
                #                 ],
                #                 inputStyle={"margin-right": "10px", "margin-left": "10px"},
                #                 labelStyle={'display': 'inline-block'}
                #             )]),
                #     ]),
                    
                #     dcc.Markdown(
                #         "**Esprit EIG ** *(engagement pour l'intérêt général, motivation, apport souhaité auprès de la communauté...)*"
                #     ),

                #     dbc.InputGroup(
                #         [
                #             dbc.InputGroupAddon("Esprit EIG", addon_type="prepend"),
                #             dbc.Textarea(),
                #         ],
                #         className="mb-3",
                #         id="esprit-eig-appreciation"
                #     ),
                    
                #     dbc.Row([
                #         dbc.Col([
                #             dbc.Label(  
                #                 "Score (1 = non qualifié, 5 = expert) :"
                #             )], align='left'),
                        
                #         dbc.Col([
                #             dcc.RadioItems(
                #                 id = 'esprit-eig-score',
                #                 options=[
                #                     {'label': '1', 'value': '1'},
                #                     {'label': '2', 'value': '2'},
                #                     {'label': '3', 'value': '3'},
                #                     {'label': '4', 'value': '4'},
                #                     {'label': '5', 'value': '5'}
                #                 ],
                #                 inputStyle={"margin-right": "10px", "margin-left": "10px"},
                #                 labelStyle={'display': 'inline-block'}
                #             )]),
                #     ]),
                    
                #     dcc.Markdown(
                #         "**Impression générale** *(Points forts et points faibles de la candidature)*"
                #     ),

                #     dbc.InputGroup(
                #         [
                #             dbc.InputGroupAddon("Impression générale", addon_type="prepend"),
                #             dbc.Textarea(),
                #         ],
                #         className="mb-3",
                #     ),
                    
                #     dcc.Markdown(
                #         "**Coup de coeur ?** *(Cochez cette case si cette candidature vous impressionne)*"
                #     ),
                    
                #     dcc.Checklist(
                #         id="coup-de-coeur", 
                #         options=[
                #             {'label': 'Coup de coeur', 'value': '1'}
                #         ],
                #         inputStyle={"margin-right": "10px", "margin-left": "10px"}
                #         ),
                    
                #     dcc.Markdown(
                #         "**Priorisation de la candidature :**"
                #     ),

                #     dcc.RadioItems(
                #         id = 'priorite-candidature',
                #         options=[
                #             {'label': 'Profils prioritaires', 'value': '1'},
                #             {'label': 'Profils satisfaisants', 'value': '2'},
                #             {'label': 'Profils non recommandés', 'value': '3'}
                #         ],
                #         inputStyle={"margin-right": "10px", "margin-left": "10px"},
                #         labelStyle={'display': 'inline-block'}
                #         ),
                    
                #     dcc.Markdown(
                #         "**Statut de la candidature :** "
                #     ),

                #     dcc.RadioItems(
                #         id = 'statut-candidature',
                #         options=[
                #             {'label': 'Admissible au jury', 'value': '1'},
                #             {'label': 'En cours de discussion', 'value': '2'},
                #             {'label': 'Non retenu', 'value': '3'}
                #         ],
                #         inputStyle={"margin-right": "10px", "margin-left": "10px"},
                #         labelStyle={'display': 'inline-block'}
                #         ),
                    
                #     dcc.Markdown(
                #         "**Communication / Echanges en cours :**"
                #     ),

                #     dcc.RadioItems(
                #         id = 'communication-candidature',
                #         options=[
                #             {'label': 'Invitation aux jurys envoyée', 'value': '1'},
                #             {'label': 'Mail de refus envoyé', 'value': '2'},
                #             {'label': 'Réponse à faire', 'value': '3'}
                #         ],
                #         inputStyle={"margin-right": "10px", "margin-left": "10px"},
                #         labelStyle={'display': 'inline-block'}
                #         ) 
                # ], width=7),
            ], align='right'), 
            
            html.Br(),
            
            dbc.Row([
                dbc.Col([
                    dash_table.DataTable(
                        id='data-table',
                        columns=[{"name": i, "id": i} for i in df2.columns],
                        data=df2.to_dict('records'),
                        style_table={
                            'width': '100%',
                            'minWidth': '100%',
                            },
                        page_size=PAGE_SIZE,
                        filter_action="native",
                        sort_action="native",
                        sort_mode="multi"
                        ),
                ], width=12),
                dbc.Col([
                    dcc.Graph(figure=fig)
                ], width=12),
            ], justify='center'),      
        ]), color = 'light'
    )
])



#################





### testing a callback that pops the Alert when Next candidate button is clicked
# @app.callback(
#     Output("the_alert", "children"),
#     [Input("next-candidate", "n-clicks")]
# )
# def send_alert(n):
#     if n:
#         return alert
#     return not alert




if __name__ == '__main__':
    app.run_server(debug=True)