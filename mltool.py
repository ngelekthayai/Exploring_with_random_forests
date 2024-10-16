from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import train_test_split
from sklearn.inspection import permutation_importance
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sb
import etl
import pandas as pd
import numpy as np

class Model:
    
    def __init__ (self):
       
       # italizes a blank model
        
        #Let's store some placeholder meta-data that we will change in our fit.
    
        self._target = None
        self._model = None
        self._shape = None
        self._columns = []
        self._transformer = None


    def split_train_test(self, df,target = None,  *args, **kwargs):
       # if self._transformer is None:
        self._transformer = etl.PandasTransformer()
        self._transformer.fit(df, target = target)

        return self._transformer.make_train_test_split(df, *args, **kwargs)
        
        
    def learn(self,df, target = None, kind = 'RF', *args, **kwargs):
        """
         1.Make sure there is a value for target, if there isnt then throw an error 
        2. Then check if the classifier is a Random Forest and if it isnt then check if the 
        classifier is a Linear classifier.
        3.Use PandasTransformers from etl.py
        4. fit the dataframe given and set the target to what the user inputted
        5. then use transform to get X, y
        6.fit the X,y using fit from sklearn
        
        fit the model
        """
        if target is None:
            raise ValueError("The target cannot be None.")
        ...
        if kind == "RF":
            model = RandomForestClassifier(*args, **kwargs)
        else:
            raise ValueError("The target should be RF, for now")
        
     
        # now fit the model
        if self._transformer is None:   
            transformer = etl.PandasTransformer()
        else:
            transformer = self._transformer
    
        transformer.fit(df, target = target)
        X,y = transformer.transform(df)
        
        model.fit(X,y)
     
        self._model = model
        self._target = target
        self._shape = X.shape
        self._columns = df.columns
        self._transformer = transformer



    def predict(self, df):
        """
        first we check if there is a trained model
        if there is a trained model I return a a prediction using the self._model.predict.
        need to figure out a way to transform my numpy back to pandas
        i make it a pandas dataframe and make the column the name of the target
        """
        if self._model is None:
             raise ValueError("You must train a model first with learn first.")

        X, y = self._transformer.transform(df)
         
        yh = self._model.predict(X)

        yht = self._transformer.transform_predictions(yh)
         
        return yht


    def accuracy(self, df):
         """
         so I score both the training and testing sets of data and then print out what the values would be
         """
         X, y = self._transformer.transform(df)
         
         return self._model.score(X,y) 
    
    def feature_importances(self,df, num_trials):
        """
        A poor man's permutation importance. (From Damian Eads)
        First create out transformer from etl.py
        fit our pandas dataframe and make it a numpy array
        split the numpy array into training and testing arrays
        split the test dataframe into a test X and test y
        
        using the test X and test y compute feature_importances
        
        find our feature importances by calling the transform_feature_importances from etl.py which converts the feature importances from numpy arrays to pandas dataframes and labels each feature importance.

return feature importance
        """
        X, y =self._transformer.transform(df)
        nrows, ncols = X.shape
        # The original score of the unaltered data.
        original_score = self._model.score(X, y)
        # Store the result here.
        fimps = np.zeros((ncols,))
        Xc = X.copy()
        usr = np.arange(nrows)
        # Over each feature column
        for i in range(ncols):
            sr = np.arange(nrows)
            # Over each trial.
            for j in range(num_trials):
                np.random.shuffle(sr)
                # Shuffle the rows for feature i
                Xc[:, i] = X[sr, i]

                # Compute the shuffled_score
                shuffled_score = self._model.score(Xc, y)
                Xc[:, i] = X[usr, i]

                # Accumulate for the mean: difference in score (more positive means more important)
                fimps[i] += original_score - shuffled_score
                # Compute the mean
            fimps[i] /= num_trials


        #Return the feature importances
        d = {}
        d["importances"] = fimps
        
        return self._transformer.transform_feature_importances(d, df)
    
    def confusion(self,df):
        if self._model is None:
            raise ValueError("You must train a model first with learn first.")
        
        X, y = self._transformer.transform(df)

        y_pred = self._model.predict(X)

        cm = confusion_matrix(y, y_pred)

        return cm
        
