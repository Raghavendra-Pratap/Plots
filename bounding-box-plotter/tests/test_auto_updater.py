"""
Tests for the auto-updater module
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add the parent directory to the path to import the module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auto_updater import AutoUpdater, FallbackUpdater, create_updater, UpdateNotifier

class TestAutoUpdater:
    """Test cases for AutoUpdater class"""
    
    def test_initialization(self):
        """Test AutoUpdater initialization"""
        updater = AutoUpdater("Test App", "1.0.0")
        assert updater.app_name == "Test App"
        assert updater.app_version == "1.0.0"
        assert updater.update_check_interval == 24 * 60 * 60  # 24 hours
    
    def test_update_status_initial(self):
        """Test initial update status"""
        updater = AutoUpdater("Test App", "1.0.0")
        status = updater.get_update_status()
        
        assert status['update_available'] == False
        assert status['is_checking'] == False
        assert status['is_downloading'] == False
        assert status['download_progress'] == 0
    
    @patch('auto_updater.PY_UPDATER_AVAILABLE', False)
    def test_pyupdater_unavailable(self):
        """Test behavior when PyUpdater is not available"""
        updater = AutoUpdater("Test App", "1.0.0")
        assert updater.client is None
        
        # Should return False when PyUpdater is not available
        result = updater.check_for_updates()
        assert result == False
    
    def test_force_update_check(self):
        """Test forced update check"""
        updater = AutoUpdater("Test App", "1.0.0")
        
        # Mock the check_for_updates method
        with patch.object(updater, 'check_for_updates') as mock_check:
            mock_check.return_value = True
            result = updater.force_update_check()
            assert result == True
            mock_check.assert_called_once_with(force=True)
    
    def test_is_update_ready(self):
        """Test update readiness check"""
        updater = AutoUpdater("Test App", "1.0.0")
        
        # Initially should not be ready
        assert updater.is_update_ready() == False
        
        # Set update as available
        updater.update_available = True
        updater.update_info = {'version': '2.0.0'}
        updater.is_checking = False
        updater.is_downloading = False
        
        assert updater.is_update_ready() == True

class TestFallbackUpdater:
    """Test cases for FallbackUpdater class"""
    
    def test_initialization(self):
        """Test FallbackUpdater initialization"""
        updater = FallbackUpdater("Test App", "1.0.0")
        assert updater.app_name == "Test App"
        assert updater.app_version == "1.0.0"
        assert updater.update_available == False
    
    def test_version_comparison(self):
        """Test version comparison logic"""
        updater = FallbackUpdater("Test App", "1.0.0")
        
        # Test version comparison
        assert updater._compare_versions("2.0.0", "1.0.0") == 1  # Newer
        assert updater._compare_versions("1.0.0", "2.0.0") == -1  # Older
        assert updater._compare_versions("1.0.0", "1.0.0") == 0   # Same
    
    @patch('auto_updater.requests.get')
    def test_github_api_check_success(self, mock_get):
        """Test successful GitHub API check"""
        updater = FallbackUpdater("Test App", "1.0.0")
        
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'tag_name': 'v2.0.0',
            'body': 'New features and improvements',
            'html_url': 'https://github.com/test/repo/releases/tag/v2.0.0',
            'published_at': '2025-01-18T10:00:00Z'
        }
        mock_get.return_value = mock_response
        
        result = updater.check_for_updates()
        assert result == True
        assert updater.update_available == True
        assert updater.update_info['version'] == '2.0.0'
    
    @patch('auto_updater.requests.get')
    def test_github_api_check_no_update(self, mock_get):
        """Test GitHub API check when no update is available"""
        updater = FallbackUpdater("Test App", "2.0.0")  # Same version
        
        # Mock successful response with same version
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'tag_name': 'v2.0.0',
            'body': 'No new features',
            'html_url': 'https://github.com/test/repo/releases/tag/v2.0.0',
            'published_at': '2025-01-18T10:00:00Z'
        }
        mock_get.return_value = mock_response
        
        result = updater.check_for_updates()
        assert result == False
        assert updater.update_available == False
    
    @patch('auto_updater.requests.get')
    def test_github_api_check_failure(self, mock_get):
        """Test GitHub API check failure"""
        updater = FallbackUpdater("Test App", "1.0.0")
        
        # Mock failed response
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        result = updater.check_for_updates()
        assert result == False
        assert updater.update_available == False
    
    @patch('auto_updater.requests.get')
    def test_github_api_check_exception(self, mock_get):
        """Test GitHub API check with exception"""
        updater = FallbackUpdater("Test App", "1.0.0")
        
        # Mock exception
        mock_get.side_effect = Exception("Network error")
        
        result = updater.check_for_updates()
        assert result == False
        assert updater.update_available == False

class TestUpdateNotifier:
    """Test cases for UpdateNotifier class"""
    
    def test_initialization(self):
        """Test UpdateNotifier initialization"""
        updater = Mock()
        notifier = UpdateNotifier(updater)
        
        assert notifier.updater == updater
        assert notifier.notification_shown == False
    
    def test_notification_not_shown_when_no_update(self):
        """Test that notification is not shown when no update is available"""
        updater = Mock()
        updater.update_available = False
        
        notifier = UpdateNotifier(updater)
        notifier.show_update_notification()
        
        # Should not show notification
        assert notifier.notification_shown == False
    
    def test_notification_shown_once(self):
        """Test that notification is only shown once"""
        updater = Mock()
        updater.update_available = True
        updater.get_update_summary.return_value = {
            'version': '2.0.0',
            'description': 'Test update'
        }
        
        notifier = UpdateNotifier(updater)
        
        # First call should show notification
        with patch('tkinter.messagebox.askyesno') as mock_ask:
            mock_ask.return_value = False
            notifier.show_update_notification()
            assert notifier.notification_shown == True
        
        # Second call should not show notification
        notifier.show_update_notification()
        # Should not call askyesno again

class TestCreateUpdater:
    """Test cases for create_updater function"""
    
    @patch('auto_updater.PY_UPDATER_AVAILABLE', True)
    def test_create_auto_updater(self):
        """Test creating AutoUpdater when PyUpdater is available"""
        updater = create_updater("Test App", "1.0.0")
        assert isinstance(updater, AutoUpdater)
    
    @patch('auto_updater.PY_UPDATER_AVAILABLE', False)
    def test_create_fallback_updater(self):
        """Test creating FallbackUpdater when PyUpdater is not available"""
        updater = create_updater("Test App", "1.0.0")
        assert isinstance(updater, FallbackUpdater)

class TestIntegration:
    """Integration tests for the auto-updater system"""
    
    def test_updater_lifecycle(self):
        """Test complete updater lifecycle"""
        updater = FallbackUpdater("Test App", "1.0.0")
        
        # Initial state
        assert updater.update_available == False
        assert updater.get_update_status()['update_available'] == False
        
        # Simulate update check
        with patch('auto_updater.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'tag_name': 'v2.0.0',
                'body': 'Test update',
                'html_url': 'https://test.com',
                'published_at': '2025-01-18T10:00:00Z'
            }
            mock_get.return_value = mock_response
            
            result = updater.check_for_updates()
            assert result == True
        
        # Check final state
        assert updater.update_available == True
        assert updater.get_update_status()['update_available'] == True
        
        # Test update summary
        summary = updater.get_update_summary()
        assert summary['version'] == '2.0.0'
        assert summary['description'] == 'Test update'

if __name__ == '__main__':
    pytest.main([__file__]) 