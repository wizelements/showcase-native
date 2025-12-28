#!/data/data/com.termux/files/usr/bin/bash
#
# ✨ Quick Dependency Installer for Showcase
# Installs all required packages for the Kivy app
#

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo ""
echo "✨ ═══════════════════════════════════════════════════════ ✨"
echo ""
echo "    SHOWCASE DEPENDENCY INSTALLER"
echo ""
echo "✨ ═══════════════════════════════════════════════════════ ✨"
echo ""

# Step 1: Update packages
echo -e "${BLUE}[1/5]${NC} Updating package lists..."
pkg update -y

# Step 2: Install x11-repo for SDL2 packages
echo -e "${BLUE}[2/5]${NC} Installing x11-repo (required for SDL2)..."
pkg install -y x11-repo

# Step 3: System packages
echo -e "${BLUE}[3/5]${NC} Installing system packages..."
pkg install -y \
    python \
    clang \
    make \
    cmake \
    libffi \
    openssl \
    libjpeg-turbo \
    zlib \
    pkg-config \
    git \
    wget

# Step 4: Install Kivy from TUR packages (pre-built, fast!)
echo -e "${BLUE}[4/5]${NC} Installing Kivy and dependencies..."
pkg install -y python-kivy

# This also installs: sdl2, sdl2-image, sdl2-mixer, sdl2-ttf, python-pillow

# Step 5: Install additional Python packages
echo -e "${BLUE}[5/5]${NC} Installing Python packages..."
pip install --upgrade pip
pip install qrcode pyyaml buildozer cython

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${GREEN}  ✓ All dependencies installed!${NC}"
echo ""
echo "  Verify installation:"
echo -e "    ${BLUE}python -c \"import kivy; print(kivy.__version__)\"${NC}"
echo ""
echo "  Test the app:"
echo -e "    ${BLUE}./test-app.sh${NC}"
echo ""
echo "  Build APK:"
echo -e "    ${BLUE}./setup-android-env.sh  # First time only${NC}"
echo -e "    ${BLUE}./build-apk.sh${NC}"
echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
