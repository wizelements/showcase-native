#!/data/data/com.termux/files/usr/bin/bash
#
# ✨ Showcase APK Builder - Complete Termux Solution
# Builds native Android APK from Kivy app with all workarounds
#

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

echo ""
echo "✨ ═══════════════════════════════════════════════════════ ✨"
echo ""
echo "         SHOWCASE APK BUILDER"
echo "         Building on Termux ARM64"
echo ""
echo "✨ ═══════════════════════════════════════════════════════ ✨"
echo ""

cd ~/showcase-native

# ═══════════════════════════════════════════════════════════
# Load environment
# ═══════════════════════════════════════════════════════════
if [ -f "$HOME/.showcase-env" ]; then
    source "$HOME/.showcase-env"
    echo -e "${GREEN}✓${NC} Environment loaded"
else
    echo -e "${YELLOW}!${NC} Environment not set up. Running setup first..."
    ./setup-android-env.sh
    source "$HOME/.showcase-env"
fi

# ═══════════════════════════════════════════════════════════
# Step 1: Verify dependencies
# ═══════════════════════════════════════════════════════════
echo -e "${BLUE}[1/6]${NC} Verifying dependencies..."

# Check Python packages
python -c "import kivy; import PIL; import qrcode; import yaml" 2>/dev/null || {
    echo -e "${YELLOW}Installing missing Python packages...${NC}"
    pip install kivy pillow qrcode pyyaml
}

# Check buildozer
python -c "import buildozer" 2>/dev/null || {
    echo -e "${YELLOW}Installing buildozer...${NC}"
    pip install buildozer
}

echo -e "${GREEN}✓${NC} Dependencies verified"

# ═══════════════════════════════════════════════════════════
# Step 2: Test app syntax
# ═══════════════════════════════════════════════════════════
echo -e "${BLUE}[2/6]${NC} Testing app syntax..."

python -c "
import sys
sys.path.insert(0, '.')
# Test imports work
import main
print('✓ All imports OK')
" || {
    echo -e "${RED}✗ Syntax error in main.py${NC}"
    echo "Fix errors before building."
    exit 1
}

echo -e "${GREEN}✓${NC} App syntax validated"

# ═══════════════════════════════════════════════════════════
# Step 3: Ensure projects exist
# ═══════════════════════════════════════════════════════════
echo -e "${BLUE}[3/6]${NC} Checking project data..."

if [ ! -d "projects" ] || [ -z "$(ls -A projects/*.yml 2>/dev/null)" ]; then
    echo "Creating sample projects..."
    python -c "
import yaml
from pathlib import Path

projects_dir = Path('projects')
projects_dir.mkdir(exist_ok=True)

samples = [
    {
        'id': 'agency-portfolio',
        'name': 'Agency Portfolio',
        'tagline': 'Modern creative agency website',
        'description': 'Full-stack portfolio with headless CMS',
        'url': 'https://cod3black.dev',
        'tech_stack': ['Next.js', 'Sanity', 'Tailwind'],
        'metrics': {'visitors': '12K/mo', 'score': '98'},
        'tags': ['web', 'portfolio'],
        'order': 1
    },
    {
        'id': 'ecommerce-platform',
        'name': 'E-Commerce Platform',
        'tagline': 'Full-stack shop with payments',
        'description': 'Complete e-commerce with Stripe integration',
        'url': 'https://shop.example.com',
        'tech_stack': ['React', 'Node.js', 'Stripe', 'PostgreSQL'],
        'metrics': {'transactions': '5K+', 'revenue': '\$50K'},
        'tags': ['web', 'e-commerce'],
        'order': 2
    },
    {
        'id': 'ai-dashboard',
        'name': 'AI Analytics Dashboard',
        'tagline': 'ML insights visualization',
        'description': 'Real-time ML model monitoring platform',
        'url': 'https://ai-dash.example.com',
        'tech_stack': ['Python', 'FastAPI', 'React', 'TensorFlow'],
        'metrics': {'models': '15+', 'uptime': '99.9%'},
        'tags': ['ai', 'dashboard'],
        'order': 3
    },
    {
        'id': 'mobile-fitness',
        'name': 'FitTrack Pro',
        'tagline': 'Cross-platform workout tracker',
        'description': 'Mobile app for fitness tracking and analytics',
        'url': 'https://fittrack.example.com',
        'tech_stack': ['React Native', 'Firebase', 'Node.js'],
        'metrics': {'downloads': '10K+', 'rating': '4.8★'},
        'tags': ['mobile', 'health'],
        'order': 4
    },
    {
        'id': 'saas-platform',
        'name': 'CloudOps Suite',
        'tagline': 'DevOps automation platform',
        'description': 'Enterprise SaaS for infrastructure management',
        'url': 'https://cloudops.example.com',
        'tech_stack': ['Go', 'Kubernetes', 'React', 'PostgreSQL'],
        'metrics': {'clients': '50+', 'uptime': '99.99%'},
        'tags': ['saas', 'devops'],
        'order': 5
    }
]

for project in samples:
    path = projects_dir / f\"{project['id']}.yml\"
    path.write_text(yaml.dump(project, default_flow_style=False, allow_unicode=True))
    print(f'  Created {path}')
"
fi

PROJECT_COUNT=$(ls projects/*.yml 2>/dev/null | wc -l)
echo -e "${GREEN}✓${NC} Found $PROJECT_COUNT projects"

# ═══════════════════════════════════════════════════════════
# Step 4: Prepare buildozer
# ═══════════════════════════════════════════════════════════
echo -e "${BLUE}[4/6]${NC} Preparing build environment..."

# Ensure buildozer.spec is correct
if [ ! -f "buildozer.spec" ]; then
    cat > buildozer.spec << 'SPEC'
[app]
title = Showcase
package.name = showcase
package.domain = dev.cod3black
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,yml,json
source.include_patterns = projects/*,config.json,assets/*
version = 1.0.0

requirements = python3,kivy,pillow,qrcode,pyyaml

android.permissions = INTERNET
android.api = 31
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
android.archs = arm64-v8a

orientation = portrait
fullscreen = 0
android.presplash_color = #0a0a0f

log_level = 2
warn_on_root = 0

[buildozer]
log_level = 2
warn_on_root = 0
SPEC
fi

# Clean previous build artifacts if requested
if [ "$1" = "clean" ]; then
    echo -e "${YELLOW}Cleaning build artifacts...${NC}"
    rm -rf .buildozer/android/platform/build-*
    rm -rf .buildozer/android/app
    rm -rf bin/*.apk
fi

echo -e "${GREEN}✓${NC} Build environment ready"

# ═══════════════════════════════════════════════════════════
# Step 5: Build APK
# ═══════════════════════════════════════════════════════════
echo -e "${BLUE}[5/6]${NC} Building APK..."
echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}  First build downloads ~1GB of SDK/NDK files${NC}"
echo -e "${YELLOW}  This can take 30-60 minutes on first run${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Set environment variables for build
export ANDROIDSDK="$ANDROID_HOME"
export ANDROIDNDK="$ANDROID_NDK_HOME"
export ANDROIDAPI=31
export NDKAPI=21

# Run buildozer
buildozer -v android debug 2>&1 | tee build.log

# ═══════════════════════════════════════════════════════════
# Step 6: Check result
# ═══════════════════════════════════════════════════════════
echo -e "${BLUE}[6/6]${NC} Checking build result..."

APK_FILE=$(find bin -name "*.apk" 2>/dev/null | head -1)

if [ -n "$APK_FILE" ] && [ -f "$APK_FILE" ]; then
    APK_SIZE=$(du -h "$APK_FILE" | cut -f1)
    
    echo ""
    echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${GREEN}  ✓ APK Built Successfully!${NC}"
    echo ""
    echo -e "  ${CYAN}File:${NC} $APK_FILE"
    echo -e "  ${CYAN}Size:${NC} $APK_SIZE"
    echo ""
    echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "  Install options:"
    echo ""
    echo "  1. Copy to Downloads and install from file manager:"
    echo -e "     ${BLUE}cp $APK_FILE ~/storage/downloads/${NC}"
    echo ""
    echo "  2. Install via ADB (if connected):"
    echo -e "     ${BLUE}adb install $APK_FILE${NC}"
    echo ""
    echo "  3. Share via Termux (requires termux-api):"
    echo -e "     ${BLUE}termux-share -a send $APK_FILE${NC}"
    echo ""
else
    echo ""
    echo -e "${RED}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${RED}  ✗ Build Failed${NC}"
    echo ""
    echo "  Check build.log for errors:"
    echo -e "  ${BLUE}tail -100 build.log${NC}"
    echo ""
    echo "  Common issues:"
    echo "  - Java not found: Run ./setup-android-env.sh"
    echo "  - SDK download failed: Check internet connection"
    echo "  - Memory issues: Close other apps, increase swap"
    echo ""
    echo -e "${RED}═══════════════════════════════════════════════════════════${NC}"
    exit 1
fi
