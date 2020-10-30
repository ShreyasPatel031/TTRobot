#!/usr/bin/env python

import tf
import rospy
from geometry_msgs.msg import TwistStamped
from gazebo_msgs.srv import GetModelState


def node():

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
        node()
    except rospy.ROSInterruptException:
        pass
    print("bye")