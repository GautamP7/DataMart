import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix, hstack
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.preprocessing import LabelBinarizer
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error
import lightgbm as lgb

NUM_REGIONS = 1000
NUM_CATEGORIES = 1000
NUM_SELLERS = 4000
NAME_MIN_DF = 10
MAX_FEATURES_DATASET_DESCRIPTION = 50000

def cutting(dataset):
    pop_seller = dataset['seller'].value_counts().loc[lambda x: x.index != 'missing'].index[:NUM_SELLERS]
    dataset.loc[~dataset['seller'].isin(pop_seller), 'seller'] = 'missing'
    pop_category = dataset['category'].value_counts().loc[lambda x: x.index != 'missing'].index[:NUM_CATEGORIES]

def to_categorical(dataset):
    dataset['category'] = dataset['category'].astype('category')
    dataset['seller'] = dataset['seller'].astype('category')
    dataset['region'] = dataset['region'].astype('category')
    dataset['offering_type'] = dataset['offering_type'].astype('category')
    dataset['update_frequency'] = dataset['update_frequency'].astype('category')

def calc_price(dataset, file_name):
    
    df = pd.read_csv(file_name)

    df_mod = df.append(dataset, ignore_index=True)
    
    train, test = train_test_split(df_mod, test_size=0.20, random_state=1, shuffle=False)
    test_new = test.drop('price', axis=1)
    y_test =  np.log1p(test["price"])
    train = train[train.price != 0].reset_index(drop=True)
    nrow_train = train.shape[0]
    y = np.log1p(train["price"])
    merge: pd.DataFrame = pd.concat([train, test_new])
    cutting(merge)
    to_categorical(merge)
    
    cv = CountVectorizer()
    X_name = cv.fit_transform(merge['name'])

    cv = CountVectorizer()
    X_category = cv.fit_transform(merge['category'])
    X_region = cv.fit_transform(merge['region'])

    tv = TfidfVectorizer(max_features=MAX_FEATURES_DATASET_DESCRIPTION, ngram_range=(1, 3), stop_words='english')
    X_description = tv.fit_transform(merge['description'])

    lb = LabelBinarizer(sparse_output=True)
    X_seller = lb.fit_transform(merge['seller'])

    X_dummies = csr_matrix(pd.get_dummies(merge[['update_frequency', 'offering_type']], sparse=True).values)

    sparse_merge = hstack((X_dummies, X_description, X_seller, X_region, X_category, X_name)).tocsr()

    mask = np.array(np.clip(sparse_merge.getnnz(axis=0) - 1, 0, 1), dtype=bool)
    sparse_merge = sparse_merge[:, mask]

    X = sparse_merge[:nrow_train]
    X_test = sparse_merge[nrow_train:]

    train_X = lgb.Dataset(X, label=y)

    params = {
        'learning_rate': 0.75,
        'application': 'regression',
        'max_depth': 3,
        'num_leaves': 100,
        'verbosity': -1,
        'metric': 'RMSE',
    }

    gbm = lgb.train(params, train_set=train_X, num_boost_round=3200, verbose_eval=100)

    y_pred = gbm.predict(X_test, num_iteration=gbm.best_iteration)

    return np.expm1(y_pred[-1])

