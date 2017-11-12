from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from sklearn.model_selection import train_test_split
import numpy as np
import tensorflow as tf
import pickle

tf.logging.set_verbosity(tf.logging.INFO)

def new_biases(length):
    return tf.Variable(tf.constant(0.05, shape=[length]))

def cnn_model_fn(features, labels, mode):
  # Input Layer
  input_layer = tf.reshape(features["x"], [-1, 64, 64, 1])


  # ______Convolutional Layer #1______
  conv1 = tf.layers.conv2d(
      inputs=input_layer,
      filters=96,
      kernel_size=[7, 7],
      padding="same",
      kernel_initializer=tf.truncated_normal_initializer(stddev=0.05),
      bias_initializer=tf.random_uniform_initializer(minval=0.0, maxval=0.05),
      activation=tf.nn.relu)
  # ______Pooling Layer #1____________
  pool1 = tf.layers.max_pooling2d(inputs=conv1, pool_size=[3, 3], strides=3, padding="same")
  normd1 = tf.nn.local_response_normalization(
          input = pool1,
          name="norm1")


  # ______Convolutional Layer #2______
  conv2 = tf.layers.conv2d(
      inputs=normd1,
      filters=256,
      kernel_size=[5, 5],
      padding="same",
      kernel_initializer=tf.truncated_normal_initializer(stddev=0.05),
      bias_initializer=tf.random_uniform_initializer(minval=0.0, maxval=0.05),
      activation=tf.nn.relu)
  # ______Pooling Layer #2____________
  pool2 = tf.layers.max_pooling2d(inputs=conv2, pool_size=[3, 3], strides=3, padding="same")


  # ______Convolutional Layer #3______
  conv3 = tf.layers.conv2d(
      inputs=normd1,
      filters=384,
      kernel_size=[3, 3],
      padding="same",
      kernel_initializer=tf.truncated_normal_initializer(stddev=0.05),
      bias_initializer=tf.random_uniform_initializer(minval=0.0, maxval=0.05),
      activation=tf.nn.relu)


  # ______Convolutional Layer #4______
  conv4 = tf.layers.conv2d(
      inputs=normd1,
      filters=256,
      kernel_size=[3, 3],
      padding="same",
      kernel_initializer=tf.truncated_normal_initializer(stddev=0.05),
      bias_initializer=tf.random_uniform_initializer(minval=0.0, maxval=0.05),
      activation=tf.nn.relu)
  # ______Pooling Layer #3____________
  pool3 = tf.layers.max_pooling2d(inputs=conv4, pool_size=[3, 3], strides=3, padding="same")


  # ______Flatten tensor into a batch of vectors______
  pool3_flat = tf.reshape(pool3, [-1, 16 * 16 * 64])


  # ______Dense Layer1 #1_____________
  dense1 = tf.layers.dense(inputs=pool3_flat, units=4096, activation=tf.nn.relu)

  # Add dropout operation #1; 0.6 probability that element will be kept
  dropout1 = tf.layers.dropout(
      inputs=dense1, rate=0.5, training=mode == tf.estimator.ModeKeys.TRAIN)

  # ______Dense Layer1 #2_____________
  dense2 = tf.layers.dense(inputs=dropout1, units=4096, activation=tf.nn.relu)

  # Add dropout operation #2; 0.6 probability that element will be kept
  dropout2 = tf.layers.dropout(
      inputs=dense2, rate=0.5, training=mode == tf.estimator.ModeKeys.TRAIN)

#  #Dense round 2
#  dense2 = tf.layers.dense(inputs=dropout, units=512, activation=tf.nn.relu)
#
#  # Add dropout operation; 0.6 probability that element will be kept
#  dropout2 = tf.layers.dropout(
#      inputs=dense2, rate=0.4, training=mode == tf.estimator.ModeKeys.TRAIN)
  # Logits layer
  # Input Tensor Shape: [batch_size, 1024]
  # Output Tensor Shape: [batch_size, 10]
  # NEW Input Tensor Shape: [batch_size, 1024]
  # NEW Output Tensor Shape: [batch_size, 40]
  logits = tf.layers.dense(inputs=dropout2, units=82)

  predictions = {
      # Generate predictions (for PREDICT and EVAL mode)
      "classes": tf.argmax(input=logits, axis=1),
      # Add `softmax_tensor` to the graph. It is used for PREDICT and by the
      # `logging_hook`.
      "probabilities": tf.nn.softmax(logits, name="softmax_tensor")
  }
  if mode == tf.estimator.ModeKeys.PREDICT:
    return tf.estimator.EstimatorSpec(mode=mode, predictions=predictions)

  # Calculate Loss (for both TRAIN and EVAL modes)
  onehot_labels = tf.one_hot(indices=tf.cast(labels, tf.int32), depth=82)
  loss = tf.losses.softmax_cross_entropy(
      onehot_labels=onehot_labels, logits=logits)

    #onehot fix?
#  onehot_labels = tf.one_hot(indices=outcomes_vector, depth=40)
#  loss = tf.losses.softmax_cross_entropy(
#      onehot_labels=onehot_labels, logits=logits)
  # Configure the Training Op (for TRAIN mode)
  ##modified GradientDescentOptimizer(learning_rate=0.0001) for adamoptimizer
  if mode == tf.estimator.ModeKeys.TRAIN:
    optimizer = tf.train.AdamOptimizer(learning_rate=0.001)
    train_op = optimizer.minimize(
        loss=loss,
        global_step=tf.train.get_global_step())
    return tf.estimator.EstimatorSpec(mode=mode, loss=loss, train_op=train_op)

  # Add evaluation metrics (for EVAL mode)
  eval_metric_ops = {
      "accuracy": tf.metrics.accuracy(
          labels=labels, predictions=predictions["classes"])}
  return tf.estimator.EstimatorSpec(
      mode=mode, loss=loss, eval_metric_ops=eval_metric_ops)



def main(unused_argv):
  # Load training and eval data
    
  #____________________________________________________________________________________________________
  #____________________________________________________________________________________________________
  #THESE PATHS MIGHT BE WRONG FOR YOU. MAKE SURE YOU CHANGE THEM TO THE CORRECT ONES.
  x_in = open('../data/pkl/x_train_data.pkl','rb')
  y_in = open('../data/pkl/y_train_data.pkl', 'rb')

  x = pickle.load(x_in) # load from text
  print('done loading x data')
  y = pickle.load(y_in)
  print('done loading y data')
  x = np.asarray(x, dtype=np.float32)
  y = np.asarray(y, dtype=np.int32)
  #y = y.reshape(-1)
  #x = x.reshape(-1, 64, 64) # reshape
  ###Testing for encoding issues
#  outcomes_vector = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 20, 21, 24, 25, 27, 28, 30, 32, 35, 36, 40, 42, 45, 48, 49, 54, 56, 63, 64, 72, 81]
#  outcomes_vector =np.asarray(outcomes_vector, dtype=np.int32)
  train_data, eval_data, train_labels, eval_labels = train_test_split(x, y, test_size=0.25)
#  mnist = tf.contrib.learn.datasets.load_dataset("mnist")
#  train_data = mnist.train.images  # Returns np.array
#  train_labels = np.asarray(mnist.train.labels, dtype=np.int32)
#  eval_data = mnist.test.images  # Returns np.array
#  eval_labels = np.asarray(mnist.test.labels, dtype=np.int32)

  # Create the Estimator
  # to start from scratch change the model number each time.

  #____________________________________________________________________________________________________
  #____________________________________________________________________________________________________
  #RIGHT HERE IS WHERE YOU HAVE TO CHANGE TO MODEL NUMBER EACH TIME
  #IF YOU DONT IT WILL KEEP THE STORED LOSS FROM THE MODEL AND ITLL LOOK LIKE YOU ARE MAKING 
  #MORE PROGRESS THAN YOU ACTUALLY ARE. change the line model_dir="/tmp/comp551_convnet_model1" to
  #something like model_dir="/tmp/comp551_convnet_model2"
  mnist_classifier = tf.estimator.Estimator(
      model_fn=cnn_model_fn, model_dir="/tmp/comp551_convnet_model1")

  # Set up logging for predictions
  # Log the values in the "Softmax" tensor with label "probabilities"
  tensors_to_log = {"probabilities": "softmax_tensor"}
  logging_hook = tf.train.LoggingTensorHook(
      tensors=tensors_to_log, every_n_iter=50)

  # Train the model
  train_input_fn = tf.estimator.inputs.numpy_input_fn(
      x={"x": train_data},
      y=train_labels,
      batch_size=50,
      num_epochs=None,
      shuffle=True)

  #the number of steps of training is a hyperparameter! gotta find the best. 10,000 is a lot and will need
  # a large GPU to do it. it'd take 4 hours on a macbook. 
  mnist_classifier.train(
      input_fn=train_input_fn,
      steps=10000
      #steps=500,
      hooks=[logging_hook])

  # Evaluate the model and print results
  eval_input_fn = tf.estimator.inputs.numpy_input_fn(
      x={"x": eval_data},
      y=eval_labels,
      num_epochs=1,
      shuffle=False)
  eval_results = mnist_classifier.evaluate(input_fn=eval_input_fn)
  print(eval_results)


if __name__ == "__main__":
  tf.app.run()
