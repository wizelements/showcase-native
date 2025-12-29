#!/usr/bin/env python3
"""
✨ Showcase - Native Portfolio App
Beautiful project display with QR sharing
Built with Kivy
"""

import os
import json
import yaml
import urllib.request
import urllib.error
import ssl
import certifi
from pathlib import Path
from io import BytesIO
from datetime import datetime, timedelta
import qrcode
from PIL import Image as PILImage

def get_ssl_context():
    """Get SSL context that works on Android"""
    try:
        ctx = ssl.create_default_context(cafile=certifi.where())
        return ctx
    except Exception:
        pass
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return ctx
    except Exception:
        return None

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.carousel import Carousel
from kivy.uix.popup import Popup
from kivy.core.image import Image as CoreImage
from kivy.graphics import Color, RoundedRectangle, Rectangle, Line
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.clock import Clock
from kivy.metrics import dp, sp
from kivy.properties import StringProperty, ListProperty, ObjectProperty

# ═══════════════════════════════════════════════════════════
# Colors
# ═══════════════════════════════════════════════════════════

COLORS = {
    'bg_primary': '#0d0d12',
    'bg_secondary': '#16161e',
    'bg_card': '#1a1a24',
    'bg_card_hover': '#222230',
    'accent': '#7c3aed',
    'accent_light': '#a78bfa',
    'accent_glow': '#8b5cf6',
    'gradient_start': '#6366f1',
    'gradient_end': '#8b5cf6',
    'text_primary': '#f8fafc',
    'text_secondary': '#cbd5e1',
    'text_muted': '#64748b',
    'success': '#22c55e',
    'success_glow': '#4ade80',
    'warning': '#f59e0b',
    'border': '#2d2d3a',
    'border_glow': '#7c3aed',
    'gold': '#fbbf24',
    'silver': '#94a3b8',
}

def hex_to_rgba(hex_color, alpha=1):
    """Convert hex color to RGBA tuple"""
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16) / 255
    g = int(hex_color[2:4], 16) / 255
    b = int(hex_color[4:6], 16) / 255
    return (r, g, b, alpha)

# ═══════════════════════════════════════════════════════════
# Data Loading
# ═══════════════════════════════════════════════════════════

CACHE_FILE = Path(__file__).parent / '.github_cache.json'

def fetch_url_with_retry(url, headers=None, retries=3, timeout=15):
    """Fetch URL with SSL fallback and retries for Android compatibility"""
    if headers is None:
        headers = {'User-Agent': 'Showcase-App/1.0'}
    
    req = urllib.request.Request(url, headers=headers)
    ssl_ctx = get_ssl_context()
    
    for attempt in range(retries):
        try:
            if ssl_ctx:
                with urllib.request.urlopen(req, timeout=timeout, context=ssl_ctx) as response:
                    return json.loads(response.read().decode())
            else:
                with urllib.request.urlopen(req, timeout=timeout) as response:
                    return json.loads(response.read().decode())
        except ssl.SSLError as e:
            print(f"SSL error (attempt {attempt+1}): {e}")
            ssl_ctx = ssl.create_default_context()
            ssl_ctx.check_hostname = False
            ssl_ctx.verify_mode = ssl.CERT_NONE
        except urllib.error.URLError as e:
            print(f"URL error (attempt {attempt+1}): {e}")
        except Exception as e:
            print(f"Fetch error (attempt {attempt+1}): {e}")
    return None

def fetch_github_pinned_repos(username):
    """Fetch pinned repositories from GitHub using REST API"""
    try:
        pinned_url = f"https://gh-pinned-repos-tsj7ta5xfhep.deno.dev/?username={username}"
        print(f"🔗 Fetching from: {pinned_url}")
        pinned = fetch_url_with_retry(pinned_url)
        if pinned and isinstance(pinned, list) and len(pinned) > 0:
            print(f"✅ Got {len(pinned)} pinned repos")
            return [convert_pinned_to_project(p, i) for i, p in enumerate(pinned)]
        
        print("⚠️ Pinned API empty, trying GitHub API...")
        url = f"https://api.github.com/users/{username}/repos?sort=updated&per_page=100"
        repos = fetch_url_with_retry(url, headers={
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'Showcase-App/1.0'
        })
        
        if repos and isinstance(repos, list):
            top_repos = [r for r in repos if not r.get('fork')][:6]
            print(f"✅ Got {len(top_repos)} repos from GitHub API")
            return [convert_repo_to_project(r, i) for i, r in enumerate(top_repos)]
        
        print("❌ All GitHub fetches failed")
        return None
        
    except Exception as e:
        print(f"GitHub fetch error: {e}")
        return None

def convert_pinned_to_project(pinned, order):
    """Convert pinned repo format to project format"""
    return {
        'id': pinned.get('repo', f'project-{order}'),
        'name': pinned.get('repo', 'Untitled'),
        'tagline': pinned.get('description', '')[:80] if pinned.get('description') else '',
        'description': pinned.get('description', ''),
        'url': pinned.get('link', ''),
        'tech_stack': [pinned.get('language', 'Code')] if pinned.get('language') else [],
        'metrics': {
            'stars': str(pinned.get('stars', 0)),
            'forks': str(pinned.get('forks', 0))
        },
        'tags': ['github', pinned.get('language', '').lower()] if pinned.get('language') else ['github'],
        'order': order
    }

def convert_repo_to_project(repo, order):
    """Convert GitHub repo to project format"""
    return {
        'id': repo.get('name', f'project-{order}'),
        'name': repo.get('name', 'Untitled'),
        'tagline': (repo.get('description', '') or '')[:80],
        'description': repo.get('description', ''),
        'url': repo.get('html_url', ''),
        'tech_stack': [repo.get('language', 'Code')] if repo.get('language') else [],
        'metrics': {
            'stars': str(repo.get('stargazers_count', 0)),
            'forks': str(repo.get('forks_count', 0))
        },
        'tags': ['github', (repo.get('language', '') or '').lower()],
        'order': order
    }

def load_cached_github(config):
    """Load GitHub repos from cache if valid"""
    if not CACHE_FILE.exists():
        return None
    try:
        cache = json.loads(CACHE_FILE.read_text())
        cached_time = datetime.fromisoformat(cache.get('timestamp', '2000-01-01'))
        ttl = config.get('github', {}).get('cache_ttl_minutes', 30)
        if datetime.now() - cached_time < timedelta(minutes=ttl):
            return cache.get('projects', [])
    except Exception as e:
        print(f"Cache read error: {e}")
    return None

def save_github_cache(projects):
    """Save projects to cache"""
    try:
        CACHE_FILE.write_text(json.dumps({
            'timestamp': datetime.now().isoformat(),
            'projects': projects
        }, indent=2))
    except Exception as e:
        print(f"Cache write error: {e}")

def get_bundled_projects():
    """Return bundled projects as ultimate fallback"""
    return [
        {
            'id': 'showcase-native',
            'name': 'Showcase Native',
            'tagline': 'Portfolio app for Android',
            'description': 'Native Android portfolio app built with Kivy',
            'url': 'https://github.com/wizelements/showcase-native',
            'tech_stack': ['Python', 'Kivy', 'Android'],
            'metrics': {'stars': '⭐', 'status': 'Live'},
            'tags': ['mobile', 'portfolio'],
            'order': 1
        },
        {
            'id': 'github-profile',
            'name': 'GitHub Profile',
            'tagline': 'Check out all repositories',
            'description': 'View full GitHub profile and all projects',
            'url': 'https://github.com/wizelements',
            'tech_stack': ['GitHub'],
            'metrics': {'repos': 'All', 'type': 'Profile'},
            'tags': ['github', 'profile'],
            'order': 2
        },
        {
            'id': 'cod3black-dev',
            'name': 'Cod3Black Agency',
            'tagline': 'Building Digital Excellence',
            'description': 'Full-stack development agency portfolio',
            'url': 'https://cod3black.dev',
            'tech_stack': ['Next.js', 'React', 'Node.js'],
            'metrics': {'clients': 'Active', 'rating': '5⭐'},
            'tags': ['web', 'agency'],
            'order': 3
        }
    ]

def load_projects():
    """Load projects from GitHub pinned repos with robust fallback"""
    config = load_config()
    github_config = config.get('github', {})
    
    if github_config.get('use_pinned') and github_config.get('username'):
        cached = load_cached_github(config)
        if cached and len(cached) > 0:
            print(f"📦 Using {len(cached)} cached GitHub projects")
            return cached
        
        print(f"🔄 Fetching GitHub pinned repos for {github_config['username']}...")
        projects = fetch_github_pinned_repos(github_config['username'])
        if projects and len(projects) > 0:
            save_github_cache(projects)
            print(f"✅ Loaded {len(projects)} projects from GitHub")
            return projects
        
        print("⚠️ GitHub fetch failed - using bundled projects")
        bundled = get_bundled_projects()
        print(f"📱 Loaded {len(bundled)} bundled projects")
        return bundled
    
    projects = []
    projects_dir = Path(__file__).parent / 'projects'
    
    if projects_dir.exists():
        for f in sorted(projects_dir.glob('*.yml')):
            try:
                data = yaml.safe_load(f.read_text())
                if data:
                    projects.append(data)
            except Exception as e:
                print(f"Error loading {f}: {e}")
        
        for f in sorted(projects_dir.glob('*.json')):
            try:
                data = json.loads(f.read_text())
                if data:
                    projects.append(data)
            except Exception as e:
                print(f"Error loading {f}: {e}")
    
    if not projects:
        print("📱 No local projects found - using bundled projects")
        return get_bundled_projects()
    
    projects.sort(key=lambda p: (p.get('order', 999), p.get('name', '')))
    return projects

def create_sample_projects(projects_dir):
    """Create sample project files"""
    samples = [
        {
            'id': 'agency-portfolio',
            'name': 'Agency Portfolio',
            'tagline': 'Modern creative agency site',
            'description': 'Full-stack portfolio with headless CMS',
            'url': 'https://cod3black.dev',
            'tech_stack': ['Next.js', 'Sanity', 'Tailwind'],
            'metrics': {'visitors': '12K/mo', 'score': '98'},
            'tags': ['web', 'portfolio'],
            'order': 1
        },
        {
            'id': 'ecommerce',
            'name': 'E-Commerce Platform',
            'tagline': 'Full-stack shop with payments',
            'description': 'Complete e-commerce solution with Stripe',
            'url': 'https://shop.example.com',
            'tech_stack': ['React', 'Node.js', 'Stripe'],
            'metrics': {'visitors': '45K/mo', 'revenue': '$50K'},
            'tags': ['web', 'e-commerce'],
            'order': 2
        },
        {
            'id': 'ai-dashboard',
            'name': 'AI Analytics',
            'tagline': 'ML insights visualization',
            'description': 'Real-time ML model monitoring',
            'url': 'https://ai-dash.example.com',
            'tech_stack': ['Python', 'FastAPI', 'React'],
            'metrics': {'models': '15', 'uptime': '99.9%'},
            'tags': ['ai', 'dashboard'],
            'order': 3
        },
        {
            'id': 'mobile-app',
            'name': 'Fitness App',
            'tagline': 'Cross-platform workout tracker',
            'description': 'Mobile app for fitness tracking',
            'url': 'https://fitapp.example.com',
            'tech_stack': ['React Native', 'Firebase'],
            'metrics': {'downloads': '10K', 'rating': '4.8'},
            'tags': ['mobile', 'health'],
            'order': 4
        },
    ]
    
    for project in samples:
        path = projects_dir / f"{project['id']}.yml"
        path.write_text(yaml.dump(project, default_flow_style=False))

def load_config():
    """Load app configuration"""
    config_path = Path(__file__).parent / 'config.json'
    if config_path.exists():
        return json.loads(config_path.read_text())
    return {
        'owner': {
            'name': 'Cod3BlackAgency',
            'tagline': 'Building Digital Excellence'
        }
    }

# ═══════════════════════════════════════════════════════════
# QR Code Generation
# ═══════════════════════════════════════════════════════════

def generate_qr_texture(url, size=256):
    """Generate QR code and return as Kivy texture"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    img = img.resize((size, size), PILImage.LANCZOS)
    
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    return CoreImage(buffer, ext='png').texture

# ═══════════════════════════════════════════════════════════
# Custom Widgets
# ═══════════════════════════════════════════════════════════

class GlowCard(BoxLayout):
    """Beautiful card with glow effect and gradient border"""
    
    def __init__(self, glow_color=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(20)
        self.spacing = dp(14)
        self.glow_color = glow_color or COLORS['accent_glow']
        
        with self.canvas.before:
            Color(*hex_to_rgba(self.glow_color, 0.15))
            self.glow = RoundedRectangle(
                pos=(self.x - dp(4), self.y - dp(4)),
                size=(self.width + dp(8), self.height + dp(8)),
                radius=[dp(24)]
            )
            Color(*hex_to_rgba(COLORS['bg_card']))
            self.bg = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(20)]
            )
            Color(*hex_to_rgba(self.glow_color, 0.5))
            self.border = Line(
                rounded_rectangle=[*self.pos, *self.size, dp(20)],
                width=1.5
            )
        
        self.bind(pos=self._update_graphics, size=self._update_graphics)
    
    def _update_graphics(self, *args):
        self.glow.pos = (self.x - dp(4), self.y - dp(4))
        self.glow.size = (self.width + dp(8), self.height + dp(8))
        self.bg.pos = self.pos
        self.bg.size = self.size
        self.border.rounded_rectangle = [*self.pos, *self.size, dp(20)]


class RoundedCard(BoxLayout):
    """Card with rounded corners and shadow effect"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(16)
        self.spacing = dp(12)
        
        with self.canvas.before:
            Color(*hex_to_rgba(COLORS['bg_card']))
            self.bg = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(16)]
            )
            Color(*hex_to_rgba(COLORS['accent'], 0.3))
            self.border = Line(
                rounded_rectangle=[*self.pos, *self.size, dp(16)],
                width=1
            )
        
        self.bind(pos=self._update_graphics, size=self._update_graphics)
    
    def _update_graphics(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size
        self.border.rounded_rectangle = [*self.pos, *self.size, dp(16)]


class GradientButton(Button):
    """Button with gradient-like appearance"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        
        with self.canvas.before:
            Color(*hex_to_rgba(COLORS['accent']))
            self.bg = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(12)]
            )
        
        self.bind(pos=self._update_bg, size=self._update_bg)
    
    def _update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size


class ProjectCard(GlowCard):
    """Individual project display card with enhanced styling"""
    
    def __init__(self, project, index=0, on_qr=None, on_visit=None, **kwargs):
        glow_colors = [COLORS['accent_glow'], COLORS['success'], COLORS['gold'], COLORS['accent_light']]
        super().__init__(glow_color=glow_colors[index % len(glow_colors)], **kwargs)
        self.project = project
        self.on_qr_callback = on_qr
        self.on_visit_callback = on_visit
        self.size_hint = (None, None)
        self.size = (dp(320), dp(420))
        
        self._build_ui()
    
    def _build_ui(self):
        # Header with status and order badge
        header = BoxLayout(size_hint_y=None, height=dp(32))
        
        # Status indicator with animation-like styling
        status_box = BoxLayout(size_hint_x=None, width=dp(80))
        status_box.add_widget(Label(
            text='● LIVE',
            font_size=sp(11),
            bold=True,
            color=hex_to_rgba(COLORS['success']),
            halign='left'
        ))
        header.add_widget(status_box)
        
        header.add_widget(BoxLayout())
        
        # Order badge
        order = self.project.get('order', 0)
        if order > 0:
            badge = Label(
                text=f'#{order}',
                font_size=sp(12),
                bold=True,
                color=hex_to_rgba(COLORS['gold']),
                size_hint_x=None,
                width=dp(40)
            )
            header.add_widget(badge)
        
        self.add_widget(header)
        
        # Project name with larger font
        name = self.project.get('name', 'Untitled')
        self.add_widget(Label(
            text=name,
            font_size=sp(24),
            bold=True,
            color=hex_to_rgba(COLORS['text_primary']),
            halign='left',
            valign='middle',
            size_hint_y=None,
            height=dp(36),
            text_size=(dp(280), None)
        ))
        
        # Tagline with better styling
        tagline = self.project.get('tagline', '')
        if tagline:
            self.add_widget(Label(
                text=tagline,
                font_size=sp(14),
                color=hex_to_rgba(COLORS['text_secondary']),
                halign='left',
                valign='top',
                size_hint_y=None,
                height=dp(44),
                text_size=(dp(280), None)
            ))
        
        # Tech stack with pill-style badges
        tech_box = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(6))
        tech_stack = self.project.get('tech_stack', [])
        for tech in tech_stack[:3]:
            tech_name = tech.get('name', tech) if isinstance(tech, dict) else tech
            pill = Button(
                text=tech_name,
                font_size=sp(10),
                bold=True,
                size_hint=(None, None),
                size=(dp(max(60, len(tech_name) * 8)), dp(28)),
                background_color=hex_to_rgba(COLORS['accent'], 0.25),
                color=hex_to_rgba(COLORS['accent_light'])
            )
            pill.background_normal = ''
            tech_box.add_widget(pill)
        if len(tech_stack) > 3:
            more = Button(
                text=f'+{len(tech_stack)-3}',
                font_size=sp(10),
                size_hint=(None, None),
                size=(dp(36), dp(28)),
                background_color=hex_to_rgba(COLORS['border'], 0.5),
                color=hex_to_rgba(COLORS['text_muted'])
            )
            more.background_normal = ''
            tech_box.add_widget(more)
        tech_box.add_widget(BoxLayout())
        self.add_widget(tech_box)
        
        # Metrics with icons
        metrics = self.project.get('metrics', {})
        if metrics:
            metrics_box = BoxLayout(size_hint_y=None, height=dp(36), spacing=dp(20))
            icons = {'stars': '⭐', 'forks': '🔀', 'downloads': '📥', 'visitors': '👁', 
                     'rating': '⭐', 'uptime': '🟢', 'score': '📊', 'clients': '👥'}
            for key, value in list(metrics.items())[:3]:
                icon = icons.get(key.lower(), '📌')
                metrics_box.add_widget(Label(
                    text=f'{icon} {value}',
                    font_size=sp(13),
                    color=hex_to_rgba(COLORS['text_secondary']),
                    halign='left',
                    size_hint_x=None,
                    width=dp(80)
                ))
            metrics_box.add_widget(BoxLayout())
            self.add_widget(metrics_box)
        
        # Spacer
        self.add_widget(BoxLayout())
        
        # Action buttons with better styling
        btn_box = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(12))
        
        # Visit button (primary)
        visit_btn = Button(
            text='🚀 Visit',
            font_size=sp(15),
            bold=True,
            background_color=hex_to_rgba(COLORS['accent']),
            color=hex_to_rgba(COLORS['text_primary']),
            size_hint_x=0.55
        )
        visit_btn.background_normal = ''
        visit_btn.bind(on_release=self._on_visit)
        btn_box.add_widget(visit_btn)
        
        # QR button (secondary)
        qr_btn = Button(
            text='📱 QR',
            font_size=sp(15),
            bold=True,
            background_color=hex_to_rgba(COLORS['bg_secondary']),
            color=hex_to_rgba(COLORS['accent_light']),
            size_hint_x=0.45
        )
        qr_btn.background_normal = ''
        qr_btn.bind(on_release=self._on_qr)
        btn_box.add_widget(qr_btn)
        
        self.add_widget(btn_box)
    
    def _on_qr(self, *args):
        if self.on_qr_callback:
            self.on_qr_callback(self.project)
    
    def _on_visit(self, *args):
        if self.on_visit_callback:
            self.on_visit_callback(self.project)


class QRPopup(Popup):
    """Popup showing QR code for sharing"""
    
    def __init__(self, project, **kwargs):
        super().__init__(**kwargs)
        self.title = ''
        self.separator_height = 0
        self.size_hint = (0.9, 0.7)
        self.background_color = hex_to_rgba(COLORS['bg_secondary'])
        self.background = ''
        
        url = project.get('url', project.get('urls', {}).get('live', ''))
        
        layout = BoxLayout(orientation='vertical', padding=dp(24), spacing=dp(16))
        
        # Background
        with layout.canvas.before:
            Color(*hex_to_rgba(COLORS['bg_secondary']))
            self.bg = RoundedRectangle(pos=layout.pos, size=layout.size, radius=[dp(24)])
        layout.bind(pos=lambda *a: setattr(self.bg, 'pos', layout.pos))
        layout.bind(size=lambda *a: setattr(self.bg, 'size', layout.size))
        
        # QR Code
        if url:
            qr_texture = generate_qr_texture(url, size=256)
            qr_image = Image(texture=qr_texture, size_hint=(None, None), size=(dp(200), dp(200)))
            qr_box = BoxLayout(size_hint_y=0.6)
            qr_box.add_widget(BoxLayout())
            qr_box.add_widget(qr_image)
            qr_box.add_widget(BoxLayout())
            layout.add_widget(qr_box)
        
        # Project name
        layout.add_widget(Label(
            text=project.get('name', ''),
            font_size=sp(20),
            bold=True,
            color=hex_to_rgba(COLORS['text_primary']),
            size_hint_y=None,
            height=dp(32)
        ))
        
        # URL
        layout.add_widget(Label(
            text=url,
            font_size=sp(12),
            color=hex_to_rgba(COLORS['accent']),
            size_hint_y=None,
            height=dp(24)
        ))
        
        # Close button
        close_btn = Button(
            text='Close',
            font_size=sp(14),
            size_hint=(None, None),
            size=(dp(120), dp(44)),
            pos_hint={'center_x': 0.5},
            background_color=hex_to_rgba(COLORS['accent']),
            color=hex_to_rgba(COLORS['text_primary'])
        )
        close_btn.background_normal = ''
        close_btn.bind(on_release=self.dismiss)
        layout.add_widget(close_btn)
        
        self.content = layout

# ═══════════════════════════════════════════════════════════
# Screens
# ═══════════════════════════════════════════════════════════

class HomeScreen(Screen):
    """Main carousel screen"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.projects = load_projects()
        self.config = load_config()
        self._build_ui()
    
    def _build_ui(self):
        layout = FloatLayout()
        
        # Background
        with layout.canvas.before:
            Color(*hex_to_rgba(COLORS['bg_primary']))
            self.bg = Rectangle(pos=layout.pos, size=layout.size)
        layout.bind(pos=lambda *a: setattr(self.bg, 'pos', layout.pos))
        layout.bind(size=lambda *a: setattr(self.bg, 'size', layout.size))
        
        # Main content
        content = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(16))
        
        # Header
        header = BoxLayout(size_hint_y=None, height=dp(56))
        header.add_widget(Label(
            text='✨ ' + self.config.get('owner', {}).get('name', 'Showcase'),
            font_size=sp(18),
            bold=True,
            color=hex_to_rgba(COLORS['text_primary']),
            halign='left',
            size_hint_x=0.7
        ))
        
        # Share portfolio button
        share_btn = Button(
            text='Share All',
            font_size=sp(12),
            size_hint=(None, None),
            size=(dp(80), dp(36)),
            background_color=hex_to_rgba(COLORS['accent'], 0.3),
            color=hex_to_rgba(COLORS['accent_light'])
        )
        share_btn.background_normal = ''
        share_btn.bind(on_release=self._show_portfolio_qr)
        header.add_widget(share_btn)
        
        content.add_widget(header)
        
        # Tagline
        content.add_widget(Label(
            text=self.config.get('owner', {}).get('tagline', 'Building Digital Excellence'),
            font_size=sp(24),
            bold=True,
            color=hex_to_rgba(COLORS['text_primary']),
            halign='center',
            size_hint_y=None,
            height=dp(36)
        ))
        
        content.add_widget(Label(
            text=f'{len(self.projects)} Projects',
            font_size=sp(14),
            color=hex_to_rgba(COLORS['text_muted']),
            halign='center',
            size_hint_y=None,
            height=dp(24)
        ))
        
        # Carousel
        self.carousel = Carousel(
            direction='right',
            loop=True,
            size_hint_y=0.75
        )
        
        for i, project in enumerate(self.projects):
            card_container = BoxLayout(padding=dp(20))
            card = ProjectCard(
                project,
                index=i,
                on_qr=self._show_qr,
                on_visit=self._visit_site
            )
            card.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
            card_container.add_widget(BoxLayout())
            card_container.add_widget(card)
            card_container.add_widget(BoxLayout())
            self.carousel.add_widget(card_container)
        
        content.add_widget(self.carousel)
        
        # Navigation hint
        content.add_widget(Label(
            text='← Swipe to explore →',
            font_size=sp(12),
            color=hex_to_rgba(COLORS['text_muted']),
            halign='center',
            size_hint_y=None,
            height=dp(32)
        ))
        
        layout.add_widget(content)
        self.add_widget(layout)
    
    def _show_qr(self, project):
        popup = QRPopup(project)
        popup.open()
    
    def _show_portfolio_qr(self, *args):
        portfolio_project = {
            'name': self.config.get('owner', {}).get('name', 'Portfolio'),
            'url': self.config.get('owner', {}).get('website', 'https://cod3black.dev')
        }
        popup = QRPopup(portfolio_project)
        popup.open()
    
    def _visit_site(self, project):
        url = project.get('url', project.get('urls', {}).get('live', ''))
        if url:
            import webbrowser
            webbrowser.open(url)

# ═══════════════════════════════════════════════════════════
# Main App
# ═══════════════════════════════════════════════════════════

class ShowcaseApp(App):
    """Main application"""
    
    def build(self):
        self.title = 'Showcase'
        Window.clearcolor = hex_to_rgba(COLORS['bg_primary'])
        
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name='home'))
        
        return sm
    
    def on_start(self):
        print("✨ Showcase started!")


if __name__ == '__main__':
    ShowcaseApp().run()
