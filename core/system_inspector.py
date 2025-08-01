"""
File: core/system_inspector.py
Purpose: Advanced System Intelligence for CONFIGO - detects comprehensive system metadata
         to adapt installation strategies dynamically.
Maintainer: Kishore Kumar S
Description: Provides detailed system analysis including OS, architecture, package managers,
             GPU detection, virtualization, and hardware specifications for intelligent
             tool installation and configuration.
"""

import os
import sys
import platform
import subprocess
import shutil
import logging
import json
import requests
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime

# System analysis libraries
import psutil
import distro

# Optional GPU detection
try:
    import GPUtil
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False

# Optional CPU info
try:
    import cpuinfo
    CPUINFO_AVAILABLE = True
except ImportError:
    CPUINFO_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class SystemWarning:
    """System warning or blocker information."""
    level: str  # 'warning', 'error', 'info'
    message: str
    category: str  # 'package_manager', 'virtualization', 'permissions', etc.
    recommendation: Optional[str] = None


@dataclass
class SystemIntelligence:
    """Comprehensive system intelligence data."""
    # Basic system info
    os_name: str
    os_version: str
    arch: str
    shell: str
    
    # Package managers and tools
    package_managers: List[str]
    installed_tools: List[str]
    
    # Hardware info
    gpu: Optional[str]
    cuda_available: bool
    ram_gb: int
    cpu_model: str
    cpu_cores: int
    cpu_threads: int
    
    # Environment info
    virtualization: str
    has_sudo: bool
    internet: bool
    python_version: str
    
    # Additional metadata
    user_home: str
    temp_dir: str
    system_timezone: str
    
    # Warnings and blockers
    warnings: List[SystemWarning]
    
    # Analysis metadata
    analysis_timestamp: datetime
    analysis_duration: float


class SystemInspector:
    """
    Advanced System Intelligence for CONFIGO.
    
    Detects comprehensive system metadata including OS, architecture, package managers,
    GPU detection, virtualization, and hardware specifications for intelligent tool
    installation and configuration.
    """
    
    def __init__(self):
        """Initialize the system inspector."""
        self.analysis_start = None
        self.warnings = []
        logger.info("SystemInspector initialized")
    
    def analyze(self) -> SystemIntelligence:
        """
        Perform comprehensive system analysis.
        
        Returns:
            SystemIntelligence: Complete system intelligence data
        """
        self.analysis_start = datetime.now()
        self.warnings = []
        
        logger.info("Starting comprehensive system analysis...")
        
        try:
            # Basic system detection
            os_info = self._detect_os()
            arch = self._detect_architecture()
            shell = self._detect_shell()
            
            # Package managers and tools
            package_managers = self._detect_package_managers()
            installed_tools = self._detect_installed_tools()
            
            # Hardware detection
            gpu_info = self._detect_gpu()
            ram_info = self._detect_ram()
            cpu_info = self._detect_cpu()
            
            # Environment detection
            virtualization = self._detect_virtualization()
            has_sudo = self._check_sudo_access()
            internet = self._check_internet()
            python_version = self._get_python_version()
            
            # Additional metadata
            user_home = os.path.expanduser("~")
            temp_dir = os.environ.get('TMPDIR', '/tmp')
            system_timezone = self._get_timezone()
            
            # Calculate analysis duration
            analysis_duration = (datetime.now() - self.analysis_start).total_seconds()
            
            # Create system intelligence object
            system_intelligence = SystemIntelligence(
                os_name=os_info['name'],
                os_version=os_info['version'],
                arch=arch,
                shell=shell,
                package_managers=package_managers,
                installed_tools=installed_tools,
                gpu=gpu_info['gpu'],
                cuda_available=gpu_info['cuda_available'],
                ram_gb=ram_info['ram_gb'],
                cpu_model=cpu_info['model'],
                cpu_cores=cpu_info['cores'],
                cpu_threads=cpu_info['threads'],
                virtualization=virtualization,
                has_sudo=has_sudo,
                internet=internet,
                python_version=python_version,
                user_home=user_home,
                temp_dir=temp_dir,
                system_timezone=system_timezone,
                warnings=self.warnings,
                analysis_timestamp=self.analysis_start,
                analysis_duration=analysis_duration
            )
            
            logger.info(f"System analysis completed in {analysis_duration:.2f}s")
            return system_intelligence
            
        except Exception as e:
            logger.error(f"Error during system analysis: {e}")
            # Return minimal system info on error
            return self._create_fallback_intelligence()
    
    def _detect_os(self) -> Dict[str, str]:
        """Detect operating system and version."""
        try:
            if platform.system() == "Linux":
                # Use distro for Linux distribution detection
                try:
                    distro_info = distro.info()
                    return {
                        'name': distro_info.get('name', 'Linux'),
                        'version': distro_info.get('version', 'Unknown')
                    }
                except Exception as distro_error:
                    logger.warning(f"Distro detection failed: {distro_error}")
                    # Fallback to basic Linux detection
                    return {
                        'name': 'Linux',
                        'version': 'Unknown'
                    }
            elif platform.system() == "Darwin":
                # macOS detection
                version = platform.mac_ver()[0]
                return {
                    'name': 'macOS',
                    'version': version
                }
            elif platform.system() == "Windows":
                # Windows detection
                version = platform.win32_ver()[0]
                return {
                    'name': 'Windows',
                    'version': version
                }
            else:
                return {
                    'name': platform.system(),
                    'version': 'Unknown'
                }
        except Exception as e:
            logger.warning(f"Error detecting OS: {e}")
            return {
                'name': platform.system(),
                'version': 'Unknown'
            }
    
    def _detect_architecture(self) -> str:
        """Detect system architecture."""
        return platform.machine()
    
    def _detect_shell(self) -> str:
        """Detect current shell."""
        shell = os.environ.get('SHELL', 'unknown')
        return os.path.basename(shell)
    
    def _detect_package_managers(self) -> List[str]:
        """Detect available package managers."""
        package_managers = []
        
        # Common package managers to check
        managers = {
            'apt': 'apt-get',
            'snap': 'snap',
            'brew': 'brew',
            'choco': 'choco',
            'dnf': 'dnf',
            'yum': 'yum',
            'pacman': 'pacman',
            'zypper': 'zypper',
            'flatpak': 'flatpak',
            'pip': 'pip',
            'npm': 'npm',
            'cargo': 'cargo'
        }
        
        for name, command in managers.items():
            if shutil.which(command):
                package_managers.append(name)
        
        # Check for WSL-specific limitations
        if self._is_wsl() and 'snap' in package_managers:
            self.warnings.append(SystemWarning(
                level='warning',
                message='Snap may not work properly in WSL',
                category='virtualization',
                recommendation='Consider using apt or flatpak instead'
            ))
        
        return package_managers
    
    def _detect_installed_tools(self) -> List[str]:
        """Detect commonly installed development tools."""
        tools = []
        
        # Common development tools to check
        common_tools = [
            'git', 'python3', 'python', 'node', 'npm', 'docker', 'code',
            'cursor', 'vim', 'nano', 'curl', 'wget', 'ssh', 'rsync',
            'make', 'gcc', 'g++', 'clang', 'cmake', 'ninja', 'meson',
            'jupyter', 'pip', 'pip3', 'conda', 'poetry', 'cargo',
            'go', 'rustc', 'java', 'javac', 'mvn', 'gradle'
        ]
        
        for tool in common_tools:
            if shutil.which(tool):
                tools.append(tool)
        
        return tools
    
    def _detect_gpu(self) -> Dict[str, Any]:
        """Detect GPU information and CUDA availability with improved accuracy."""
        gpu_info = {
            'gpu': [],
            'cuda_available': False,
            'nvidia_smi_available': False,
            'lshw_available': False
        }
        
        try:
            # Check if nvidia-smi is available
            try:
                result = subprocess.run(['which', 'nvidia-smi'], 
                                     capture_output=True, text=True, timeout=3)
                gpu_info['nvidia_smi_available'] = result.returncode == 0
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass
            
            # Check if lshw is available
            try:
                result = subprocess.run(['which', 'lshw'], 
                                     capture_output=True, text=True, timeout=3)
                gpu_info['lshw_available'] = result.returncode == 0
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass
            
            # Method 1: Use lspci to detect all GPUs
            try:
                result = subprocess.run(['lspci'], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    gpu_lines = []
                    for line in result.stdout.split('\n'):
                        if any(keyword in line.lower() for keyword in ['vga', '3d', 'display']):
                            gpu_lines.append(line.strip())
                    
                    # Parse GPU information from lspci output
                    for line in gpu_lines:
                        if 'nvidia' in line.lower():
                            # Extract NVIDIA GPU name
                            gpu_name = self._extract_nvidia_name(line)
                            if gpu_name:
                                gpu_info['gpu'].append(f"NVIDIA {gpu_name}")
                        elif 'amd' in line.lower() or 'radeon' in line.lower():
                            # Extract AMD GPU name
                            gpu_name = self._extract_amd_name(line)
                            if gpu_name:
                                gpu_info['gpu'].append(f"AMD {gpu_name}")
                        elif 'intel' in line.lower() and 'graphics' in line.lower():
                            # Extract Intel GPU name
                            gpu_name = self._extract_intel_name(line)
                            if gpu_name:
                                gpu_info['gpu'].append(f"Intel {gpu_name}")
            except (subprocess.TimeoutExpired, FileNotFoundError) as e:
                logger.debug(f"lspci not available: {e}")
            
            # Method 2: Use nvidia-smi for detailed NVIDIA info
            if gpu_info['nvidia_smi_available']:
                try:
                    result = subprocess.run(['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'],
                                         capture_output=True, text=True, timeout=5)
                    if result.returncode == 0 and result.stdout.strip():
                        nvidia_gpus = result.stdout.strip().split('\n')
                        # Update or add NVIDIA GPUs
                        for gpu_name in nvidia_gpus:
                            if gpu_name.strip():
                                nvidia_full_name = f"NVIDIA {gpu_name.strip()}"
                                # Replace if already exists, otherwise add
                                if not any('NVIDIA' in gpu for gpu in gpu_info['gpu']):
                                    gpu_info['gpu'].append(nvidia_full_name)
                                else:
                                    # Replace the generic NVIDIA entry with specific one
                                    gpu_info['gpu'] = [gpu for gpu in gpu_info['gpu'] if 'NVIDIA' not in gpu]
                                    gpu_info['gpu'].append(nvidia_full_name)
                        gpu_info['cuda_available'] = True
                except (subprocess.TimeoutExpired, FileNotFoundError) as e:
                    logger.debug(f"nvidia-smi failed: {e}")
            
            # Method 3: Use lshw for detailed hardware info (if available)
            if gpu_info['lshw_available'] and not gpu_info['gpu']:
                try:
                    result = subprocess.run(['lshw', '-C', 'display'], 
                                         capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        # Parse lshw output for GPU information
                        gpu_info['gpu'] = self._parse_lshw_gpu_info(result.stdout)
                except (subprocess.TimeoutExpired, FileNotFoundError) as e:
                    logger.debug(f"lshw failed: {e}")
            
            # Method 4: Use GPUtil as fallback
            if not gpu_info['gpu'] and GPU_AVAILABLE:
                try:
                    gpus = GPUtil.getGPUs()
                    if gpus:
                        for gpu in gpus:
                            gpu_info['gpu'].append(f"NVIDIA {gpu.name}")
                        gpu_info['cuda_available'] = True
                except Exception as e:
                    logger.debug(f"GPUtil failed: {e}")
            
            # Ensure we have at least one GPU entry or None
            if not gpu_info['gpu']:
                gpu_info['gpu'] = None
            elif len(gpu_info['gpu']) == 1:
                gpu_info['gpu'] = gpu_info['gpu'][0]
                    
        except Exception as e:
            logger.warning(f"Error detecting GPU: {e}")
            gpu_info['gpu'] = None
        
        return gpu_info
    
    def _extract_nvidia_name(self, lspci_line: str) -> Optional[str]:
        """Extract NVIDIA GPU name from lspci output."""
        try:
            # Look for common NVIDIA patterns
            if 'nvidia' in lspci_line.lower():
                # Extract the model part after NVIDIA Corporation
                if 'nvidia corporation' in lspci_line.lower():
                    # Find the GPU model after "NVIDIA Corporation"
                    parts = lspci_line.split()
                    for i, part in enumerate(parts):
                        if part.lower() == 'corporation':
                            # Get the model name after "Corporation"
                            model_parts = parts[i+1:]
                            # Remove common suffixes like "(rev xx)"
                            model_name = ' '.join(model_parts)
                            if '(' in model_name:
                                model_name = model_name.split('(')[0].strip()
                            return model_name
                else:
                    # Fallback: extract after "NVIDIA"
                    parts = lspci_line.split()
                    for i, part in enumerate(parts):
                        if 'nvidia' in part.lower():
                            model_parts = parts[i+1:i+4]
                            return ' '.join(model_parts).strip()
            return None
        except Exception:
            return None
    
    def _extract_amd_name(self, lspci_line: str) -> Optional[str]:
        """Extract AMD GPU name from lspci output."""
        try:
            if 'amd' in lspci_line.lower() or 'radeon' in lspci_line.lower():
                # Extract AMD model information
                parts = lspci_line.split()
                for i, part in enumerate(parts):
                    if 'amd' in part.lower() or 'radeon' in part.lower():
                        model_parts = parts[i+1:i+4]
                        return ' '.join(model_parts).strip()
            return None
        except Exception:
            return None
    
    def _extract_intel_name(self, lspci_line: str) -> Optional[str]:
        """Extract Intel GPU name from lspci output."""
        try:
            if 'intel' in lspci_line.lower() and 'graphics' in lspci_line.lower():
                # Extract Intel graphics model
                if 'intel corporation' in lspci_line.lower():
                    # Find the GPU model after "Intel Corporation"
                    parts = lspci_line.split()
                    for i, part in enumerate(parts):
                        if part.lower() == 'corporation':
                            # Get the model name after "Corporation"
                            model_parts = parts[i+1:]
                            # Remove common suffixes like "(rev xx)"
                            model_name = ' '.join(model_parts)
                            if '(' in model_name:
                                model_name = model_name.split('(')[0].strip()
                            return model_name
                else:
                    # Fallback: extract after "Intel"
                    parts = lspci_line.split()
                    for i, part in enumerate(parts):
                        if 'intel' in part.lower():
                            model_parts = parts[i+1:i+4]
                            return ' '.join(model_parts).strip()
            return None
        except Exception:
            return None
    
    def _parse_lshw_gpu_info(self, lshw_output: str) -> List[str]:
        """Parse lshw output to extract GPU information."""
        gpus = []
        try:
            lines = lshw_output.split('\n')
            current_gpu = None
            
            for line in lines:
                line = line.strip()
                if '*-display' in line or '*display' in line:
                    current_gpu = None
                elif 'product:' in line and current_gpu is None:
                    product = line.split('product:')[1].strip()
                    if product and product != 'UNKNOWN':
                        current_gpu = product
                elif 'vendor:' in line and current_gpu:
                    vendor = line.split('vendor:')[1].strip()
                    if vendor and vendor != 'UNKNOWN':
                        gpu_name = f"{vendor} {current_gpu}"
                        gpus.append(gpu_name)
                        current_gpu = None
            
            return gpus
        except Exception as e:
            logger.debug(f"Error parsing lshw output: {e}")
            return []
    
    def _detect_ram(self) -> Dict[str, int]:
        """Detect RAM information."""
        try:
            ram_bytes = psutil.virtual_memory().total
            ram_gb = round(ram_bytes / (1024**3), 1)
            return {'ram_gb': ram_gb}
        except Exception as e:
            logger.warning(f"Error detecting RAM: {e}")
            return {'ram_gb': 0}
    
    def _detect_cpu(self) -> Dict[str, Any]:
        """Detect CPU information with improved accuracy."""
        try:
            # Get physical and logical core counts
            cpu_cores_physical = psutil.cpu_count(logical=False)
            cpu_cores_logical = psutil.cpu_count(logical=True)
            
            # Get CPU model with multiple fallback methods
            cpu_model = "Unknown"
            
            # Method 1: Use cpuinfo for detailed brand information
            if CPUINFO_AVAILABLE:
                try:
                    cpu_info = cpuinfo.get_cpu_info()
                    if cpu_info.get('brand_raw'):
                        cpu_model = cpu_info['brand_raw']
                except Exception as e:
                    logger.debug(f"cpuinfo failed: {e}")
            
            # Method 2: Use /proc/cpuinfo on Linux
            if cpu_model == "Unknown" and platform.system() == "Linux":
                try:
                    with open('/proc/cpuinfo', 'r') as f:
                        cpuinfo_content = f.read()
                        for line in cpuinfo_content.split('\n'):
                            if line.startswith('model name'):
                                cpu_model = line.split(':')[1].strip()
                                break
                except Exception as e:
                    logger.debug(f"/proc/cpuinfo failed: {e}")
            
            # Method 3: Use platform.processor() as fallback
            if cpu_model == "Unknown":
                cpu_model = platform.processor()
            
            # Method 4: Use lscpu on Linux for additional info
            if platform.system() == "Linux":
                try:
                    result = subprocess.run(['lscpu'], capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        for line in result.stdout.split('\n'):
                            if 'Model name:' in line:
                                model_name = line.split(':')[1].strip()
                                if model_name and model_name != "Unknown":
                                    cpu_model = model_name
                                break
                except (subprocess.TimeoutExpired, FileNotFoundError) as e:
                    logger.debug(f"lscpu failed: {e}")
            
            # Clean up CPU model name
            if cpu_model and cpu_model != "Unknown":
                # Remove extra whitespace and common prefixes
                cpu_model = cpu_model.strip()
                if cpu_model.startswith('CPU '):
                    cpu_model = cpu_model[4:]
                if cpu_model.startswith('Intel(R) '):
                    cpu_model = cpu_model[9:]
                if cpu_model.startswith('AMD '):
                    cpu_model = cpu_model[4:]
            
            return {
                'model': cpu_model,
                'cores': cpu_cores_physical,
                'threads': cpu_cores_logical
            }
        except Exception as e:
            logger.warning(f"Error detecting CPU: {e}")
            return {
                'model': 'Unknown',
                'cores': 0,
                'threads': 0
            }
    
    def _detect_virtualization(self) -> str:
        """Detect virtualization environment."""
        try:
            # Check for WSL
            if self._is_wsl():
                return "WSL"
            
            # Check for Docker
            if os.path.exists('/.dockerenv'):
                return "Docker"
            
            # Check for VirtualBox
            try:
                result = subprocess.run(['dmidecode', '-s', 'system-product-name'],
                                     capture_output=True, text=True, timeout=5)
                if result.returncode == 0 and 'VirtualBox' in result.stdout:
                    return "VirtualBox"
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass
            
            # Check for VMware
            try:
                result = subprocess.run(['dmidecode', '-s', 'system-product-name'],
                                     capture_output=True, text=True, timeout=5)
                if result.returncode == 0 and 'VMware' in result.stdout:
                    return "VMware"
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass
            
            # Check for KVM/QEMU
            try:
                result = subprocess.run(['dmidecode', '-s', 'system-product-name'],
                                     capture_output=True, text=True, timeout=5)
                if result.returncode == 0 and ('KVM' in result.stdout or 'QEMU' in result.stdout):
                    return "KVM/QEMU"
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass
            
            return "None"
            
        except Exception as e:
            logger.warning(f"Error detecting virtualization: {e}")
            return "Unknown"
    
    def _is_wsl(self) -> bool:
        """Check if running in WSL."""
        try:
            with open('/proc/version', 'r') as f:
                version = f.read()
                return 'microsoft' in version.lower() or 'wsl' in version.lower()
        except:
            return False
    
    def _check_sudo_access(self) -> bool:
        """Check if user has sudo access."""
        try:
            result = subprocess.run(['sudo', '-n', 'true'], 
                                 capture_output=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def _check_internet(self) -> bool:
        """Check internet connectivity."""
        try:
            response = requests.get('https://httpbin.org/get', timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def _get_python_version(self) -> str:
        """Get Python version."""
        return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    
    def _get_timezone(self) -> str:
        """Get system timezone."""
        try:
            import time
            return time.tzname[time.daylight]
        except:
            return "UTC"
    
    def _create_fallback_intelligence(self) -> SystemIntelligence:
        """Create fallback system intelligence on error."""
        return SystemIntelligence(
            os_name=platform.system(),
            os_version="Unknown",
            arch=platform.machine(),
            shell=os.environ.get('SHELL', 'unknown'),
            package_managers=[],
            installed_tools=[],
            gpu=None,
            cuda_available=False,
            ram_gb=0,
            cpu_model="Unknown",
            cpu_cores=0,
            cpu_threads=0,
            virtualization="Unknown",
            has_sudo=False,
            internet=False,
            python_version=self._get_python_version(),
            user_home=os.path.expanduser("~"),
            temp_dir="/tmp",
            system_timezone="UTC",
            warnings=[SystemWarning(
                level='error',
                message='System analysis failed, using fallback data',
                category='analysis'
            )],
            analysis_timestamp=datetime.now(),
            analysis_duration=0.0
        )
    
    def get_installation_recommendations(self, system_info: SystemIntelligence) -> List[str]:
        """
        Get installation recommendations based on system intelligence.
        
        Args:
            system_info: System intelligence data
            
        Returns:
            List[str]: List of installation recommendations
        """
        recommendations = []
        
        # Package manager recommendations
        if 'apt' in system_info.package_managers:
            recommendations.append("Use apt for system packages")
        if 'snap' in system_info.package_managers and system_info.virtualization != "WSL":
            recommendations.append("Use snap for containerized applications")
        if 'flatpak' in system_info.package_managers:
            recommendations.append("Use flatpak for sandboxed applications")
        
        # GPU-specific recommendations
        if system_info.gpu and "NVIDIA" in system_info.gpu:
            if system_info.cuda_available:
                recommendations.append("CUDA available - use GPU-accelerated AI tools")
            else:
                recommendations.append("NVIDIA GPU detected but CUDA not available")
        
        # Virtualization warnings
        if system_info.virtualization == "WSL":
            recommendations.append("WSL detected - some tools may have limitations")
        
        # Performance recommendations
        if system_info.ram_gb < 8:
            recommendations.append("Low RAM detected - consider lightweight tools")
        if system_info.cpu_cores < 4:
            recommendations.append("Limited CPU cores - avoid resource-intensive tools")
        
        return recommendations
    
    def save_to_memory(self, system_info: SystemIntelligence, memory_dir: str = ".configo_memory") -> None:
        """
        Save system intelligence to memory for future reference.
        
        Args:
            system_info: System intelligence data
            memory_dir: Memory directory path
        """
        try:
            memory_path = Path(memory_dir)
            memory_path.mkdir(exist_ok=True)
            
            # Convert to dictionary for JSON serialization
            system_dict = {
                'os_name': system_info.os_name,
                'os_version': system_info.os_version,
                'arch': system_info.arch,
                'shell': system_info.shell,
                'package_managers': system_info.package_managers,
                'installed_tools': system_info.installed_tools,
                'gpu': system_info.gpu,
                'cuda_available': system_info.cuda_available,
                'ram_gb': system_info.ram_gb,
                'cpu_model': system_info.cpu_model,
                'cpu_cores': system_info.cpu_cores,
                'cpu_threads': system_info.cpu_threads,
                'virtualization': system_info.virtualization,
                'has_sudo': system_info.has_sudo,
                'internet': system_info.internet,
                'python_version': system_info.python_version,
                'user_home': system_info.user_home,
                'temp_dir': system_info.temp_dir,
                'system_timezone': system_info.system_timezone,
                'warnings': [
                    {
                        'level': w.level,
                        'message': w.message,
                        'category': w.category,
                        'recommendation': w.recommendation
                    } for w in system_info.warnings
                ],
                'analysis_timestamp': system_info.analysis_timestamp.isoformat(),
                'analysis_duration': system_info.analysis_duration
            }
            
            # Save to file
            system_file = memory_path / 'system_intelligence.json'
            with open(system_file, 'w') as f:
                json.dump(system_dict, f, indent=2)
            
            logger.info(f"System intelligence saved to {system_file}")
            
        except Exception as e:
            logger.error(f"Error saving system intelligence: {e}")


def display_system_summary(system_info: SystemIntelligence) -> None:
    """
    Display a beautiful system intelligence summary using rich.
    
    Args:
        system_info: System intelligence data to display
    """
    try:
        from rich.console import Console
        from rich.table import Table
        from rich.panel import Panel
        from rich.text import Text
        from rich.columns import Columns
        
        console = Console()
        
        # Create main table
        table = Table(title="📡 CONFIGO System Intelligence Report", show_header=False)
        table.add_column("Category", style="cyan", no_wrap=True)
        table.add_column("Value", style="white")
        
        # Basic system info
        table.add_row("🖥️  OS", f"{system_info.os_name} {system_info.os_version}")
        table.add_row("🧠 Architecture", system_info.arch)
        table.add_row("💻 Shell", system_info.shell)
        
        # Package managers
        pm_text = ", ".join(system_info.package_managers) if system_info.package_managers else "None detected"
        table.add_row("🔧 Package Mgrs", pm_text)
        
        # Installed tools (show first 5)
        tools_text = ", ".join(system_info.installed_tools[:5])
        if len(system_info.installed_tools) > 5:
            tools_text += f" (+{len(system_info.installed_tools) - 5} more)"
        table.add_row("📦 Tools Found", tools_text)
        
        # GPU info
        if isinstance(system_info.gpu, list):
            gpu_text = ", ".join(system_info.gpu)
        else:
            gpu_text = system_info.gpu or "None detected"
        
        if system_info.gpu and "NVIDIA" in str(system_info.gpu):
            cuda_status = "✅" if system_info.cuda_available else "❌"
            gpu_text += f" (CUDA: {cuda_status})"
        table.add_row("🎮 GPU", gpu_text)
        
        # Hardware info
        table.add_row("💾 RAM", f"{system_info.ram_gb} GB")
        table.add_row("🖥️  CPU", f"{system_info.cpu_model} ({system_info.cpu_cores} cores, {system_info.cpu_threads} threads)")
        
        # Environment info
        sudo_status = "✅" if system_info.has_sudo else "❌"
        table.add_row("🔐 Sudo Access", sudo_status)
        
        internet_status = "✅ Online" if system_info.internet else "❌ Offline"
        table.add_row("🌐 Internet", internet_status)
        
        table.add_row("🧪 Virtualization", system_info.virtualization)
        table.add_row("🐍 Python", system_info.python_version)
        
        # Display the table
        console.print(table)
        
        # Display warnings if any
        if system_info.warnings:
            console.print("\n⚠️  Warnings:")
            for warning in system_info.warnings:
                color = "yellow" if warning.level == "warning" else "red"
                console.print(f"  • [{color}]{warning.message}[/{color}]")
                if warning.recommendation:
                    console.print(f"    💡 Recommendation: {warning.recommendation}")
        
        # Display recommendations
        inspector = SystemInspector()
        recommendations = inspector.get_installation_recommendations(system_info)
        if recommendations:
            console.print("\n💡 Installation Recommendations:")
            for rec in recommendations:
                console.print(f"  • {rec}")
        
        # Analysis info
        console.print(f"\n[dim]Analysis completed in {system_info.analysis_duration:.2f}s[/dim]")
        
    except ImportError:
        # Fallback to simple print if rich is not available
        print("📡 CONFIGO System Intelligence Report")
        print("=" * 50)
        print(f"🖥️  OS: {system_info.os_name} {system_info.os_version}")
        print(f"🧠 Architecture: {system_info.arch}")
        print(f"💻 Shell: {system_info.shell}")
        print(f"🔧 Package Mgrs: {', '.join(system_info.package_managers)}")
        print(f"📦 Tools Found: {', '.join(system_info.installed_tools[:5])}")
        print(f"🎮 GPU: {system_info.gpu or 'None detected'}")
        print(f"💾 RAM: {system_info.ram_gb} GB")
        print(f"🖥️  CPU: {system_info.cpu_model}")
        print(f"🔐 Sudo Access: {'✅' if system_info.has_sudo else '❌'}")
        print(f"🌐 Internet: {'✅ Online' if system_info.internet else '❌ Offline'}")
        print(f"🧪 Virtualization: {system_info.virtualization}")
        print(f"🐍 Python: {system_info.python_version}")


if __name__ == "__main__":
    # Test the system inspector
    inspector = SystemInspector()
    system_info = inspector.analyze()
    display_system_summary(system_info) 