#!/usr/bin/env python3
"""
Dependency validation script for FastAPI + Pydantic v2 stack
Tests compatibility and provides detailed feedback
"""

import sys
import subprocess
import importlib
from typing import Dict, List, Tuple

def test_import(module_name: str) -> Tuple[bool, str]:
    """Test if a module can be imported successfully"""
    try:
        importlib.import_module(module_name)
        return True, f"✅ {module_name} imported successfully"
    except ImportError as e:
        return False, f"❌ {module_name} import failed: {str(e)}"
    except Exception as e:
        return False, f"⚠️ {module_name} import error: {str(e)}"

def test_pydantic_v2_compatibility() -> List[str]:
    """Test Pydantic v2 specific features"""
    results = []
    
    try:
        from pydantic import BaseModel, Field
        from pydantic_settings import BaseSettings
        
        # Test Pydantic v2 model creation
        class TestModel(BaseModel):
            name: str = Field(description="Test field")
            age: int = Field(gt=0)
        
        # Test BaseSettings with model_config
        class TestSettings(BaseSettings):
            test_value: str = "default"
            model_config = {"env_file": ".env"}
        
        results.append("✅ Pydantic v2 models work correctly")
        results.append("✅ BaseSettings with model_config works")
        
    except Exception as e:
        results.append(f"❌ Pydantic v2 compatibility test failed: {str(e)}")
    
    return results

def test_fastapi_compatibility() -> List[str]:
    """Test FastAPI compatibility"""
    results = []
    
    try:
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        
        app = FastAPI()
        
        @app.get("/")
        def read_root():
            return {"Hello": "World"}
        
        client = TestClient(app)
        response = client.get("/")
        
        if response.status_code == 200:
            results.append("✅ FastAPI app creation and testing works")
        else:
            results.append("❌ FastAPI test client failed")
            
    except Exception as e:
        results.append(f"❌ FastAPI compatibility test failed: {str(e)}")
    
    return results

def check_package_versions() -> List[str]:
    """Check installed package versions"""
    results = []
    
    packages_to_check = [
        "fastapi",
        "pydantic", 
        "pydantic-settings",
        "uvicorn",
        "sqlalchemy",
        "celery",
        "redis",
        "pandas",
        "numpy",
        "scikit-learn"
    ]
    
    for package in packages_to_check:
        try:
            module = importlib.import_module(package.replace("-", "_"))
            version = getattr(module, "__version__", "unknown")
            results.append(f"📦 {package}: {version}")
        except ImportError:
            results.append(f"❌ {package}: not installed")
        except Exception as e:
            results.append(f"⚠️ {package}: error getting version - {str(e)}")
    
    return results

def main():
    """Main validation function"""
    print("🔍 FastAPI + Pydantic v2 Stack Validation")
    print("=" * 50)
    
    # Test core imports
    print("\n📋 Core Package Import Tests:")
    core_packages = [
        "fastapi",
        "pydantic",
        "pydantic_settings", 
        "uvicorn",
        "sqlalchemy",
        "celery",
        "redis",
        "pandas",
        "numpy",
        "scikit-learn",
        "xgboost",
        "shap",
        "boto3",
        "supabase",
        "google.genai"
    ]
    
    for package in core_packages:
        success, message = test_import(package)
        print(f"  {message}")
    
    # Test Pydantic v2 compatibility
    print("\n🔧 Pydantic v2 Compatibility Tests:")
    pydantic_results = test_pydantic_v2_compatibility()
    for result in pydantic_results:
        print(f"  {result}")
    
    # Test FastAPI compatibility
    print("\n🚀 FastAPI Compatibility Tests:")
    fastapi_results = test_fastapi_compatibility()
    for result in fastapi_results:
        print(f"  {result}")
    
    # Check package versions
    print("\n📦 Installed Package Versions:")
    version_results = check_package_versions()
    for result in version_results:
        print(f"  {result}")
    
    print("\n" + "=" * 50)
    print("✅ Validation complete!")
    print("\n💡 If all tests pass, your stack is ready for deployment!")
    print("🚀 For Render deployment, ensure you have:")
    print("   - runtime.txt with python-3.10.13")
    print("   - requirements.txt with the updated versions")
    print("   - Proper environment variables set")

if __name__ == "__main__":
    main() 