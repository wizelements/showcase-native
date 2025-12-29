[app]
# Showcase - Portfolio App
title = Showcase
package.name = showcase
package.domain = dev.cod3black
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,yml,json
version = 1.0.0

# Requirements
requirements = python3,kivy,pillow,qrcode,pyyaml

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

# Icon (create a 512x512 icon.png in assets/)
# icon.filename = assets/icon.png

# Build settings
log_level = 2
warn_on_root = 1

[buildozer]
log_level = 2
warn_on_root = 1
