# VSLAM Core Container
# Intel RealSense D435i driver + ROS 2 camera node
FROM ubuntu:focal

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y git sudo net-tools vim nano

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

RUN apt-get update && apt-get install -y gnupg wget software-properties-common && \
    add-apt-repository universe

RUN wget -qO - https://isaac.download.nvidia.com/isaac-ros/repos.key | apt-key add - && \
    grep -qxF "deb https://isaac.download.nvidia.com/isaac-ros/ubuntu/main $(lsb_release -cs) main" /etc/apt/sources.list || \
    echo "deb https://isaac.download.nvidia.com/isaac-ros/ubuntu/main $(lsb_release -cs) main" | tee -a /etc/apt/sources.list && \
    apt-get update && apt-get install curl -y && \
    curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | tee /etc/apt/sources.list.d/ros2.list > /dev/null

RUN apt-get update && apt-get install -y ros-humble-desktop

COPY scripts/ /opt/realsense/
RUN chmod +x /opt/realsense/*.sh && \
    /opt/realsense/install-realsense-dependencies.sh; \
    /opt/realsense/build-librealsense.sh -n -v v2.55.1;

RUN mkdir -p /opt/realsense/
COPY scripts/hotplug-realsense.sh /opt/realsense/hotplug-realsense.sh
COPY udev_rules/99-realsense-libusb-custom.rules /etc/udev/rules.d/99-realsense-libusb.rules

RUN apt-get install python3-colcon-common-extensions ros-humble-diagnostic-updater -y
RUN rm -rf /var/lib/apt/lists/* && apt-get clean

# Setup non-root user
RUN useradd -m jetson && echo "jetson:jetson" | chpasswd && adduser jetson sudo
RUN echo "jetson ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
USER jetson

# Build RealSense ROS wrapper
WORKDIR /home/jetson
RUN mkdir -p ros2_ws/src && cd ros2_ws/src && \
    git clone https://github.com/IntelRealSense/realsense-ros.git -b 4.51.1

WORKDIR /home/jetson/ros2_ws
RUN /bin/bash -c "source /opt/ros/humble/setup.bash && colcon build --symlink-install"

# Pull project files
WORKDIR /home/jetson
RUN git clone https://github.com/jenarohi/VSLAM-UAV.git

WORKDIR /home/jetson/VSLAM-UAV

RUN echo "source /opt/ros/humble/setup.bash" >> /home/jetson/.bashrc && \
    echo "source /home/jetson/ros2_ws/install/setup.bash" >> /home/jetson/.bashrc && \
    echo "export ROS_DOMAIN_ID=\${ROS_DOMAIN_ID:-1}" >> /home/jetson/.bashrc

ENTRYPOINT ["/bin/bash"]
