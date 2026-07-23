"""
Login system for 3D Ludo.
This module handles user authentication, accounts, and online features.
"""

import json
import hashlib
import time
import secrets
import threading
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timedelta
class AuthProvider(Enum):
    LOCAL = "local"
    GOOGLE = "google"
    FACEBOOK = "facebook"
    APPLE = "apple"
    MICROSOFT = "microsoft"
class AccountStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    BANNED = "banned"
    DELETED = "deleted"
class TwoFactorMethod(Enum):
    NONE = "none"
    SMS = "sms"
    EMAIL = "email"
    AUTH_APP = "auth_app"
@dataclass
class UserProfile:
    """User profile information."""

    user_id: str
    username: str
    email: str
    display_name: str
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    country: Optional[str] = None
    birthday: Optional[str] = None
    created_at: str = ""
    last_login: str = ""
    status: AccountStatus = AccountStatus.INACTIVE
    is_verified: bool = False
    preferences: Dict[str, Any] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'display_name': self.display_name,
            'avatar_url': self.avatar_url,
            'bio': self.bio,
            'country': self.country,
            'birthday': self.birthday,
            'created_at': self.created_at,
            'last_login': self.last_login,
            'status': self.status.value,
            'is_verified': self.is_verified,
            'preferences': self.preferences or {}
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserProfile':
        return cls(
            user_id=data['user_id'],
            username=data['username'],
            email=data['email'],
            display_name=data['display_name'],
            avatar_url=data.get('avatar_url'),
            bio=data.get('bio'),
            country=data.get('country'),
            birthday=data.get('birthday'),
            created_at=data.get('created_at', ''),
            last_login=data.get('last_login', ''),
            status=AccountStatus(data.get('status', 'inactive')),
            is_verified=data.get('is_verified', False),
            preferences=data.get('preferences', {})
        )
@dataclass
class Session:
    """User session."""

    session_id: str
    user_id: str
    token: str
    created_at: str
    expires_at: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    is_active: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            'session_id': self.session_id,
            'user_id': self.user_id,
            'token': self.token,
            'created_at': self.created_at,
            'expires_at': self.expires_at,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'is_active': self.is_active
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Session':
        return cls(
            session_id=data['session_id'],
            user_id=data['user_id'],
            token=data['token'],
            created_at=data['created_at'],
            expires_at=data['expires_at'],
            ip_address=data.get('ip_address'),
            user_agent=data.get('user_agent'),
            is_active=data.get('is_active', True)
        )
@dataclass
class PasswordReset:
    """Password reset request."""

    reset_id: str
    user_id: str
    token: str
    expires_at: str
    used: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            'reset_id': self.reset_id,
            'user_id': self.user_id,
            'token': self.token,
            'expires_at': self.expires_at,
            'used': self.used
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PasswordReset':
        return cls(
            reset_id=data['reset_id'],
            user_id=data['user_id'],
            token=data['token'],
            expires_at=data['expires_at'],
            used=data.get('used', False)
        )
class LoginSystem:
    """
    Login system for 3D Ludo.
    Handles user authentication, accounts, and online features.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the login system with configuration.

        Args:
            config: Login system configuration dictionary
        """
        self.config = config
        self.is_enabled = config.get('enabled', True)
        self.require_login = config.get('require_login', True)
        self.providers = [AuthProvider.LOCAL]

        # Add other providers if configured
        provider_configs = config.get('providers', [])
        for provider_config in provider_configs:
            try:
                provider = AuthProvider(provider_config)
                if provider not in self.providers:
                    self.providers.append(provider)
            except ValueError:
                pass

        # Account data storage
        self.users: Dict[str, UserProfile] = {}
        self.sessions: Dict[str, Session] = {}
        self.password_resets: Dict[str, PasswordReset] = {}

        # Load existing data
        self._load_user_data()

        # Session cleanup
        self.session_cleanup_interval = config.get('session_cleanup_interval', 3600)  # 1 hour
        self.password_reset_cleanup_interval = config.get('password_reset_cleanup_interval', 86400)  # 24 hours
        self.last_session_cleanup = time.time()
        self.last_password_reset_cleanup = time.time()

    def _load_user_data(self) -> None:
        """Load user data from files."""
        data_dir = self.config.get('data_directory', 'data')
        users_file = os.path.join(data_dir, 'users.json')
        sessions_file = os.path.join(data_dir, 'sessions.json')
        resets_file = os.path.join(data_dir, 'password_resets.json')

        # Load users
        if os.path.exists(users_file):
            try:
                with open(users_file, 'r') as f:
                    users_data = json.load(f)
                    for user_data in users_data:
                        user = UserProfile.from_dict(user_data)
                        self.users[user.user_id] = user
            except Exception as e:
                print(f"Error loading users: {e}")

        # Load sessions
        if os.path.exists(sessions_file):
            try:
                with open(sessions_file, 'r') as f:
                    sessions_data = json.load(f)
                    for session_data in sessions_data:
                        session = Session.from_dict(session_data)
                        self.sessions[session.session_id] = session
            except Exception as e:
                print(f"Error loading sessions: {e}")

        # Load password resets
        if os.path.exists(resets_file):
            try:
                with open(resets_file, 'r') as f:
                    resets_data = json.load(f)
                    for reset_data in resets_data:
                        reset = PasswordReset.from_dict(reset_data)
                        self.password_resets[reset.reset_id] = reset
            except Exception as e:
                print(f"Error loading password resets: {e}")

    def _save_user_data(self) -> None:
        """Save user data to files."""
        data_dir = self.config.get('data_directory', 'data')
        os.makedirs(data_dir, exist_ok=True)

        # Save users
        users_data = [user.to_dict() for user in self.users.values()]
        with open(os.path.join(data_dir, 'users.json'), 'w') as f:
            json.dump(users_data, f, indent=2)

        # Save sessions
        sessions_data = [session.to_dict() for session in self.sessions.values()]
        with open(os.path.join(data_dir, 'sessions.json'), 'w') as f:
            json.dump(sessions_data, f, indent=2)

        # Save password resets
        resets_data = [reset.to_dict() for reset in self.password_resets.values()]
        with open(os.path.join(data_dir, 'password_resets.json'), 'w') as f:
            json.dump(resets_data, f, indent=2)

    def register(self, username: str, email: str, password: str,
                 display_name: str, auth_provider: AuthProvider = AuthProvider.LOCAL) -> Tuple[bool, str]:
        """
        Register a new user account.

        Args:
            username: Username
            email: Email address
            password: Password
            display_name: Display name
            auth_provider: Authentication provider

        Returns:
            Tuple of (success, message)
        """
        if not self.is_enabled:
            return False, "Login system is disabled"

        # Validate input
        if not username or not email or not password or not display_name:
            return False, "All fields are required"

        if len(username) < 3 or len(username) > 30:
            return False, "Username must be between 3 and 30 characters"

        if len(password) < 8:
            return False, "Password must be at least 8 characters"

        if auth_provider not in self.providers:
            return False, f"Authentication provider {auth_provider.value} is not supported"

        # Check if username or email already exists
        for user in self.users.values():
            if user.username.lower() == username.lower():
                return False, "Username already exists"

            if user.email.lower() == email.lower():
                return False, "Email already exists"

        # Create user
        user_id = secrets.token_hex(16)
        created_at = datetime.now().isoformat()

        user = UserProfile(
            user_id=user_id,
            username=username,
            email=email,
            display_name=display_name,
            created_at=created_at,
            status=AccountStatus.ACTIVE,
            is_verified=False,
            preferences=self.config.get('default_preferences', {})
        )

        # Hash and store password
        password_hash = self._hash_password(password, auth_provider)
        user.preferences['password_hash'] = password_hash

        # Add user
        self.users[user_id] = user
        self._save_user_data()

        # Send verification email if needed
        if self.config.get('require_email_verification', False):
            self._send_verification_email(user)

        return True, "Account created successfully"

    def login(self, username_or_email: str, password: str,
              ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> Tuple[bool, str, Optional[Session]]:
        """
        Log a user in.

        Args:
            username_or_email: Username or email address
            password: Password
            ip_address: User's IP address
            user_agent: User's user agent

        Returns:
            Tuple of (success, message, session)
        """
        if not self.is_enabled:
            return False, "Login system is disabled", None

        # Find user
        user = None
        for u in self.users.values():
            if u.username.lower() == username_or_email.lower() or u.email.lower() == username_or_email.lower():
                user = u
                break

        if not user:
            return False, "Invalid username or password", None

        # Check account status
        if user.status != AccountStatus.ACTIVE:
            if user.status == AccountStatus.BANNED:
                return False, "Account is banned", None
            elif user.status == AccountStatus.SUSPENDED:
                return False, "Account is suspended", None
            else:
                return False, "Account is not active", None

        # Verify password
        password_hash = user.preferences.get('password_hash', '')
        if not self._verify_password(password, password_hash):
            # Increment failed login attempts
            self._increment_failed_login_attempts(user)
            return False, "Invalid username or password", None

        # Check two-factor authentication
        if user.preferences.get('two_factor_method') != TwoFactorMethod.NONE:
            # In a real implementation, this would prompt for 2FA code
            return False, "Two-factor authentication required", None

        # Create session
        session = self._create_session(user, ip_address, user_agent)
        if session:
            # Update user last login
            user.last_login = datetime.now().isoformat()

            # Reset failed login attempts
            user.preferences['failed_login_attempts'] = 0
            user.preferences['last_failed_login'] = None

            self._save_user_data()

            return True, "Login successful", session

        return False, "Error creating session", None

    def logout(self, session_id: str) -> bool:
        """
        Log a user out.

        Args:
            session_id: Session ID to invalidate

        Returns:
            True if logged out successfully, False otherwise
        """
        if session_id in self.sessions:
            session = self.sessions[session_id]
            session.is_active = False
            self._save_user_data()
            return True

        return False

    def is_authenticated(self, session_id: Optional[str] = None) -> bool:
        """
        Check if a session is authenticated.

        Args:
            session_id: Session ID to check

        Returns:
            True if session is authenticated, False otherwise
        """
        # If no session_id provided, return True if any active session exists
        if session_id is None:
            for s in self.sessions.values():
                try:
                    if s.is_active and datetime.fromisoformat(s.expires_at) > datetime.now():
                        return True
                except Exception:
                    continue
            return False

        if session_id not in self.sessions:
            return False

        session = self.sessions[session_id]

        # Check if session is active
        if not session.is_active:
            return False

        # Check if session is expired
        expires_at = datetime.fromisoformat(session.expires_at)
        if expires_at < datetime.now():
            # Session expired
            del self.sessions[session_id]
            self._save_user_data()
            return False

        return True

    def get_user(self, user_id: str) -> Optional[UserProfile]:
        """
        Get user by ID.

        Args:
            user_id: User ID

        Returns:
            User profile or None
        """
        return self.users.get(user_id)

    def get_session(self, session_id: str) -> Optional[Session]:
        """
        Get session by ID.

        Args:
            session_id: Session ID

        Returns:
            Session or None
        """
        return self.sessions.get(session_id)

    def forgot_password(self, username_or_email: str) -> Tuple[bool, str]:
        """
        Handle password reset request.

        Args:
            username_or_email: Username or email address

        Returns:
            Tuple of (success, message)
        """
        # Find user
        user = None
        for u in self.users.values():
            if u.username.lower() == username_or_email.lower() or u.email.lower() == username_or_email.lower():
                user = u
                break

        if not user:
            return False, "User not found"

        # Create password reset token
        reset_id = secrets.token_hex(16)
        token = secrets.token_hex(32)
        expires_at = (datetime.now() + timedelta(hours=1)).isoformat()

        reset = PasswordReset(
            reset_id=reset_id,
            user_id=user.user_id,
            token=token,
            expires_at=expires_at
        )

        self.password_resets[reset_id] = reset
        self._save_user_data()

        # Send reset email
        self._send_password_reset_email(user, reset)

        return True, "Password reset email sent"

    def reset_password(self, token: str, new_password: str) -> Tuple[bool, str]:
        """
        Reset password using reset token.

        Args:
            token: Password reset token
            new_password: New password

        Returns:
            Tuple of (success, message)
        """
        # Find reset
        reset = None
        for r in self.password_resets.values():
            if r.token == token:
                reset = r
                break

        if not reset:
            return False, "Invalid reset token"

        # Check if reset is used or expired
        expires_at = datetime.fromisoformat(reset.expires_at)
        if expires_at < datetime.now():
            del self.password_resets[reset.reset_id]
            self._save_user_data()
            return False, "Reset token has expired"

        if reset.used:
            return False, "Reset token has already been used"

        # Find user
        user = self.users.get(reset.user_id)
        if not user:
            return False, "User not found"

        # Update password
        password_hash = self._hash_password(new_password, AuthProvider.LOCAL)
        user.preferences['password_hash'] = password_hash

        # Mark reset as used
        reset.used = True
        self._save_user_data()

        return True, "Password reset successfully"

    def show_login(self) -> None:
        """Show login interface."""
        # This would display a login UI
        pass

    def update(self, delta_time: float) -> None:
        """
        Update login system.

        Args:
            delta_time: Time elapsed since last update
        """
        current_time = time.time()

        # Cleanup sessions periodically
        if current_time - self.last_session_cleanup > self.session_cleanup_interval:
            self._cleanup_sessions()
            self.last_session_cleanup = current_time

        # Cleanup password resets periodically
        if current_time - self.last_password_reset_cleanup > self.password_reset_cleanup_interval:
            self._cleanup_password_resets()
            self.last_password_reset_cleanup = current_time

    def _create_session(self, user: UserProfile, ip_address: Optional[str], user_agent: Optional[str]) -> Optional[Session]:
        """
        Create a new session for a user.

        Args:
            user: User profile
            ip_address: User's IP address
            user_agent: User's user agent

        Returns:
            Session or None
        """
        # Generate session ID and token
        session_id = secrets.token_hex(16)
        token = secrets.token_hex(32)
        created_at = datetime.now().isoformat()

        # Calculate expiration time
        session_duration = self.config.get('session_duration', 86400)  # 24 hours
        expires_at = (datetime.now() + timedelta(seconds=session_duration)).isoformat()

        # Create session
        session = Session(
            session_id=session_id,
            user_id=user.user_id,
            token=token,
            created_at=created_at,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent
        )

        # Add session
        self.sessions[session_id] = session
        self._save_user_data()

        return session

    def _hash_password(self, password: str, provider: AuthProvider) -> str:
        """
        Hash a password.

        Args:
            password: Password to hash
            provider: Authentication provider

        Returns:
            Hashed password
        """
        if provider == AuthProvider.LOCAL:
            # Use bcrypt in a real implementation
            return hashlib.sha256(password.encode()).hexdigest()
        else:
            # For OAuth providers, password hash is not used
            return ""

    def _verify_password(self, password: str, password_hash: str) -> bool:
        """
        Verify a password against its hash.

        Args:
            password: Password to verify
            password_hash: Stored password hash

        Returns:
            True if password is correct, False otherwise
        """
        # Compute hash and compare
        computed_hash = hashlib.sha256(password.encode()).hexdigest()
        return computed_hash == password_hash

    def _increment_failed_login_attempts(self, user: UserProfile) -> None:
        """
        Increment failed login attempts for a user.

        Args:
            user: User profile
        """
        if 'failed_login_attempts' not in user.preferences:
            user.preferences['failed_login_attempts'] = 0
        else:
            user.preferences['failed_login_attempts'] += 1

        # Record last failed login time
        user.preferences['last_failed_login'] = datetime.now().isoformat()

        # Lock account after too many failed attempts
        max_attempts = self.config.get('max_failed_login_attempts', 5)
        lockout_duration = self.config.get('account_lockout_duration', 3600)  # 1 hour

        if user.preferences['failed_login_attempts'] >= max_attempts:
            user.status = AccountStatus.SUSPENDED
            user.preferences['lockout_until'] = (
                datetime.now() + timedelta(seconds=lockout_duration)
            ).isoformat()

    def _cleanup_sessions(self) -> None:
        """Clean up expired sessions."""
        current_time = datetime.now()

        expired_sessions = []
        for session_id, session in self.sessions.items():
            if not session.is_active:
                expired_sessions.append(session_id)
            else:
                expires_at = datetime.fromisoformat(session.expires_at)
                if expires_at < current_time:
                    expired_sessions.append(session_id)

        for session_id in expired_sessions:
            del self.sessions[session_id]

        if expired_sessions:
            self._save_user_data()

    def _cleanup_password_resets(self) -> None:
        """Clean up expired or used password resets."""
        current_time = datetime.now()

        expired_resets = []
        for reset_id, reset in self.password_resets.items():
            expires_at = datetime.fromisoformat(reset.expires_at)
            if expires_at < current_time or reset.used:
                expired_resets.append(reset_id)

        for reset_id in expired_resets:
            del self.password_resets[reset_id]

        if expired_resets:
            self._save_user_data()

    def _send_verification_email(self, user: UserProfile) -> None:
        """Send email verification."""
        # This would send an email in a real implementation
        pass

    def _send_password_reset_email(self, user: UserProfile, reset: PasswordReset) -> None:
        """Send password reset email."""
        # This would send an email in a real implementation
        pass

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert login system to dictionary for saving.

        Returns:
            Dictionary representation of login system
        """
        return {
            'is_enabled': self.is_enabled,
            'require_login': self.require_login,
            'providers': [provider.value for provider in self.providers],
            'users_count': len(self.users),
            'sessions_count': len(self.sessions),
            'password_resets_count': len(self.password_resets)
        }

    def from_dict(self, data: Dict[str, Any]) -> None:
        """
        Load login system from dictionary.

        Args:
            data: Dictionary representation of login system
        """
        self.is_enabled = data['is_enabled']
        self.require_login = data['require_login']

        # Restore providers
        providers = []
        for provider_name in data['providers']:
            try:
                provider = AuthProvider(provider_name)
                providers.append(provider)
            except ValueError:
                pass
        self.providers = providers

    def cleanup(self) -> None:
        """Cleanup login system resources."""
        self._cleanup_sessions()
        self._cleanup_password_resets()
        self.users.clear()
        self.sessions.clear()
        self.password_resets.clear()

    def save_data(self) -> None:
        """Save all data to files."""
        self._save_user_data()
import os