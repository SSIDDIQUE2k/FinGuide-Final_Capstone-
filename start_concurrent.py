#!/usr/bin/env python3
"""
Concurrent Server Runner - Runs Django and Ollama simultaneously
Handles process management, logging, and graceful shutdown
"""

import subprocess
import time
import os
import sys
import signal
import requests
from pathlib import Path

# Configuration
PROJECT_DIR = Path("/Users/shazibsiddique/Desktop/ai capstone project ")
DJANGO_PORT = 8000
OLLAMA_PORT = 11434
LOG_DIR = Path("/tmp/financial_tools")

# Colors
GREEN = '\033[0;32m'
BLUE = '\033[0;34m'
YELLOW = '\033[1;33m'
RED = '\033[0;31m'
NC = '\033[0m'

class ConcurrentServer:
    def __init__(self):
        self.ollama_process = None
        self.django_process = None
        self.venv_path = PROJECT_DIR / ".venv" / "bin" / "activate"
        self.log_dir = LOG_DIR
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
    def print_banner(self, title):
        print(f"{BLUE}╔════════════════════════════════════════════════════════════╗{NC}")
        print(f"{BLUE}║{title.center(60)}║{NC}")
        print(f"{BLUE}╚════════════════════════════════════════════════════════════╝{NC}")
    
    def print_status(self, icon, message):
        print(f"{GREEN}{icon} {message}{NC}")
    
    def print_warning(self, icon, message):
        print(f"{YELLOW}{icon} {message}{NC}")
    
    def print_error(self, icon, message):
        print(f"{RED}{icon} {message}{NC}")
    
    def check_ollama(self):
        """Check if Ollama is installed"""
        result = subprocess.run(['which', 'ollama'], capture_output=True)
        return result.returncode == 0
    
    def wait_for_ollama(self, timeout=30):
        """Wait for Ollama to be ready"""
        self.print_warning('⏳', 'Waiting for Ollama to be ready...')
        start = time.time()
        while time.time() - start < timeout:
            try:
                response = requests.get(f'http://localhost:{OLLAMA_PORT}/api/tags', timeout=1)
                if response.status_code == 200:
                    self.print_status('✅', 'Ollama is ready')
                    return True
            except Exception:
                pass
            time.sleep(1)
        self.print_warning('⚠️ ', 'Ollama timeout, continuing anyway...')
        return False
    
    def start_ollama(self):
        """Start Ollama server"""
        self.print_status('🚀', 'Starting Ollama server...')
        log_file = self.log_dir / "ollama.log"
        try:
            self.ollama_process = subprocess.Popen(
                ['ollama', 'serve'],
                stdout=open(log_file, 'w'),
                stderr=subprocess.STDOUT,
                preexec_fn=os.setsid
            )
            self.print_status('✅', f'Ollama started (PID: {self.ollama_process.pid})')
            time.sleep(2)
            return True
        except Exception as e:
            self.print_error('❌', f'Failed to start Ollama: {e}')
            return False
    
    def start_django(self):
        """Start Django server"""
        self.print_status('🚀', 'Starting Django server...')
        
        # Run migrations
        self.print_status('🔄', 'Running migrations...')
        os.chdir(PROJECT_DIR)
        migrate_result = subprocess.run(
            f'source {self.venv_path} && python manage.py migrate',
            shell=True,
            capture_output=True,
            text=True
        )
        if migrate_result.returncode != 0:
            self.print_warning('⚠️ ', 'Migration warning (may be okay)')
        
        # Start server
        log_file = self.log_dir / "django.log"
        try:
            self.django_process = subprocess.Popen(
                f'source {self.venv_path} && python manage.py runserver 0.0.0.0:{DJANGO_PORT}',
                shell=True,
                stdout=open(log_file, 'w'),
                stderr=subprocess.STDOUT,
                preexec_fn=os.setsid,
                cwd=PROJECT_DIR
            )
            self.print_status('✅', f'Django started (PID: {self.django_process.pid})')
            time.sleep(2)
            return True
        except Exception as e:
            self.print_error('❌', f'Failed to start Django: {e}')
            return False
    
    def display_info(self):
        """Display startup information"""
        print()
        self.print_banner('🎉 SERVERS RUNNING 🎉')
        print()
        self.print_status('📍', 'Services Available:')
        print(f"   🤖 Ollama:  {YELLOW}http://localhost:{OLLAMA_PORT}{NC}")
        print(f"   💻 Django:  {YELLOW}http://localhost:{DJANGO_PORT}{NC}")
        print()
        self.print_status('📊', 'Open in Browser:')
        print(f"   {YELLOW}http://localhost:{DJANGO_PORT}{NC}")
        print()
        self.print_status('📋', 'Log Files:')
        print(f"   {self.log_dir}/ollama.log")
        print(f"   {self.log_dir}/django.log")
        print()
        self.print_warning('⌨️ ', 'Press Ctrl+C to stop both servers')
        print()
    
    def is_process_alive(self, process):
        """Check if process is still running"""
        if process is None:
            return False
        return process.poll() is None
    
    def monitor_processes(self):
        """Monitor and restart processes if they crash"""
        while True:
            try:
                if not self.is_process_alive(self.ollama_process):
                    self.print_warning('⚠️ ', 'Ollama crashed, restarting...')
                    self.start_ollama()
                    self.wait_for_ollama()
                
                if not self.is_process_alive(self.django_process):
                    self.print_warning('⚠️ ', 'Django crashed, restarting...')
                    self.start_django()
                
                time.sleep(5)
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.print_error('❌', f'Monitor error: {e}')
                time.sleep(5)
    
    def cleanup(self, signum, frame):
        """Clean up processes on exit"""
        print()
        self.print_warning('⏹️ ', 'Shutting down servers...')
        
        if self.ollama_process and self.is_process_alive(self.ollama_process):
            try:
                os.killpg(os.getpgid(self.ollama_process.pid), signal.SIGTERM)
            except Exception:
                pass
        
        if self.django_process and self.is_process_alive(self.django_process):
            try:
                os.killpg(os.getpgid(self.django_process.pid), signal.SIGTERM)
            except Exception:
                pass
        
        self.print_status('✅', 'Servers stopped')
        sys.exit(0)
    
    def run(self):
        """Run both servers concurrently"""
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.cleanup)
        signal.signal(signal.SIGTERM, self.cleanup)
        
        print()
        self.print_banner('💰 Financial Tools - Concurrent Server Runner 💰')
        print()
        
        # Check prerequisites
        if not self.check_ollama():
            self.print_error('❌', 'Ollama not found')
            self.print_warning('⚠️ ', 'Install from https://ollama.ai')
            sys.exit(1)
        
        # Start servers
        if not self.start_ollama():
            sys.exit(1)
        
        self.wait_for_ollama()
        
        if not self.start_django():
            self.cleanup(None, None)
            sys.exit(1)
        
        # Display info and monitor
        self.display_info()
        self.monitor_processes()

if __name__ == '__main__':
    server = ConcurrentServer()
    server.run()
