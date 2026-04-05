"""Security audit script - checks for exposed secrets and security issues"""
import os
import re
import sys


def check_for_exposed_secrets():
    """Check for exposed API keys and secrets in codebase"""
    print("🔍 Checking for exposed secrets...")
    
    # Patterns that should NOT appear in committed code
    dangerous_patterns = [
        (r'MISTRAL_API_KEY\s*[:=]\s*["\']?[A-Za-z0-9]{20,}', 'Mistral API key exposed'),
        (r'password\s*[:=]\s*["\'][^"\']{8,}', 'Hardcoded password'),
        (r'secret\s*[:=]\s*["\'][^"\']{10,}', 'Hardcoded secret'),
    ]
    
    # Files to skip
    skip_dirs = ['.git', 'node_modules', '__pycache__', '.venv', 'venv']
    skip_files = ['.env', '.env.local', '.env.example', 'test_api.py']
    
    issues = []
    
    for root, dirs, files in os.walk('.'):
        # Skip certain directories
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            if file in skip_files:
                continue
            
            if not file.endswith(('.py', '.js', '.yml', '.yaml', '.json', '.md', '.txt')):
                continue
            
            filepath = os.path.join(root, file)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    for pattern, description in dangerous_patterns:
                        matches = re.finditer(pattern, content, re.IGNORECASE)
                        for match in matches:
                            issues.append(f"  ❌ {filepath}: {description}")
            except Exception as e:
                pass
    
    if issues:
        print("\n🚨 Security Issues Found:")
        for issue in issues:
            print(issue)
        return False
    else:
        print("  ✅ No exposed secrets found")
        return True


def check_gitignore():
    """Check .env file is in .gitignore"""
    print("\n📁 Checking .gitignore...")
    
    if not os.path.exists('.gitignore'):
        print("  ❌ .gitignore file not found")
        return False
    
    with open('.gitignore', 'r') as f:
        content = f.read()
    
    if '.env' in content:
        print("  ✅ .env file is in .gitignore")
        return True
    else:
        print("  ❌ .env file is NOT in .gitignore")
        return False


def check_docker_compose_security():
    """Check docker-compose.yml for hardcoded secrets"""
    print("\n🐳 Checking docker-compose.yml...")
    
    if not os.path.exists('docker-compose.yml'):
        print("  ❌ docker-compose.yml not found")
        return False
    
    with open('docker-compose.yml', 'r') as f:
        content = f.read()
    
    # Check for hardcoded API keys (should use variables or env_file)
    if re.search(r'MISTRAL_API_KEY:\s*["\']?[A-Za-z0-9]{20,}', content):
        print("  ❌ Hardcoded API key in docker-compose.yml")
        return False
    else:
        print("  ✅ No hardcoded API keys in docker-compose.yml")
        return True


def check_backend_security():
    """Check backend security configuration"""
    print("\n🔒 Checking backend security...")
    
    issues = []
    
    # Check CORS configuration
    with open('backend/app/main.py', 'r') as f:
        content = f.read()
    
    if 'allow_origins=["*"]' in content:
        issues.append("  ⚠️  CORS allows all origins (ok for development, restrict in production)")
    
    if not issues:
        print("  ✅ Backend security checks passed")
        return True
    else:
        for issue in issues:
            print(issue)
        return True  # Warnings, not failures


def main():
    print("=" * 60)
    print("🛡️  TourStats Security Audit")
    print("=" * 60)
    
    all_passed = True
    
    all_passed &= check_for_exposed_secrets()
    all_passed &= check_gitignore()
    all_passed &= check_docker_compose_security()
    all_passed &= check_backend_security()
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ Security audit PASSED")
    else:
        print("❌ Security audit FAILED")
        sys.exit(1)
    print("=" * 60)


if __name__ == "__main__":
    main()
