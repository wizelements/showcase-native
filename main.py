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
from pathlib import Path
from io import BytesIO
from datetime import datetime, timedelta
import qrcode
from PIL import Image as PILImage

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
    'bg_primary': '#0a0a0f',
    'bg_secondary': '#1a1a2e',
    'bg_card': '#12121a',
    'accent': '#6366f1',
    'accent_light': '#818cf8',
    'text_primary': '#ffffff',
    'text_secondary': '#94a3b8',
    'text_muted': '#64748b',
    'success': '#10b981',
    'border': '#1e1e2e',
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

def fetch_github_pinned_repos(username):
    """Fetch pinned repositories from GitHub using REST API"""
    try:
        url = f"https://api.github.com/users/{username}/repos?sort=updated&per_page=100"
        req = urllib.request.Request(url, headers={
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'Showcase-App'
        })
        with urllib.request.urlopen(req, timeout=10) as response:
            repos = json.loads(response.read().decode())
        
        pinned_url = f"https://gh-pinned-repos-tsj7ta5xfhep.deno.dev/?username={username}"
        try:
            req = urllib.request.Request(pinned_url, headers={'User-Agent': 'Showcase-App'})
            with urllib.request.urlopen(req, timeout=10) as response:
                pinned = json.loads(response.read().decode())
                if pinned:
                    return [convert_pinned_to_project(p, i) for i, p in enumerate(pinned)]
        except Exception as e:
            print(f"Pinned API failed, using top repos: {e}")
        
        top_repos = [r for r in repos if not r.get('fork')][:6]
        return [convert_repo_to_project(r, i) for i, r in enumerate(top_repos)]
        
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

def load_projects():
    """Load projects from GitHub pinned repos or local files"""
    config = load_config()
    github_config = config.get('github', {})
    
    if github_config.get('use_pinned') and github_config.get('username'):
        cached = load_cached_github(config)
        if cached:
            print("📦 Using cached GitHub projects")
            return cached
        
        print(f"🔄 Fetching GitHub pinned repos for {github_config['username']}...")
        projects = fetch_github_pinned_repos(github_config['username'])
        if projects:
            save_github_cache(projects)
            print(f"✅ Loaded {len(projects)} projects from GitHub")
            return projects
        print("⚠️ Falling back to local projects")
    
    projects = []
    projects_dir = Path(__file__).parent / 'projects'
    
    if not projects_dir.exists():
        projects_dir.mkdir(exist_ok=True)
        create_sample_projects(projects_dir)
    
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


class ProjectCard(RoundedCard):
    """Individual project display card"""
    
    def __init__(self, project, on_qr=None, on_visit=None, **kwargs):
        super().__init__(**kwargs)
        self.project = project
        self.on_qr_callback = on_qr
        self.on_visit_callback = on_visit
        self.size_hint = (None, None)
        self.size = (dp(300), dp(380))
        
        self._build_ui()
    
    def _build_ui(self):
        # Status indicator
        status_box = BoxLayout(size_hint_y=None, height=dp(24))
        status_box.add_widget(Label(
            text='🟢 Live',
            font_size=sp(12),
            color=hex_to_rgba(COLORS['success']),
            halign='left',
            size_hint_x=None,
            width=dp(60)
        ))
        status_box.add_widget(BoxLayout())  # Spacer
        self.add_widget(status_box)
        
        # Project name
        self.add_widget(Label(
            text=self.project.get('name', 'Untitled'),
            font_size=sp(22),
            bold=True,
            color=hex_to_rgba(COLORS['text_primary']),
            halign='left',
            valign='middle',
            size_hint_y=None,
            height=dp(32),
            text_size=(dp(268), None)
        ))
        
        # Tagline
        self.add_widget(Label(
            text=self.project.get('tagline', ''),
            font_size=sp(14),
            color=hex_to_rgba(COLORS['text_secondary']),
            halign='left',
            valign='top',
            size_hint_y=None,
            height=dp(40),
            text_size=(dp(268), None)
        ))
        
        # Tech stack
        tech_box = BoxLayout(size_hint_y=None, height=dp(36), spacing=dp(8))
        tech_stack = self.project.get('tech_stack', [])
        for tech in tech_stack[:4]:
            tech_name = tech.get('name', tech) if isinstance(tech, dict) else tech
            btn = Button(
                text=tech_name,
                font_size=sp(11),
                size_hint=(None, None),
                size=(dp(70), dp(28)),
                background_color=hex_to_rgba(COLORS['accent'], 0.2),
                color=hex_to_rgba(COLORS['accent_light'])
            )
            btn.background_normal = ''
            tech_box.add_widget(btn)
        tech_box.add_widget(BoxLayout())  # Spacer
        self.add_widget(tech_box)
        
        # Metrics
        metrics = self.project.get('metrics', {})
        if metrics:
            metrics_box = BoxLayout(size_hint_y=None, height=dp(32), spacing=dp(16))
            for key, value in list(metrics.items())[:2]:
                metrics_box.add_widget(Label(
                    text=f"{value}",
                    font_size=sp(12),
                    color=hex_to_rgba(COLORS['text_muted']),
                    halign='left'
                ))
            self.add_widget(metrics_box)
        
        # Spacer
        self.add_widget(BoxLayout())
        
        # Action buttons
        btn_box = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(12))
        
        # Visit button
        visit_btn = Button(
            text='Visit Site',
            font_size=sp(14),
            bold=True,
            background_color=hex_to_rgba(COLORS['accent']),
            color=hex_to_rgba(COLORS['text_primary']),
            size_hint_x=0.6
        )
        visit_btn.background_normal = ''
        visit_btn.bind(on_release=self._on_visit)
        btn_box.add_widget(visit_btn)
        
        # QR button
        qr_btn = Button(
            text='QR',
            font_size=sp(14),
            bold=True,
            background_color=hex_to_rgba(COLORS['bg_secondary']),
            color=hex_to_rgba(COLORS['text_primary']),
            size_hint_x=0.4
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
        
        for project in self.projects:
            card_container = BoxLayout(padding=dp(24))
            card = ProjectCard(
                project,
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
