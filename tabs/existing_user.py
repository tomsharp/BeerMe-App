import dash
import dash_core_components as dcc
import dash_html_components as html 
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import pickle
import numpy as np

from app import app
from util import *

layout = html.Div(className = 'row', children =[

    dcc.Store(id="session", storage_type='session',
                data=beer_options()
            ),
    
    # username section
    html.Div(className='container-outlined padded', style={'background':'white'}, children=[
        html.H3("Let's Build a Model", style={'font-weight': 'bold', 'margin':'0'}),
        html.Div(className='container', children=[
            html.H4("Select Your Username"),
            dcc.Dropdown(
                id = 'username-selection-dropdown-exisiting-user',
                options=username_options(),
                multi = False
            ),
            html.H4("Select Your Technique"),
                dcc.Dropdown(
                    id='technique-dropdown',
                    options=[
                        {'label': 'Content Based Filtering', 'value': 'cbf'},
                        {'label': 'Collaborative Filtering', 'value': 'collab-filt'},
                        {'label': 'Hybrid', 'value': 'hybrid'}
                    ],
                    value='cbf'
                ), 

            html.Div(id='model-setup'),

        ]),
    
    ]),

    html.Div(id='explanation-container', className='container-outlined padded', style={'margin-top':'50px', 'background':'white'}, children=[
        html.H3("Using the Model we just Built", style={'font-weight': 'bold', 'margin':'0'}),
        # html.Button('Yup!', id='select-model-button', className=''),
        html.Div(id='select-model-radio', children=[
            html.Div(className='container', children=[
            html.H5("""How do you want to put that model to work? It can be used to rate a specific beer you're interested in,
                            rank a list of beers that you're trying to choose between, or we can just suggest a brand new beer 
                            that you may never even heard of!"""),
                dcc.Dropdown(
                        id='model-use-dropdown',
                        options=[
                            {'label': 'Rate a Beer', 'value': 'rate'},
                            {'label': 'Rank some Beers', 'value': 'rank'},
                            {'label': 'Suggest a Beer', 'value': 'suggest'}
                        ],
                        value='rate',
                        style={'width':'300px'}
                ), 
                html.Button('Let\'s do this', id='popup-cards-button', className='btn btn-outline-dark'),
            ]),
        ]),
    ]),

    html.Div(id='model-use-section', style={'margin-top':'50px'}),

])
# end container





# Callbacks
@app.callback(Output('beer-loader-exisiting-user', 'style'),
                [Input('search-button-exisiting-user', 'n_clicks')],
                [State('beer-selection-dropdown-exisiting-user', 'value')])
def display_beer_loader(n_clicks, value):
    if value != None:
        if len(value) == 1:
            return {'display': 'none'}
    elif n_clicks != None and value != None and value != []:
        return {'display': 'block'}
    else:
        return {'display': 'none'}


@app.callback(Output('model-setup', 'children'),
                [Input('technique-dropdown', 'value')])
def technique_options(value):
        if value == 'cbf':
            return html.Div([
                # feature selection
                html.Div(className='col-lg-5', children=[
                        html.H4("Select Which Feature Selection You'd Like to Use"),
                        dcc.Dropdown(
                            id = 'feature-selection-dropdown-exisiting-user',
                            options = [{'label': 'Simple', 'value': 'simple'},
                                        {'label': 'Categorical Encoding of Beer Description', 'value': 'cat-encoding'},
                                        {'label': 'Count Vectorizer of Beer Description', 'value': 'count-vect'},
                                        {'label': 'TFIDF Vectorizer of Beer Description', 'value': 'tfidf-vect'}],
                            multi = False
                        )
                ]),
                # alg selection
                html.Div(className='col-lg-5', children=[
                        html.H4("Select Which Model You'd Like to Use"),
                        dcc.Dropdown(
                            id = 'model-selection-dropdown-exisiting-user',
                            options = [{'label': 'Lasso', 'value': 'Lasso'},
                                        {'label': 'Ridge', 'value': 'Ridge'},
                                        {'label': 'ElasticNet', 'value': 'ElasticNet'}],
                            multi = False
                        )
                ]),

                html.Div(className='row', children=[
                    html.Button('Build Model', id='model-button-exisiting-user', className='btn btn-outline-dark'),
                    dcc.Loading(id="loading-model", children=[html.Div(id="loading-model-output")], type="default"),
                ]),
                html.Div(className='row', children=[
                    html.Div(id='model-results-exisiting-user'),
                    html.Div(id='dummy-div')
                ])
            ])

        elif value == 'hybrid':
            return html.Div([
                # feature selection
                html.Div(className='col-lg-5', children=[
                        html.H4("Select Which Feature Selection You'd Like to Use"),
                        dcc.Dropdown(
                            id = 'feature-selection-dropdown-exisiting-user',
                            options = [{'label': 'Simple', 'value': 'simple'},
                                        {'label': 'Categorical Encoding of Beer Description', 'value': 'cat-encoding'},
                                        {'label': 'Count Vectorizer of Beer Description', 'value': 'count-vect'},
                                        {'label': 'TFIDF Vectorizer of Beer Description', 'value': 'tfidf-vect'}],
                            multi = False
                        )
                ]),
                # alg selection
                html.Div(className='col-lg-5', children=[
                        html.H4("Select Which Model You'd Like to Use"),
                        dcc.Dropdown(
                            id = 'model-selection-dropdown-exisiting-user',
                            options = [{'label': 'Lasso', 'value': 'Lasso'}],
                            multi = False
                        )
                ]),

                html.Div(className='row', children=[
                    html.Button('Build Model', id='model-button-exisiting-user', className='btn btn-outline-dark'),
                    dcc.Loading(id="loading-model", children=[html.Div(id="loading-model-output")], type="default"),
                ]),
                html.Div(className='row', children=[
                    html.Div(id='model-results-exisiting-user')
                ])
            ])

        else:
            return html.Div([
                # feature selection
                html.Div(className='col-lg-5', children=[
                        html.H4("Select Which Feature Selection You'd Like to Use"),
                        dcc.Dropdown(
                            id = 'feature-selection-dropdown-exisiting-user',
                            options = [{'label': 'NA', 'value': 'NA'}],
                            multi = False
                        )
                ]),
                # alg selection
                html.Div(className='col-lg-5', children=[
                        html.H4("Select Which Model You'd Like to Use"),
                        dcc.Dropdown(
                            id = 'model-selection-dropdown-exisiting-user',
                            options = [{'label': 'NA', 'value': 'NA'}],
                            multi = False
                        )
                ]),
                html.Div(className='row', children=[
                    html.Button('Build Model', id='model-button-exisiting-user', className='btn btn-outline-dark'),
                    dcc.Loading(id="loading-model", children=[html.Div(id="loading-model-output")], type="default"),
                ]),
                html.Div(className='row', children=[
                    html.Div(id='model-results-exisiting-user')
                ])
            ])

# @app.callback(Output('dummy-div', 'children'),
#                 [Input('model-button-exisiting-user', 'n_clicks'),
#                 Input('technique-dropdown', 'value'),
#                 Input('username-selection-dropdown-exisiting-user', 'value')])
# def build_model(n_clicks, technique, user_of_interest):
    
#     print(technique)
    
#     if technique == 'cf':
#         print("...")
#         query = "SELECT user_rating, beer_name, username FROM prepped_data"
#         df = import_table(db_path, query, remove_dups=False)
#         mae, quarter, half = collaborative_filtering(df, user_of_interest)
#         print("HEEERRREE")
        
#         # structure html and return 
#         children = [html.Div("We have created a predictive model based on your taste preferences".format(quarter, half, mae),
#                             style={'font-size':'large', 'font-weight':'bold'}),
#                     html.Br(),
#                     html.Div("Full analysis below:", style={'text-align':'center', 'font-weight':'bold'}),
#                     html.Div("Accuracy within 0.25 stars: {:.2f}%".format(quarter), style={'text-align':'center', 'font-size':'small'}),
#                     html.Div("Accuracy within 0.50 stars: {:.2f}%".format(half), style={'text-align':'center', 'font-size':'small'}),
#                     html.Div("Mean Absolute Error (MAE): {:.2f}".format(mae), style={'text-align':'center', 'font-size':'small'})]
#         ret_html = html.Div(children=children)
#         print(ret_html)
#         return ret_html

@app.callback(Output('model-results-exisiting-user', 'children'),
                [Input('model-button-exisiting-user', 'n_clicks')],
                [State('username-selection-dropdown-exisiting-user', 'value'),
                 State('technique-dropdown', 'value'),
                 State('feature-selection-dropdown-exisiting-user', 'value'),
                 State('model-selection-dropdown-exisiting-user', 'value')])
def build_model(n_clicks, user_of_interest, technique, feature_selection, alg):

    if n_clicks != None:

        print(technique)
        
        if technique == 'cbf':
        
            # feature prep
            if feature_selection == 'simple':
                df = import_table(db_path, query = "SELECT username, beer_description, ABV, IBU, global_rating, user_rating FROM prepped_data WHERE username = '{}'".format(user_of_interest))
                user_df = df[df['username']==user_of_interest].drop(['username', 'beer_description'], axis=1, inplace=False)
            elif feature_selection == 'cat-encoding':
                df = import_table(db_path, query = "SELECT username, beer_description, ABV, IBU, global_rating, user_rating FROM prepped_data")
                df = cat_encoding(df, 'beer_description')
                user_df = df[df['username'] == user_of_interest]
                user_df.drop(['username'], axis=1, inplace=True)
            elif feature_selection == 'count-vect':
                df = import_table(db_path, query = "SELECT username, beer_description, ABV, IBU, global_rating, user_rating FROM prepped_data")
                df = count_vectorizer(df, 'beer_description')
                user_df = df[df['username'] == user_of_interest]
                user_df.drop(['username'], axis=1, inplace=True)
            elif feature_selection == 'tfidf-vect':
                df = import_table(db_path, query = "SELECT username, beer_description, ABV, IBU, global_rating, user_rating FROM prepped_data")
                df = tfidf_vectorizer(df, 'beer_description')
                user_df = df[df['username'] == user_of_interest]
                user_df.drop(['username'], axis=1, inplace=True)

            model, best_params, mae, quarter, half = cbf(user_df, alg, 'user_rating', impute_na_mean=True, remove_all_outliers=True)

            d={}
            d['model'] = model
            d['feature_selection'] = feature_selection

            with open('exisiting-user-model.pkl', 'wb') as file:
                pickle.dump(d, file)
            
            # structure html and return 
            children = [html.Div("We have created a predictive model based on your taste preferences".format(quarter, half, mae),
                                style={'font-size':'large', 'font-weight':'bold'}),
                        html.Br(),
                        html.Div("Full analysis below:", style={'text-align':'center', 'font-weight':'bold'}),
                        html.Div("Accuracy within 0.25 stars: {:.2f}%".format(quarter), style={'text-align':'center', 'font-size':'small'}),
                        html.Div("Accuracy within 0.50 stars: {:.2f}%".format(half), style={'text-align':'center', 'font-size':'small'}),
                        html.Div("Mean Absolute Error (MAE): {:.2f}".format(mae), style={'text-align':'center', 'font-size':'small'}),
                        html.Div("Best Parameters: {}".format(best_params), style={'text-align':'center', 'font-size':'small'})]
            ret_html = html.Div(children=children)

        elif technique=='collab-filt':
            print("HERE")
            query = "SELECT user_rating, beer_name, username FROM prepped_data"
            df = import_table(db_path, query, remove_dups=False)
            mae, quarter, half = collaborative_filtering(df, user_of_interest)
            print("HEEERRREE")
            
            # structure html and return 
            children = [html.Div("We have created a predictive model based on your taste preferences".format(quarter, half, mae),
                                style={'font-size':'large', 'font-weight':'bold'}),
                        html.Br(),
                        html.Div("Full analysis below:", style={'text-align':'center', 'font-weight':'bold'}),
                        html.Div("Accuracy within 0.25 stars: {:.2f}%".format(quarter), style={'text-align':'center', 'font-size':'small'}),
                        html.Div("Accuracy within 0.50 stars: {:.2f}%".format(half), style={'text-align':'center', 'font-size':'small'}),
                        html.Div("Mean Absolute Error (MAE): {:.2f}".format(mae), style={'text-align':'center', 'font-size':'small'})]
            ret_html = html.Div(children=children)

        else:
            df = import_table(db_path, query = "SELECT username, beer_name, beer_description, ABV, IBU, global_rating, user_rating FROM prepped_data")
    
            # feature prep
            if feature_selection == 'simple':
                hybrid_df = df.drop(['beer_description'], axis=1, inplace=False)
            
            elif feature_selection == 'cat-encoding':
                df = import_table(db_path, query = "SELECT username, user_rating, beer_name, beer_description, ABV, IBU, global_rating FROM prepped_data")
                hybrid_df = cat_encoding(df, 'beer_description')
            elif feature_selection == 'count-vect':
                df = import_table(db_path, query = "SELECT username, user_rating, beer_name, beer_description, ABV, IBU, global_rating FROM prepped_data")
                hybrid_df = count_vectorizer(df, 'beer_description')
            elif feature_selection == 'tfidf-vect':
                df = import_table(db_path, query = "SELECT username, user_rating, beer_name, beer_description, ABV, IBU, global_rating FROM prepped_data")
                hybrid_df = count_vectorizer(df, 'beer_description')

            model_list, mae_list, quarter_list, half_list = run_hybrid(hybrid_df, user_of_interest, 'user_rating')

            mae = min(i for i in mae_list if i > 0)
            ind = mae_list.index(mae)

            model = model_list[ind]
            quarter = quarter_list[ind]
            half = half_list[ind]

            d={}
            d['model'] = model
            d['feature_selection'] = feature_selection

            with open('hybrid-model.pkl', 'wb') as file:
                pickle.dump(d, file)

            # structure html and return 
            children = [html.Div("We have created a predictive model based on your taste preferences".format(quarter, half, mae),
                                style={'font-size':'large', 'font-weight':'bold'}),
                        html.Br(),
                        html.Div("Full analysis below:", style={'text-align':'center', 'font-weight':'bold'}),
                        html.Div("Accuracy within 0.25 stars: {:.2f}%".format(quarter), style={'text-align':'center', 'font-size':'small'}),
                        html.Div("Accuracy within 0.50 stars: {:.2f}%".format(half), style={'text-align':'center', 'font-size':'small'}),
                        html.Div("Mean Absolute Error (MAE): {:.2f}".format(mae), style={'text-align':'center', 'font-size':'small'})]
            ret_html = html.Div(children=children)
        
        return ret_html

@app.callback(Output('explanation-container', 'style'),
                [Input('model-results-exisiting-user', 'children')])
def display_explanation_container(children):
    if children != None:
        return {'margin-top':'50px', 'background':'white', 'display': 'block'}
    else:
        return {'margin-top':'50px', 'background':'white', 'display': 'none'}

@app.callback(Output('prediction-results-exisiting-user', 'children'),
                [Input('prediction-button-exisiting-user', 'n_clicks')],
                [State('beer-selection-dropdown-exisiting-user', 'value')])
def predict_beer_rating(n_clicks, beer):

    if n_clicks != None:
        with open('exisiting-user-model.pkl', 'rb') as file:
            d = pickle.load(file)
            model = d['model']
            feature_selection = d['feature_selection']
    
    
        if feature_selection == 'simple':
            query = "SELECT ABV, IBU, global_rating FROM prepped_data WHERE beer_name = '{}'".format(beer)
            beer_df = import_table(db_path, query, remove_dups=False)
            beer_df['global_rating'] = beer_df['global_rating'].mean()
            beer_df = beer_df[~beer_df.duplicated()]
            prediction = model.predict(beer_df)

        elif feature_selection == 'cat-encoding':
            df = import_table(db_path, query = "SELECT beer_name, beer_description, ABV, IBU, global_rating FROM prepped_data")
            df = cat_encoding(df, 'beer_description')
            beer_df = df[df['beer_name']==beer].drop('beer_name', axis=1)
            beer_df['global_rating'] = beer_df['global_rating'].mean()
            beer_df = beer_df[~beer_df.duplicated()]
            prediction = model.predict(beer_df)

        elif feature_selection == 'count-vect':
            df = import_table(db_path, query = "SELECT beer_name, beer_description, ABV, IBU, global_rating FROM prepped_data")
            df = count_vectorizer(df, 'beer_description')
            beer_df = df[df['beer_name']==beer].drop('beer_name', axis=1)
            beer_df['global_rating'] = beer_df['global_rating'].mean()
            beer_df = beer_df[~beer_df.duplicated()]
            prediction = model.predict(beer_df)
           
        elif feature_selection == 'tfidf-vect':
            df = import_table(db_path, query = "SELECT beer_name, beer_description, ABV, IBU, global_rating FROM prepped_data")
            df = tfidf_vectorizer(df, 'beer_description')
            beer_df = df[df['beer_name']==beer].drop('beer_name', axis=1)
            beer_df['global_rating'] = beer_df['global_rating'].mean()
            beer_df = beer_df[~beer_df.duplicated()]
            prediction = model.predict(beer_df)
            if prediction > 5.0:
                prediction = 5.0
            elif prediction < 0.0:
                prediction = 0.0
        
        ret_html = html.Div("We predict that your rating for this beer will be {:.2f}".format(prediction[0]),
                             style={'font-size':'large', 'font-weight':'bold'})
        return ret_html


@app.callback(Output('ranking-results-exisiting-user', 'children'),
                [Input('ranking-button-exisiting-user', 'n_clicks')],
                [State('ranking-beer-selection-dropdown-exisiting-user', 'value')])
def rank_beers(n_clicks, beers):

    if n_clicks != None:
        with open('exisiting-user-model.pkl', 'rb') as file:
            d = pickle.load(file)
            model = d['model']
            feature_selection = d['feature_selection']
    
    
        drop_cols =['username', 'beer_name', 'brewery']
        if feature_selection == 'simple':
            query = "SELECT beer_name, ABV, IBU, global_rating FROM prepped_data WHERE beer_name in {}".format(tuple(beers))
            beer_df = import_table(db_path, query, remove_dups=False)

            beer_df['global_rating'] = beer_df.groupby("beer_name").transform(lambda x: x.fillna(x.mean()))['global_rating']
            beer_df = beer_df[~beer_df.duplicated('beer_name')]
            
            predictions = model.predict(beer_df.drop('beer_name', axis=1))
            beer_df['predictions'] = predictions

        elif feature_selection == 'cat-encoding':
            df = import_table(db_path, query = "SELECT beer_name, beer_description, ABV, IBU, global_rating FROM prepped_data")
            df = cat_encoding(df, 'beer_description')

            beer_df = df[df['beer_name'].isin(beers)]
            beer_df['global_rating'] = beer_df['global_rating'].mean()
            beer_df = beer_df[~beer_df.duplicated()]

            predictions = model.predict(beer_df.drop('beer_name', axis=1))
            beer_df['predictions'] = predictions

        elif feature_selection == 'count-vect':
            df = import_table(db_path, query = "SELECT beer_name, beer_description, ABV, IBU, global_rating FROM prepped_data")
            df = count_vectorizer(df, 'beer_description')

            beer_df = df[df['beer_name'].isin(beers)]
            beer_df['global_rating'] = beer_df['global_rating'].mean()
            beer_df = beer_df[~beer_df.duplicated()]

            predictions = model.predict(beer_df.drop('beer_name', axis=1))
            beer_df['predictions'] = predictions
           
        elif feature_selection == 'tfidf-vect':
            df = import_table(db_path, query = "SELECT beer_name, beer_description, ABV, IBU, global_rating FROM prepped_data")
            df = tfidf_vectorizer(df, 'beer_description')

            beer_df = df[df['beer_name'].isin(beers)]
            beer_df['global_rating'] = beer_df['global_rating'].mean()
            beer_df = beer_df[~beer_df.duplicated()]

            predictions = model.predict(beer_df.drop('beer_name', axis=1))
            for prediction in predictions:
                if prediction > 5.0:
                    prediction = 5.0
                elif prediction < 0.0:
                    prediction = 0.0
            beer_df['predictions'] = predictions

        beer_df.sort_values('predictions', inplace=True, ascending=False)
        top_beer = beer_df.iloc[0,0]
        
        random_responses = ["Our best guess is you're gonna love {}!", 
                            "Forget the other options, {} should be your next one!"]
        rand_ind = np.random.randint(0,len(random_responses))

        children = [html.Div(random_responses[rand_ind].format(str(top_beer)), style={'font-size':'large', 'font-weight':'bold'}), 
                    html.Br(),
                    html.Div("Full analysis below: ", style={'text-align':'center', 'font-weight':'bold'})]
        for beer in beer_df['beer_name']:
            child = html.Div("{} predicted rating: {:.2f}".format(beer, float(beer_df[beer_df['beer_name']==beer]['predictions'])), style={'text-align':'center', 'font-size':'small'})
            children.append(child)

        ret_html = html.Div(children=children)
        return ret_html

@app.callback(Output('suggestion-results-exisiting-user', 'children'),
                [Input('suggestion-button-exisiting-user', 'n_clicks')])
def suggest_beers(n_clicks):

     if n_clicks != None:
        with open('exisiting-user-model.pkl', 'rb') as file:
            d = pickle.load(file)
            model = d['model']
            feature_selection = d['feature_selection']
    
    
        if feature_selection == 'simple':
            query = "SELECT beer_name, ABV, IBU, global_rating FROM prepped_data"
            beer_df = import_table(db_path, query, remove_dups=False)
            beer_df = beer_df.groupby('beer_name').mean().reset_index()
            beer_df = beer_df[~beer_df.duplicated()]
            beer_list = beer_df['beer_name']
            beer_df.drop('beer_name', axis=1, inplace=True)
            predictions = model.predict(beer_df)

        elif feature_selection == 'cat-encoding':
            df = import_table(db_path, query = "SELECT beer_name, beer_description, ABV, IBU, global_rating FROM prepped_data")
            descriptions = df[['beer_name', 'beer_description']]
            df = df.groupby('beer_name').mean().reset_index()
            df = pd.merge(df, descriptions, on='beer_name')
            beer_df = cat_encoding(df, 'beer_description')
            beer_list = beer_df['beer_name']
            beer_df = beer_df.drop('beer_name', axis=1)
            beer_df = beer_df[~beer_df.duplicated()]
            predictions = model.predict(beer_df)

        elif feature_selection == 'count-vect':
            df = import_table(db_path, query = "SELECT beer_name, beer_description, ABV, IBU, global_rating FROM prepped_data")
            df = count_vectorizer(df, 'beer_description')
            beer_df = df.groupby('beer_name').mean().reset_index()
            beer_list = beer_df['beer_name']
            beer_df = beer_df.drop('beer_name', axis=1)
            beer_df = beer_df[~beer_df.duplicated()]
            predictions = model.predict(beer_df)
           
        elif feature_selection == 'tfidf-vect':
            df = import_table(db_path, query = "SELECT beer_name, beer_description, ABV, IBU, global_rating FROM prepped_data")
            df = tfidf_vectorizer(df, 'beer_description')
            beer_df = df.groupby('beer_name').mean().reset_index()
            beer_list = beer_df['beer_name']
            beer_df = beer_df.drop('beer_name', axis=1)
            beer_df = beer_df[~beer_df.duplicated()]
            predictions = model.predict(beer_df)

        beer_df['predictions'] = predictions
        beer_df['beer_name'] = beer_list
        if len(beer_df) > 10:
            beer_df = beer_df.sort_values('predictions').iloc[0:10]
        else:
            pass

        ind = np.random.randint(0, len(beer_df))
        prediction = beer_df.iloc[ind,]['predictions']
        if prediction > 5.0:
            prediction = 5.0
        elif prediction < 0.0:
            prediction = 0.0
        beer_name = beer_df.iloc[ind,]['beer_name']

        ret_html = html.Div("We think your next one should be {} (rating = {:.2f})".format(beer_name, prediction),
                             style={'font-size':'large', 'font-weight':'bold'})
        return ret_html


# @app.callback(Output('select-model-radio', 'children'),
#                 [Input('select-model-button', 'n_clicks')])
# def show_model_radio(n_clicks):
#     if n_clicks != None:
#         return html.Div(className='container', children=[
#             html.H5("""How do you want to put that model to work? It can be used to rate a specific beer you're interested in,
#                         rank a list of beers that you're trying to choose between, or we can just suggest a brand new beer 
#                         that you may never even heard of!"""),
#             dcc.Dropdown(
#                     id='model-use-dropdown',
#                     options=[
#                         {'label': 'Rate a Beer', 'value': 'rate'},
#                         {'label': 'Rank some Beers', 'value': 'rank'},
#                         {'label': 'Suggest a Beer', 'value': 'suggest'}
#                     ],
#                     value='rate',
#                     style={'width':'300px'}
#             ), 
#             html.Button('Let\'s do this', id='popup-cards-button', className=''),
#         ])


@app.callback(Output('model-use-section', 'children'),
                [Input('popup-cards-button', 'n_clicks')],
                [State('model-use-dropdown', 'value'),
                State('session', 'data')])
def show_selected_card(n_clicks, value, data):
    if n_clicks != None:

        if value == 'rate':
            # prediciton section
            return html.Div(className='container-outlined padded', style={'background':'white'}, children = [
                html.H2("Rate A Beer", style={'font-weight': 'bold', 'margin':'0'}),
                html.Div(className='container', children=[
                    html.H6([
                            """
                            Select a beer and our algorithm will predict your rating!
                            """
                    ]),
                    html.Div(className='row', children=[
                        html.Div(className='col-lg-5 m-4', children=[
                            dcc.Dropdown(
                                id = 'beer-selection-dropdown-exisiting-user',
                                options = data,
                                multi = False,
                                style={'width':'500px'}
                            )
                        ]),
                    ]),
                    html.Div(className='row', children=[
                        html.Button('Predict', id='prediction-button-exisiting-user', className='btn btn-warning', style={'width':'10rem'})
                    ]),
                    html.Div(className='row', children=[
                        html.Div(id='prediction-results-exisiting-user', style={'text-align':'center'}),
                    ]),
                ]),
            ])
        
        elif value == 'rank':
            # ranking section
            return html.Div(className='container-outlined padded', style={'background':'white'}, children = [
                    html.H2("Rank My Beers", style={'font-weight': 'bold', 'margin':'0'}),
                    html.Div(className='container', children=[
                        html.H6(className='', children = [
                                """
                                Select a few beers and will tell you which one you'll like best!
                                """
                        ]),
                        html.Div(className='row', children=[
                            html.Div(className='col-lg-5 m-4', children=[
                                dcc.Dropdown(
                                    id = 'ranking-beer-selection-dropdown-exisiting-user',
                                    options = data,
                                    multi = True,
                                    # style={'width':'500px'}
                                )
                            ]),
                        ]),
                        html.Div(className='row', children=[
                            html.Button('Rank', id='ranking-button-exisiting-user', className='btn btn-warning', style={'width':'10rem'})
                        ]),
                        html.Div(className='row', children=[
                            html.Div(id='ranking-results-exisiting-user', style={'text-align':'center'}),
                        ]),
                    ]),
                ]),

        elif value == 'suggest':
            # suggestion section
            return html.Div(className='container-outlined padded', style={'background':'white'}, children = [
                    html.H2("Suggest a Beer", style={'font-weight': 'bold', 'margin':'0'}),
                    html.Div(className='container', children=[
                        html.H6(
                                """
                                Let us suggest a new beer for you!
                                """
                        ),
                        html.Div(className='row', children=[
                            html.Button('Suggest', id='suggestion-button-exisiting-user', className='btn btn-warning', style={'width':'10rem'})
                        ]),
                        html.Div(className='row', children=[
                            html.Div(id='suggestion-results-exisiting-user', style={'text-align':'center'}),
                        ]),
                    ]),
                ])
