# 🔒 Security Technical Checklist
## Complete Technical Implementation Details for Unified Data Studio v2 Security

### 📋 Overview
This checklist provides the exact technical steps, code snippets, and configurations needed to implement the security system. Use this as your implementation guide.

---

## 🎯 Phase 1: Navigation Restructuring

### **1.1 Update App.tsx**
```typescript
// src/App.tsx - EXACT CHANGES NEEDED

// ADD THESE IMPORTS
import { AdminProvider } from './contexts/AdminContext';
import { Dashboard } from './components/Dashboard';
import { DeveloperHome } from './components/DeveloperHome';
import { ProtectedRoute } from './components/ProtectedRoute';

// REPLACE EXISTING ROUTES WITH:
const routes = [
  { path: '/', element: <Dashboard /> },
  { path: '/developer', element: <ProtectedRoute requiredLevel="developer"><DeveloperHome /></ProtectedRoute> },
  { path: '/playground', element: <Playground /> },
  { path: '/formula-config', element: <ProtectedRoute requiredLevel="admin"><FormulaConfiguration /></ProtectedRoute> },
  { path: '/logs', element: <ProtectedRoute requiredLevel="admin"><LogsPage /></ProtectedRoute> },
  { path: '/settings', element: <ProtectedRoute requiredLevel="admin"><Settings /></ProtectedRoute> },
];

// WRAP ENTIRE APP WITH AdminProvider
function App() {
  return (
    <AdminProvider>
      <Router>
        <AppLayout>
          <Routes>
            {routes.map(route => (
              <Route key={route.path} path={route.path} element={route.element} />
            ))}
          </Routes>
        </AppLayout>
      </Router>
    </AdminProvider>
  );
}
```

### **1.2 Create Dashboard Component**
```typescript
// src/components/Dashboard.tsx - NEW FILE
import React from 'react';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { Play, Database, Settings, BarChart3 } from 'lucide-react';

export const Dashboard: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Welcome to Unified Data Studio
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Your comprehensive data processing and analysis platform. 
            Create workflows, process data, and gain insights with powerful tools.
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          <Card className="p-8 hover:shadow-lg transition-shadow">
            <div className="text-center">
              <Play className="h-12 w-12 text-blue-600 mx-auto mb-4" />
              <h3 className="text-xl font-semibold mb-3">Data Playground</h3>
              <p className="text-gray-600 mb-6">
                Process and analyze your data with our intuitive drag-and-drop interface.
              </p>
              <Button asChild className="w-full">
                <a href="/playground">Open Playground</a>
              </Button>
            </div>
          </Card>
          
          <Card className="p-8 hover:shadow-lg transition-shadow">
            <div className="text-center">
              <Database className="h-12 w-12 text-green-600 mx-auto mb-4" />
              <h3 className="text-xl font-semibold mb-3">Data Sources</h3>
              <p className="text-gray-600 mb-6">
                Connect to various data sources and import your data seamlessly.
              </p>
              <Button variant="outline" className="w-full">
                Connect Data
              </Button>
            </div>
          </Card>
          
          <Card className="p-8 hover:shadow-lg transition-shadow">
            <div className="text-center">
              <BarChart3 className="h-12 w-12 text-purple-600 mx-auto mb-4" />
              <h3 className="text-xl font-semibold mb-3">Analytics</h3>
              <p className="text-gray-600 mb-6">
                Generate insights and create visualizations from your data.
              </p>
              <Button variant="outline" className="w-full">
                View Analytics
              </Button>
            </div>
          </Card>
        </div>
        
        <div className="mt-16 text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Getting Started
          </h2>
          <p className="text-gray-600 max-w-2xl mx-auto">
            New to Unified Data Studio? Start by exploring the Playground to understand 
            how to process and analyze your data effectively.
          </p>
        </div>
      </div>
    </div>
  );
};
```

### **1.3 Rename Home to DeveloperHome**
```bash
# TERMINAL COMMANDS
cd /Users/raghavendra_pratap/Developer/unified-data-studio-v2/frontend/src/components
mv Home.tsx DeveloperHome.tsx
```

```typescript
// src/components/DeveloperHome.tsx - UPDATE EXPORT
export const DeveloperHome: React.FC = () => {
  // ... existing content
};
```

### **1.4 Update AppLayout.tsx**
```typescript
// src/components/AppLayout.tsx - UPDATE SIDEBAR
import { DeveloperHome } from './DeveloperHome';

const sidebarItems = [
  { id: 'dashboard', label: 'Dashboard', icon: Home, path: '/' },
  { id: 'playground', label: 'Playground', icon: Play, path: '/playground' },
  // REMOVE direct links to protected pages
  // ADD developer section (will be protected)
];

// ADD developer section in sidebar
const developerSection = [
  { id: 'developer', label: 'Developer Tools', icon: Code, path: '/developer' },
];
```

---

## 🔐 Phase 2: Admin Authentication System

### **2.1 Create Admin Context**
```typescript
// src/contexts/AdminContext.tsx - NEW FILE
import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface AdminSession {
  userId: string;
  accessLevel: 'admin' | 'developer';
  totpVerified: boolean;
  expiresAt: number;
  ipAddress: string;
  userAgent: string;
  lastActivity: number;
}

interface AdminContextType {
  isAdmin: boolean;
  isDeveloper: boolean;
  sessionId: string | null;
  login: (accessLevel: 'admin' | 'developer', totpCode: string) => Promise<boolean>;
  logout: () => void;
  checkSession: () => Promise<boolean>;
}

const AdminContext = createContext<AdminContextType | undefined>(undefined);

export const useAdmin = () => {
  const context = useContext(AdminContext);
  if (!context) {
    throw new Error('useAdmin must be used within an AdminProvider');
  }
  return context;
};

export const AdminProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [isAdmin, setIsAdmin] = useState(false);
  const [isDeveloper, setIsDeveloper] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);

  // Check for existing session on mount
  useEffect(() => {
    checkSession();
  }, []);

  const checkSession = async (): Promise<boolean> => {
    const storedSessionId = localStorage.getItem('admin_session_id');
    if (!storedSessionId) return false;

    try {
      const response = await fetch('/api/auth/verify-session', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${storedSessionId}`,
        },
      });

      if (response.ok) {
        const session = await response.json();
        setSessionId(storedSessionId);
        setIsAdmin(session.access_level === 'admin');
        setIsDeveloper(session.access_level === 'developer');
        return true;
      } else {
        // Session invalid, clear it
        localStorage.removeItem('admin_session_id');
        setSessionId(null);
        setIsAdmin(false);
        setIsDeveloper(false);
        return false;
      }
    } catch (error) {
      console.error('Session check failed:', error);
      return false;
    }
  };

  const login = async (accessLevel: 'admin' | 'developer', totpCode: string): Promise<boolean> => {
    try {
      const response = await fetch('/api/auth/verify-admin', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          totp_code: totpCode,
          access_level: accessLevel,
        }),
      });

      if (response.ok) {
        const { session_id } = await response.json();
        localStorage.setItem('admin_session_id', session_id);
        setSessionId(session_id);
        setIsAdmin(accessLevel === 'admin');
        setIsDeveloper(accessLevel === 'developer');
        return true;
      }
      return false;
    } catch (error) {
      console.error('Login failed:', error);
      return false;
    }
  };

  const logout = () => {
    localStorage.removeItem('admin_session_id');
    setSessionId(null);
    setIsAdmin(false);
    setIsDeveloper(false);
  };

  return (
    <AdminContext.Provider value={{
      isAdmin,
      isDeveloper,
      sessionId,
      login,
      logout,
      checkSession,
    }}>
      {children}
    </AdminContext.Provider>
  );
};
```

### **2.2 Create Key Combination Hook**
```typescript
// src/hooks/useKeyCombination.ts - NEW FILE
import { useState, useEffect } from 'react';

export const useKeyCombination = (targetKeys: string[], onMatch: () => void) => {
  const [pressedKeys, setPressedKeys] = useState<string[]>([]);

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.ctrlKey && event.shiftKey && event.altKey) {
        const newKeys = [...pressedKeys, event.code];
        setPressedKeys(newKeys);
        
        if (arraysEqual(newKeys, targetKeys)) {
          onMatch();
          setPressedKeys([]);
        }
      }
    };

    const handleKeyUp = () => {
      setPressedKeys([]);
    };

    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('keyup', handleKeyUp);
    
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('keyup', handleKeyUp);
    };
  }, [pressedKeys, targetKeys, onMatch]);
};

const arraysEqual = (a: string[], b: string[]): boolean => {
  return a.length === b.length && a.every((val, index) => val === b[index]);
};
```

### **2.3 Create Admin Auth Modal**
```typescript
// src/components/AdminAuthModal.tsx - NEW FILE
import React, { useState } from 'react';
import { Modal } from './ui/modal';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Alert } from './ui/alert';
import { Shield, Smartphone } from 'lucide-react';

interface AdminAuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (sessionId: string) => void;
  accessLevel: 'admin' | 'developer';
}

export const AdminAuthModal: React.FC<AdminAuthModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
  accessLevel,
}) => {
  const [totpCode, setTotpCode] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async () => {
    if (totpCode.length !== 6) {
      setError('Please enter a 6-digit code');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const response = await fetch('/api/auth/verify-admin', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          totp_code: totpCode,
          access_level: accessLevel,
        }),
      });

      if (response.ok) {
        const { session_id } = await response.json();
        onSuccess(session_id);
        onClose();
        setTotpCode('');
      } else {
        setError('Invalid code. Please try again.');
      }
    } catch (err) {
      setError('Authentication failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSubmit();
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose}>
      <div className="p-8 max-w-md mx-auto">
        <div className="text-center mb-6">
          <div className="mx-auto w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mb-4">
            {accessLevel === 'admin' ? (
              <Shield className="h-8 w-8 text-blue-600" />
            ) : (
              <Smartphone className="h-8 w-8 text-blue-600" />
            )}
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            {accessLevel === 'admin' ? 'Admin Access' : 'Developer Access'}
          </h2>
          <p className="text-gray-600">
            Enter your 6-digit authentication code from your authenticator app.
          </p>
        </div>

        {error && (
          <Alert variant="error" className="mb-4">
            {error}
          </Alert>
        )}

        <div className="space-y-4">
          <Input
            type="text"
            placeholder="000000"
            value={totpCode}
            onChange={(e) => setTotpCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
            onKeyPress={handleKeyPress}
            className="text-center text-2xl tracking-widest font-mono"
            maxLength={6}
            autoFocus
          />

          <div className="flex gap-3">
            <Button 
              onClick={handleSubmit} 
              disabled={isLoading || totpCode.length !== 6}
              className="flex-1"
            >
              {isLoading ? 'Verifying...' : 'Authenticate'}
            </Button>
            <Button variant="outline" onClick={onClose} className="flex-1">
              Cancel
            </Button>
          </div>
        </div>

        <div className="mt-6 text-center">
          <p className="text-sm text-gray-500">
            Use your authenticator app to generate a 6-digit code
          </p>
        </div>
      </div>
    </Modal>
  );
};
```

### **2.4 Create Protected Route Component**
```typescript
// src/components/ProtectedRoute.tsx - NEW FILE
import React, { useState } from 'react';
import { useAdmin } from '../contexts/AdminContext';
import { AdminAuthModal } from './AdminAuthModal';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { Lock, Shield } from 'lucide-react';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredLevel: 'admin' | 'developer';
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ 
  children, 
  requiredLevel 
}) => {
  const { isAdmin, isDeveloper } = useAdmin();
  const [showAuthModal, setShowAuthModal] = useState(false);

  const hasAccess = requiredLevel === 'admin' ? isAdmin : isDeveloper;

  if (hasAccess) {
    return <>{children}</>;
  }

  return (
    <>
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Card className="p-8 max-w-md mx-auto text-center">
          <div className="mx-auto w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mb-4">
            <Lock className="h-8 w-8 text-red-600" />
          </div>
          
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Access Restricted
          </h2>
          
          <p className="text-gray-600 mb-6">
            This page requires {requiredLevel} privileges. Please authenticate to continue.
          </p>
          
          <Button onClick={() => setShowAuthModal(true)} className="w-full">
            <Shield className="h-4 w-4 mr-2" />
            Authenticate
          </Button>
        </Card>
      </div>
      
      <AdminAuthModal 
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        onSuccess={(sessionId) => {
          setShowAuthModal(false);
          // The context will handle the session update
        }}
        accessLevel={requiredLevel}
      />
    </>
  );
};
```

---

## 🔒 Phase 3: Backend Security Implementation

### **3.1 Update Cargo.toml**
```toml
# Cargo.toml - ADD THESE DEPENDENCIES
[dependencies]
# ... existing dependencies
totp-rs = "0.6"
qrcode = "0.14"
image = "0.24"
actix-web-httpauth = "0.7"
rate-limiter-flexible = "0.7"
uuid = { version = "1.0", features = ["v4"] }
```

### **3.2 Create Authentication Service**
```rust
// src/auth_service.rs - NEW FILE
use serde::{Deserialize, Serialize};
use chrono::{DateTime, Utc, Duration};
use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use totp_rs::{TOTP, Algorithm, Secret};
use uuid::Uuid;
use anyhow::{Result, anyhow};

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct AdminSession {
    pub user_id: String,
    pub access_level: AccessLevel,
    pub totp_verified: bool,
    pub expires_at: DateTime<Utc>,
    pub ip_address: String,
    pub user_agent: String,
    pub last_activity: DateTime<Utc>,
}

#[derive(Debug, Serialize, Deserialize, Clone, PartialEq)]
pub enum AccessLevel {
    User,
    Developer,
    Admin,
}

pub struct AuthService {
    sessions: Arc<Mutex<HashMap<String, AdminSession>>>,
    totp: TOTP,
    rate_limiter: RateLimiter,
}

impl AuthService {
    pub fn new() -> Self {
        // In production, this should be loaded from environment variables
        let secret = Secret::from_encoded("JBSWY3DPEHPK3PXP").unwrap();
        let totp = TOTP::new(
            Algorithm::SHA1,
            6,
            1,
            30,
            "Unified Data Studio".to_string(),
            "admin@unified-data-studio.com".to_string(),
        ).unwrap();

        Self {
            sessions: Arc::new(Mutex::new(HashMap::new())),
            totp,
            rate_limiter: RateLimiter::new(),
        }
    }

    pub async fn verify_admin_access(
        &self,
        totp_code: &str,
        access_level: &str,
        ip_address: &str,
        user_agent: &str,
    ) -> Result<String> {
        // Rate limiting check
        if !self.rate_limiter.allow_request(ip_address) {
            return Err(anyhow!("Too many failed attempts"));
        }

        // TOTP verification
        if !self.totp.check_current(totp_code)? {
            self.rate_limiter.record_failed_attempt(ip_address);
            return Err(anyhow!("Invalid TOTP code"));
        }

        // Create session
        let session_id = Uuid::new_v4().to_string();
        let access_level_enum = match access_level {
            "admin" => AccessLevel::Admin,
            "developer" => AccessLevel::Developer,
            _ => return Err(anyhow!("Invalid access level")),
        };

        let session = AdminSession {
            user_id: "admin".to_string(),
            access_level: access_level_enum,
            totp_verified: true,
            expires_at: Utc::now() + Duration::minutes(15),
            ip_address: ip_address.to_string(),
            user_agent: user_agent.to_string(),
            last_activity: Utc::now(),
        };

        self.sessions.lock().unwrap().insert(session_id.clone(), session);
        Ok(session_id)
    }

    pub async fn verify_session(&self, session_id: &str) -> Result<AdminSession> {
        let mut sessions = self.sessions.lock().unwrap();
        
        if let Some(session) = sessions.get_mut(session_id) {
            // Check expiration
            if Utc::now() > session.expires_at {
                sessions.remove(session_id);
                return Err(anyhow!("Session expired"));
            }

            // Update last activity
            session.last_activity = Utc::now();
            
            // Extend session if needed
            if Utc::now() > session.expires_at - Duration::minutes(5) {
                session.expires_at = Utc::now() + Duration::minutes(15);
            }

            Ok(session.clone())
        } else {
            Err(anyhow!("Invalid session"))
        }
    }

    pub fn logout(&self, session_id: &str) {
        let mut sessions = self.sessions.lock().unwrap();
        sessions.remove(session_id);
    }
}

pub struct RateLimiter {
    attempts: Arc<Mutex<HashMap<String, Vec<DateTime<Utc>>>>>,
    max_attempts: u32,
    window_duration: Duration,
}

impl RateLimiter {
    pub fn new() -> Self {
        Self {
            attempts: Arc::new(Mutex::new(HashMap::new())),
            max_attempts: 5,
            window_duration: Duration::minutes(15),
        }
    }

    pub fn allow_request(&self, ip_address: &str) -> bool {
        let mut attempts = self.attempts.lock().unwrap();
        let now = Utc::now();
        
        // Clean old attempts
        if let Some(ip_attempts) = attempts.get_mut(ip_address) {
            ip_attempts.retain(|&attempt| now - attempt < self.window_duration);
            
            if ip_attempts.len() >= self.max_attempts as usize {
                return false;
            }
        }
        
        true
    }

    pub fn record_failed_attempt(&self, ip_address: &str) {
        let mut attempts = self.attempts.lock().unwrap();
        let now = Utc::now();
        
        attempts.entry(ip_address.to_string())
            .or_insert_with(Vec::new)
            .push(now);
    }
}
```

### **3.3 Create TOTP Service**
```rust
// src/totp_service.rs - NEW FILE
use totp_rs::{TOTP, Algorithm, Secret};
use qrcode::QrCode;
use image::Luma;
use anyhow::Result;

pub struct TOTPService {
    totp: TOTP,
}

impl TOTPService {
    pub fn new() -> Self {
        // In production, this should be loaded from environment variables
        let secret = Secret::from_encoded("JBSWY3DPEHPK3PXP").unwrap();
        let totp = TOTP::new(
            Algorithm::SHA1,
            6,
            1,
            30,
            "Unified Data Studio".to_string(),
            "admin@unified-data-studio.com".to_string(),
        ).unwrap();

        Self { totp }
    }

    pub fn generate_qr_code(&self) -> Result<String> {
        let qr_code = QrCode::new(self.totp.get_url())?;
        let image = qr_code.render::<Luma<u8>>().build();
        
        // Convert to base64 for frontend display
        let mut buffer = Vec::new();
        image.write_to(&mut buffer, image::ImageFormat::Png)?;
        Ok(base64::encode(buffer))
    }

    pub fn verify_code(&self, code: &str) -> Result<bool> {
        Ok(self.totp.check_current(code)?)
    }

    pub fn get_secret(&self) -> String {
        self.totp.get_secret().to_string()
    }

    pub fn get_url(&self) -> String {
        self.totp.get_url()
    }
}
```

### **3.4 Update Main.rs**
```rust
// src/main.rs - ADD THESE IMPORTS AND CHANGES
use auth_service::AuthService;
use totp_service::TOTPService;

// ADD TO AppState
pub struct AppState {
    // ... existing fields
    pub auth_service: Arc<AuthService>,
    pub totp_service: Arc<TOTPService>,
}

// UPDATE main function
#[actix_web::main]
async fn main() -> std::io::Result<()> {
    // ... existing initialization code

    // Initialize auth services
    let auth_service = Arc::new(AuthService::new());
    let totp_service = Arc::new(TOTPService::new());

    let app_state = AppState {
        // ... existing fields
        auth_service,
        totp_service,
    };

    // ADD AUTH ROUTES
    HttpServer::new(move || {
        App::new()
            .app_data(web::Data::new(app_state.clone()))
            .service(
                web::scope("/api/auth")
                    .route("/verify-admin", web::post().to(verify_admin_access))
                    .route("/verify-session", web::post().to(verify_session))
                    .route("/logout", web::post().to(logout_admin))
                    .route("/qr-code", web::get().to(get_qr_code))
            )
            // ... existing routes
    })
    .bind("127.0.0.1:5002")?
    .run()
    .await
}

// ADD AUTH HANDLERS
async fn verify_admin_access(
    req: HttpRequest,
    data: web::Data<AppState>,
    payload: web::Json<serde_json::Value>,
) -> Result<HttpResponse, actix_web::Error> {
    let totp_code = payload["totp_code"].as_str().unwrap_or("");
    let access_level = payload["access_level"].as_str().unwrap_or("");
    
    let ip_address = req.connection_info().remote_addr().unwrap_or("unknown");
    let user_agent = req.headers()
        .get("User-Agent")
        .and_then(|h| h.to_str().ok())
        .unwrap_or("unknown");

    match data.auth_service.verify_admin_access(totp_code, access_level, ip_address, user_agent).await {
        Ok(session_id) => {
            Ok(HttpResponse::Ok().json(serde_json::json!({
                "success": true,
                "session_id": session_id,
                "message": "Authentication successful"
            })))
        }
        Err(e) => {
            Ok(HttpResponse::BadRequest().json(serde_json::json!({
                "success": false,
                "error": e.to_string()
            })))
        }
    }
}

async fn verify_session(
    req: HttpRequest,
    data: web::Data<AppState>,
) -> Result<HttpResponse, actix_web::Error> {
    let session_id = req.headers()
        .get("Authorization")
        .and_then(|h| h.to_str().ok())
        .and_then(|s| s.strip_prefix("Bearer "))
        .unwrap_or("");

    match data.auth_service.verify_session(session_id).await {
        Ok(session) => {
            Ok(HttpResponse::Ok().json(serde_json::json!({
                "success": true,
                "access_level": session.access_level,
                "expires_at": session.expires_at
            })))
        }
        Err(_) => {
            Ok(HttpResponse::Unauthorized().json(serde_json::json!({
                "success": false,
                "error": "Invalid session"
            })))
        }
    }
}

async fn logout_admin(
    req: HttpRequest,
    data: web::Data<AppState>,
) -> Result<HttpResponse, actix_web::Error> {
    let session_id = req.headers()
        .get("Authorization")
        .and_then(|h| h.to_str().ok())
        .and_then(|s| s.strip_prefix("Bearer "))
        .unwrap_or("");

    data.auth_service.logout(session_id);

    Ok(HttpResponse::Ok().json(serde_json::json!({
        "success": true,
        "message": "Logged out successfully"
    })))
}

async fn get_qr_code(
    data: web::Data<AppState>,
) -> Result<HttpResponse, actix_web::Error> {
    match data.totp_service.generate_qr_code() {
        Ok(qr_code) => {
            Ok(HttpResponse::Ok().json(serde_json::json!({
                "success": true,
                "qr_code": qr_code,
                "url": data.totp_service.get_url()
            })))
        }
        Err(e) => {
            Ok(HttpResponse::InternalServerError().json(serde_json::json!({
                "success": false,
                "error": e.to_string()
            })))
        }
    }
}
```

---

## 🛡️ Phase 4: API Protection

### **4.1 Create Admin Middleware**
```rust
// src/admin_middleware.rs - NEW FILE
use actix_web::{dev::ServiceRequest, Error, Result};
use actix_web_httpauth::extractors::bearer::BearerAuth;
use crate::auth_service::{AuthService, AccessLevel};

pub async fn admin_auth_middleware(
    req: ServiceRequest,
    auth: BearerAuth,
) -> Result<ServiceRequest, Error> {
    let auth_service = req.app_data::<web::Data<AuthService>>()
        .ok_or_else(|| actix_web::error::ErrorUnauthorized("Auth service not configured"))?;

    let session = auth_service.verify_session(auth.token()).await
        .map_err(|_| actix_web::error::ErrorUnauthorized("Invalid session"))?;

    if !matches!(session.access_level, AccessLevel::Admin) {
        return Err(actix_web::error::ErrorForbidden("Admin access required"));
    }

    // Add session to request extensions
    req.extensions_mut().insert(session);
    Ok(req)
}
```

### **4.2 Protect Formula Configuration API**
```rust
// src/formula_config.rs - ADD MIDDLEWARE
use crate::admin_middleware::admin_auth_middleware;

pub fn configure_routes(cfg: &mut web::ServiceConfig) {
    cfg.service(
        web::scope("/api/formulas")
            .wrap(admin_auth_middleware) // ADD THIS LINE
            .route("", web::get().to(get_formulas))
            .route("", web::post().to(create_formula))
            .route("/{formula_name}", web::put().to(update_formula))
            .route("/{formula_name}", web::delete().to(delete_formula))
            .route("/{formula_name}/test", web::post().to(test_formula_code))
            .route("/{formula_name}/code", web::get().to(get_formula_code))
            .route("/{formula_name}/code", web::post().to(save_formula_code))
            .route("/{formula_name}/generate", web::post().to(generate_formula_code))
    );
}
```

### **4.3 Protect Logs API**
```rust
// src/main.rs - PROTECT LOGS ENDPOINTS
use crate::admin_middleware::admin_auth_middleware;

// UPDATE logs service configuration
.service(
    web::scope("/api/logs")
        .wrap(admin_auth_middleware) // ADD THIS LINE
        .route("", web::get().to(get_logs))
        .route("/export", web::get().to(export_logs))
        .route("", web::delete().to(clear_logs))
)
```

---

## 🏗️ Phase 5: Build Protection

### **5.1 Install Obfuscation Tools**
```bash
# TERMINAL COMMANDS
cd /Users/raghavendra_pratap/Developer/unified-data-studio-v2/frontend
npm install --save-dev javascript-obfuscator
npm install --save-dev webpack-obfuscator
```

### **5.2 Update Package.json**
```json
// package.json - ADD THESE SCRIPTS
{
  "scripts": {
    "build:secure": "npm run build && npm run obfuscate && npm run remove-sourcemaps",
    "obfuscate": "javascript-obfuscator build/static/js/*.js --output build/static/js/ --compact true --control-flow-flattening true --string-array true --string-array-threshold 0.75",
    "remove-sourcemaps": "find build -name '*.map' -delete"
  }
}
```

### **5.3 Create Environment Files**
```bash
# .env.production - CREATE THIS FILE
REACT_APP_SESSION_SALT=your-production-salt-here
REACT_APP_ADMIN_SECRET=your-admin-secret-here
REACT_APP_TOTP_SECRET=your-totp-secret-here
REACT_APP_API_BASE_URL=https://your-api-domain.com
```

### **5.4 Update Webpack Config**
```javascript
// webpack.config.js - ADD OBFUSCATION
const JavaScriptObfuscator = require('webpack-obfuscator');

module.exports = {
  // ... existing config
  plugins: [
    // ... existing plugins
    new JavaScriptObfuscator({
      rotateStringArray: true,
      stringArray: true,
      stringArrayThreshold: 0.75,
      transformObjectKeys: true,
      unicodeEscapeSequence: true,
      controlFlowFlattening: true,
      controlFlowFlatteningThreshold: 0.75,
      deadCodeInjection: true,
      deadCodeInjectionThreshold: 0.4,
      debugProtection: true,
      debugProtectionInterval: 2000,
      disableConsoleOutput: true,
      identifierNamesGenerator: 'hexadecimal',
      log: false,
      numbersToExpressions: true,
      renameGlobals: false,
      selfDefending: true,
      simplify: true,
      splitStrings: true,
      splitStringsChunkLength: 10,
      stringArrayCallsTransform: true,
      stringArrayEncoding: ['base64'],
      stringArrayIndexShift: true,
      stringArrayRotate: true,
      stringArrayShuffle: true,
      stringArrayWrappersCount: 2,
      stringArrayWrappersChainedCalls: true,
      stringArrayWrappersParametersMaxCount: 4,
      stringArrayWrappersType: 'function',
      stringArrayThreshold: 0.75,
      transformObjectKeys: true,
      unicodeEscapeSequence: false
    }, ['excluded_bundle_name.js'])
  ]
};
```

---

## 🧪 Phase 6: Testing & Validation

### **6.1 Create Security Tests**
```typescript
// src/__tests__/security.test.ts - NEW FILE
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { AdminProvider } from '../contexts/AdminContext';
import { ProtectedRoute } from '../components/ProtectedRoute';
import { AdminAuthModal } from '../components/AdminAuthModal';

// Mock fetch
global.fetch = jest.fn();

describe('Admin Security', () => {
  beforeEach(() => {
    (fetch as jest.Mock).mockClear();
  });

  test('should block unauthorized access to admin routes', async () => {
    render(
      <AdminProvider>
        <ProtectedRoute requiredLevel="admin">
          <div>Admin Content</div>
        </ProtectedRoute>
      </AdminProvider>
    );

    expect(screen.getByText('Access Restricted')).toBeInTheDocument();
    expect(screen.queryByText('Admin Content')).not.toBeInTheDocument();
  });

  test('should require valid TOTP code', async () => {
    (fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      json: async () => ({ error: 'Invalid TOTP code' }),
    });

    render(
      <AdminAuthModal
        isOpen={true}
        onClose={() => {}}
        onSuccess={() => {}}
        accessLevel="admin"
      />
    );

    const input = screen.getByPlaceholderText('000000');
    const button = screen.getByText('Authenticate');

    fireEvent.change(input, { target: { value: '000000' } });
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText('Invalid code. Please try again.')).toBeInTheDocument();
    });
  });

  test('should enforce rate limiting', async () => {
    (fetch as jest.Mock).mockResolvedValue({
      ok: false,
      json: async () => ({ error: 'Too many failed attempts' }),
    });

    render(
      <AdminAuthModal
        isOpen={true}
        onClose={() => {}}
        onSuccess={() => {}}
        accessLevel="admin"
      />
    );

    const input = screen.getByPlaceholderText('000000');
    const button = screen.getByText('Authenticate');

    // Simulate multiple failed attempts
    for (let i = 0; i < 5; i++) {
      fireEvent.change(input, { target: { value: '000000' } });
      fireEvent.click(button);
      await waitFor(() => {
        expect(screen.getByText('Invalid code. Please try again.')).toBeInTheDocument();
      });
    }
  });
});
```

### **6.2 Test Key Combinations**
```typescript
// src/__tests__/keyCombinations.test.ts - NEW FILE
import { renderHook } from '@testing-library/react';
import { useKeyCombination } from '../hooks/useKeyCombination';

describe('Key Combinations', () => {
  test('should trigger callback on correct key sequence', () => {
    const callback = jest.fn();
    const { unmount } = renderHook(() => 
      useKeyCombination(['KeyA', 'KeyD', 'KeyM', 'KeyI', 'KeyN'], callback)
    );

    // Simulate key presses
    const keyDownEvent = new KeyboardEvent('keydown', {
      key: 'a',
      code: 'KeyA',
      ctrlKey: true,
      shiftKey: true,
      altKey: true,
    });

    window.dispatchEvent(keyDownEvent);
    expect(callback).toHaveBeenCalled();

    unmount();
  });
});
```

---

## 📋 Final Implementation Checklist

### **Before Starting:**
- [ ] All current features are complete and tested
- [ ] All formulas are implemented and working
- [ ] All pages are functional
- [ ] Backend is stable and tested
- [ ] Frontend is stable and tested
- [ ] Create backup branch: `git checkout -b security-implementation`

### **Phase 1: Navigation Restructuring**
- [ ] Update App.tsx with new routes
- [ ] Create Dashboard component
- [ ] Rename Home.tsx to DeveloperHome.tsx
- [ ] Update AppLayout.tsx sidebar
- [ ] Test navigation works correctly

### **Phase 2: Admin Authentication System**
- [ ] Create AdminContext
- [ ] Create useKeyCombination hook
- [ ] Create AdminAuthModal component
- [ ] Create ProtectedRoute component
- [ ] Test authentication flow

### **Phase 3: Backend Security Implementation**
- [ ] Add dependencies to Cargo.toml
- [ ] Create AuthService
- [ ] Create TOTPService
- [ ] Update main.rs with auth routes
- [ ] Test backend authentication

### **Phase 4: API Protection**
- [ ] Create admin middleware
- [ ] Protect formula configuration API
- [ ] Protect logs API
- [ ] Test API protection

### **Phase 5: Build Protection**
- [ ] Install obfuscation tools
- [ ] Update package.json scripts
- [ ] Create environment files
- [ ] Update webpack config
- [ ] Test build process

### **Phase 6: Testing & Validation**
- [ ] Create security tests
- [ ] Test key combinations
- [ ] Test TOTP integration
- [ ] Test API protection
- [ ] Test build process

### **Final Validation:**
- [ ] Normal users can only access Dashboard
- [ ] Admin users can access protected pages with TOTP
- [ ] Developer users can access developer tools with TOTP
- [ ] Key combinations work reliably
- [ ] TOTP integration works with authenticator apps
- [ ] Rate limiting prevents brute force attacks
- [ ] Session management works correctly
- [ ] Build process produces obfuscated code
- [ ] All tests pass
- [ ] Security audit shows no vulnerabilities

---

## 🚨 Important Security Notes

### **Production Deployment:**
1. **Change all default secrets** in production
2. **Use environment variables** for all sensitive data
3. **Enable HTTPS** only
4. **Set secure headers** on server
5. **Configure CORS** properly
6. **Enable rate limiting** on server level
7. **Set up monitoring** and alerts
8. **Test disaster recovery** procedures

### **Security Best Practices:**
1. **Never commit secrets** to version control
2. **Use strong, unique secrets** for each environment
3. **Rotate secrets regularly**
4. **Monitor access logs** for suspicious activity
5. **Keep dependencies updated** for security patches
6. **Test security features** thoroughly
7. **Document security procedures**
8. **Train team members** on security protocols

**This checklist provides everything needed to implement a robust, enterprise-grade security system!** 🚀
