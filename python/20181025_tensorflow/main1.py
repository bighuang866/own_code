# -*- coding: utf-8 -*-
# @Time    : 2018/10/25 18:53
# @Author  : Big Huang
# @Email   : kenhuang866@qq.com
# @File    : main.py
# @Software: PyCharm Community Edition
import tensorflow as tf
x = tf.Variable(3, name="x")
y = tf.Variable(4, name="y")
f = x*x*y + y + 2

sess = tf.Session()
sess.run(x.initializer)
sess.run(y.initializer)
result = sess.run(f)
print(result)
sess.close()


with tf.Session() as sess:
    x.initializer.run()
    y.initializer.run()
    result = f.eval()
print(result)


init = tf.global_variables_initializer()
with tf.Session() as sess:
    init.run()
    result = f.eval()
print(result)


w = tf.constant(3)
x = w + 2
y = x + 5
z = x * 3
with tf.Session() as sess:
    y_val, z_val = sess.run([y, z])
    print(y_val, z_val)