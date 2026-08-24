
#include <chrono>
#include <cmath>
#include <string>

#include "tf2_ros/buffer.h"
#include "tf2_ros/transform_listener.h"
#include <geometry_msgs/msg/twist.hpp>
#include <rclcpp/rclcpp.hpp>
#include <tf2/LinearMath/Matrix3x3.h>
#include <tf2/LinearMath/Quaternion.h>

class RobotChaseNode : public rclcpp::Node {
public:
  RobotChaseNode() : Node("robot_chase_node") {
    // TF
    tf_buffer_ = std::make_unique<tf2_ros::Buffer>(this->get_clock());
    tf_listener_ = std::make_shared<tf2_ros::TransformListener>(*tf_buffer_);

    // Init command Publisher
    command_publisher_ =
        this->create_publisher<geometry_msgs::msg::Twist>("/rick/cmd_vel", 10);
    auto timer_period = std::chrono::milliseconds(500);
    timer_ =
        this->create_wall_timer(timer_period, [this] { timer_callback(); });

    RCLCPP_INFO(this->get_logger(), "Node started");
  }

private:
  std::unique_ptr<tf2_ros::Buffer> tf_buffer_;
  std::shared_ptr<tf2_ros::TransformListener> tf_listener_;

  rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr command_publisher_;
  rclcpp::TimerBase::SharedPtr timer_;

  std::string fixed_frame_ = "rick/base_link";
  std::string target_frame_ = "morty/base_link";
  void timer_callback() {

    // Look up for the transformation between target_frame and turtle2 frames
    // and send velocity commands for turtle2 to reach target_frame
    try {
      auto transform = tf_buffer_->lookupTransform(fixed_frame_, target_frame_,
                                                   tf2::TimePointZero);
      RCLCPP_INFO(this->get_logger(), "Transform %s -> %s",
                  target_frame_.c_str(), fixed_frame_.c_str());

      RCLCPP_INFO(this->get_logger(), "Position: x=%.3f, y=%.3f, z=%.3f",
                  transform.transform.translation.x,
                  transform.transform.translation.y,
                  transform.transform.translation.z);
      RCLCPP_INFO(
          this->get_logger(), "Rotation: x=%.3f, y=%.3f, z=%.3f, w=%.3f",
          transform.transform.rotation.x, transform.transform.rotation.y,
          transform.transform.rotation.z, transform.transform.rotation.w);
    } catch (const tf2::TransformException &ex) {
      RCLCPP_INFO(this->get_logger(), "Could not transform %s to %s: %s",
                  target_frame_.c_str(), fixed_frame_.c_str(), ex.what());
      return;
    }
  }
};

int main(int argc, char *argv[]) {
  rclcpp::init(argc, argv);
  auto node = std::make_shared<RobotChaseNode>();

  rclcpp::spin(node);

  rclcpp::shutdown();
  return 0;
}