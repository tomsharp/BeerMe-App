import pandas as pd
import sqlite3
import json

db_path = 'data/beer.db'

def username_options(database_path=db_path):

    query = "SELECT DISTINCT username FROM prepped_data ORDER BY username"
    
    with sqlite3.connect(database_path) as conn:
        usernames = list(pd.read_sql(query, conn)['username'])

    username_options = [{'label': username, 'value': username} for username in usernames]

    return username_options


def beer_options(database_path=db_path):
    query = "SELECT DISTINCT beer_name FROM prepped_data ORDER BY beer_name"
    with sqlite3.connect(database_path) as conn:
        beers = list(pd.read_sql(query,conn)['beer_name'])
    beer_options = [{'label': beer, 'value': beer} for beer in beers]
    return beer_options



# @TODO - replace 

# # Pipeline
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sqlite3
from sklearn.preprocessing import StandardScaler
from functools import reduce

def pipeline_func(data, fns):
    return reduce(lambda a, x: x(a), fns, data)


#############################################   
# 1. Import, Clean, EDA
#############################################     

# @TODO - rename this function
def import_table(db_path, 
                 query = "SELECT * FROM user_extract",
                 remove_dups=True):
    
    conn = sqlite3.connect(db_path)
    df = pd.read_sql(query, conn)
    
    if remove_dups==True:
        df = df[~df.duplicated()]
    
    return(df)

def remove_outliers(df, features):
    for feature in features:
        q1 = df[feature].quantile(.25)
        q3 = df[feature].quantile(.75)
        iqr = q3 - q1
        non_outlier_mask = (df[feature] >= q1 - 1.5*iqr) & (df[feature] <= q3 + 1.5*iqr)
        df = df[non_outlier_mask]
    return df  

def outlier_analysis(df, features, outlier_threshold=2.5):
   
    print('\n')
    print("1. NA Count...")
    print(df.loc[:,features].isna().sum())
    
    print('\n')
    print('2. Finding IQR outliers...')
    features_to_remove = []
    for feature in features:
        try:
            q1 = df[feature].quantile(.25)
            q3 = df[feature].quantile(.75)
            iqr = q3 - q1
            non_outlier_mask = (df[feature] >= q1 - 1.5*iqr) & (df[feature] <= q3 + 1.5*iqr)
            outliers = df[~non_outlier_mask]
    
            print("FEATURE {}".format(feature))
            print("num of outliers = {:,d}".format(len(outliers)))
            print("% of outliers = {:.2f}%".format(100*len(outliers)/len(df)))

            # store feature for outlier removal if necessary
            if 100*len(outliers)/len(df) > outlier_threshold:
                features_to_remove += [feature]
            
        except TypeError:
            print("FEATURE {}".format(feature))
            print("ANALYZING ALL NON-NA VALUES")

            non_nas = df[~df[feature].isna()][feature].astype(float)
            q1 = non_nas.quantile(.25)
            q3 = non_nas.quantile(.75)
            iqr = q3 - q1
            non_outlier_mask = (non_nas >= q1 - 1.5*iqr) & (non_nas <= q3 + 1.5*iqr)
            outliers = non_nas[~non_outlier_mask]
            print("num of outliers = {:,d}".format(len(outliers)))
            print("% of outliers = {:.2f}%".format(100*len(outliers)/len(non_nas)))

            # store feature for outlier removal if necessary 
            if 100*len(outliers)/len(non_nas) > outlier_threshold:
                features_to_remove += [feature]

    # remove outliers 
    print("Removing outliers from the following features:", features_to_remove)
    df = remove_outliers(df, features_to_remove)

    return df


def impute_na(df, features, impute_method = 'mean'):

    for feature in features:
        if impute_method == 'mean':
            non_nas = df[~df[feature].isna()][feature].astype(float)
            feature_mean = non_nas.mean()
            df[feature] = df[feature].fillna(feature_mean)
        elif impute_method == 0:
            non_nas = df[~df[feature].isna()][feature].astype(float)
            df[feature] = df[feature].fillna(0)
    
    print("NA Count...")
    print(df.loc[:,features].isna().sum())
    
    return df
    

######################################################     
### 2. Cosine Similarity / Nearest Neighbors
######################################################     
def create_ui_matrix(df, fill_method=0):
    # Create User-Item Matrix 
    data = df
    values = 'user_rating'
    index = 'username'
    columns = 'beer_name'
    agg_func = 'mean'
    
    if fill_method == 'item_mean':
        ui_matrix = pd.pivot_table(data=data, values=values, index=index, 
                                   columns=columns, aggfunc=agg_func)
        ui_matrix = ui_matrix.fillna(ui_matrix.mean(axis=0), axis=0)
    
    elif fill_method == 'user_mean':
        ui_matrix = pd.pivot_table(data=data, values=values, index=index, 
                                   columns=columns, aggfunc=agg_func)
        ui_matrix.apply(lambda row: row.fillna(row.mean()), axis=1)
    
    elif fill_method == 0:
        ui_matrix = pd.pivot_table(data=data, values=values, index=index, 
                                   columns=columns, aggfunc=agg_func, fill_value=0)
    else:
        raise ValueError("Please checkout 'fill_method' value")
    
    ui_matrix.columns = list(ui_matrix.columns)
    
    return(ui_matrix)


# c. Calculate Cosine Similarity
def calculate_cosine_similarity(user_of_reference, ui_matrix):

    # Calculate Cosine Similarity 
    print("User of Reference for Cosine Sim = {}".format(user_of_reference))
    
    from sklearn.metrics.pairwise import cosine_similarity
    X = ui_matrix[ui_matrix.index == user_of_reference]
    Y = ui_matrix[ui_matrix.index != user_of_reference]
    
    sim = cosine_similarity(X,Y)[0].tolist()
    names = Y.index
    
    sim_df = pd.DataFrame({'username':names, 'sim_score':sim})
    sim_df = sim_df.sort_values(by='sim_score', ascending=False)
    
    return(sim_df)


def calculate_nearest_neighbors(sim_df):
    # add neighbor rank to df
    neighbor_rank = sim_df.reset_index(drop=True)
    neighbor_rank.index.name = 'nearest_neighbor_rank'
    neighbor_rank.reset_index(inplace=True)
    neighbor_rank['nearest_neighbor_rank'] = neighbor_rank['nearest_neighbor_rank'] + 1
    neighbor_rank = neighbor_rank[['nearest_neighbor_rank', 'username']]
    return(neighbor_rank)

def merge_nearest_neighobr_rank(df, neighbor_rank):    
    print(df.shape)
    df = pd.merge(neighbor_rank, df, on='username', how='outer')
    print(df.shape)
    
    return(df)


def COSINE_STEP(df, user_of_reference):
    ui_matrix = create_ui_matrix(df)
    sim_df = calculate_cosine_similarity(user_of_reference, ui_matrix)
    neighbor_rank = calculate_nearest_neighbors(sim_df)
    df = merge_nearest_neighobr_rank(df, neighbor_rank)
    return df
    
######################################################   
### 3. Scale / Standardize Data 
######################################################   
def transform_features_target(df, features, target):
    X_scaler = StandardScaler()
    X_scaler.fit(df[features])
    df[features] = X_scaler.transform(df[features])
    
    y_scaler = StandardScaler()
    y = np.array(df[target]).reshape(-1, 1 )
    y_scaler.fit(y)
    df[target] = y_scaler.transform(y)
    
    feature_scaler = X_scaler
    target_scaler = y_scaler 
    
    return(df, feature_scaler, target_scaler)


######################################################   
### Modeling
######################################################  
## feature selection
def cat_encoding(df, encoding_col):

    dummies = pd.get_dummies(df[encoding_col], drop_first=True, prefix=encoding_col)
    df = pd.merge(df, dummies, left_index=True, right_index=True)

    df.drop(encoding_col, axis=1, inplace=True)
    
    return df

def count_vectorizer(df, vectoring_col):

    from sklearn.feature_extraction.text import CountVectorizer
    vect = CountVectorizer()
    X = vect.fit_transform(df[vectoring_col])
    count_df = pd.DataFrame(X.toarray(), columns=vect.get_feature_names())
    df = pd.concat([df.reset_index(drop=True), count_df], axis=1)
    
    df.drop(vectoring_col, axis=1, inplace=True)
    
    return df

def tfidf_vectorizer(df, vectoring_col):
    
    from sklearn.feature_extraction.text import TfidfVectorizer
    vect = TfidfVectorizer()
    X = vect.fit_transform(df[vectoring_col])
    tfidf_df = pd.DataFrame(X.toarray(), columns=vect.get_feature_names())
    df = pd.concat([df.reset_index(drop=True), tfidf_df], axis=1)
    
    df.drop(vectoring_col, axis=1, inplace=True)
    
    return df

## models
# CBF 
def cbf(user_df, algorithm, target, impute_na_mean=False, remove_all_outliers=False, rand_state=12):
        
    features = list(user_df.columns[user_df.columns != target])
    print("LEN OF FEATURES", len(features))
    print("TOP FEATURES ", features[:10])
    print("TARGET ", target)
    
    # # impute nan with mean
    # if impute_na_mean == True:
    #     user_df = impute_na(user_df, features, impute_method='mean')
    # else:
    #     pass
    
    # remove outliers
    if remove_all_outliers == True:
        user_df = outlier_analysis(user_df, [target], outlier_threshold=0.0)
    else:
        pass
    
    # train test split
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(user_df[features], user_df[target], test_size=0.2, random_state=rand_state)
    
    # setup alg and param space for grid search 
    if algorithm == 'Lasso':
        from sklearn.linear_model import Lasso
        model = Lasso(fit_intercept=True, normalize=True, random_state=rand_state)
        param_space = {'alpha': np.linspace(0.01, 1.0)}
    
    elif algorithm == 'Ridge':
        from sklearn.linear_model import Ridge
        model = Ridge(fit_intercept=True, normalize=True, random_state=rand_state)
        param_space = {'alpha': np.linspace(0.01, 1.0)}
        
    elif algorithm == 'ElasticNet':
        from sklearn.linear_model import ElasticNet
        model = ElasticNet(fit_intercept=True, normalize=True, random_state=rand_state)
        param_space = {'alpha': np.linspace(0.1, 1.0),
                       'l1_ratio': [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],}
        
    else:
        raise ValueError("Please input a correct algorithm")
        
    # gridsearch CV 
    from sklearn.model_selection import GridSearchCV
    gscv = GridSearchCV(model, param_space, cv=5, scoring='neg_mean_absolute_error', iid=True, refit=True)
    gscv.fit(X_train, y_train)
    
    # get best model 
    best_model = gscv.best_estimator_
    preds = best_model.predict(X_test)

    # evaluate performance
    error_list = preds - y_test
    mse = np.mean(np.array(error_list)**2)
    mae = np.absolute(error_list).mean()
    quarter_error_perc = 100 * np.sum(np.absolute(error_list) < 0.25) / len(error_list)
    half_error_perc = 100 * np.sum(np.absolute(error_list) < 0.50) / len(error_list)
    print("MSE = {:.2f}".format(mse))
    print("MAE = {:.2f}".format(mae))
    print("Errors within 0.25 = {:.2f} %".format(quarter_error_perc))
    print("Errors within 0.50 = {:.2f} %".format(half_error_perc))

    # fit best model over all data 
    best_model.fit(user_df[features], user_df[target])
    best_params = {}
    print(param_space)
    for key in param_space.keys():
        best_params[key] = best_model.get_params()[key]
    print(best_params)
    
    return best_model, best_params, mae, quarter_error_perc, half_error_perc


# semi-coldstart - collaborative filtering
def collaborative_filtering(df, user_of_interest):
    try:
        df.drop('nearest_neighbor_rank', axis=1, inplace=True)
    except:
        pass
    df = COSINE_STEP(df, user_of_interest)
    beer_list = list(df[df['username']==user_of_interest]['beer_name'])
    estimated_rating_list = []
    error_list = []
    for beer in beer_list:
        try:
            estimated_rating = df[ (df.sort_values('nearest_neighbor_rank')['beer_name'] == beer) & (df['username']!=user_of_interest) ]['user_rating'].iloc[0]
            estimated_rating_list.append(estimated_rating)

            user_rating = df[(df['username']==user_of_interest) & (df['beer_name']==beer)]['user_rating'].iloc[0].astype(float)
            error_list.append(estimated_rating-user_rating)
        except IndexError:
            print("SKIPPING:", beer)
    mse = np.mean(np.array(error_list)**2)
    mae = np.absolute(error_list).mean()
    quarter_error_perc = 100 * np.sum(np.absolute(error_list) < 0.25) / len(error_list)
    half_error_perc = 100 * np.sum(np.absolute(error_list) < 0.50) / len(error_list)

    print("MSE = {:.2f}".format(mse))
    print("MAE = {:.2f}".format(mae))
    print("Errors within 0.25 = {:.2f} %".format(quarter_error_perc))
    print("Errors within 0.50 = {:.2f} %".format(half_error_perc))
    
    return mae, quarter_error_perc, half_error_perc 

# hybrid
def run_hybrid(df, user_of_interest, target):
    
    features = list(df.columns[df.columns != target])
    try:
        features.remove('username')
    except:
        pass
    try:
        features.remove('beer_name')
    except:
        pass
    try:
        df.drop('nearest_neighbor_rank', axis=1, inplace=True)
    except:
        pass
    
    print("LEN OF FEATURES", len(features))
    print("TOP FEATURES ", features[:10])
    print("TARGET ", target)
    df = COSINE_STEP(df, user_of_interest)

    min_ppu_list = [0, 50, 100, 250, 500]
    n_users_list = [5, 10, 15, 20, 30, 40, 50]

    mae_list = []
    quarter_abs_error_list = []
    half_abs_error_list = []
    model_list = []


    for min_ppu in min_ppu_list:

        user_indices = df.username.value_counts()[df.username.value_counts() > min_ppu].index
        sub_df = df[df['username'].isin(user_indices)]
        n_users_list = [n_users for n_users in n_users_list if n_users < len(user_indices)]

        for top_n in n_users_list:

            # split data 
            top_n_nn = list(sub_df['nearest_neighbor_rank'].unique())[:top_n]
            df_top_n = df[df['nearest_neighbor_rank'].isin(top_n_nn)]
            X_train = df_top_n[features]
            y_train = df_top_n[target]
            y_train = np.array(y_train).reshape(len(y_train), )

            X_test = df[df['username'] == user_of_interest][features]
            y_test = df[df['username'] == user_of_interest][target]
            y_test = np.array(y_test).reshape(len(y_test), )

            # train
            from sklearn.linear_model import LassoCV
            model = LassoCV(fit_intercept=True, normalize=True, cv=5, random_state=12)
            model.fit(X_train, y_train)

            # Evaluate model on user's data 
            preds = model.predict(X_test)

            # evaluate results
            results_df = pd.DataFrame([preds, y_test]).transpose()
            results_df.columns = ['predicted', 'actual']
            results_df['error'] = results_df['predicted'] - results_df['actual']
            results_df['abs_error'] = abs(results_df['error'])

            # Performance Metrics 
            mae = np.mean(results_df['abs_error'])

            quarter_abs_error_list.append(100*len(results_df[results_df['abs_error']<=0.25])/len(results_df))
            half_abs_error_list.append(100*len(results_df[results_df['abs_error']<=0.50])/len(results_df))
            mae_list.append(mae)
            model_list.append(model)

        # add breaks
        quarter_abs_error_list.append(0)
        half_abs_error_list.append(0)
        mae_list.append(0)
        model_list.append(0)
        
    return model_list, mae_list, quarter_abs_error_list, half_abs_error_list