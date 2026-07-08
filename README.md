# Private Personal Vault

A secure, self-hosted personal vault for managing sensitive information.

## Features

- **🔐 Two-Layer Authentication**: Master Password + PIN verification
- **📦 Multiple Vault Types**: Identity, Banking, Passwords, Notes, Documents, Emergency, Digital Assets
- **🔒 AES-256 Encryption**: All sensitive data encrypted before storage
- **📱 Mobile Responsive**: Premium dark theme optimized for all devices
- **📊 Activity Logging**: Complete audit trail of all actions
- **💾 Backup & Restore**: Encrypted backup and restore functionality
- **⚙️ Future-Ready**: Architecture prepared for additional security methods

## Tech Stack

- **Backend**: Flask 2.3.3
- **Database**: PostgreSQL 15
- **Encryption**: AES-256 (Fernet)
- **Hashing**: Argon2 + bcrypt
- **Frontend**: HTML5, CSS3, JavaScript (vanilla)

## Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd private-vault