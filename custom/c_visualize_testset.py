from b_tf_model import actual_btc_price, predicted_btc_price
import matplotlib.pyplot as plt

#visualize the testset result
plt.figure(figsize=(16,7))
plt.plot(actual_btc_price, label='actual bitcoin prices')
plt.plot(predicted_btc_price, label='predicted bitcoin prices')
plt.title('Bitcoin Prediction')
plt.xlabel('Time')
plt.ylabel('Price')
plt.legend(loc='upper right')
plt.show()