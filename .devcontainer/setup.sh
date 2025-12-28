#!/bin/bash
set -e

echo "=== Setting up Buildozer environment ==="

# Install system dependencies
sudo apt-get update
sudo apt-get install -y \
    build-essential \
    git \
    zip \
    unzip \
    autoconf \
    libtool \
    pkg-config \
    zlib1g-dev \
    libncurses5-dev \
    libncursesw5-dev \
    libtinfo5 \
    cmake \
    libffi-dev \
    libssl-dev \
    automake \
    lld

# Install Python dependencies
pip install --upgrade pip
pip install buildozer cython

# Install Android SDK command-line tools
mkdir -p ~/android-sdk/cmdline-tools
cd ~/android-sdk/cmdline-tools
wget -q https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip -O cmdline-tools.zip
unzip -q cmdline-tools.zip
mv cmdline-tools latest
rm cmdline-tools.zip

# Set environment variables
export ANDROID_HOME=~/android-sdk
export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools

# Accept licenses and install required SDK components
yes | sdkmanager --licenses || true
sdkmanager "platform-tools" "platforms;android-31" "build-tools;33.0.2" "ndk;25.2.9519653"

echo ""
echo "=== Setup complete! ==="
echo "Run: ./build-codespaces.sh"
