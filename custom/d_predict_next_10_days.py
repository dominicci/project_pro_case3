import matplotlib.pyplot as plt
import numpy as np

from b_tf_model import test_scaler, model, X_test, actual_btc_price, predicted_btc_price

#set the days to predict
days_to_predict = 10

#use index slicing to select the last 10 days of the test set
last_days = X_test[X_test.shape[0] - days_to_predict :  ]

future_forecast = []

for i in range(10):  
  predicted_days = model.predict(last_days[i:i+1])
  predicted_days = np.repeat(predicted_days, X_test.shape[2], axis=-1)
  predicted_days = test_scaler.inverse_transform(predicted_days)[:,0]

  future_forecast.append(predicted_days)

# convert future_forecast to a single array
future_forecast = np.array(future_forecast)

# flatten future_forecast array
future_forecast = future_forecast.flatten()

# flatten predicted_btc_price array
predicted_btc_price = predicted_btc_price.flatten()

#concatenate both data
concat_test_df = np.concatenate((predicted_btc_price, future_forecast))

#visualize the prediction result
plt.figure(figsize=(16,7))
plt.plot(actual_btc_price, marker='.', label='actual bitcoin prices')
plt.plot(concat_test_df, marker='.', label='predicted bitcoin prices')
plt.title('Bitcoin Prediction')
plt.xlabel('Time')
plt.ylabel('Price')
plt.legend(loc='upper right')
plt.show()