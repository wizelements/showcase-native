[app]
# Showcase Pro - Portfolio App
title = Showcase Pro
package.name = showcasepro
package.domain = dev.cod3black
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,yml,json
source.include_patterns = assets/*
source.exclude_patterns = .github_cache.json,.git,__pycache__,*.pyc,build.log
version = 1.1.0

# Requirements (pyjnius pinned for Python 3.11 compatibility)
requirements = python3,kivy,pillow,qrcode,pyyaml,pyjnius==1.6.1,certifi

# Android settings
android.permissions = INTERNET
android.api = 31
android.minapi = 21
android.ndk = 25b
android.sdk = 33
android.accept_sdk_license = True
android.archs = arm64-v8a
android.skip_update = True
android.gradle_dependencies = 

# App appearance
orientation = portrait
fullscreen = 0
android.presplash_color = #0a0a0f

# Icon
icon.filename = assets/icon.png

# Build settings
log_level = 2
warn_on_root = 1

[buildozer]
log_level = 2
warn_on_root = 1
