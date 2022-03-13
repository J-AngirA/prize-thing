'''
QUICK NOTE:
IF YOU CANT FIND THE REQUIRED FILES OR FOR WHATEVER REASON THE REQUIRED FILES DONT POP UP, 
PLEASE DOWNLOAD THE FILES FROM THE DIRECTORY

ALSO SCROLL DOWN TO THE LATEST THING
'''

# -*- coding: utf-8 -*-
"""Copy of stock prize prediction.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1edTyMelBp442Jt7JS83JDzjR2RADQJDg
"""

!pip install -U -q PyDrive
 
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from google.colab import auth
from oauth2client.client import GoogleCredentials
 
# 1. Authenticate and create the PyDrive client.
auth.authenticate_user()
gauth = GoogleAuth()
gauth.credentials = GoogleCredentials.get_application_default()
drive = GoogleDrive(gauth)
file_list = drive.ListFile({'q': "'1H3EtldNffWIY_Enq0ScdrJu2POtonu3L' in parents and trashed=false"}).GetList()
for file1 in file_list:
  print('title: %s, id: %s' % (file1['title'], file1['id']))

# type(file)
import csv

stock_downloaded = drive.CreateFile({'id': '1xLnw6J7wqB0dDqEJrXsCYJ2idfB632Cz'})
# stock_downloaded.GetContentFile('Stock_Price_MAX.csv')

#EXTRA POINTS FOR ADDING YOUR OWN CODE!
stock_downloaded = open('yahoo_stock.csv')
print(stock_downloaded)

# Commented out IPython magic to ensure Python compatibility.
import pandas as pd
import numpy as np
import pandas as pd
import io
import requests
import numpy as np
from sklearn import metrics
from keras.models import Sequential
from keras.layers.core import Dense, Activation, Dropout
from keras.callbacks import EarlyStopping
from keras.callbacks import ModelCheckpoint
import collections
from sklearn import preprocessing
import sklearn.feature_extraction.text as sk_text
from keras.callbacks import EarlyStopping, ModelCheckpoint
from keras import optimizers
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten, Embedding
from keras.layers import Conv2D, MaxPooling2D
from keras.layers import Conv1D, MaxPooling1D
import keras
from keras.preprocessing import sequence
from keras.layers import LSTM


# Encode text values to indexes(i.e. [1],[2],[3] for red,green,blue).
def encode_text_index(df, name):
    le = preprocessing.LabelEncoder()
    df[name] = le.fit_transform(df[name])
    return le.classes_
  
# Encode text values to dummy variables(i.e. [1,0,0],[0,1,0],[0,0,1] for red,green,blue)
def encode_text_dummy(df, name):
    dummies = pd.get_dummies(df[name])
    for x in dummies.columns:
        dummy_name = "{}-{}".format(name, x)
        df[dummy_name] = dummies[x]
    df.drop(name, axis=1, inplace=True)
    
# Encode a column to a range between normalized_low and normalized_high.
def encode_numeric_range(df, name, normalized_low=0, normalized_high=1,
                         data_low=None, data_high=None):
    if data_low is None:
        data_low = min(df[name])
        data_high = max(df[name])

    df[name] = ((df[name] - data_low) / (data_high - data_low)) \
               * (normalized_high - normalized_low) + normalized_low
 
# %matplotlib inline
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc


# Convert a Pandas dataframe to the x,y inputs that TensorFlow needs
def to_xy(df, target):
    result = []
    for x in df.columns:
        if x != target:
            result.append(x)
    # find out the type of the target column. 
    target_type = df[target].dtypes
    target_type = target_type[0] if isinstance(target_type, collections.Sequence) else target_type
    # Encode to int for classification, float otherwise. TensorFlow likes 32 bits.
    if target_type in (np.int64, np.int32):
        # Classification
        dummies = pd.get_dummies(df[target])
        return df[result].values.astype(np.float32), dummies.values.astype(np.float32)
    else:
        # Regression
        return df[result].values.astype(np.float32), df[target].values.astype(np.float32)
      
def class_connection(x):
  if(x=='normal.'):
    x=0
  else:
    x=1
  return x

import numpy as np

def to_sequences(seq_size, df ,data):
    x = []
    y = []

    for i in range(len(data)-SEQUENCE_SIZE-1):
        #print(i)
        window = df[i:(i+SEQUENCE_SIZE)]
        after_window = data[i+SEQUENCE_SIZE]
        #window = [[x] for x in window]
       #print("{} - {}".format(window,after_window))
        x.append(window)
        y.append(after_window)
        
    return np.array(x),np.array(y)
  
# Regression chart.
def chart_regression(pred,y,sort=True):
    t = pd.DataFrame({'pred' : pred, 'y' : y})
    if sort:
        t.sort_values(by=['y'],inplace=True)
    a = plt.plot(t['y'].tolist(),label='expected')
    b = plt.plot(t['pred'].tolist(),label='prediction')
    plt.ylabel('output')
    plt.legend()
    plt.show()
 
  # Nicely formatted time string
def hms_string(sec_elapsed):
    h = int(sec_elapsed / (60 * 60))
    m = int((sec_elapsed % (60 * 60)) / 60)
    s = sec_elapsed % 60
    return "{}:{:>02}:{:>05.2f}".format(h, m, s)

df_stock = pd.read_csv(stock_downloaded, encoding="utf-8")
df_stock[0:5]

df_stock.dtypes

df_stock=df_stock.drop(['Date', 'Adj Close'], axis=1)

df_stock = df_stock.dropna(how='any',axis=0)

encode_numeric_range(df_stock, 'Open')
encode_numeric_range(df_stock, 'High')
encode_numeric_range(df_stock, 'Low')
encode_numeric_range(df_stock, 'Volume')

#Preparing x and y
x,y = to_xy(df_stock, 'Close')

#splitting data into 70% training and 30% testing 
x_train, x_test, y_train, y_test = train_test_split (x, y, test_size=0.30, random_state=45)

x_train.shape,x_test.shape,y_train.shape,y_test.shape

#Activation: Relu 
#Optimization: Adam
#2 Hidden Layers: 50 and 25 neaurons respectively

#checkpointer
checkpointer = ModelCheckpoint(filepath="best_weights_adam_relu.hdf5", verbose=0, save_best_only=True) # save best model
for i in range(5):
    print(i)
    
    model_adam_relu = Sequential()
    
    # 50 neurons in 1st hidden layer
    model_adam_relu.add(Dense(50, input_dim=x_train.shape[1], activation='relu')) # Hidden 1 

    # 25 neurons in 2nd hidden layer
    model_adam_relu.add(Dense(25, activation='relu')) # Hidden 2
    
    model_adam_relu.add(Dense(1)) # Output

    # optimizer - Back Prop algo
    model_adam_relu.compile(loss='mean_squared_error', optimizer='adam')

    #  monitor
    monitor = EarlyStopping(monitor='val_loss', min_delta=1e-3, patience=3, verbose=2, mode='auto')

    # epochs can be increased 500 or 1000
    model_adam_relu.fit(x_train,y_train, validation_data=(x_test,y_test),callbacks=[monitor,checkpointer],verbose=2,epochs=1000)

model_adam_relu.load_weights('best_weights_adam_relu.hdf5') # load weights from best model

'''
------------------------------------------------
(multi line comment)
12-3-22 (Saksham Tehri) starting from here
also have to make sure that this runs like one single python file and that the output we wanna get is at the last
not in between since the code is from jupyter nb/google collab, thats why we gotta make sure about it
'''

from sklearn.metrics import r2_score
pred = model_adam_relu.predict(x_test)
print("Shape: {}".format(pred.shape))
score = np.sqrt(metrics.mean_squared_error(pred,y_test))
print("Final score (RMSE): {}".format(score))
print('R2 score: %2f' % r2_score(y_test,pred))
# Plot the chart
chart_regression(pred.flatten()[0:100],y_test[0:100])


#Activation: Relu 
#Optimization: Sgd
#2 Hidden Layers: 50 and 25 neaurons respectively

#checkpointer
checkpointer = ModelCheckpoint(filepath="best_weights_sgd_relu.hdf5", verbose=0, save_best_only=True) # save best model
for i in range(5):
    print(i)
    
    model_sgd_relu = Sequential()
    
    # 50 neurons in 1st hidden layer
    model_sgd_relu.add(Dense(50, input_dim=x_train.shape[1], activation='relu')) # Hidden 1 

    # 25 neurons in 2nd hidden layer
    model_sgd_relu.add(Dense(25, activation='relu')) # Hidden 2
    
    model_sgd_relu.add(Dense(1)) # Output

    # optimizer - Back Prop algo
    model_sgd_relu.compile(loss='mean_squared_error', optimizer='sgd')

    #  monitor
    monitor = EarlyStopping(monitor='val_loss', min_delta=1e-3, patience=3, verbose=2, mode='auto')

    # epochs can be increased 500 or 1000
    model_sgd_relu.fit(x_train,y_train, validation_data=(x_test,y_test),callbacks=[monitor,checkpointer],verbose=2,epochs=1000)

model_sgd_relu.load_weights('best_weights_sgd_relu.hdf5') # load weights from best model


from sklearn.metrics import r2_score
pred = model_sgd_relu.predict(x_test)
print("Shape: {}".format(pred.shape))
score = np.sqrt(metrics.mean_squared_error(pred,y_test))
print("Final score (RMSE): {}".format(score))
print('R2 score: %2f' % r2_score(y_test,pred))
# Plot the chart
chart_regression(pred.flatten()[0:100],y_test[0:100])


#Activation: Relu 
#Optimization: Rmsprop
#2 Hidden Layers: 50 and 25 neaurons respectively

#checkpointer
checkpointer = ModelCheckpoint(filepath="best_weights_rmsprop_relu.hdf5", verbose=0, save_best_only=True) # save best model
for i in range(5):
    print(i)
    
    model_rmsprop_relu = Sequential()
    
    # 50 neurons in 1st hidden layer
    model_rmsprop_relu.add(Dense(50, input_dim=x_train.shape[1], activation='relu')) # Hidden 1 

    # 25 neurons in 2nd hidden layer
    model_rmsprop_relu.add(Dense(25, activation='relu')) # Hidden 2
    
    model_rmsprop_relu.add(Dense(1)) # Output

    # optimizer - Back Prop algo
    model_rmsprop_relu.compile(loss='mean_squared_error', optimizer='rmsprop')

    #  monitor
    monitor = EarlyStopping(monitor='val_loss', min_delta=1e-3, patience=3, verbose=2, mode='auto')

    # epochs can be increased 500 or 1000
    model_rmsprop_relu.fit(x_train,y_train, validation_data=(x_test,y_test),callbacks=[monitor,checkpointer],verbose=2,epochs=1000)

model_rmsprop_relu.load_weights('best_weights_rmsprop_relu.hdf5') # load weights from best model


from sklearn.metrics import r2_score
pred = model_rmsprop_relu.predict(x_test)
print("Shape: {}".format(pred.shape))
score = np.sqrt(metrics.mean_squared_error(pred,y_test))
print("Final score (RMSE): {}".format(score))
print('R2 score: %2f' % r2_score(y_test,pred))
# Plot the chart
chart_regression(pred.flatten()[0:100],y_test[0:100])


#Activation: Sigmoid 
#Optimization: Rmsprop
#2 Hidden Layers: 50 and 25 neaurons respectively

#checkpointer
checkpointer = ModelCheckpoint(filepath="best_weights_rmsprop_sigmoid.hdf5", verbose=0, save_best_only=True) # save best model
for i in range(5):
    print(i)
    
    model_rmsprop_sigmoid = Sequential()
    
    # 50 neurons in 1st hidden layer
    model_rmsprop_sigmoid.add(Dense(50, input_dim=x_train.shape[1], activation='sigmoid')) # Hidden 1 

    # 25 neurons in 2nd hidden layer
    model_rmsprop_sigmoid.add(Dense(25, activation='sigmoid')) # Hidden 2
    
    model_rmsprop_sigmoid.add(Dense(1)) # Output

    # optimizer - Back Prop algo
    model_rmsprop_sigmoid.compile(loss='mean_squared_error', optimizer='rmsprop')

    #  monitor
    monitor = EarlyStopping(monitor='val_loss', min_delta=1e-3, patience=3, verbose=2, mode='auto')

    # epochs can be increased 500 or 1000
    model_rmsprop_sigmoid.fit(x_train,y_train, validation_data=(x_test,y_test),callbacks=[monitor,checkpointer],verbose=2,epochs=1000)

model_rmsprop_sigmoid.load_weights('best_weights_rmsprop_sigmoid.hdf5') # load weights from best model


from sklearn.metrics import r2_score
pred = model_rmsprop_sigmoid.predict(x_test)
print("Shape: {}".format(pred.shape))
score = np.sqrt(metrics.mean_squared_error(pred,y_test))
print("Final score (RMSE): {}".format(score))
print('R2 score: %2f' % r2_score(y_test,pred))
# Plot the chart
chart_regression(pred.flatten()[0:100],y_test[0:100])


#LSTM
df_stock_close = df_stock['Close'].tolist()

encode_numeric_range(df_stock, 'Close')
# df_stock

# df_stock_close


#Preparing x and y
SEQUENCE_SIZE = 7
x_lstm,y_lstm = to_sequences(SEQUENCE_SIZE, df_stock.values, df_stock_close)
#x_test,y_test = to_sequences(SEQUENCE_SIZE, df_test, close_test)

print("Shape of x: {}".format(x_lstm.shape))
print("Shape of y: {}".format(y_lstm.shape))

#Splitting data into 70% training and 30% test set
x_train_lstm,x_test_lstm,y_train_lstm,y_test_lstm = train_test_split(x_lstm,y_lstm, test_size=0.3, random_state =42)
print("Shape of x_train: {}".format(x_train_lstm.shape))
print("Shape of x_test: {}".format(x_test_lstm.shape))
print("Shape of y_train: {}".format(y_train_lstm.shape))
print("Shape of y_test: {}".format(y_test_lstm.shape))

#LSTM neuron: 100
#Optimization: Adam
#No drop out layer

#checkpointer
checkpointer = ModelCheckpoint(filepath="best_weights.hdf5", verbose=0, save_best_only=True) # save best model
for i in range(5):
    print(i)    
    print('Build model...')
    model = Sequential()
    model.add(LSTM(100, dropout=0.1, recurrent_dropout=0.1, input_shape=(7, 5)))
    model.add(Dense(50))
    model.add(Dense(1))
    model.compile(loss='mean_squared_error', optimizer='adam')
    monitor = EarlyStopping(monitor='val_loss', min_delta=1e-3, patience=5, verbose=1, mode='auto')
    print('Train...')
    model.fit(x_train_lstm,y_train_lstm,validation_data=(x_test_lstm,y_test_lstm),callbacks=[monitor,checkpointer],verbose=2, epochs=10) 
model.load_weights('best_weights.hdf5')


from sklearn import metrics

pred = model.predict(x_test_lstm)
score = np.sqrt(metrics.mean_squared_error(pred,y_test_lstm))
print("Score (RMSE): {}".format(score))
print('R2 score: %2f' % r2_score(y_test_lstm,pred))
# Plot the chart
chart_regression(pred.flatten()[0:100],y_test_lstm[0:100])
#pred


#LSTM neuron: 100
#Optimization: Adam
#With drop out layer

#checkpointer
checkpointer = ModelCheckpoint(filepath="best_weights.hdf5", verbose=0, save_best_only=True) # save best model
for i in range(5):
    print(i)    
    print('Build model...')
    model = Sequential()
    model.add(LSTM(100, dropout=0.1, recurrent_dropout=0.1, input_shape=(7, 5)))
    model.add(Dropout(0.1))
    model.add(Dense(50))
    model.add(Dense(1))
    model.compile(loss='mean_squared_error', optimizer='adam')
    monitor = EarlyStopping(monitor='val_loss', min_delta=1e-3, patience=5, verbose=1, mode='auto')
    print('Train...')
    model.fit(x_train_lstm,y_train_lstm,validation_data=(x_test_lstm,y_test_lstm),callbacks=[monitor,checkpointer],verbose=2, epochs=10) 
model.load_weights('best_weights.hdf5')


from sklearn import metrics

pred = model.predict(x_test_lstm)
score = np.sqrt(metrics.mean_squared_error(pred,y_test_lstm))
print("Score (RMSE): {}".format(score))
print('R2 score: %2f' % r2_score(y_test_lstm,pred))
chart_regression(pred.flatten()[0:100],y_test_lstm[0:100])


#LSTM neuron: 100
#Optimization: SGD
#With drop out layer

#checkpointer
checkpointer = ModelCheckpoint(filepath="best_weights.hdf5", verbose=0, save_best_only=True) # save best model
for i in range(5):
    print(i)    
    print('Build model...')
    model = Sequential()
    model.add(LSTM(100, dropout=0.1, recurrent_dropout=0.1, input_shape=(7, 5)))
    model.add(Dropout(0.1))
    model.add(Dense(50))
    model.add(Dense(1))
    model.compile(loss='mean_squared_error', optimizer='adam')
    monitor = EarlyStopping(monitor='val_loss', min_delta=1e-3, patience=5, verbose=1, mode='auto')
    print('Train...')
    model.fit(x_train_lstm,y_train_lstm,validation_data=(x_test_lstm,y_test_lstm),callbacks=[monitor,checkpointer],verbose=2, epochs=10) 
model.load_weights('best_weights.hdf5')

from sklearn import metrics

pred = model.predict(x_test_lstm)
score = np.sqrt(metrics.mean_squared_error(pred,y_test_lstm))
print("Score (RMSE): {}".format(score))
print('R2 score: %2f' % r2_score(y_test_lstm,pred))
chart_regression(pred.flatten()[0:100],y_test_lstm[0:100])


#LSTM neuron: 500
#Optimization: Rmsprop
#With drop out layer

#checkpointer
checkpointer = ModelCheckpoint(filepath="best_weights.hdf5", verbose=0, save_best_only=True) # save best model
for i in range(5):
    print(i)    
    print('Build model...')
    model = Sequential()
    model.add(LSTM(500, dropout=0.1, recurrent_dropout=0.1, input_shape=(7, 5)))
    model.add(Dropout(0.5))
    model.add(Dense(50))
    model.add(Dense(1))
    model.compile(loss='mean_squared_error', optimizer='rmsprop')
    monitor = EarlyStopping(monitor='val_loss', min_delta=1e-3, patience=5, verbose=1, mode='auto')
    print('Train...')
    model.fit(x_train_lstm,y_train_lstm,validation_data=(x_test_lstm,y_test_lstm),callbacks=[monitor,checkpointer],verbose=2, epochs=10) 
model.load_weights('best_weights.hdf5')


from sklearn import metrics

pred = model.predict(x_test_lstm)
score = np.sqrt(metrics.mean_squared_error(pred,y_test_lstm))
print("Score (RMSE): {}".format(score))
print('R2 score: %2f' % r2_score(y_test_lstm,pred))
chart_regression(pred.flatten()[0:100],y_test_lstm[0:100])

def to_sequences1(seq_size, df ,data):
    x = []
    y = []

    for i in range(len(data)-SEQUENCE_SIZE-1):
        #print(i)
        window = df[i:(i+SEQUENCE_SIZE)]
        after_window = data[i+SEQUENCE_SIZE]
        window = [[x] for x in window]
       #print("{} - {}".format(window,after_window))
        x.append(window)
        y.append(after_window)
        
    return np.array(x),np.array(y)
#SEQUENCE_SIZE = 7
#x_train1,y_train1 = to_sequences1(SEQUENCE_SIZE, df_train,close_train)
#x_test1,y_test1 = to_sequences1(SEQUENCE_SIZE, df_test, close_test)
#print("Shape of x_train: {}".format(x_train1.shape))
#print("Shape of x_test: {}".format(x_test1.shape))
#print("Shape of y_train: {}".format(y_train1.shape))
#print("Shape of y_test: {}".format(y_test1.shape))

#Preparing x and y
SEQUENCE_SIZE = 7
x_cnn,y_cnn = to_sequences1(SEQUENCE_SIZE, df_stock.values, df_stock_close)

print("Shape of x: {}".format(x_cnn.shape))
print("Shape of y: {}".format(y_cnn.shape))
#Splitting data into 70% training and 30% test set
x_train1,x_test1,y_train1,y_test1 = train_test_split(x_cnn,y_cnn, test_size=0.3, random_state =42)
print("Shape of x_train: {}".format(x_train1.shape))
print("Shape of x_test: {}".format(x_test1.shape))
print("Shape of y_train: {}".format(y_train1.shape))
print("Shape of y_test: {}".format(y_test1.shape))
#Splitting data into 70% training and 30% test set
x_train1,x_test1,y_train1,y_test1 = train_test_split(x_cnn,y_cnn, test_size=0.3, random_state =42)
print("Shape of x_train: {}".format(x_train1.shape))
print("Shape of x_test: {}".format(x_test1.shape))
print("Shape of y_train: {}".format(y_train1.shape))
print("Shape of y_test: {}".format(y_test1.shape))



from tensorflow.keras.optimizers import Adam
# Define batch_size and # of epochs
batch_size = 128
#kernel size = 2,1 
#kernel number = 32,64
#activation='relu'
#optimizer='adam'
import time
checkpointer = ModelCheckpoint(filepath="best_weights_cnn_extra.hdf5", verbose=0, save_best_only=True) # save best model

model_cnn = Sequential()
model_cnn.add(Conv2D(32, kernel_size=(2, 1), strides=(1, 1),activation='relu', padding='valid',input_shape=(7,1,5)))
model_cnn.add(MaxPooling2D(pool_size=(1, 1), strides=(1, 1)))
model_cnn.add(Conv2D(64, (2, 1), activation='relu'))
model_cnn.add(MaxPooling2D(pool_size=(1, 1)))
model_cnn.add(Flatten())
model_cnn.add(Dense(1000, activation='relu'))
model_cnn.add(Dense(1))
    
model_cnn.compile(loss='mean_squared_error', optimizer=Adam(lr=0.001, decay=1e-6), metrics=['accuracy'])
monitor = EarlyStopping(monitor='val_loss', min_delta=1e-3, patience=2, verbose=2, mode='auto')

start_time = time.time()

model_cnn.fit(x_train1,y_train1,
              batch_size=batch_size,
              epochs=10,
              verbose=2,
              callbacks=[monitor,checkpointer],
              validation_data=(x_test1,y_test1))

elapsed_time = time.time() - start_time
print("Elapsed time: {}".format(hms_string(elapsed_time)))
model_cnn.load_weights('best_weights_cnn_extra.hdf5') # load weights from best model

pred = model_cnn.predict(x_test1)
score = np.sqrt(metrics.mean_squared_error(pred,y_test1))
print("Score (RMSE): {}".format(score))
print('R2 score: %2f' % r2_score(y_test1,pred))
chart_regression(pred.flatten()[0:100],y_test1[0:100])



#from keras.optimizers import Adam
# Define batch_size and # of epochs
batch_size = 128
#kernel size = 3,1 
#kernel number = 64,128
#activation='sigmoid'
#optimizer='rmsprop'
import time
checkpointer = ModelCheckpoint(filepath="best_weights_cnn_extra.hdf5", verbose=0, save_best_only=True) # save best model

model_cnn = Sequential()
model_cnn.add(Conv2D(64, kernel_size=(3, 1), strides=(1, 1),activation='sigmoid', padding='valid',input_shape=(7,1,5)))
model_cnn.add(MaxPooling2D(pool_size=(1, 1), strides=(1, 1)))
model_cnn.add(Conv2D(128, (3, 1), activation='sigmoid'))
model_cnn.add(MaxPooling2D(pool_size=(1, 1)))
model_cnn.add(Flatten())
model_cnn.add(Dense(1000, activation='sigmoid'))
model_cnn.add(Dense(1))
    
#model_cnn.compile(loss='mean_squared_error', optimizer=Adam(lr=0.001, decay=1e-6), metrics=['accuracy'])
#monitor = EarlyStopping(monitor='val_loss', min_delta=1e-3, patience=2, verbose=2, mode='auto')

model_cnn.compile(loss='mean_squared_error', optimizer='rmsprop')
monitor = EarlyStopping(monitor='val_loss', min_delta=1e-3, patience=5, verbose=1, mode='auto')

start_time = time.time()

#model_cnn.fit(x_train1,y_train1,validation_data=(x_test,y_test),callbacks=[monitor,checkpointer],verbose=2, epochs=10) 
model_cnn.fit(x_train1,y_train1,batch_size=batch_size,epochs=10,verbose=2,callbacks=[monitor,checkpointer],validation_data=(x_test1,y_test1))

elapsed_time = time.time() - start_time
print("Elapsed time: {}".format(hms_string(elapsed_time)))
model_cnn.load_weights('best_weights_cnn_extra.hdf5') # load weights from best model


pred = model_cnn.predict(x_test1)
score = np.sqrt(metrics.mean_squared_error(pred,y_test1))
print("Score (RMSE): {}".format(score))
print('R2 score: %2f' % r2_score(y_test1,pred))
chart_regression(pred.flatten()[0:100],y_test1[0:100])


#from keras.optimizers import Adam
# Define batch_size and # of epochs
batch_size = 128
#kernel size = 2,1 
#kernel number = 32,64
#activation='tanh'
#optimizer='rmsprop'
import time
checkpointer = ModelCheckpoint(filepath="best_weights_cnn_extra.hdf5", verbose=0, save_best_only=True) # save best model

model_cnn = Sequential()
model_cnn.add(Conv2D(32, kernel_size=(2, 1), strides=(1, 1),activation='tanh', padding='valid',input_shape=(7,1,5)))
model_cnn.add(MaxPooling2D(pool_size=(1, 1), strides=(1, 1)))
model_cnn.add(Conv2D(64, (2, 1), activation='tanh'))
model_cnn.add(MaxPooling2D(pool_size=(1, 1)))
model_cnn.add(Flatten())
model_cnn.add(Dense(1000, activation='tanh'))
model_cnn.add(Dense(1))
    
#model_cnn.compile(loss='mean_squared_error', optimizer=Adam(lr=0.001, decay=1e-6), metrics=['accuracy'])
#monitor = EarlyStopping(monitor='val_loss', min_delta=1e-3, patience=2, verbose=2, mode='auto')

model_cnn.compile(loss='mean_squared_error', optimizer='rmsprop')
monitor = EarlyStopping(monitor='val_loss', min_delta=1e-3, patience=5, verbose=1, mode='auto')

start_time = time.time()

#model_cnn.fit(x_train1,y_train1,validation_data=(x_test,y_test),callbacks=[monitor,checkpointer],verbose=2, epochs=10) 
model_cnn.fit(x_train1,y_train1,batch_size=batch_size,epochs=10,verbose=2,callbacks=[monitor,checkpointer],validation_data=(x_test1,y_test1))

elapsed_time = time.time() - start_time
print("Elapsed time: {}".format(hms_string(elapsed_time)))
model_cnn.load_weights('best_weights_cnn_extra.hdf5') # load weights from best model


pred = model_cnn.predict(x_test1)
score = np.sqrt(metrics.mean_squared_error(pred,y_test1))
print("Score (RMSE): {}".format(score))
print('R2 score: %2f' % r2_score(y_test1,pred))
chart_regression(pred.flatten()[0:100],y_test1[0:100])


#from keras.optimizers import Adam
# Define batch_size and # of epochs
batch_size = 128
#kernel size = 4,1 and 4,1 
#kernel number = 64,128
#activation='relu'
#optimizer='adam'
#With dropout layer
import time
checkpointer = ModelCheckpoint(filepath="best_weights_cnn_extra.hdf5", verbose=0, save_best_only=True) # save best model

model_cnn = Sequential()
model_cnn.add(Conv2D(64, kernel_size=(4, 1), strides=(1, 1),activation='relu', padding='valid',input_shape=(7,1,5)))
model_cnn.add(MaxPooling2D(pool_size=(1, 1), strides=(1, 1)))
model_cnn.add(Conv2D(128, (4, 1), activation='relu'))
model_cnn.add(MaxPooling2D(pool_size=(1, 1)))
model_cnn.add(Flatten())
model_cnn.add(Dense(500, activation='relu'))
model_cnn.add(Dropout(0.1))
model_cnn.add(Dense(1))
    
model_cnn.compile(loss='mean_squared_error', optimizer=Adam(lr=0.001, decay=1e-6), metrics=['accuracy'])
monitor = EarlyStopping(monitor='val_loss', min_delta=1e-3, patience=2, verbose=2, mode='auto')

start_time = time.time()

#model_cnn.fit(x_train1,y_train1,validation_data=(x_test,y_test),callbacks=[monitor,checkpointer],verbose=2, epochs=10) 
model_cnn.fit(x_train1,y_train1,batch_size=batch_size,epochs=10,verbose=2,callbacks=[monitor,checkpointer],validation_data=(x_test1,y_test1))

elapsed_time = time.time() - start_time
print("Elapsed time: {}".format(hms_string(elapsed_time)))
model_cnn.load_weights('best_weights_cnn_extra.hdf5') # load weights from best model



pred = model_cnn.predict(x_test1)
score = np.sqrt(metrics.mean_squared_error(pred,y_test1))
print("Score (RMSE): {}".format(score))
print('R2 score: %2f' % r2_score(y_test1,pred))
chart_regression(pred.flatten()[0:100],y_test1[0:100])


#from keras.optimizers import Adam
# Define batch_size and # of epochs
batch_size = 128
#kernel size = 2,1 and 2,1 
#kernel number = 32,64
#activation='relu'
#optimizer='adam'
#With dropout layer
import time
checkpointer = ModelCheckpoint(filepath="best_weights_cnn_extra.hdf5", verbose=0, save_best_only=True) # save best model

model_cnn = Sequential()
model_cnn.add(Conv2D(32, kernel_size=(2, 1), strides=(1, 1),activation='relu', padding='valid',input_shape=(7,1,5)))
model_cnn.add(MaxPooling2D(pool_size=(1, 1), strides=(1, 1)))
model_cnn.add(Conv2D(64, (2, 1), activation='relu'))
model_cnn.add(MaxPooling2D(pool_size=(1, 1)))
model_cnn.add(Flatten())
model_cnn.add(Dense(1000, activation='relu'))
model_cnn.add(Dropout(0.1))
model_cnn.add(Dense(1))
    
model_cnn.compile(loss='mean_squared_error', optimizer=Adam(lr=0.001, decay=1e-6), metrics=['accuracy'])
monitor = EarlyStopping(monitor='val_loss', min_delta=1e-3, patience=2, verbose=2, mode='auto')

start_time = time.time()

#model_cnn.fit(x_train1,y_train1,validation_data=(x_test,y_test),callbacks=[monitor,checkpointer],verbose=2, epochs=10) 
model_cnn.fit(x_train1,y_train1,batch_size=batch_size,epochs=10,verbose=2,callbacks=[monitor,checkpointer],validation_data=(x_test1,y_test1))

elapsed_time = time.time() - start_time
print("Elapsed time: {}".format(hms_string(elapsed_time)))
model_cnn.load_weights('best_weights_cnn_extra.hdf5') # load weights from best model


pred = model_cnn.predict(x_test1)
score = np.sqrt(metrics.mean_squared_error(pred,y_test1))
print("Score (RMSE): {}".format(score))
print('R2 score: %2f' % r2_score(y_test1,pred))
chart_regression(pred.flatten()[0:100],y_test1[0:100])

#done everything before addititional features, now need to do after additional features - Saksham Tehri

#Preparing x and y
#SEQUENCE_SIZE = 5
#x_train2,y_train2 = to_sequences(SEQUENCE_SIZE, df_train,close_train)
#x_test2,y_test2 = to_sequences(SEQUENCE_SIZE, df_test, close_test)

#print("Shape of x_train: {}".format(x_train2.shape))
#print("Shape of x_test: {}".format(x_test2.shape))
#print("Shape of y_train: {}".format(y_train2.shape))
#print("Shape of y_test: {}".format(y_test2.shape))

SEQUENCE_SIZE = 5
x2,y2 = to_sequences(SEQUENCE_SIZE, df_stock.values, df_stock_close)

print("Shape of x: {}".format(x2.shape))
print("Shape of y: {}".format(y2.shape))

#Splitting data into 70% training and 30% test set
x_train2,x_test2,y_train2,y_test2 = train_test_split(x2,y2, test_size=0.3, random_state =42)
print("Shape of x_train: {}".format(x_train2.shape))
print("Shape of x_test: {}".format(x_test2.shape))
print("Shape of y_train: {}".format(y_train2.shape))
print("Shape of y_test: {}".format(y_test2.shape))

#LSTM neuron: 100
#Optimization: SGD
#With drop out layer

#checkpointer
checkpointer = ModelCheckpoint(filepath="best_weights.hdf5", verbose=0, save_best_only=True) # save best model
for i in range(5):
    print(i)    
    print('Build model...')
    model = Sequential()
    model.add(LSTM(100, dropout=0.1, recurrent_dropout=0.1, input_shape=(SEQUENCE_SIZE, 5)))
    model.add(Dense(50))
    model.add(Dropout(0.1))
    model.add(Dense(1))
    model.compile(loss='mean_squared_error', optimizer='adam')
    monitor = EarlyStopping(monitor='val_loss', min_delta=1e-3, patience=5, verbose=1, mode='auto')
    print('Train...')
    model.fit(x_train2,y_train2,validation_data=(x_test2,y_test2),callbacks=[monitor,checkpointer],verbose=2, epochs=10) 
model.load_weights('best_weights.hdf5')


pred = model.predict(x_test2)
score = np.sqrt(metrics.mean_squared_error(pred,y_test2))
print("Score (RMSE): {}".format(score))
print('R2 score: %2f' % r2_score(y_test2,pred))
chart_regression(pred.flatten()[0:100],y_test2[0:100])

#Preparing x and y
SEQUENCE_SIZE = 7
x2,y2 = to_sequences(SEQUENCE_SIZE, df_stock.values, df_stock_close)
print("Shape of x: {}".format(x2.shape))
print("Shape of y: {}".format(y2.shape))

#Splitting data into 70% training and 30% test set
x_train2,x_test2,y_train2,y_test2 = train_test_split(x2,y2, test_size=0.3, random_state =42)
print("Shape of x_train: {}".format(x_train2.shape))
print("Shape of x_test: {}".format(x_test2.shape))
print("Shape of y_train: {}".format(y_train2.shape))
print("Shape of y_test: {}".format(y_test2.shape))

#LSTM neuron: 100
#Optimization: SGD
#With drop out layer

#checkpointer
checkpointer = ModelCheckpoint(filepath="best_weights.hdf5", verbose=0, save_best_only=True) # save best model
for i in range(5):
    print(i)    
    print('Build model...')
    model = Sequential()
    model.add(LSTM(100, dropout=0.1, recurrent_dropout=0.1, input_shape=(SEQUENCE_SIZE, 5)))
    model.add(Dropout(0.1))
    model.add(Dense(50))
    model.add(Dense(1))
    model.compile(loss='mean_squared_error', optimizer='adam')
    monitor = EarlyStopping(monitor='val_loss', min_delta=1e-3, patience=5, verbose=1, mode='auto')
    print('Train...')
    model.fit(x_train2,y_train2,validation_data=(x_test2,y_test2),callbacks=[monitor,checkpointer],verbose=2, epochs=10) 
model.load_weights('best_weights.hdf5')

pred = model.predict(x_test2)
score = np.sqrt(metrics.mean_squared_error(pred,y_test2))
print("Score (RMSE): {}".format(score))
print('R2 score: %2f' % r2_score(y_test2,pred))
chart_regression(pred.flatten()[0:100],y_test2[0:100])
