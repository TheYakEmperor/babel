"""
Wiki-style database for user accounts, sessions, revisions, and moderation.
Uses SQLite for persistent storage.
"""

import sqlite3
import hashlib
import secrets
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path(__file__).parent / 'wiki.db'

def get_db():
    """Get database connection with row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database schema."""
    conn = get_db()
    c = conn.cursor()
    
    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'pending',  -- pending, viewer, editor, admin
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            email_verified INTEGER DEFAULT 0,
            verification_token TEXT,
            last_login TEXT,
            edit_count INTEGER DEFAULT 0
        )
    ''')
    
    # Sessions table
    c.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            session_token TEXT UNIQUE NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            expires_at TEXT NOT NULL,
            ip_address TEXT,
            user_agent TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Revisions table - stores all edits
    c.execute('''
        CREATE TABLE IF NOT EXISTS revisions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_type TEXT NOT NULL,  -- text, work, author, region, page_order
            entity_id TEXT NOT NULL,
            user_id INTEGER,
            username TEXT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            action TEXT NOT NULL,  -- create, update, delete
            summary TEXT,
            data_before TEXT,  -- JSON
            data_after TEXT,   -- JSON
            ip_address TEXT,
            is_minor INTEGER DEFAULT 0,
            is_approved INTEGER DEFAULT 1,  -- 0 = pending moderation
            approved_by INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Page locks - prevent edit conflicts
    c.execute('''
        CREATE TABLE IF NOT EXISTS page_locks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_type TEXT NOT NULL,
            entity_id TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            acquired_at TEXT DEFAULT CURRENT_TIMESTAMP,
            expires_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(entity_type, entity_id)
        )
    ''')
    
    # Watchlist - users watching specific entities
    c.execute('''
        CREATE TABLE IF NOT EXISTS watchlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            entity_type TEXT NOT NULL,
            entity_id TEXT NOT NULL,
            added_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(user_id, entity_type, entity_id)
        )
    ''')
    
    # Moderation queue - edits pending approval
    c.execute('''
        CREATE TABLE IF NOT EXISTS moderation_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            revision_id INTEGER NOT NULL,
            status TEXT DEFAULT 'pending',  -- pending, approved, rejected
            reviewed_by INTEGER,
            reviewed_at TEXT,
            rejection_reason TEXT,
            FOREIGN KEY (revision_id) REFERENCES revisions(id),
            FOREIGN KEY (reviewed_by) REFERENCES users(id)
        )
    ''')
    
    # Create indexes
    c.execute('CREATE INDEX IF NOT EXISTS idx_sessions_token ON sessions(session_token)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_sessions_expires ON sessions(expires_at)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_revisions_entity ON revisions(entity_type, entity_id)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_revisions_user ON revisions(user_id)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_revisions_timestamp ON revisions(timestamp DESC)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_locks_expires ON page_locks(expires_at)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_watchlist_user ON watchlist(user_id)')
    
    conn.commit()
    conn.close()
    
    # Create default admin user if none exists
    create_default_admin()

def create_default_admin():
    """Create default admin user if no admins exist."""
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM users WHERE role = ?', ('admin',))
    if c.fetchone()[0] == 0:
        # Create default admin - password is 'admin' (should be changed!)
        password_hash = hash_password('admin')
        c.execute('''
            INSERT INTO users (username, email, password_hash, role, email_verified)
            VALUES (?, ?, ?, ?, ?)
        ''', ('admin', 'admin@localhost', password_hash, 'admin', 1))
        conn.commit()
        print("Created default admin user: admin / admin (CHANGE THIS PASSWORD!)")
    conn.close()

# =============================================================================
# Password hashing
# =============================================================================

def hash_password(password: str) -> str:
    """Hash password with salt using SHA-256."""
    salt = secrets.token_hex(16)
    hash_obj = hashlib.sha256((salt + password).encode())
    return salt + ':' + hash_obj.hexdigest()

def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against hash."""
    try:
        salt, stored_hash = password_hash.split(':')
        hash_obj = hashlib.sha256((salt + password).encode())
        return hash_obj.hexdigest() == stored_hash
    except:
        return False

# =============================================================================
# User management
# =============================================================================

def create_user(username: str, email: str, password: str) -> dict:
    """Create a new user. Returns user dict or error."""
    conn = get_db()
    c = conn.cursor()
    
    # Check if username or email exists
    c.execute('SELECT id FROM users WHERE username = ?', (username,))
    if c.fetchone():
        conn.close()
        return {'error': 'Username already exists'}
    
    c.execute('SELECT id FROM users WHERE email = ?', (email,))
    if c.fetchone():
        conn.close()
        return {'error': 'Email already registered'}
    
    password_hash = hash_password(password)
    verification_token = secrets.token_urlsafe(32)
    
    c.execute('''
        INSERT INTO users (username, email, password_hash, role, verification_token)
        VALUES (?, ?, ?, ?, ?)
    ''', (username, email, password_hash, 'pending', verification_token))
    
    user_id = c.lastrowid
    conn.commit()
    conn.close()
    
    return {
        'id': user_id,
        'username': username,
        'email': email,
        'role': 'pending',
        'verification_token': verification_token
    }

def verify_email(token: str) -> bool:
    """Verify user email with token."""
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT id FROM users WHERE verification_token = ?', (token,))
    row = c.fetchone()
    if row:
        c.execute('''
            UPDATE users 
            SET email_verified = 1, verification_token = NULL, role = 'editor'
            WHERE id = ?
        ''', (row['id'],))
        conn.commit()
        conn.close()
        return True
    conn.close()
    return False

def login(username: str, password: str, ip_address: str = None, user_agent: str = None) -> dict:
    """Authenticate user and create session."""
    conn = get_db()
    c = conn.cursor()
    
    c.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = c.fetchone()
    
    if not user or not verify_password(password, user['password_hash']):
        conn.close()
        return {'error': 'Invalid username or password'}
    
    if not user['email_verified'] and user['role'] != 'admin':
        conn.close()
        return {'error': 'Please verify your email address'}
    
    # Create session token
    session_token = secrets.token_urlsafe(32)
    expires_at = datetime.now() + timedelta(days=30)
    
    c.execute('''
        INSERT INTO sessions (user_id, session_token, expires_at, ip_address, user_agent)
        VALUES (?, ?, ?, ?, ?)
    ''', (user['id'], session_token, expires_at.isoformat(), ip_address, user_agent))
    
    # Update last login
    c.execute('UPDATE users SET last_login = ? WHERE id = ?', 
              (datetime.now().isoformat(), user['id']))
    
    conn.commit()
    conn.close()
    
    return {
        'session_token': session_token,
        'user': {
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'role': user['role'],
            'edit_count': user['edit_count']
        }
    }

def logout(session_token: str) -> bool:
    """Invalidate session."""
    conn = get_db()
    c = conn.cursor()
    c.execute('DELETE FROM sessions WHERE session_token = ?', (session_token,))
    conn.commit()
    affected = c.rowcount
    conn.close()
    return affected > 0

def get_user_from_session(session_token: str) -> dict:
    """Get user from session token. Returns None if invalid/expired."""
    if not session_token:
        return None
    
    conn = get_db()
    c = conn.cursor()
    
    c.execute('''
        SELECT u.* FROM users u
        JOIN sessions s ON u.id = s.user_id
        WHERE s.session_token = ? AND s.expires_at > ?
    ''', (session_token, datetime.now().isoformat()))
    
    user = c.fetchone()
    conn.close()
    
    if user:
        return {
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'role': user['role'],
            'edit_count': user['edit_count']
        }
    return None

def get_user_by_id(user_id: int) -> dict:
    """Get user by ID."""
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = c.fetchone()
    conn.close()
    if user:
        return dict(user)
    return None

def list_users(role: str = None) -> list:
    """List all users, optionally filtered by role."""
    conn = get_db()
    c = conn.cursor()
    if role:
        c.execute('SELECT id, username, email, role, created_at, edit_count, last_login FROM users WHERE role = ? ORDER BY created_at DESC', (role,))
    else:
        c.execute('SELECT id, username, email, role, created_at, edit_count, last_login FROM users ORDER BY created_at DESC')
    users = [dict(row) for row in c.fetchall()]
    conn.close()
    return users

def update_user_role(user_id: int, new_role: str) -> bool:
    """Update user role."""
    valid_roles = ['pending', 'viewer', 'editor', 'admin']
    if new_role not in valid_roles:
        return False
    
    conn = get_db()
    c = conn.cursor()
    c.execute('UPDATE users SET role = ? WHERE id = ?', (new_role, user_id))
    conn.commit()
    affected = c.rowcount
    conn.close()
    return affected > 0

def change_password(user_id: int, new_password: str) -> bool:
    """Change user password."""
    conn = get_db()
    c = conn.cursor()
    password_hash = hash_password(new_password)
    c.execute('UPDATE users SET password_hash = ? WHERE id = ?', (password_hash, user_id))
    conn.commit()
    affected = c.rowcount
    conn.close()
    return affected > 0

# =============================================================================
# Revision history
# =============================================================================

def create_revision(entity_type: str, entity_id: str, user_id: int, username: str,
                    action: str, data_before: dict, data_after: dict, 
                    summary: str = None, ip_address: str = None, is_minor: bool = False,
                    needs_approval: bool = False) -> int:
    """Create a revision record. Returns revision ID."""
    conn = get_db()
    c = conn.cursor()
    
    is_approved = 0 if needs_approval else 1
    
    c.execute('''
        INSERT INTO revisions 
        (entity_type, entity_id, user_id, username, action, data_before, data_after, 
         summary, ip_address, is_minor, is_approved)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (entity_type, entity_id, user_id, username, action,
          json.dumps(data_before) if data_before else None,
          json.dumps(data_after) if data_after else None,
          summary, ip_address, 1 if is_minor else 0, is_approved))
    
    revision_id = c.lastrowid
    
    # Update user edit count
    if user_id:
        c.execute('UPDATE users SET edit_count = edit_count + 1 WHERE id = ?', (user_id,))
    
    # Add to moderation queue if needs approval
    if needs_approval:
        c.execute('''
            INSERT INTO moderation_queue (revision_id, status)
            VALUES (?, 'pending')
        ''', (revision_id,))
    
    conn.commit()
    conn.close()
    
    return revision_id

def get_revisions(entity_type: str = None, entity_id: str = None, 
                  limit: int = 50, offset: int = 0) -> list:
    """Get revision history. Filter by entity if specified."""
    conn = get_db()
    c = conn.cursor()
    
    query = 'SELECT * FROM revisions WHERE is_approved = 1'
    params = []
    
    if entity_type:
        query += ' AND entity_type = ?'
        params.append(entity_type)
    if entity_id:
        query += ' AND entity_id = ?'
        params.append(entity_id)
    
    query += ' ORDER BY timestamp DESC LIMIT ? OFFSET ?'
    params.extend([limit, offset])
    
    c.execute(query, params)
    revisions = [dict(row) for row in c.fetchall()]
    conn.close()
    
    # Parse JSON fields
    for rev in revisions:
        if rev['data_before']:
            rev['data_before'] = json.loads(rev['data_before'])
        if rev['data_after']:
            rev['data_after'] = json.loads(rev['data_after'])
    
    return revisions

def get_revision(revision_id: int) -> dict:
    """Get specific revision."""
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM revisions WHERE id = ?', (revision_id,))
    rev = c.fetchone()
    conn.close()
    
    if rev:
        rev = dict(rev)
        if rev['data_before']:
            rev['data_before'] = json.loads(rev['data_before'])
        if rev['data_after']:
            rev['data_after'] = json.loads(rev['data_after'])
        return rev
    return None

def get_recent_changes(limit: int = 50, include_minor: bool = True) -> list:
    """Get recent changes across all entities."""
    conn = get_db()
    c = conn.cursor()
    
    query = 'SELECT * FROM revisions WHERE is_approved = 1'
    if not include_minor:
        query += ' AND is_minor = 0'
    query += ' ORDER BY timestamp DESC LIMIT ?'
    
    c.execute(query, (limit,))
    revisions = [dict(row) for row in c.fetchall()]
    conn.close()
    
    return revisions

# =============================================================================
# Page locking
# =============================================================================

def acquire_lock(entity_type: str, entity_id: str, user_id: int, 
                 duration_minutes: int = 15) -> dict:
    """Acquire edit lock. Returns lock info or error."""
    conn = get_db()
    c = conn.cursor()
    
    # Clean up expired locks
    c.execute('DELETE FROM page_locks WHERE expires_at < ?', (datetime.now().isoformat(),))
    
    # Check for existing lock
    c.execute('''
        SELECT pl.*, u.username FROM page_locks pl
        JOIN users u ON pl.user_id = u.id
        WHERE pl.entity_type = ? AND pl.entity_id = ?
    ''', (entity_type, entity_id))
    
    existing = c.fetchone()
    if existing:
        if existing['user_id'] == user_id:
            # Extend own lock
            new_expires = datetime.now() + timedelta(minutes=duration_minutes)
            c.execute('''
                UPDATE page_locks SET expires_at = ?
                WHERE entity_type = ? AND entity_id = ?
            ''', (new_expires.isoformat(), entity_type, entity_id))
            conn.commit()
            conn.close()
            return {'locked': True, 'expires_at': new_expires.isoformat()}
        else:
            conn.close()
            return {
                'error': f'Page is locked by {existing["username"]}',
                'locked_by': existing['username'],
                'expires_at': existing['expires_at']
            }
    
    # Create new lock
    expires_at = datetime.now() + timedelta(minutes=duration_minutes)
    c.execute('''
        INSERT INTO page_locks (entity_type, entity_id, user_id, expires_at)
        VALUES (?, ?, ?, ?)
    ''', (entity_type, entity_id, user_id, expires_at.isoformat()))
    
    conn.commit()
    conn.close()
    
    return {'locked': True, 'expires_at': expires_at.isoformat()}

def release_lock(entity_type: str, entity_id: str, user_id: int) -> bool:
    """Release edit lock."""
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        DELETE FROM page_locks 
        WHERE entity_type = ? AND entity_id = ? AND user_id = ?
    ''', (entity_type, entity_id, user_id))
    conn.commit()
    affected = c.rowcount
    conn.close()
    return affected > 0

def force_release_lock(entity_type: str, entity_id: str) -> bool:
    """Force release lock (admin only)."""
    conn = get_db()
    c = conn.cursor()
    c.execute('DELETE FROM page_locks WHERE entity_type = ? AND entity_id = ?', 
              (entity_type, entity_id))
    conn.commit()
    affected = c.rowcount
    conn.close()
    return affected > 0

def check_lock(entity_type: str, entity_id: str) -> dict:
    """Check if entity is locked."""
    conn = get_db()
    c = conn.cursor()
    
    # Clean up expired
    c.execute('DELETE FROM page_locks WHERE expires_at < ?', (datetime.now().isoformat(),))
    conn.commit()
    
    c.execute('''
        SELECT pl.*, u.username FROM page_locks pl
        JOIN users u ON pl.user_id = u.id
        WHERE pl.entity_type = ? AND pl.entity_id = ?
    ''', (entity_type, entity_id))
    
    lock = c.fetchone()
    conn.close()
    
    if lock:
        return {
            'locked': True,
            'locked_by': lock['username'],
            'user_id': lock['user_id'],
            'expires_at': lock['expires_at']
        }
    return {'locked': False}

# =============================================================================
# Watchlist
# =============================================================================

def add_to_watchlist(user_id: int, entity_type: str, entity_id: str) -> bool:
    """Add entity to user's watchlist."""
    conn = get_db()
    c = conn.cursor()
    try:
        c.execute('''
            INSERT INTO watchlist (user_id, entity_type, entity_id)
            VALUES (?, ?, ?)
        ''', (user_id, entity_type, entity_id))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False  # Already watching

def remove_from_watchlist(user_id: int, entity_type: str, entity_id: str) -> bool:
    """Remove entity from watchlist."""
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        DELETE FROM watchlist 
        WHERE user_id = ? AND entity_type = ? AND entity_id = ?
    ''', (user_id, entity_type, entity_id))
    conn.commit()
    affected = c.rowcount
    conn.close()
    return affected > 0

def get_watchlist(user_id: int) -> list:
    """Get user's watchlist."""
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        SELECT entity_type, entity_id, added_at FROM watchlist
        WHERE user_id = ? ORDER BY added_at DESC
    ''', (user_id,))
    items = [dict(row) for row in c.fetchall()]
    conn.close()
    return items

def get_watchlist_changes(user_id: int, since: str = None, limit: int = 50) -> list:
    """Get recent changes to watched entities."""
    conn = get_db()
    c = conn.cursor()
    
    query = '''
        SELECT r.* FROM revisions r
        JOIN watchlist w ON r.entity_type = w.entity_type AND r.entity_id = w.entity_id
        WHERE w.user_id = ? AND r.is_approved = 1
    '''
    params = [user_id]
    
    if since:
        query += ' AND r.timestamp > ?'
        params.append(since)
    
    query += ' ORDER BY r.timestamp DESC LIMIT ?'
    params.append(limit)
    
    c.execute(query, params)
    changes = [dict(row) for row in c.fetchall()]
    conn.close()
    return changes

# =============================================================================
# Moderation
# =============================================================================

def get_pending_moderations(limit: int = 50) -> list:
    """Get pending moderation items."""
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        SELECT mq.*, r.entity_type, r.entity_id, r.user_id, r.username, 
               r.action, r.summary, r.timestamp, r.data_after
        FROM moderation_queue mq
        JOIN revisions r ON mq.revision_id = r.id
        WHERE mq.status = 'pending'
        ORDER BY r.timestamp ASC
        LIMIT ?
    ''', (limit,))
    items = [dict(row) for row in c.fetchall()]
    conn.close()
    
    for item in items:
        if item['data_after']:
            item['data_after'] = json.loads(item['data_after'])
    
    return items

def approve_moderation(moderation_id: int, reviewer_id: int) -> bool:
    """Approve a moderation item."""
    conn = get_db()
    c = conn.cursor()
    
    # Get revision ID
    c.execute('SELECT revision_id FROM moderation_queue WHERE id = ?', (moderation_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        return False
    
    revision_id = row['revision_id']
    
    # Update moderation queue
    c.execute('''
        UPDATE moderation_queue 
        SET status = 'approved', reviewed_by = ?, reviewed_at = ?
        WHERE id = ?
    ''', (reviewer_id, datetime.now().isoformat(), moderation_id))
    
    # Approve the revision
    c.execute('UPDATE revisions SET is_approved = 1, approved_by = ? WHERE id = ?',
              (reviewer_id, revision_id))
    
    conn.commit()
    conn.close()
    return True

def reject_moderation(moderation_id: int, reviewer_id: int, reason: str = None) -> bool:
    """Reject a moderation item."""
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        UPDATE moderation_queue 
        SET status = 'rejected', reviewed_by = ?, reviewed_at = ?, rejection_reason = ?
        WHERE id = ?
    ''', (reviewer_id, datetime.now().isoformat(), reason, moderation_id))
    conn.commit()
    affected = c.rowcount
    conn.close()
    return affected > 0

# =============================================================================
# Utility
# =============================================================================

def cleanup_expired():
    """Clean up expired sessions and locks."""
    conn = get_db()
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute('DELETE FROM sessions WHERE expires_at < ?', (now,))
    c.execute('DELETE FROM page_locks WHERE expires_at < ?', (now,))
    conn.commit()
    conn.close()

# Initialize database on import
init_db()
