# ✨ Showcase - Native Portfolio App

A beautiful, native Android portfolio app built with Kivy, designed to showcase your projects with QR code sharing.

## Features

- 📱 **Native Android App** - Built with Kivy for smooth performance
- 🎨 **Modern Dark UI** - Beautiful gradient cards with accent colors
- 🔄 **Carousel Navigation** - Swipe through projects elegantly
- 📷 **QR Code Sharing** - Generate QR codes for any project URL
- 📊 **Project Metrics** - Display visitors, ratings, and custom stats
- 🏷️ **Tech Stack Tags** - Show technologies used in each project
- 📂 **YAML/JSON Projects** - Easy project management via files

## Project Structure

```
showcase-native/
├── main.py              # Main Kivy application
├── config.json          # App configuration
├── buildozer.spec       # Android build configuration
├── projects/            # Project data files (YAML/JSON)
│   ├── agency-portfolio.yml
│   ├── ecommerce-platform.yml
│   └── ...
├── assets/              # Icons and images
├── setup-android-env.sh # One-time environment setup
├── build-apk.sh         # Build the APK
├── test-app.sh          # Test before building
└── README.md            # This file
```

## Quick Start

### Option A: Build on GitHub Codespaces (Recommended)

1. Push this repo to GitHub
2. Click **Code → Codespaces → Create codespace**
3. Wait for setup to complete (~5 min)
4. Run:
   ```bash
   ./build-codespaces.sh
   ```
5. Download the APK from `bin/` folder

### Option B: Build Locally

### 1. Test the App

```bash
cd ~/showcase-native
chmod +x *.sh
./test-app.sh
```

### 2. Setup Build Environment (First Time Only)

```bash
./setup-android-env.sh
```

This installs:
- Java environment (OpenJDK or ECJ stubs)
- Android SDK/NDK directories
- Python packages (kivy, pillow, qrcode, pyyaml)
- Buildozer with Termux patches

### 3. Build the APK

```bash
source ~/.showcase-env   # Load environment
./build-apk.sh           # Build APK
```

First build downloads ~1GB of SDK files and takes 30-60 minutes.
Subsequent builds are much faster (5-10 minutes).

### 4. Install the APK

After successful build, the APK is in `bin/`:

```bash
# Copy to Downloads folder
cp bin/showcase-*.apk ~/storage/downloads/

# Or install via ADB
adb install bin/showcase-*.apk

# Or share (requires termux-api)
termux-share -a send bin/showcase-*.apk
```

## Adding Projects

Create a new YAML file in the `projects/` directory:

```yaml
# projects/my-project.yml
id: my-project
name: My Awesome Project
tagline: A short description
description: Longer description of the project
url: https://myproject.example.com
tech_stack:
  - React
  - Node.js
  - PostgreSQL
metrics:
  visitors: 10K/mo
  rating: "4.9★"
tags:
  - web
  - fullstack
order: 1  # Display order (lower = first)
```

## Configuration

Edit `config.json` to customize:

```json
{
  "owner": {
    "name": "Your Name",
    "tagline": "Your Tagline",
    "website": "https://yoursite.com"
  }
}
```

## Customizing Colors

Edit the `COLORS` dictionary in `main.py`:

```python
COLORS = {
    'bg_primary': '#0a0a0f',      # Main background
    'bg_secondary': '#1a1a2e',    # Secondary background
    'bg_card': '#12121a',         # Card background
    'accent': '#6366f1',          # Primary accent (purple)
    'accent_light': '#818cf8',    # Light accent
    'text_primary': '#ffffff',    # Primary text
    'text_secondary': '#94a3b8',  # Secondary text
    'text_muted': '#64748b',      # Muted text
    'success': '#10b981',         # Success/live indicator
    'border': '#1e1e2e',          # Border color
}
```

## Troubleshooting

### Build Fails with Java Error

```bash
# Re-run setup
./setup-android-env.sh

# Then source and rebuild
source ~/.showcase-env
./build-apk.sh
```

### SDK Download Fails

- Check internet connection
- Ensure enough storage space (~2GB needed)
- Try: `./build-apk.sh clean` to start fresh

### Memory Issues

Close other apps and try:

```bash
# Add swap space (optional)
dd if=/dev/zero of=~/swap bs=1M count=512
mkswap ~/swap
swapon ~/swap

# Then rebuild
./build-apk.sh
```

### Python Package Errors

```bash
pip install --upgrade pip setuptools wheel
pip install kivy pillow qrcode pyyaml cython buildozer
```

## Build Specifications

- **Target API**: 31 (Android 12)
- **Min API**: 21 (Android 5.0)
- **Architecture**: arm64-v8a
- **NDK Version**: r25b
- **Python**: 3.x

## License

MIT License - Use freely for your portfolio!

---

Built with ❤️ using Kivy and Buildozer on Termux
