
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import StandardScaler
from keras.models import Sequential
from keras.layers import Dense, LSTM, Dropout
from a_get_data import btc_df


#Use 80% of the dataframe as training size and 20% as test size
train_size = int(len(btc_df)*0.90)
test_size = len(btc_df) - train_size

#Use index slicing to select the head/older set of data as traing set
df_train= btc_df[:len(btc_df)-test_size].values
df_train.shape

#Use index slicing to select the tail/newer set of data as test set
df_test= btc_df[len(btc_df)-test_size:].values
df_test.shape

#Using MinMaxScaler to normalize data between 0 & 1
train_scaler = MinMaxScaler(feature_range=(0, 1))
scaled_train = train_scaler.fit_transform(df_train)

test_scaler = MinMaxScaler(feature_range=(0, 1))
scaled_test = test_scaler.fit_transform(df_test)

#create dataset in time series for LSTM model 
def generate_lstm(scaled_data, look_back_days, future = 1):

  #Empty lists to be populated using formatted training data
  trainX = []
  trainY = []

  # look_back_days = Number of past days we want to use to predict the future.
  # future = Number of days in the future we want to look into based on the past days.

  #Reformat input data into a shape: (n_samples x timesteps x n_features)
  for i in range(look_back_days, len(scaled_data) - future +1):
      trainX.append(scaled_data[i - look_back_days:i, 0:btc_df.shape[1]])
      trainY.append(scaled_data[i + future - 1:i + future, 0])
      

  return np.array(trainX), np.array(trainY)

#Taking 14 days price into one window
look_back_days = 10

# splitting the scaled_train data into windows 
X_train, y_train = generate_lstm(scaled_train,look_back_days)

# splitting the scaled_test data into windows 
X_test, y_test = generate_lstm(scaled_test,look_back_days)

# Creating LSTM model using keras
model = Sequential()
model.add(LSTM(units=64,return_sequences=True,input_shape=(X_train.shape[1],X_train.shape[2]), activation = 'relu'))
model.add(Dropout(0.2))
model.add(LSTM(units=50,return_sequences=True))
model.add(Dropout(0.2))
model.add(LSTM(units=50))
model.add(Dropout(0.2))
model.add(Dense(units=1))
# model.summary()

# compile the model
model.compile(loss='mean_squared_error',optimizer='adam')

#train the model
model.fit(X_train,y_train,validation_split=0.20,epochs=50,batch_size=15)


# Making the predictions on test data
predicted_btc_price = model.predict(X_test)

#make 6 copies of the predicted_btc_price
prediction_copies = np.repeat(predicted_btc_price, X_test.shape[2], axis=-1)

# Transform data to the original form 
predicted_btc_price = test_scaler.inverse_transform(prediction_copies)[:,0]

#make 6 copies of the train label
train_label = np.repeat(y_test, X_test.shape[2], axis=-1)

# Transform data to the original form 
actual_btc_price = test_scaler.inverse_transform(train_label)[:,0]
