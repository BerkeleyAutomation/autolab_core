#!/usr/bin/env python

""" Buffers ROS TF and provides a service to get transforms
"""

import rospy
import tf2_ros

try:
    from autolab_core.srv import (
        RigidTransformListener,
        RigidTransformListenerResponse,
    )
except ImportError:
    raise RuntimeError(
        "rigid_transform_ros_listener service unavailable outside of "
        "catkin package"
    )

if __name__ == "__main__":
    rospy.init_node("rigid_transform_listener")

    tfBuffer = tf2_ros.Buffer()
    listener = tf2_ros.TransformListener(tfBuffer)

    def handle_request(req):
        trans = tfBuffer.lookup_transform(
            req.from_frame, req.to_frame, rospy.Time()
        )
        return RigidTransformListenerResponse(
            trans.transform.translation.x,
            trans.transform.translation.y,
            trans.transform.translation.z,
            trans.transform.rotation.w,
            trans.transform.rotation.x,
            trans.transform.rotation.y,
            trans.transform.rotation.z,
        )

    s = rospy.Service(
        "rigid_transform_listener", RigidTransformListener, handle_request
    )

    rospy.spin()
