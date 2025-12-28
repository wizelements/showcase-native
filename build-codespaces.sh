#!/bin/bash
set -e

echo "╔══════════════════════════════════════════╗"
echo "║   Showcase APK Builder (Codespaces)      ║"
echo "╚══════════════════════════════════════════╝"

# Set environment
export ANDROID_HOME=~/android-sdk
export ANDROID_NDK_HOME=~/android-sdk/ndk/25.2.9519653
export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools

# Clean previous builds
echo "[1/3] Cleaning previous builds..."
rm -rf .buildozer/android/platform/build-* 2>/dev/null || true
rm -rf bin/*.apk 2>/dev/null || true

# Build
echo "[2/3] Building APK (this takes 10-20 minutes first time)..."
buildozer -v android debug 2>&1 | tee build.log

# Check result
echo "[3/3] Checking build result..."
if ls bin/*.apk 1>/dev/null 2>&1; then
    echo ""
    echo "══════════════════════════════════════════"
    echo "  ✓ BUILD SUCCESSFUL!"
    echo ""
    echo "  APK location:"
    ls -lh bin/*.apk
    echo ""
    echo "  Download the APK from the bin/ folder"
    echo "══════════════════════════════════════════"
else
    echo ""
    echo "══════════════════════════════════════════"
    echo "  ✗ Build failed. Check build.log"
    echo "══════════════════════════════════════════"
    exit 1
fi
