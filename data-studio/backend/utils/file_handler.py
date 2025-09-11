#!/usr/bin/env python3
"""
File Handler Utility for Unified Data Studio
Handles file operations, validation, and processing
"""

import os
import shutil
import hashlib
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import mimetypes

logger = logging.getLogger(__name__)

class FileHandler:
    """Handles file operations and management"""
    
    def __init__(self, base_dir: str = "data"):
        self.base_dir = Path(base_dir)
        self.uploads_dir = self.base_dir / "uploads"
        self.exports_dir = self.base_dir / "exports"
        self.temp_dir = self.base_dir / "temp"
        
        # Create directories if they don't exist
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure all required directories exist"""
        for directory in [self.uploads_dir, self.exports_dir, self.temp_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get comprehensive file information"""
        try:
            path = Path(file_path)
            
            if not path.exists():
                return {'error': 'File does not exist'}
            
            # Get basic file stats
            stat = path.stat()
            
            # Calculate file hash
            file_hash = self.calculate_file_hash(file_path)
            
            # Get MIME type
            mime_type, _ = mimetypes.guess_type(file_path)
            
            return {
                'filename': path.name,
                'file_path': str(path.absolute()),
                'file_size': stat.st_size,
                'file_size_mb': round(stat.st_size / (1024 * 1024), 2),
                'created_time': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified_time': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'accessed_time': datetime.fromtimestamp(stat.st_atime).isoformat(),
                'file_hash': file_hash,
                'mime_type': mime_type,
                'extension': path.suffix.lower(),
                'is_file': path.is_file(),
                'is_directory': path.is_dir(),
                'permissions': oct(stat.st_mode)[-3:]
            }
            
        except Exception as e:
            logger.error(f"Failed to get file info for {file_path}: {e}")
            return {'error': str(e)}
    
    def calculate_file_hash(self, file_path: str, algorithm: str = 'sha256') -> str:
        """Calculate file hash using specified algorithm"""
        try:
            hash_func = hashlib.new(algorithm)
            
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_func.update(chunk)
            
            return hash_func.hexdigest()
            
        except Exception as e:
            logger.error(f"Failed to calculate hash for {file_path}: {e}")
            return ""
    
    def validate_file(self, file_path: str, allowed_extensions: List[str] = None, 
                     max_size_mb: int = 100) -> Dict[str, Any]:
        """Validate file for upload/processing"""
        try:
            validation_result = {
                'valid': True,
                'errors': [],
                'warnings': []
            }
            
            # Check if file exists
            if not os.path.exists(file_path):
                validation_result['valid'] = False
                validation_result['errors'].append("File does not exist")
                return validation_result
            
            # Get file info
            file_info = self.get_file_info(file_path)
            
            if 'error' in file_info:
                validation_result['valid'] = False
                validation_result['errors'].append(f"File info error: {file_info['error']}")
                return validation_result
            
            # Check file size
            max_size_bytes = max_size_mb * 1024 * 1024
            if file_info['file_size'] > max_size_bytes:
                validation_result['valid'] = False
                validation_result['errors'].append(f"File size ({file_info['file_size_mb']} MB) exceeds limit ({max_size_mb} MB)")
            
            # Check file extension
            if allowed_extensions:
                if file_info['extension'] not in allowed_extensions:
                    validation_result['valid'] = False
                    validation_result['errors'].append(f"File extension {file_info['extension']} not allowed. Allowed: {', '.join(allowed_extensions)}")
            
            # Check if file is readable
            try:
                with open(file_path, 'rb') as f:
                    f.read(1)
            except Exception as e:
                validation_result['valid'] = False
                validation_result['errors'].append(f"File is not readable: {str(e)}")
            
            # Check for suspicious file types
            suspicious_extensions = ['.exe', '.bat', '.cmd', '.com', '.pif', '.scr', '.vbs', '.js']
            if file_info['extension'] in suspicious_extensions:
                validation_result['warnings'].append(f"File type {file_info['extension']} may be suspicious")
            
            return validation_result
            
        except Exception as e:
            logger.error(f"File validation failed for {file_path}: {e}")
            return {
                'valid': False,
                'errors': [f"Validation error: {str(e)}"],
                'warnings': []
            }
    
    def copy_file(self, source_path: str, destination_path: str, 
                  overwrite: bool = False) -> Dict[str, Any]:
        """Copy file to destination"""
        try:
            source = Path(source_path)
            destination = Path(destination_path)
            
            # Check if source exists
            if not source.exists():
                return {'success': False, 'error': 'Source file does not exist'}
            
            # Check if destination exists and overwrite is not allowed
            if destination.exists() and not overwrite:
                return {'success': False, 'error': 'Destination file exists and overwrite not allowed'}
            
            # Create destination directory if it doesn't exist
            destination.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            shutil.copy2(source, destination)
            
            # Verify copy
            if destination.exists():
                source_hash = self.calculate_file_hash(source_path)
                dest_hash = self.calculate_file_hash(destination_path)
                
                if source_hash == dest_hash:
                    return {
                        'success': True,
                        'source_path': str(source.absolute()),
                        'destination_path': str(destination.absolute()),
                        'file_size': destination.stat().st_size
                    }
                else:
                    return {'success': False, 'error': 'File copy verification failed'}
            else:
                return {'success': False, 'error': 'Destination file not found after copy'}
                
        except Exception as e:
            logger.error(f"File copy failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def move_file(self, source_path: str, destination_path: str, 
                  overwrite: bool = False) -> Dict[str, Any]:
        """Move file to destination"""
        try:
            source = Path(source_path)
            destination = Path(destination_path)
            
            # Check if source exists
            if not source.exists():
                return {'success': False, 'error': 'Source file does not exist'}
            
            # Check if destination exists and overwrite is not allowed
            if destination.exists() and not overwrite:
                return {'success': False, 'error': 'Destination file exists and overwrite not allowed'}
            
            # Create destination directory if it doesn't exist
            destination.parent.mkdir(parents=True, exist_ok=True)
            
            # Move file
            shutil.move(source, destination)
            
            # Verify move
            if destination.exists() and not source.exists():
                return {
                    'success': True,
                    'source_path': str(source.absolute()),
                    'destination_path': str(destination.absolute()),
                    'file_size': destination.stat().st_size
                }
            else:
                return {'success': False, 'error': 'File move verification failed'}
                
        except Exception as e:
            logger.error(f"File move failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def delete_file(self, file_path: str) -> Dict[str, Any]:
        """Delete file"""
        try:
            path = Path(file_path)
            
            if not path.exists():
                return {'success': False, 'error': 'File does not exist'}
            
            # Get file info before deletion
            file_info = self.get_file_info(file_path)
            
            # Delete file
            path.unlink()
            
            # Verify deletion
            if not path.exists():
                return {
                    'success': True,
                    'deleted_file': file_info,
                    'deletion_time': datetime.now().isoformat()
                }
            else:
                return {'success': False, 'error': 'File still exists after deletion'}
                
        except Exception as e:
            logger.error(f"File deletion failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def create_backup(self, file_path: str, backup_dir: str = None) -> Dict[str, Any]:
        """Create backup of file"""
        try:
            if backup_dir is None:
                backup_dir = self.base_dir / "backups"
            
            backup_dir = Path(backup_dir)
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            source = Path(file_path)
            if not source.exists():
                return {'success': False, 'error': 'Source file does not exist'}
            
            # Create backup filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"{source.stem}_backup_{timestamp}{source.suffix}"
            backup_path = backup_dir / backup_filename
            
            # Copy file to backup location
            copy_result = self.copy_file(file_path, str(backup_path))
            
            if copy_result['success']:
                return {
                    'success': True,
                    'original_file': str(source.absolute()),
                    'backup_file': str(backup_path.absolute()),
                    'backup_time': timestamp,
                    'backup_size': backup_path.stat().st_size
                }
            else:
                return copy_result
                
        except Exception as e:
            logger.error(f"Backup creation failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def list_directory(self, directory_path: str, pattern: str = "*", 
                      recursive: bool = False) -> Dict[str, Any]:
        """List files in directory"""
        try:
            directory = Path(directory_path)
            
            if not directory.exists():
                return {'success': False, 'error': 'Directory does not exist'}
            
            if not directory.is_dir():
                return {'success': False, 'error': 'Path is not a directory'}
            
            files = []
            directories = []
            
            if recursive:
                # Recursive search
                for item in directory.rglob(pattern):
                    if item.is_file():
                        files.append(self.get_file_info(str(item)))
                    elif item.is_dir():
                        directories.append(str(item))
            else:
                # Non-recursive search
                for item in directory.glob(pattern):
                    if item.is_file():
                        files.append(self.get_file_info(str(item)))
                    elif item.is_dir():
                        directories.append(str(item))
            
            return {
                'success': True,
                'directory': str(directory.absolute()),
                'files': files,
                'directories': directories,
                'total_files': len(files),
                'total_directories': len(directories),
                'pattern': pattern,
                'recursive': recursive
            }
            
        except Exception as e:
            logger.error(f"Directory listing failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def cleanup_temp_files(self, max_age_hours: int = 24) -> Dict[str, Any]:
        """Clean up temporary files older than specified age"""
        try:
            cleanup_stats = {
                'files_removed': 0,
                'bytes_freed': 0,
                'errors': []
            }
            
            current_time = datetime.now()
            max_age_seconds = max_age_hours * 3600
            
            for temp_file in self.temp_dir.iterdir():
                if temp_file.is_file():
                    try:
                        # Check file age
                        file_age = current_time.timestamp() - temp_file.stat().st_mtime
                        
                        if file_age > max_age_seconds:
                            # Get file size before deletion
                            file_size = temp_file.stat().st_size
                            
                            # Delete old file
                            temp_file.unlink()
                            
                            cleanup_stats['files_removed'] += 1
                            cleanup_stats['bytes_freed'] += file_size
                            
                    except Exception as e:
                        cleanup_stats['errors'].append(f"Failed to clean up {temp_file}: {str(e)}")
            
            return cleanup_stats
            
        except Exception as e:
            logger.error(f"Temp file cleanup failed: {e}")
            return {'error': str(e)}
    
    def get_storage_info(self) -> Dict[str, Any]:
        """Get storage information for all data directories"""
        try:
            storage_info = {}
            
            for directory_name in ['data', 'uploads', 'exports', 'temp', 'backups']:
                directory = self.base_dir / directory_name
                
                if directory.exists():
                    total_size = 0
                    file_count = 0
                    
                    for item in directory.rglob('*'):
                        if item.is_file():
                            total_size += item.stat().st_size
                            file_count += 1
                    
                    storage_info[directory_name] = {
                        'path': str(directory.absolute()),
                        'total_size_bytes': total_size,
                        'total_size_mb': round(total_size / (1024 * 1024), 2),
                        'file_count': file_count
                    }
                else:
                    storage_info[directory_name] = {
                        'path': str(directory.absolute()),
                        'total_size_bytes': 0,
                        'total_size_mb': 0,
                        'file_count': 0
                    }
            
            return storage_info
            
        except Exception as e:
            logger.error(f"Storage info retrieval failed: {e}")
            return {'error': str(e)}
