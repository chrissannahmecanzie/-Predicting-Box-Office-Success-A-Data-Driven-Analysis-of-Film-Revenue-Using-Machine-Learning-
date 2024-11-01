# -*- coding: utf-8 -*-
"""ML Project : "Predicting Box Office Success : A Data Driven Analysis of Film Revenue Using Machine Learning

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1Kv1YbjzBDL0pV6uvRIX-J_Zs3SGVQrjH

**Title of ML Project :** "Predicting Box Office Success : A Data Driven Analysis of Film Revenue Using Machine Learning"

---

**Name :** Chrissannah Mecanzie KJ

**Organization :** Entri Elevate

**Date :** 25/09/2024

---

**Step 1 :  Overview of the Problem Statement**

   The prime motive of this project is to predict the box office revenue of films using machine learning techniques by evaluating historical data, that includes variables such as budget, cast, genre and the release timing. The model helps to understand the pattern and the main factors that might influence a film's financial success. The challenge is in accurately forecasting revenue. This analysis will provide valuable insights for film producers and studios helping them make informed about the marketing strategies to maximize profitability.

**Step 2 : Objective**

   The objective of this project is to develop a machine learning model to accurately predict a film's box office revenue based on key factors such as budget, cast, genre, and release timing.

**Step 3 : Data Description**

  Source   -- data.world https://data.world/cye/update-movie-imdb

  Features  -- [Title,Budget,Genre,Director,Cast,Release date,Runtime,Production Company,Box office gross,IMDb rating,Metascore,Number of Screens,Country of origin,language,Marketing spend,Pre-release social media activity,Awards,Competition,Sequel or Original,Production Time]

**Step 4 : Data Collection**

-- Importing essential python libraries
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.impute import KNNImputer
from sklearn.preprocessing import RobustScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import LogisticRegression
from sklearn.feature_selection import SelectKBest, f_regression
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.neural_network import MLPRegressor
from sklearn.ensemble import AdaBoostRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.feature_selection import f_classif
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.metrics import mean_squared_error,r2_score
from sklearn.metrics import mean_absolute_error,mean_squared_error
from sklearn.preprocessing import LabelEncoder,OneHotEncoder
from sklearn.model_selection import RandomizedSearchCV
import time
import joblib

"""-- Importing the dataset"""

from google.colab import files
upload =files.upload()

df=pd.read_csv('movie_metadata (1).csv')

"""-- Insights"""

df.head()

df.info()

df.describe()

df.tail()

"""# **Step 5 : Data Preprocessing - Data Cleaning**

-- Finding missing values
"""

df.isnull().sum()

"""-- Handling missing values using appropriate imputation techniques.

Using KNN for numerical data
"""

knn_imputer = KNNImputer(n_neighbors=5)

df[['budget', 'gross', 'duration','num_critic_for_reviews','title_year','director_facebook_likes','actor_3_facebook_likes','aspect_ratio']] = knn_imputer.fit_transform(df[['budget', 'gross', 'duration','num_critic_for_reviews','title_year','director_facebook_likes','actor_3_facebook_likes','aspect_ratio']])

"""*-- Using mode or 'Unknown' for Categorical data*"""

df['color'].fillna(df['color'].mode()[0],inplace=True)

df['director_name'].fillna('Unknown',inplace=True)

df['actor_2_name'].fillna('Unknown',inplace=True)

df['actor_3_name'].fillna('Unknown',inplace=True)

df['actor_1_name'].fillna('Unknown',inplace=True)

df['plot_keywords'].fillna('Unknown',inplace=True)

df['content_rating'].fillna('Unknown',inplace=True)

df['language'].fillna(df['language'].mode()[0],inplace=True)

"""-- RobustScaler to handle outliers"""

robust_scaler = RobustScaler()

df[['budget', 'gross', 'duration', 'num_critic_for_reviews','num_critic_for_reviews','title_year','director_facebook_likes','actor_3_facebook_likes','aspect_ratio']] = robust_scaler.fit_transform(
    df[['budget', 'gross', 'duration', 'num_critic_for_reviews','num_critic_for_reviews','title_year','director_facebook_likes','actor_3_facebook_likes','aspect_ratio']]
)

"""*-- Identifying Outliers using IQR method*"""

def find_outliers_IQR(df, column):
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)]
    return outliers

"""# **Step 6 : Exploratory Data Analysis**

-- **Bar Plot** : *Compare counts of different categories*
"""

plt.figure(figsize=(20, 8))
sns.barplot(x='content_rating', y='gross', data=df)
plt.title('Gross Revenue by Content Rating')
plt.show()

plt.figure(figsize=(20, 8))
sns.barplot(x='budget', y='content_rating', data=df)
plt.title('Budget by Content Rating')
plt.show()

"""-- **Count Plot** : *Count plot can visualize the frequency of categorical features*"""

sns.countplot(x='color', data=df)
plt.title('Count of movies by color')
plt.show()

"""-- **Line plot** : *Visualize trends over time*"""

df.groupby('title_year')['gross'].sum().plot(kind='line', title='Gross Revenue by Year')

df.groupby('language')['gross'].sum().plot(kind='line', title='Gross Revenue by language')

df.groupby('country')['gross'].sum().plot(kind='line', title='Gross Revenue by country ')

"""# **Step 7 : Feature Engineering**

*-- Label Encoding*
"""

le = LabelEncoder()
df['content_rating_encoded'] = le.fit_transform(df['content_rating'])
print(df[['content_rating', 'content_rating_encoded']].head())

print(df[['content_rating', 'content_rating']].tail())

df_encoded = pd.get_dummies(df, columns=['content_rating'], drop_first=True)
print(df_encoded.head())

"""*-- One-Hot Encoding*"""

X = df.drop(columns=['gross'])
categorical_cols = X.select_dtypes(include=['object']).columns
print("Categorical columns:", categorical_cols)
X_encoded = pd.get_dummies(X, columns=categorical_cols, drop_first=True)
print(X_encoded.head())

"""# **Step : 8 Feature Selection**"""

features = df[['director_name', 'actor_1_name', 'budget',
                'num_critic_for_reviews', 'gross',
                'movie_facebook_likes', 'genres',
                'imdb_score','cast_total_facebook_likes','content_rating']].copy()

target = df['gross']


for col in ['director_name', 'actor_1_name', 'genres', 'content_rating']:
    if df[col].dtype == 'object':
        le = LabelEncoder()
        features[col] = le.fit_transform(features[col].fillna('Unknown'))


X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42)

selector = SelectKBest(f_regression, k=10)
selector.fit(X_train, y_train)


selected_features = X_train.columns[selector.get_support()]
print("Top 10 selected features:", selected_features)


model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

feature_importances = pd.Series(model.feature_importances_, index=X_train.columns)
top_10_features = feature_importances.nlargest(10)
print("Top 10 features based on importance:\n", top_10_features)

"""# **Step 9 : Splitting data into training and testing sets**"""

X = df.drop(columns=['gross'])
y = df['gross']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print(f"Training set shape: X_train: {X_train.shape}, y_train: {y_train.shape}")
print(f"Testing set shape: X_test: {X_test.shape}, y_test: {y_test.shape}")

"""# **Step 10 : Feature Scaling**"""

df.fillna(df.median(numeric_only=True), inplace=True)
df.fillna(df.mode().iloc[0], inplace=True)

X = df.drop(columns=['gross'])
y = df['gross']

min_max_scaler = MinMaxScaler()
standard_scaler = StandardScaler()

X = pd.get_dummies(X, drop_first=True)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

X_train_min_max = min_max_scaler.fit_transform(X)
X_test_min_max = min_max_scaler.transform(X_test)

X_train_standardized = standard_scaler.fit_transform(X_train)
X_test_standardized = standard_scaler.transform(X_test)

print("Min-Max Scaled Training Features:", X_train_min_max.shape)
print("Min-Max Scaled Testing Features:", X_test_min_max.shape)
print("Standardized Training Features:", X_train_standardized.shape)
print("Standardized Testing Features:", X_test_standardized.shape)

"""# **Step 11 : Build the ML models**

*-- 1. Linear Regression*
"""

lr = LinearRegression()
lr.fit(X_train_standardized, y_train)
y_pred = lr.predict(X_test_standardized)
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
r2 = r2_score(y_test, y_pred)
print(f"Linear Regression - RMSE: {rmse:.2f}, R²: {r2:.2f}")

"""*-- 2. Random Forest Regression*"""

rfr = RandomForestRegressor(n_estimators=100, random_state=42)
rfr.fit(X_train_standardized, y_train)
y_pred = rfr.predict(X_test_standardized)
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
r2 = r2_score(y_test, y_pred)
print(f"Random Forest Regressor - RMSE: {rmse:.2f}, R²: {r2:.2f}")

"""*-- 3.MLP Regressor*"""

mlp = MLPRegressor(hidden_layer_sizes=(100, 50), max_iter=1000, random_state=42)
mlp.fit(X_train_standardized, y_train)
y_pred = mlp.predict(X_test_standardized)
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
r2 = r2_score(y_test, y_pred)
print(f"MLP Regressor - RMSE: {rmse:.2f}, R²: {r2:.2f}")

"""*-- 4. Gradient Boosting Regressor*"""

gbr = GradientBoostingRegressor(n_estimators=100, random_state=42)
gbr.fit(X_train_standardized, y_train)
y_pred = gbr.predict(X_test_standardized)
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
r2 = r2_score(y_test, y_pred)
print(f"Gradient Boosting Regressor - RMSE: {rmse:.2f}, R²: {r2:.2f}")

"""*-- 5. Ada Boost Regressor*"""

abr = AdaBoostRegressor(n_estimators=100, random_state=42)
abr.fit(X_train_standardized, y_train)
y_pred_ada = abr.predict(X_test_standardized)
mse_ada = mean_squared_error(y_test, y_pred_ada)
rmse_ada = np.sqrt(mse_ada)
r2_ada = r2_score(y_test, y_pred_ada)
print(f"AdaBoost Regressor - RMSE: {rmse_ada:.2f}, R²: {r2_ada:.2f}")

"""# **Step 12 : Model Evaluation**

*-- For Gradient Booster Regressor*
"""

y_pred = gbr.predict(X_test_standardized)
mae = mean_absolute_error(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
r2 = r2_score(y_test, y_pred)

print(f"Mean Absolute Error (MAE): {mae:.2f}")
print(f"Mean Squared Error (MSE): {mse:.2f}")
print(f"Root Mean Squared Error (RMSE): {rmse:.2f}")
print(f"R² Score: {r2:.2f}")

"""*-- For Random Forest Regressor*"""

y_pred = rfr.predict(X_test_standardized)
mae = mean_absolute_error(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
r2 = r2_score(y_test, y_pred)

# Print the evaluation metrics
print(f"Mean Absolute Error (MAE): {mae:.2f}")
print(f"Mean Squared Error (MSE): {mse:.2f}")
print(f"Root Mean Squared Error (RMSE): {rmse:.2f}")
print(f"R² Score: {r2:.2f}")

"""*-- For Linear Regression*"""

y_pred = lr.predict(X_test_standardized)
mae = mean_absolute_error(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
r2 = r2_score(y_test, y_pred)


print(f"Mean Absolute Error (MAE): {mae:.2f}")
print(f"Mean Squared Error (MSE): {mse:.2f}")
print(f"Root Mean Squared Error (RMSE): {rmse:.2f}")
print(f"R² Score: {r2:.2f}")

"""*-- For AdaBoost Regressor*"""

y_pred = abr.predict(X_test_standardized)
mae = mean_absolute_error(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
r2 = r2_score(y_test, y_pred)

print(f"Mean Absolute Error (MAE): {mae:.2f}")
print(f"Mean Squared Error (MSE): {mse:.2f}")
print(f"Root Mean Squared Error (RMSE): {rmse:.2f}")
print(f"R² Score: {r2:.2f}")

"""*-- For MLP*"""

y_pred = mlp.predict(X_test_standardized)
mae = mean_absolute_error(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
r2 = r2_score(y_test, y_pred)

print(f"Mean Absolute Error (MAE): {mae:.2f}")
print(f"Mean Squared Error (MSE): {mse:.2f}")
print(f"Root Mean Squared Error (RMSE): {rmse:.2f}")
print(f"R² Score: {r2:.2f}")

"""# **Step 13: Hyperparameter Tuning**"""

model = RandomForestRegressor(random_state=42)
param_dist = {
    'n_estimators': [50, 100, 150],
    'max_depth': [None, 10, 20],
    'min_samples_split': [2, 5],
    'min_samples_leaf': [1, 2]
}
random_search = RandomizedSearchCV(estimator=model, param_distributions=param_dist,
                                   n_iter=10, scoring='neg_mean_squared_error',
                                   cv=3, verbose=2, n_jobs=-1, random_state=42)

random_search.fit(X_train, y_train)

best_params = random_search.best_params_
print(f"Best Hyperparameters: {best_params}")

best_model = random_search.best_estimator_


y_pred = best_model.predict(X_test)
print(f"R² Score: {r2_score(y_test, y_pred):.2f}")

"""# **Step 14 : Save the model**"""

import joblib
joblib.dump(best_model, 'random_forest_best_model.pkl')

print("Model saved successfully!")

"""# **Step 15 : Test with unseen data**"""

from google.colab import files
upload =files.upload()

unseen_df=pd.read_csv('insurance.csv')

unseen_df.fillna(unseen_df.median(numeric_only=True), inplace=True)

categorical_cols = unseen_df.select_dtypes(include=['object']).columns
unseen_df_encoded = pd.get_dummies(unseen_df, columns=categorical_cols, drop_first=True)

model = joblib.load('random_forest_best_model.pkl')

trained_model_columns = model.feature_names_in_

for col in trained_model_columns:
    if col not in unseen_df_encoded.columns:
        unseen_df_encoded[col] = 0

unseen_df_encoded = unseen_df_encoded[trained_model_columns]

predictions = model.predict(unseen_df_encoded)

print(predictions)

"""# **Step 16 : Interpretation of Results (Conclusion)**

***--Model Performance (Random Forest)***

In the conclusion after training and evaluating models (Random Forest,Linear Regression,Ada Boost Regressor,MLP Regressor,Gradient Boosting Regressor) The Random Forest Regressor performs the best across all metrics, with the lowest MAE, MSE, and RMSE and the highest R² score (0.75).Random Forest also balances training time and scalability better than any other models trained.Therefore, Random Forest is concluded to be the best model for this regression project

***--Dataset Limitations***

Missing values - Several important features were missing such as budget, content rating etc.But these missing values were managed using imputation techniques (median,mode)

Other limitations was also there such as outliers and categorical variables which were difficult to manage without removing important datapoints also categorical variables were managed by one-hot encoding

***--Challenges Faced***

Feature encoding - Dealing with a large number of categorical variable was complex.This increased the time taken for both training and hyperparameter tuning.

Computational Time - Hyperparameter tuning took a considerable amount of time due to the size of the dataset and high dimentionality after encoding.

***--Conclusion***

In this project, multiple machine learning models were implemented to predict the gross revenue of films using various features from the dataset. After evaluating different models, Random Forest Regressordemonstrated the best performance.Despite these difficulties, the results indicate that with further data refinement and model tuning, accurate predictions of movie gross revenue can be achieved.
"""