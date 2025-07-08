#!/usr/bin/env python3
"""
CONFIGO Security Diagnostics Script
==================================

This script performs security checks on the repository to detect:
- Sensitive files that shouldn't be committed
- API keys or secrets in code
- Missing security configurations
- Build artifacts that should be ignored

Usage:
    python scripts/diagnostics.py
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Any

# Sensitive file patterns
SENSITIVE_PATTERNS = [
    r'\.env$',
    r'\.key$',
    r'\.pem$',
    r'\.p12$',
    r'\.pfx$',
    r'secrets\.json$',
    r'config\.json$',
    r'credentials\.json$',
    r'service-account\.json$',
    r'api_keys\.txt$',
    r'secrets\.txt$',
]

# API key patterns
API_KEY_PATTERNS = [
    r'AIza[0-9A-Za-z-_]{35}',  # Google API keys
    r'sk-[0-9A-Za-z]{48}',     # OpenAI API keys
    r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',  # UUIDs
    r'[0-9A-Za-z]{32,}',       # Generic long strings
]

# Build artifact patterns
BUILD_PATTERNS = [
    r'__pycache__',
    r'\.pyc$',
    r'\.pyo$',
    r'\.pyd$',
    r'\.so$',
    r'\.egg$',
    r'\.egg-info$',
    r'build/',
    r'dist/',
    r'\.cache/',
    r'\.pytest_cache/',
    r'\.coverage',
    r'htmlcov/',
]

# Files that should be ignored
IGNORE_PATTERNS = [
    r'\.git/',
    r'\.gitignore',
    r'\.env\.template',
    r'README\.md',
    r'FEATURES\.md',
    r'LICENSE',
    r'requirements\.txt',
    r'scripts/diagnostics\.py',
]

class SecurityDiagnostics:
    """Security diagnostics for the CONFIGO repository."""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        self.issues = []
        self.warnings = []
        self.successes = []
        
    def run_all_checks(self) -> Dict[str, Any]:
        """Run all security checks."""
        print("🔍 CONFIGO Security Diagnostics")
        print("=" * 50)
        
        self.check_sensitive_files()
        self.check_api_keys_in_code()
        self.check_build_artifacts()
        self.check_gitignore()
        self.check_env_template()
        
        return {
            'issues': self.issues,
            'warnings': self.warnings,
            'successes': self.successes
        }
    
    def check_sensitive_files(self) -> None:
        """Check for sensitive files in the repository."""
        print("\n🔐 Checking for sensitive files...")
        
        sensitive_files = []
        for pattern in SENSITIVE_PATTERNS:
            for file_path in self.repo_path.rglob(pattern):
                if not self._should_ignore_file(file_path):
                    sensitive_files.append(str(file_path))
        
        if sensitive_files:
            self.issues.append(f"Found {len(sensitive_files)} sensitive files:")
            for file_path in sensitive_files:
                self.issues.append(f"  - {file_path}")
        else:
            self.successes.append("✅ No sensitive files found")
    
    def check_api_keys_in_code(self) -> None:
        """Check for API keys in code files."""
        print("🔑 Checking for API keys in code...")
        
        code_extensions = {'.py', '.js', '.ts', '.json', '.yaml', '.yml', '.md', '.txt'}
        api_keys_found = []
        
        for file_path in self.repo_path.rglob('*'):
            if (file_path.is_file() and 
                file_path.suffix in code_extensions and 
                not self._should_ignore_file(file_path)):
                
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    for pattern in API_KEY_PATTERNS:
                        matches = re.findall(pattern, content)
                        for match in matches:
                            api_keys_found.append({
                                'file': str(file_path),
                                'key': match[:10] + '...' if len(match) > 10 else match
                            })
                except Exception as e:
                    self.warnings.append(f"Could not read {file_path}: {e}")
        
        if api_keys_found:
            self.issues.append(f"Found {len(api_keys_found)} potential API keys:")
            for item in api_keys_found:
                self.issues.append(f"  - {item['file']}: {item['key']}")
        else:
            self.successes.append("✅ No API keys found in code")
    
    def check_build_artifacts(self) -> None:
        """Check for build artifacts that shouldn't be committed."""
        print("🔨 Checking for build artifacts...")
        
        build_files = []
        for pattern in BUILD_PATTERNS:
            for file_path in self.repo_path.rglob(pattern):
                if not self._should_ignore_file(file_path):
                    build_files.append(str(file_path))
        
        if build_files:
            self.warnings.append(f"Found {len(build_files)} build artifacts:")
            for file_path in build_files[:10]:  # Show first 10
                self.warnings.append(f"  - {file_path}")
            if len(build_files) > 10:
                self.warnings.append(f"  ... and {len(build_files) - 10} more")
        else:
            self.successes.append("✅ No build artifacts found")
    
    def check_gitignore(self) -> None:
        """Check if .gitignore exists and contains necessary patterns."""
        print("📋 Checking .gitignore...")
        
        gitignore_path = self.repo_path / '.gitignore'
        if not gitignore_path.exists():
            self.issues.append("❌ .gitignore file not found")
            return
        
        content = gitignore_path.read_text()
        required_patterns = [
            '.env',
            '__pycache__',
            '*.log',
            '.configo_memory',
            '*.pyc'
        ]
        
        missing_patterns = []
        for pattern in required_patterns:
            if pattern not in content:
                missing_patterns.append(pattern)
        
        if missing_patterns:
            self.warnings.append(f"Missing patterns in .gitignore: {', '.join(missing_patterns)}")
        else:
            self.successes.append("✅ .gitignore contains all required patterns")
    
    def check_env_template(self) -> None:
        """Check if .env.template exists and is properly configured."""
        print("📝 Checking .env.template...")
        
        template_path = self.repo_path / '.env.template'
        if not template_path.exists():
            self.issues.append("❌ .env.template file not found")
            return
        
        content = template_path.read_text()
        
        # Check for placeholder values
        if 'your-gemini-api-key-here' in content:
            self.successes.append("✅ .env.template contains placeholder values")
        else:
            self.warnings.append("⚠️ .env.template may contain real values")
        
        # Check for security warnings
        if 'DO NOT commit' in content or 'sensitive' in content.lower():
            self.successes.append("✅ .env.template contains security warnings")
        else:
            self.warnings.append("⚠️ .env.template missing security warnings")
    
    def _should_ignore_file(self, file_path: Path) -> bool:
        """Check if file should be ignored during scanning."""
        file_str = str(file_path)
        
        # Check ignore patterns
        for pattern in IGNORE_PATTERNS:
            if re.search(pattern, file_str):
                return True
        
        # Check if file is in .gitignore
        gitignore_path = self.repo_path / '.gitignore'
        if gitignore_path.exists():
            try:
                import subprocess
                result = subprocess.run(
                    ['git', 'check-ignore', str(file_path)],
                    capture_output=True,
                    text=True,
                    cwd=self.repo_path
                )
                if result.returncode == 0:
                    return True
            except Exception:
                pass
        
        return False
    
    def print_report(self) -> None:
        """Print the diagnostic report."""
        print("\n" + "=" * 50)
        print("📊 SECURITY DIAGNOSTICS REPORT")
        print("=" * 50)
        
        if self.successes:
            print("\n✅ SUCCESSES:")
            for success in self.successes:
                print(f"  {success}")
        
        if self.warnings:
            print("\n⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"  {warning}")
        
        if self.issues:
            print("\n🚨 CRITICAL ISSUES:")
            for issue in self.issues:
                print(f"  {issue}")
        
        # Summary
        total_issues = len(self.issues) + len(self.warnings)
        if total_issues == 0:
            print("\n🎉 All security checks passed! Repository is secure.")
        elif len(self.issues) == 0:
            print(f"\n⚠️  {len(self.warnings)} warnings found. Review recommended.")
        else:
            print(f"\n🚨 {len(self.issues)} critical issues and {len(self.warnings)} warnings found.")
            print("   Immediate action required!")


def main():
    """Main function to run diagnostics."""
    diagnostics = SecurityDiagnostics()
    results = diagnostics.run_all_checks()
    diagnostics.print_report()
    
    # Exit with error code if critical issues found
    if results['issues']:
        sys.exit(1)
    elif results['warnings']:
        sys.exit(2)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main() 