#!/usr/bin/env python2

import tf
import rospy
from geometry_msgs.msg import TwistStamped


def node():

    rospy.init_node('listener')
    
    listener = tf.TransformListener()

    pub = rospy.Publisher('/servo_server/delta_twist_cmds', TwistStamped, queue_size=1)

    listener.waitForTransform( '/tool0','/world', rospy.Time(0), rospy.Duration(3)  )

    msg = TwistStamped()

    rate = rospy.Rate(10)

    while not rospy.is_shutdown():

        (trans,rot) = listener.lookupTransform( '/tool0','/world', rospy.Time(0))

        print(trans,rot)

        # msg.header

        msg.twist.linear.x = 0.1
        msg.twist.linear.y = 0.1
        msg.twist.linear.z = 0.1

        msg.twist.angular.x = 0
        msg.twist.angular.y = 0
        msg.twist.angular.z = 0

        pub.publish( msg )

        # rostopic pub -r 100 /servo_server/delta_twist_cmds geometry_msgs/TwistStamped "header: auto
        # twist:
        #   linear:
        #     x: 0.0
        #     y: 0.01
        #     z: -0.01
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