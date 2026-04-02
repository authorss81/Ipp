"""
FTP module for Ipp language - FTP client support
"""
from ftplib import FTP, FTP_TLS
import os


class FTPClient:
    """FTP client wrapper for Ipp"""
    
    def __init__(self, host=None, user=None, password='', secure=False):
        self.host = host
        self.user = user
        self.password = password
        self.secure = secure
        self._ftp = None
        self.connected = False
    
    def connect(self, host=None, user=None, password='', port=21):
        """Connect to an FTP server"""
        host = host or self.host
        user = user or self.user
        password = password or self.password
        
        if not host or not user:
            raise RuntimeError("Host and user are required for FTP connection")
        
        try:
            if self.secure:
                self._ftp = FTP_TLS()
            else:
                self._ftp = FTP()
            
            self._ftp.connect(host, port)
            self._ftp.login(user, password)
            self.connected = True
            return True
        except Exception as e:
            raise RuntimeError(f"FTP connection failed: {e}")
    
    def disconnect(self):
        """Disconnect from the FTP server"""
        if self._ftp and self.connected:
            try:
                self._ftp.quit()
            except Exception:
                pass
            self.connected = False
    
    def list_files(self, path='.'):
        """List files in a directory"""
        if not self.connected:
            raise RuntimeError("Not connected to FTP server")
        
        try:
            files = []
            self._ftp.dir(path, files.append)
            return files
        except Exception as e:
            raise RuntimeError(f"Failed to list files: {e}")
    
    def list_names(self, path='.'):
        """List file names in a directory (names only)"""
        if not self.connected:
            raise RuntimeError("Not connected to FTP server")
        
        try:
            names = []
            self._ftp.retrlines(f'NLST {path}', names.append)
            return names
        except Exception as e:
            raise RuntimeError(f"Failed to list names: {e}")
    
    def change_dir(self, path):
        """Change the current directory"""
        if not self.connected:
            raise RuntimeError("Not connected to FTP server")
        
        try:
            self._ftp.cwd(path)
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to change directory: {e}")
    
    def get_file(self, remote_path, local_path=None):
        """Download a file from the FTP server"""
        if not self.connected:
            raise RuntimeError("Not connected to FTP server")
        
        if local_path is None:
            local_path = os.path.basename(remote_path)
        
        try:
            with open(local_path, 'wb') as f:
                self._ftp.retrbinary(f'RETR {remote_path}', f.write)
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to download file: {e}")
    
    def put_file(self, local_path, remote_path=None):
        """Upload a file to the FTP server"""
        if not self.connected:
            raise RuntimeError("Not connected to FTP server")
        
        if remote_path is None:
            remote_path = os.path.basename(local_path)
        
        try:
            with open(local_path, 'rb') as f:
                self._ftp.storbinary(f'STOR {remote_path}', f)
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to upload file: {e}")
    
    def delete_file(self, path):
        """Delete a file on the FTP server"""
        if not self.connected:
            raise RuntimeError("Not connected to FTP server")
        
        try:
            self._ftp.delete(path)
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to delete file: {e}")
    
    def make_dir(self, path):
        """Create a directory on the FTP server"""
        if not self.connected:
            raise RuntimeError("Not connected to FTP server")
        
        try:
            self._ftp.mkd(path)
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to create directory: {e}")
    
    def remove_dir(self, path):
        """Remove a directory on the FTP server"""
        if not self.connected:
            raise RuntimeError("Not connected to FTP server")
        
        try:
            self._ftp.rmd(path)
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to remove directory: {e}")
    
    def get_size(self, path):
        """Get the size of a file on the FTP server"""
        if not self.connected:
            raise RuntimeError("Not connected to FTP server")
        
        try:
            return self._ftp.size(path)
        except Exception as e:
            raise RuntimeError(f"Failed to get file size: {e}")
    
    def __repr__(self):
        return f"<FTPClient host={self.host} connected={self.connected}>"


def ftp_connect(host, user, password='', port=21, secure=False):
    """Create and connect an FTP client"""
    client = FTPClient(host, user, password, secure)
    client.connect(host, user, password, port)
    return client


def ftp_disconnect(client):
    """Disconnect an FTP client"""
    if not isinstance(client, FTPClient):
        raise RuntimeError("First argument must be an FTPClient")
    client.disconnect()
    return True


def ftp_list(client, path='.'):
    """List files via FTP"""
    if not isinstance(client, FTPClient):
        raise RuntimeError("First argument must be an FTPClient")
    return client.list_names(path)


def ftp_get(client, remote_path, local_path=None):
    """Download a file via FTP"""
    if not isinstance(client, FTPClient):
        raise RuntimeError("First argument must be an FTPClient")
    return client.get_file(remote_path, local_path)


def ftp_put(client, local_path, remote_path=None):
    """Upload a file via FTP"""
    if not isinstance(client, FTPClient):
        raise RuntimeError("First argument must be an FTPClient")
    return client.put_file(local_path, remote_path)
