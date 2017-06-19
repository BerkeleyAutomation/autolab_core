#!/usr/bin/env python
""" Publisher service that takes transforms and publishes them to ROS TF periodically
"""


import logging
import rospy
import tf
import tf2_ros
import tf2_msgs
import geometry_msgs

try:
    from autolab_core.srv import *
except ImportError:
    raise RuntimeError("rigid_transform_ros_publisher service unavailable outside of catkin package")

if __name__ == '__main__':
    to_publish = {}
    
    def handle_request(req):
        mode = req.mode.lower()
        transform_key = frozenset((req.from_frame, req.to_frame))
        if mode == 'delete':
            if transform_key in to_publish:
                del to_publish[transform_key]
        elif req.mode == 'frame' or mode == 'transform':
            t = geometry_msgs.msg.TransformStamped()
            
            t.header.stamp = rospy.Time.now()
            t.header.frame_id = req.from_frame
            t.child_frame_id = req.to_frame
            
            t.transform.translation.x = req.x_trans
            t.transform.translation.y = req.y_trans
            t.transform.translation.z = req.z_trans
            t.transform.rotation.w = req.w_rot
            t.transform.rotation.x = req.x_rot
            t.transform.rotation.y = req.y_rot
            t.transform.rotation.z = req.z_rot
        
            to_publish[transform_key] = (t, mode)
        else:
            raise RuntimeError("mode {0} is not supported".format(req.mode))
        return RigidTransformPublisherResponse()
    
    rospy.init_node('rigid_transform_publisher')
    s = rospy.Service('rigid_transform_publisher', RigidTransformPublisher, handle_request)
    
    publisher = rospy.Publisher("/tf", tf2_msgs.msg.TFMessage, queue_size=1)
    publish_transform_frame = lambda msg: publisher.publish(tf2_msgs.msg.TFMessage([msg]))
    broadcaster = tf2_ros.TransformBroadcaster()
    publish_transform_transform = broadcaster.sendTransform
    
    rate_keeper = rospy.Rate(10)
    while not rospy.is_shutdown():
        for transform, mode in to_publish.values():
            if mode == 'frame':
                publish_transform = publish_transform_frame
            elif mode == 'transform':
                publish_transform = publish_transform_transform
            transform.header.stamp = rospy.Time.now()
            publish_transform(transform)
        rate_keeper.sleep()
    
