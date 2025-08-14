"""
Auto-updater module for Bounding Box Plotter using PyUpdater
"""

import os
import sys
import json
import hashlib
import tempfile
import shutil
import subprocess
import threading
import time
from pathlib import Path
from datetime import datetime, timedelta
import logging

try:
    from PyUpdater import Client
    from PyUpdater.utils.config import Config
    PY_UPDATER_AVAILABLE = True
except ImportError:
    PY_UPDATER_AVAILABLE = False
    print("⚠ PyUpdater not available. Auto-updates will be disabled.")

from .version import get_version_info, get_update_url, get_download_url

class AutoUpdater:
    """Handles automatic updates for the application"""
    
    def __init__(self, app_name="Bounding Box Plotter", app_version="2.0.0"):
        self.app_name = app_name
        self.app_version = app_version
        self.logger = logging.getLogger(__name__)
        
        # Update configuration
        self.update_check_interval = 24 * 60 * 60  # 24 hours in seconds
        self.last_update_check = None
        self.update_available = False
        self.update_info = None
        
        # PyUpdater client
        self.client = None
        self.config = None
        
        # Initialize PyUpdater if available
        if PY_UPDATER_AVAILABLE:
            self._initialize_pyupdater()
        
        # Update status
        self.is_checking = False
        self.is_downloading = False
        self.download_progress = 0
        
    def _initialize_pyupdater(self):
        """Initialize PyUpdater client and configuration"""
        try:
            # Create PyUpdater configuration
            self.config = Config()
            self.config.APP_NAME = self.app_name
            self.config.APP_VERSION = self.app_version
            self.config.UPDATE_URLS = [get_update_url()]
            
            # Initialize client
            self.client = Client(self.config)
            self.logger.info("✓ PyUpdater initialized successfully")
            
        except Exception as e:
            self.logger.error(f"✗ Failed to initialize PyUpdater: {e}")
            self.client = None
    
    def check_for_updates(self, force=False):
        """Check for available updates"""
        if not PY_UPDATER_AVAILABLE or not self.client:
            self.logger.warning("⚠ PyUpdater not available - cannot check for updates")
            return False
        
        # Check if we should skip update check
        if not force and self.last_update_check:
            time_since_last_check = time.time() - self.last_update_check
            if time_since_last_check < self.update_check_interval:
                self.logger.info(f"ℹ Update check skipped (last check was {time_since_last_check/3600:.1f} hours ago)")
                return False
        
        self.is_checking = True
        self.logger.info("🔍 Checking for updates...")
        
        try:
            # Check for updates
            update_info = self.client.check_for_updates()
            
            if update_info and update_info.get('available', False):
                self.update_available = True
                self.update_info = update_info
                self.logger.info(f"✓ Update available: {update_info.get('version', 'Unknown')}")
                return True
            else:
                self.update_available = False
                self.update_info = None
                self.logger.info("✓ No updates available")
                return False
                
        except Exception as e:
            self.logger.error(f"✗ Error checking for updates: {e}")
            return False
        finally:
            self.last_update_check = time.time()
            self.is_checking = False
    
    def download_update(self, progress_callback=None):
        """Download the available update"""
        if not self.update_available or not self.update_info:
            self.logger.warning("⚠ No update available to download")
            return False
        
        if not PY_UPDATER_AVAILABLE or not self.client:
            self.logger.error("✗ PyUpdater not available - cannot download update")
            return False
        
        self.is_downloading = True
        self.download_progress = 0
        
        try:
            self.logger.info("📥 Downloading update...")
            
            # Download update with progress tracking
            def progress_hook(progress):
                self.download_progress = progress
                if progress_callback:
                    progress_callback(progress)
            
            # Download the update
            download_result = self.client.download_update(
                self.update_info['version'],
                progress_hook=progress_hook
            )
            
            if download_result:
                self.logger.info("✓ Update downloaded successfully")
                return True
            else:
                self.logger.error("✗ Failed to download update")
                return False
                
        except Exception as e:
            self.logger.error(f"✗ Error downloading update: {e}")
            return False
        finally:
            self.is_downloading = False
            self.download_progress = 0
    
    def install_update(self):
        """Install the downloaded update"""
        if not self.update_available or not self.update_info:
            self.logger.warning("⚠ No update available to install")
            return False
        
        if not PY_UPDATER_AVAILABLE or not self.client:
            self.logger.error("✗ PyUpdater not available - cannot install update")
            return False
        
        try:
            self.logger.info("🔧 Installing update...")
            
            # Install the update
            install_result = self.client.install_update(self.update_info['version'])
            
            if install_result:
                self.logger.info("✓ Update installed successfully")
                self._cleanup_after_update()
                return True
            else:
                self.logger.error("✗ Failed to install update")
                return False
                
        except Exception as e:
            self.logger.error(f"✗ Error installing update: {e}")
            return False
    
    def _cleanup_after_update(self):
        """Clean up after successful update"""
        try:
            # Reset update status
            self.update_available = False
            self.update_info = None
            self.last_update_check = None
            
            # Clear downloaded files
            if hasattr(self.client, 'cleanup'):
                self.client.cleanup()
            
            self.logger.info("✓ Update cleanup completed")
            
        except Exception as e:
            self.logger.warning(f"⚠ Warning during update cleanup: {e}")
    
    def get_update_status(self):
        """Get current update status"""
        return {
            'update_available': self.update_available,
            'update_info': self.update_info,
            'is_checking': self.is_checking,
            'is_downloading': self.is_downloading,
            'download_progress': self.download_progress,
            'last_check': self.last_update_check,
            'next_check': self.last_update_check + self.update_check_interval if self.last_update_check else None
        }
    
    def get_update_summary(self):
        """Get a user-friendly update summary"""
        if not self.update_available:
            return "No updates available"
        
        info = self.update_info or {}
        return {
            'version': info.get('version', 'Unknown'),
            'size': info.get('size', 'Unknown'),
            'description': info.get('description', 'No description available'),
            'release_date': info.get('release_date', 'Unknown'),
            'download_url': info.get('download_url', ''),
            'changelog': info.get('changelog', 'No changelog available')
        }
    
    def schedule_update_check(self, callback=None):
        """Schedule a background update check"""
        def background_check():
            try:
                if self.check_for_updates():
                    if callback:
                        callback(self.get_update_summary())
            except Exception as e:
                self.logger.error(f"✗ Background update check failed: {e}")
        
        # Start background thread
        thread = threading.Thread(target=background_check, daemon=True)
        thread.start()
        return thread
    
    def force_update_check(self):
        """Force an immediate update check"""
        return self.check_for_updates(force=True)
    
    def is_update_ready(self):
        """Check if update is ready to install"""
        return (self.update_available and 
                self.update_info and 
                not self.is_checking and 
                not self.is_downloading)
    
    def get_manual_update_url(self):
        """Get manual update URL for users"""
        return get_download_url()

# Fallback updater for when PyUpdater is not available
class FallbackUpdater:
    """Simple fallback updater that checks GitHub releases"""
    
    def __init__(self, app_name="Bounding Box Plotter", app_version="2.0.0"):
        self.app_name = app_name
        self.app_version = app_version
        self.logger = logging.getLogger(__name__)
        self.update_available = False
        self.update_info = None
    
    def check_for_updates(self, force=False):
        """Check for updates using GitHub API"""
        try:
            import requests
            
            # GitHub API endpoint for releases
            api_url = "https://api.github.com/repos/Raghavendra-Pratap/Plots/releases/latest"
            
            response = requests.get(api_url, timeout=10)
            if response.status_code == 200:
                release_data = response.json()
                latest_version = release_data.get('tag_name', '').lstrip('v')
                
                if self._compare_versions(latest_version, self.app_version) > 0:
                    self.update_available = True
                    self.update_info = {
                        'version': latest_version,
                        'description': release_data.get('body', ''),
                        'download_url': release_data.get('html_url', ''),
                        'release_date': release_data.get('published_at', ''),
                        'size': 'Unknown'
                    }
                    self.logger.info(f"✓ Update available: {latest_version}")
                    return True
                else:
                    self.update_available = False
                    self.logger.info("✓ No updates available")
                    return False
            else:
                self.logger.warning(f"⚠ GitHub API returned status {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"✗ Error checking GitHub for updates: {e}")
            return False
    
    def _compare_versions(self, version1, version2):
        """Compare two version strings"""
        def normalize(v):
            return [int(x) for x in v.split('.')]
        
        try:
            v1 = normalize(version1)
            v2 = normalize(version2)
            
            for i in range(max(len(v1), len(v2))):
                num1 = v1[i] if i < len(v1) else 0
                num2 = v2[i] if i < len(v2) else 0
                if num1 > num2:
                    return 1
                elif num1 < num2:
                    return -1
            return 0
        except:
            return 0
    
    def get_update_status(self):
        """Get current update status"""
        return {
            'update_available': self.update_available,
            'update_info': self.update_info,
            'is_checking': False,
            'is_downloading': False,
            'download_progress': 0
        }
    
    def get_update_summary(self):
        """Get a user-friendly update summary"""
        if not self.update_available:
            return "No updates available"
        
        info = self.update_info or {}
        return {
            'version': info.get('version', 'Unknown'),
            'description': info.get('description', 'No description available'),
            'release_date': info.get('release_date', 'Unknown'),
            'download_url': info.get('download_url', ''),
            'changelog': info.get('description', 'No changelog available')
        }

# Factory function to create the appropriate updater
def create_updater(app_name="Bounding Box Plotter", app_version="2.0.0"):
    """Create the appropriate updater based on available dependencies"""
    if PY_UPDATER_AVAILABLE:
        return AutoUpdater(app_name, app_version)
    else:
        return FallbackUpdater(app_name, app_version)

# Update notification system
class UpdateNotifier:
    """Handles update notifications to users"""
    
    def __init__(self, updater):
        self.updater = updater
        self.notification_shown = False
        self.logger = logging.getLogger(__name__)
    
    def show_update_notification(self, parent_widget=None):
        """Show update notification to user"""
        if self.notification_shown or not self.updater.update_available:
            return
        
        try:
            import tkinter as tk
            from tkinter import messagebox
            
            update_info = self.updater.get_update_summary()
            
            message = f"""A new version of {update_info.get('version', 'Unknown')} is available!

What's new:
{update_info.get('description', 'No description available')}

Would you like to update now?"""
            
            result = messagebox.askyesno("Update Available", message)
            
            if result:
                self._perform_update()
            else:
                self.logger.info("User declined update")
                
        except Exception as e:
            self.logger.error(f"✗ Error showing update notification: {e}")
    
    def _perform_update(self):
        """Perform the update process"""
        try:
            self.logger.info("Starting update process...")
            
            # For now, just open the download URL
            update_info = self.updater.get_update_summary()
            download_url = update_info.get('download_url', '')
            
            if download_url:
                import webbrowser
                webbrowser.open(download_url)
                self.logger.info("✓ Opened download URL in browser")
            else:
                self.logger.warning("⚠ No download URL available")
                
        except Exception as e:
            self.logger.error(f"✗ Error performing update: {e}")
    
    def check_and_notify(self, parent_widget=None):
        """Check for updates and notify if available"""
        if self.updater.check_for_updates():
            self.show_update_notification(parent_widget)
            self.notification_shown = True 