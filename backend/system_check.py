"""System health check diagnostic for TruthLens AI."""

import subprocess
import sys
import logging
from pathlib import Path
from typing import Dict, List, Tuple
import importlib.util

logger = logging.getLogger(__name__)


class SystemHealthCheck:
    """Comprehensive system diagnostics for TruthLens."""

    def __init__(self):
        """Initialize health check."""
        self.checks = {}
        self.warnings = []
        self.errors = []

    def check_python_version(self) -> Tuple[bool, str]:
        """Check Python version."""
        version = sys.version_info
        min_version = (3, 9)

        if version >= min_version:
            return True, f"Python {version.major}.{version.minor}.{version.micro} ✓"
        else:
            return (
                False,
                f"Python {version.major}.{version.minor} (require >= {min_version[0]}.{min_version[1]})",
            )

    def check_required_packages(self) -> Tuple[bool, Dict]:
        """Check if all required packages are installed."""
        required = {
            "torch": "PyTorch",
            "transformers": "Transformers",
            "sentence_transformers": "Sentence Transformers",
            "fastapi": "FastAPI",
            "sqlalchemy": "SQLAlchemy",
            "cv2": "OpenCV",
            "pytesseract": "Tesseract",
            "spacy": "spaCy",
            "nltk": "NLTK",
            "numpy": "NumPy",
            "pandas": "Pandas",
            "sklearn": "Scikit-learn",
            "shap": "SHAP",
            "lime": "LIME",
            "faiss": "FAISS",
            "pinecone": "Pinecone",
            "redis": "Redis",
            "newspaper": "Newspaper3k",
            "bs4": "Beautiful Soup",
            "requests": "Requests",
        }

        installed = {}
        missing = []

        for module_name, package_name in required.items():
            spec = importlib.util.find_spec(module_name)
            if spec is not None:
                try:
                    module = __import__(module_name)
                    version = getattr(module, "__version__", "unknown")
                    installed[package_name] = version
                except Exception as e:
                    missing.append(f"{package_name} (error: {str(e)})")
            else:
                missing.append(package_name)

        all_installed = len(missing) == 0
        return all_installed, {"installed": installed, "missing": missing}

    def check_pytorch_gpu(self) -> Tuple[bool, str]:
        """Check PyTorch GPU availability."""
        try:
            import torch

            if torch.cuda.is_available():
                gpu_name = torch.cuda.get_device_name(0)
                gpu_count = torch.cuda.device_count()
                return (
                    True,
                    f"{gpu_count} GPU(s) detected: {gpu_name} ✓",
                )
            else:
                return False, "No CUDA GPU detected (CPU mode)"
        except Exception as e:
            return False, f"GPU check failed: {e}"

    def check_database_connection(self) -> Tuple[bool, str]:
        """Check PostgreSQL database connection."""
        try:
            import psycopg2

            try:
                conn = psycopg2.connect(
                    host="localhost",
                    port=5432,
                    database="truthlens_db",
                    user="postgres",
                    password="postgres",
                )
                conn.close()
                return True, "PostgreSQL connection successful ✓"
            except psycopg2.OperationalError:
                return (
                    False,
                    "PostgreSQL not running (expected for dev, use 'docker-compose up')",
                )
        except ImportError:
            return False, "psycopg2 not installed"
        except Exception as e:
            return False, f"Database connection failed: {e}"

    def check_redis_connection(self) -> Tuple[bool, str]:
        """Check Redis connection."""
        try:
            import redis

            try:
                r = redis.Redis(host="localhost", port=6379, db=0, socket_connect_timeout=2)
                r.ping()
                return True, "Redis connection successful ✓"
            except redis.ConnectionError:
                return (
                    False,
                    "Redis not running (expected for dev, use 'docker-compose up')",
                )
        except ImportError:
            return False, "redis package not installed"
        except Exception as e:
            return False, f"Redis check failed: {e}"

    def check_tesseract_ocr(self) -> Tuple[bool, str]:
        """Check Tesseract OCR installation."""
        try:
            result = subprocess.run(
                ["tesseract", "--version"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                version = result.stdout.split("\n")[0]
                return True, f"Tesseract OCR installed: {version} ✓"
            else:
                return (
                    False,
                    "Tesseract not found (install with: brew install tesseract)",
                )
        except FileNotFoundError:
            return (
                False,
                "Tesseract not found (install with: brew install tesseract)",
            )
        except Exception as e:
            return False, f"Tesseract check failed: {e}"

    def check_ml_models(self) -> Tuple[bool, Dict]:
        """Check if ML models can be loaded."""
        models = {
            "roberta-base": "RoBERTa",
            "all-MiniLM-L6-v2": "Sentence-BERT",
        }

        loadable = {}
        failed = {}

        for model_name, display_name in models.items():
            try:
                from transformers import AutoTokenizer

                AutoTokenizer.from_pretrained(model_name)
                loadable[display_name] = model_name
            except Exception as e:
                failed[display_name] = str(e)

        success = len(failed) == 0
        return success, {"loadable": loadable, "failed": failed}

    def check_fastapi_server(self) -> Tuple[bool, str]:
        """Check if FastAPI server can start."""
        try:
            # Try to import main app
            import sys
            from pathlib import Path

            backend_path = Path(__file__).parent.parent
            sys.path.insert(0, str(backend_path))

            from main import app

            return True, "FastAPI app loaded successfully ✓"
        except Exception as e:
            return False, f"FastAPI app load failed: {e}"

    def check_config_files(self) -> Tuple[bool, Dict]:
        """Check if required config files exist."""
        backend_path = Path(__file__).parent.parent
        required_files = {
            "requirements.txt": backend_path / "requirements.txt",
            "trusted_sources.json": backend_path / "config" / "trusted_sources.json",
            ".env.example": backend_path / ".env.example",
        }

        existing = {}
        missing = []

        for name, path in required_files.items():
            if path.exists():
                existing[name] = str(path)
            else:
                missing.append(name)

        success = len(missing) == 0
        return success, {"existing": existing, "missing": missing}

    def check_disk_space(self) -> Tuple[bool, str]:
        """Check available disk space."""
        try:
            import shutil

            total, used, free = shutil.disk_usage("/")
            free_gb = free / (1024 ** 3)

            if free_gb > 10:
                return True, f"Disk space: {free_gb:.1f} GB free ✓"
            elif free_gb > 1:
                return False, f"Low disk space: {free_gb:.1f} GB free"
            else:
                return False, "Critical disk space: < 1 GB free"
        except Exception as e:
            return False, f"Disk check failed: {e}"

    def check_api_endpoints(self) -> Tuple[bool, Dict]:
        """Check if API endpoints are properly defined."""
        try:
            import sys
            from pathlib import Path

            backend_path = Path(__file__).parent.parent
            sys.path.insert(0, str(backend_path))

            from main import app

            endpoints = [
                str(route.path) for route in app.routes if hasattr(route, "path")
            ]
            return True, {"endpoints": endpoints, "count": len(endpoints)}
        except Exception as e:
            return False, f"API check failed: {e}"

    def run_all_checks(self) -> Dict:
        """Run all health checks."""
        print("\n" + "=" * 60)
        print("TruthLens AI - System Health Check")
        print("=" * 60 + "\n")

        # Python version
        status, msg = self.check_python_version()
        print(f"{'✓' if status else '✗'} Python Version: {msg}")
        self.checks["python_version"] = (status, msg)

        # Required packages
        status, details = self.check_required_packages()
        print(f"\n{'✓' if status else '✗'} Required Packages:")
        for pkg, version in list(details["installed"].items())[:10]:
            print(f"    ✓ {pkg}: {version}")
        if details["installed"] and len(details["installed"]) > 10:
            print(f"    ... and {len(details['installed']) - 10} more")
        if details["missing"]:
            print(f"    ✗ Missing: {', '.join(details['missing'][:5])}")
            if len(details["missing"]) > 5:
                print(f"      ... and {len(details['missing']) - 5} more")
        self.checks["required_packages"] = (status, details)

        # GPU check
        status, msg = self.check_pytorch_gpu()
        print(f"\n{'✓' if status else '~'} GPU: {msg}")
        self.checks["pytorch_gpu"] = (status, msg)

        # Database
        status, msg = self.check_database_connection()
        print(f"{'✓' if status else '~'} Database: {msg}")
        self.checks["database"] = (status, msg)

        # Redis
        status, msg = self.check_redis_connection()
        print(f"{'✓' if status else '~'} Redis: {msg}")
        self.checks["redis"] = (status, msg)

        # Tesseract OCR
        status, msg = self.check_tesseract_ocr()
        print(f"{'✓' if status else '✗'} Tesseract OCR: {msg}")
        self.checks["tesseract_ocr"] = (status, msg)

        # ML Models
        status, details = self.check_ml_models()
        print(f"\n{'✓' if status else '✗'} ML Models:")
        for model, path in details["loadable"].items():
            print(f"    ✓ {model}")
        if details["failed"]:
            for model, error in details["failed"].items():
                print(f"    ✗ {model}: {error[:50]}...")
        self.checks["ml_models"] = (status, details)

        # FastAPI
        status, msg = self.check_fastapi_server()
        print(f"\n{'✓' if status else '✗'} FastAPI Server: {msg}")
        self.checks["fastapi_server"] = (status, msg)

        # Config files
        status, details = self.check_config_files()
        print(f"{'✓' if status else '✗'} Config Files:")
        for name in details["existing"]:
            print(f"    ✓ {name}")
        if details["missing"]:
            print(f"    ✗ Missing: {', '.join(details['missing'])}")
        self.checks["config_files"] = (status, details)

        # Disk space
        status, msg = self.check_disk_space()
        print(f"\n{'✓' if status else '⚠'} Disk Space: {msg}")
        self.checks["disk_space"] = (status, msg)

        # API Endpoints
        status, details = self.check_api_endpoints()
        print(f"{'✓' if status else '✗'} API Endpoints: {details.get('count', 0)} endpoints")
        if status and details.get("endpoints"):
            for endpoint in list(details["endpoints"])[:5]:
                print(f"    ✓ {endpoint}")
            if len(details["endpoints"]) > 5:
                print(f"    ... and {len(details['endpoints']) - 5} more")
        self.checks["api_endpoints"] = (status, details)

        # Summary
        print("\n" + "=" * 60)
        all_passed = all(check[0] for check in self.checks.values())
        if all_passed:
            print("✓ All critical checks passed!")
        else:
            print("⚠ Some checks failed or warned - see details above")
        print("=" * 60 + "\n")

        return {
            "all_passed": all_passed,
            "checks": {
                name: {"status": status, "details": details}
                for name, (status, details) in self.checks.items()
            },
        }


if __name__ == "__main__":
    checker = SystemHealthCheck()
    results = checker.run_all_checks()
    sys.exit(0 if results["all_passed"] else 1)
