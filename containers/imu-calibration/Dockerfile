# IMU Calibration Container
# Allan Variance analysis for RealSense D435i IMU characterization
FROM ubuntu:focal

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y git sudo python3 python3-pip net-tools vim nano

RUN apt-get update && apt-get install -y debconf-utils && \
    echo 'keyboard-configuration keyboard-configuration/layoutcode select us' | debconf-set-selections && \
    echo 'keyboard-configuration keyboard-configuration/model select Generic 105-key PC (intl.)' | debconf-set-selections

RUN apt-get update && apt-get install -y locales tzdata && \
    locale-gen en_US en_US.UTF-8 && \
    update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8 && \
    ln -fs /usr/share/zoneinfo/Asia/Kolkata /etc/localtime && \
    dpkg-reconfigure --frontend noninteractive tzdata
ENV LANG=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8

# Non-root user
RUN useradd -m calibrator && echo "calibrator:calibrator" | chpasswd && adduser calibrator sudo
RUN echo "calibrator ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
USER calibrator

# ROS 2 setup
RUN sudo apt-get update && sudo apt-get install -y gnupg wget software-properties-common && \
    sudo add-apt-repository universe

RUN wget -qO - https://isaac.download.nvidia.com/isaac-ros/repos.key | sudo apt-key add - && \
    grep -qxF "deb https://isaac.download.nvidia.com/isaac-ros/ubuntu/main $(lsb_release -cs) main" /etc/apt/sources.list || \
    echo "deb https://isaac.download.nvidia.com/isaac-ros/ubuntu/main $(lsb_release -cs) main" | sudo tee -a /etc/apt/sources.list && \
    sudo apt-get update && sudo apt-get install curl -y && \
    sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

RUN sudo apt-get update && sudo apt-get install -y ros-humble-desktop ros-humble-realsense2-camera ros-humble-rviz2

WORKDIR /home/calibrator
RUN git clone https://github.com/jenarohi/VSLAM-UAV.git

RUN sudo apt-get update && sudo apt-get install -y python3-scipy python3-rosdep python3-colcon-common-extensions
RUN sudo rm -rf /var/lib/apt/lists/* && sudo apt-get clean

# Allan variance workspace
WORKDIR /home/calibrator/ros2_ws/src
RUN git clone https://github.com/PX4/px4_msgs.git && \
    git clone https://github.com/CruxDevStuff/allan_ros2.git && \
    git clone --recurse-submodules https://github.com/IMRCLab/motion_capture_tracking.git
WORKDIR /home/calibrator/ros2_ws/src/px4_msgs
RUN git reset --hard 87741f4
WORKDIR /home/calibrator/ros2_ws/src/motion_capture_tracking
RUN git reset --hard 35adc3e && git submodule update --init --recursive

WORKDIR /home/calibrator/ros2_ws
RUN sudo rosdep init && rosdep update && \
    /bin/bash -c "source /opt/ros/humble/setup.bash && rosdep install --from-paths src -y --ignore-src" && \
    /bin/bash -c "source /opt/ros/humble/setup.bash && colcon build --symlink-install"

RUN cp -r /home/calibrator/ros2_ws/src/motion_capture_tracking/motion_capture_tracking_interfaces /home/calibrator/VSLAM-UAV/tools
RUN pip3 install pandas rosbags numpy==1.21

RUN echo "source /opt/ros/humble/setup.bash" >> /home/calibrator/.bashrc && \
    echo "source /home/calibrator/ros2_ws/install/setup.bash" >> /home/calibrator/.bashrc && \
    echo "export ROS_DOMAIN_ID=\${ROS_DOMAIN_ID:-1}" >> /home/calibrator/.bashrc

WORKDIR /home/calibrator/VSLAM-UAV
ENTRYPOINT ["/bin/bash"]
