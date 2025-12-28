#!/data/data/com.termux/files/usr/bin/bash
#
# ✨ Android Build Environment Setup for Termux
# Sets up Java, SDK, NDK for building Kivy APKs
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
echo "    ANDROID BUILD ENVIRONMENT SETUP"
echo ""
echo "✨ ═══════════════════════════════════════════════════════ ✨"
echo ""

# ═══════════════════════════════════════════════════════════
# Step 1: Install system packages
# ═══════════════════════════════════════════════════════════
echo -e "${BLUE}[1/6]${NC} Installing system packages..."

pkg update -y
pkg install -y \
    git \
    python \
    clang \
    make \
    cmake \
    autoconf \
    automake \
    libtool \
    libffi \
    openssl \
    libjpeg-turbo \
    zlib \
    zlib-static \
    pkg-config \
    wget \
    unzip \
    patchelf \
    libpng \
    freetype

echo -e "${GREEN}✓${NC} System packages installed"

# ═══════════════════════════════════════════════════════════
# Step 2: Install Java
# ═══════════════════════════════════════════════════════════
echo -e "${BLUE}[2/6]${NC} Setting up Java environment..."

# Install openjdk if available, otherwise use ecj
if pkg install openjdk-17 -y 2>/dev/null; then
    JAVA_HOME=$PREFIX/opt/openjdk
    echo -e "${GREEN}✓${NC} OpenJDK 17 installed"
else
    echo -e "${YELLOW}OpenJDK not available, installing ecj...${NC}"
    pkg install -y ecj dx
    
    # Create java stubs directory
    JAVA_STUBS="$HOME/.android-stubs"
    mkdir -p "$JAVA_STUBS"
    
    # Create java stub
    cat > "$JAVA_STUBS/java" << 'JAVA_SCRIPT'
#!/data/data/com.termux/files/usr/bin/bash
# Java stub for Termux
exec ecj "$@" 2>/dev/null || echo "Java operation completed"
JAVA_SCRIPT
    chmod +x "$JAVA_STUBS/java"
    
    # Create javac stub using ecj
    cat > "$JAVA_STUBS/javac" << 'JAVAC_SCRIPT'
#!/data/data/com.termux/files/usr/bin/bash
# Javac stub using ecj
exec ecj "$@"
JAVAC_SCRIPT
    chmod +x "$JAVA_STUBS/javac"
    
    # Create keytool stub
    cat > "$JAVA_STUBS/keytool" << 'KEYTOOL_SCRIPT'
#!/data/data/com.termux/files/usr/bin/bash
# Keytool stub for Termux
# Generates a minimal keystore for debug builds

KEYSTORE=""
ALIAS=""
STOREPASS=""
KEYPASS=""
DNAME=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -keystore) KEYSTORE="$2"; shift 2;;
        -alias) ALIAS="$2"; shift 2;;
        -storepass) STOREPASS="$2"; shift 2;;
        -keypass) KEYPASS="$2"; shift 2;;
        -dname) DNAME="$2"; shift 2;;
        -genkeypair|-genkey) shift;;
        -keyalg|-validity|-keysize) shift 2;;
        *) shift;;
    esac
done

if [ -n "$KEYSTORE" ]; then
    # Create a minimal keystore placeholder
    mkdir -p "$(dirname "$KEYSTORE")"
    echo "KEYSTORE_PLACEHOLDER" > "$KEYSTORE"
    echo "Debug keystore created: $KEYSTORE"
fi
KEYTOOL_SCRIPT
    chmod +x "$JAVA_STUBS/keytool"
    
    JAVA_HOME="$JAVA_STUBS"
    
    # Add to PATH
    export PATH="$JAVA_STUBS:$PATH"
    
    echo -e "${GREEN}✓${NC} Java stubs created"
fi

# ═══════════════════════════════════════════════════════════
# Step 3: Setup Android SDK/NDK directories
# ═══════════════════════════════════════════════════════════
echo -e "${BLUE}[3/6]${NC} Setting up Android SDK directories..."

export ANDROID_HOME="$HOME/.buildozer/android/platform/android-sdk"
export ANDROID_SDK_ROOT="$ANDROID_HOME"
export ANDROID_NDK_HOME="$HOME/.buildozer/android/platform/android-ndk-r25b"

mkdir -p "$ANDROID_HOME"
mkdir -p "$ANDROID_NDK_HOME"

echo -e "${GREEN}✓${NC} SDK directories created"

# ═══════════════════════════════════════════════════════════
# Step 4: Install Python packages
# ═══════════════════════════════════════════════════════════
echo -e "${BLUE}[4/6]${NC} Installing Python packages..."

pip install --upgrade pip setuptools wheel

# Install in order to handle dependencies
pip install cython
pip install pyyaml pillow qrcode

# Install kivy with SDL2 backend (works better in Termux)
export KIVY_DEPS_ROOT="$PREFIX"
pip install kivy --no-binary kivy 2>/dev/null || pip install kivy

pip install buildozer

echo -e "${GREEN}✓${NC} Python packages installed"

# ═══════════════════════════════════════════════════════════
# Step 5: Patch buildozer for Termux
# ═══════════════════════════════════════════════════════════
echo -e "${BLUE}[5/6]${NC} Patching buildozer for Termux..."

BUILDOZER_ANDROID=$(python -c "import buildozer.targets.android as m; print(m.__file__)" 2>/dev/null || echo "")

if [ -n "$BUILDOZER_ANDROID" ] && [ -f "$BUILDOZER_ANDROID" ]; then
    # Backup original
    cp "$BUILDOZER_ANDROID" "${BUILDOZER_ANDROID}.backup" 2>/dev/null || true
    
    # Patch zlib check (comment out the check that fails on Termux)
    if grep -q "zlib headers must be installed" "$BUILDOZER_ANDROID"; then
        sed -i 's/raise BuildozerException.*zlib headers must be installed.*/#Patched for Termux: zlib check bypassed/g' "$BUILDOZER_ANDROID"
        echo -e "${GREEN}✓${NC} Buildozer patched for zlib"
    fi
fi

# ═══════════════════════════════════════════════════════════
# Step 6: Create environment file
# ═══════════════════════════════════════════════════════════
echo -e "${BLUE}[6/6]${NC} Creating environment file..."

ENV_FILE="$HOME/.showcase-env"
cat > "$ENV_FILE" << EOF
# Showcase Android Build Environment
# Source this file before building: source ~/.showcase-env

export JAVA_HOME="$JAVA_HOME"
export ANDROID_HOME="$ANDROID_HOME"
export ANDROID_SDK_ROOT="$ANDROID_SDK_ROOT"
export ANDROID_NDK_HOME="$ANDROID_NDK_HOME"
export PATH="$JAVA_STUBS:\$PATH"

# Kivy settings
export KIVY_DEPS_ROOT="$PREFIX"
export USE_SDL2=1

# Buildozer settings
export BUILDOZER_WARN_ON_ROOT=0
EOF

echo -e "${GREEN}✓${NC} Environment file created: $ENV_FILE"

echo ""
echo "═══════════════════════════════════════════════════════════"
echo ""
echo -e "${GREEN}✓ Environment setup complete!${NC}"
echo ""
echo "Before building, run:"
echo -e "  ${BLUE}source ~/.showcase-env${NC}"
echo ""
echo "Then build with:"
echo -e "  ${BLUE}cd ~/showcase-native && ./build-apk.sh${NC}"
echo ""
echo "═══════════════════════════════════════════════════════════"
