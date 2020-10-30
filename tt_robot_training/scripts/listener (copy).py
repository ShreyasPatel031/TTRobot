#!/usr/bin/env python

import tf
import rospy
from geometry_msgs.msg import TwistStamped
from gazebo_msgs.srv import GetModelState

from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam

states = 12
actions = 6
learn_rate = 0.001

def huber_loss( y_true, y_pred, clip_delta=1.0):
    error = y_true - y_pred
    cond  = K.abs(error) <= clip_delta
    squared_loss = 0.5 * K.square(error)
    quadratic_loss = 0.5 * K.square(clip_delta) + clip_delta * (K.abs(error) - clip_delta)
    return K.mean(tf.where(cond, squared_loss, quadratic_loss))

def init_model(  ):
    model = Sequential()
    model.add(Dense(128, input_dim=states, activation='relu'))
    model.add(Dense(64, activation='relu'))
    model.add(Dense(32, activation='relu'))
    model.add(Dense(actions, activation='tanh'))
    model.compile(
                loss=huber_loss,
                optimizer=Adam(lr=learn_rate))
    return model

def node( curr_model ):

    print(curr_model)

    rospy.init_node('listener')
    
    listener = tf.TransformListener()

    pub = rospy.Publisher('/servo_server/delta_twist_cmds', TwistStamped, queue_size=3)

    listener.waitForTransform( '/tool0','/world', rospy.Time(0), rospy.Duration(3)  )

    try:
        model_coordinates = rospy.ServiceProxy('/gazebo/get_model_state', GetModelState)
    except rospy.ServiceException as e:
            rospy.loginfo("Get Model State service call failed:  {0}".format(e))

    msg = TwistStamped()

    rate = rospy.Rate(1000)

    (trans,rot) = listener.lookupTransform( '/tool0','/world', rospy.Time(0))

    

    while not rospy.is_shutdown():

        ball = model_coordinates('table_tennis_ball', 'ground_plane')

        print(ball.twist.linear.z)

        msg.twist.linear.x = 0
        msg.twist.linear.y = 0
        msg.twist.linear.z = ball.twist.linear.z

        msg.twist.angular.x = 0
        msg.twist.angular.y = 0
        msg.twist.angular.z = 0

        for i in range(0,100) : pub.publish( msg )

        # rostopic pub -r 100 /servo_server/delta_twist_cmds geometry_msgs/TwistStamped "header: auto
        # twist:
        #   linear:
        #     x: 0.0
        #     y: 0.01
        #     z: 4
        #   angular:
        #     x: 0.0
        #     y: 0.0
        #     z: 0.0"
            
        rate.sleep()

if __name__ == '__main__':
    print("hello")
    try:
        node( init_model() )
    except rospy.ROSInterruptException:
        pass
    print("bye")