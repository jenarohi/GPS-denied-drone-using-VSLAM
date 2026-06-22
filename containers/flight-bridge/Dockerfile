# Flight Bridge Container
# MAVROS + mavrospy for PX4 communication and autonomous flight patterns
FROM ros:humble

ENV DEBIAN_FRONTEND=noninteractive

# Core dependencies
RUN apt-get update && apt-get install -y \
    sudo wget git net-tools python3-pip nano vim \
    ros-dev-tools ros-humble-rviz2 ros-humble-topic-tools \
    python3-vcstool python3-rosinstall-generator python3-osrf-pycommon \
    ros-humble-tf-transformations

# Non-root user with serial port access
RUN useradd -m jetson && echo "jetson:jetson" | chpasswd && adduser jetson sudo && \
    echo "jetson ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers && \
    usermod -aG dialout jetson

WORKDIR /home/jetson/ros2_ws/src
RUN mkdir -p /home/jetson/ros2_ws/src && chown -R jetson:jetson /home/jetson/ros2_ws
USER jetson

# Python dependencies
RUN pip install --user -U empy==3.3.4 pyros-genmsg setuptools packaging pymavlink transforms3d

# Build MAVROS + mavrospy workspace
WORKDIR /home/jetson/ros2_ws/src
RUN git clone -b ros2 https://github.com/jenarohi/mavrospy.git && \
    git clone --recurse-submodules https://github.com/IMRCLab/motion_capture_tracking.git
WORKDIR /home/jetson/ros2_ws
RUN rosinstall_generator --format repos mavlink | tee /tmp/mavlink.repos && \
    rosinstall_generator --format repos --upstream mavros | tee -a /tmp/mavros.repos && \
    vcs import src < /tmp/mavlink.repos && \
    vcs import src < /tmp/mavros.repos && \
    rosdep update && \
    rosdep install --from-paths src --ignore-src -y && \
    sudo ./src/mavros/mavros/scripts/install_geographiclib_datasets.sh
RUN /bin/bash -c "source /opt/ros/humble/setup.bash && colcon build"

# Shell setup
RUN echo "source /opt/ros/humble/setup.bash" >> /home/jetson/.bashrc && \
    echo "source /home/jetson/ros2_ws/install/setup.bash" >> /home/jetson/.bashrc && \
    echo "export FCU_URL=\${PIXHAWK_PORT:-/dev/ttyUSB0}:\${PIXHAWK_BAUD:-921600}" >> /home/jetson/.bashrc && \
    echo "export ROS_DOMAIN_ID=\${ROS_DOMAIN_ID:-1}" >> /home/jetson/.bashrc

# Pull project files
WORKDIR /home/jetson
RUN git clone https://github.com/jenarohi/VSLAM-UAV.git

RUN sudo rm -rf /var/lib/apt/lists/* && sudo apt-get clean

ENTRYPOINT ["/bin/bash"]
