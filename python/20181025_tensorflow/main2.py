# -*- coding: utf-8 -*-
# @Time    : 2018/10/25 19:12
# @Author  : Big Huang
# @Email   : kenhuang866@qq.com
# @File    : main2.py
# @Software: PyCharm Community Edition
import tensorflow as tf
import pandas as pd

import numpy as np
from sklearn.datasets import fetch_california_housing
housing = fetch_california_housing()
m, n = housing.data.shape
Y_array = housing.target.reshape(-1, 1)
constant_array = np.ones_like(Y_array)
X_array = np.c_[constant_array, housing.data]
X = tf.constant(X_array, dtype=tf.float32, name="X")
Y = tf.constant(Y_array, dtype=tf.float32, name="Y")
XT = tf.transpose(X)
theta = tf.matmul(tf.matmul(tf.matrix_inverse(tf.matmul(XT, X)), XT), Y)
with tf.Session() as sess:
    theta_value = theta.eval()
print(theta_value)


import sklearn
from sklearn.preprocessing import scale
housing = fetch_california_housing()
m, n = housing.data.shape
housing_data_plus_bias = np.c_[np.ones((m, 1)), housing.data]
scaled_housing_data_plus_bias = scale(housing_data_plus_bias)
n_epochs = 1000
learning_rate = 0.01
X = tf.constant(scaled_housing_data_plus_bias, dtype=tf.float32, name="X")
y = tf.constant(housing.target.reshape(-1, 1), dtype=tf.float32, name="y")
theta = tf.Variable(tf.random_uniform([n+1, 1], -1.0, 1.0), name="theta")
y_pred = tf.matmul(X, theta, name="predictions")
error = y_pred - y
mse = tf.reduce_mean(tf.square(error), name="mse")
gradients = 2/m * tf.matmul(tf.transpose(X), error)
training_op = tf.assign(theta, theta-learning_rate*gradients)
init = tf.global_variables_initializer()
with tf.Session() as sess:
    sess.run(init)
    for epoch in range(n_epochs):
        if epoch % 100 == 0:
            print("Epoch", epoch, "MSE = ", mse.eval())
        sess.run(training_op)
    best_theta = theta.eval()





