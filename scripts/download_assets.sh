#!/bin/bash
# Download NVIDIA Isaac ROS Visual SLAM model assets from NGC

set -e

NGC_ORG="nvidia"
NGC_TEAM="isaac"
PACKAGE="isaac_ros_visual_slam"
RESOURCE="isaac_ros_visual_slam_assets"
ARCHIVE="quickstart.tar.gz"
TARGET_MAJOR=3
TARGET_MINOR=2

echo "▸ Querying NGC for available versions..."
API_URL="https://catalog.ngc.nvidia.com/api/resources/versions?orgName=$NGC_ORG&teamName=$NGC_TEAM&name=$RESOURCE&isPublic=true&pageNumber=0&pageSize=100&sortOrder=CREATED_DATE_DESC"

VERSIONS_JSON=$(curl -s -H "Accept: application/json" "$API_URL")

MATCHED_VERSION=$(echo $VERSIONS_JSON | jq -r "
    .recipeVersions[]
    | .versionId as \$v
    | \$v | select(test(\"^\\\\d+\\\\.\\\\d+\\\\.\\\\d+$\"))
    | split(\".\") | {major: .[0]|tonumber, minor: .[1]|tonumber, patch: .[2]|tonumber}
    | select(.major == $TARGET_MAJOR and .minor <= $TARGET_MINOR)
    | \$v
    " | sort -V | tail -n 1
)

if [ -z "$MATCHED_VERSION" ]; then
    echo "✗ No compatible version found for Isaac ROS $TARGET_MAJOR.$TARGET_MINOR"
    echo "  Available versions:"
    echo "$VERSIONS_JSON" | jq -r '.recipeVersions[].versionId'
    exit 1
fi

echo "▸ Downloading assets v$MATCHED_VERSION..."
mkdir -p ${ISAAC_ROS_WS}/isaac_ros_assets

DOWNLOAD_URL="https://api.ngc.nvidia.com/v2/resources/$NGC_ORG/$NGC_TEAM/$RESOURCE/versions/$MATCHED_VERSION/files/$ARCHIVE"

curl -LO --request GET "$DOWNLOAD_URL"
tar -xf "$ARCHIVE" -C ${ISAAC_ROS_WS}/isaac_ros_assets
rm "$ARCHIVE"

echo "✓ Assets installed to ${ISAAC_ROS_WS}/isaac_ros_assets"
