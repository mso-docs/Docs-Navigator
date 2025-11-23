#!/usr/bin/env python3
"""
OCR Installation Helper Script

This script helps install and configure OCR dependencies for the docs-navigator project.
"""

import subprocess
import sys
import os
import platform
from pathlib import Path

def run_command(cmd, description):
    """Run a command and show the result."""
    print(f"\n🔧 {description}")
    print(f"📝 Running: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ Success!")
            if result.stdout.strip():
                print(f"📄 Output: {result.stdout.strip()}")
            return True
        else:
            print("❌ Failed!")
            if result.stderr.strip():
                print(f"❗ Error: {result.stderr.strip()}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Command timed out!")
        return False
    except Exception as e:
        print(f"❌ Error running command: {e}")
        return False


def install_python_packages():
    """Install Python OCR packages with user choice."""
    print("\n📦 Installing Python OCR packages...")
    
    print("\n🤔 Choose your OCR installation option:")
    print("1. 🚀 Easy Setup (Pure Python - EasyOCR + TrOCR) - Recommended")
    print("2. ⚡ Performance Setup (Tesseract + EasyOCR backup)")
    print("3. 🎯 Complete Setup (All OCR backends)")
    print("4. 📋 Basic Setup (Tesseract only - requires manual installation)")
    
    choice = input("\nEnter your choice (1-4) [1]: ").strip() or "1"
    
    if choice == "1":
        # Pure Python setup - works without external dependencies
        packages = [
            "easyocr>=1.7.0",
            "transformers>=4.25.0", 
            "torch>=1.13.0",
            "pdf2image>=1.16.3",
            "Pillow>=10.0.0"
        ]
        print("\n✨ Installing Pure Python OCR (no external dependencies needed)...")
        
    elif choice == "2":
        # Performance setup with backup
        packages = [
            "pytesseract>=0.3.10",
            "easyocr>=1.7.0",
            "pdf2image>=1.16.3",
            "Pillow>=10.0.0"
        ]
        print("\n⚡ Installing Performance Setup (will need Tesseract, but has EasyOCR backup)...")
        
    elif choice == "3":
        # Complete setup
        packages = [
            "pytesseract>=0.3.10",
            "easyocr>=1.7.0", 
            "transformers>=4.25.0",
            "torch>=1.13.0",
            "pdf2image>=1.16.3",
            "Pillow>=10.0.0"
        ]
        print("\n🎯 Installing Complete OCR Setup (all backends)...")
        
    elif choice == "4":
        # Basic Tesseract only
        packages = [
            "pytesseract>=0.3.10",
            "pdf2image>=1.16.3", 
            "Pillow>=10.0.0"
        ]
        print("\n📋 Installing Basic Setup (Tesseract only)...")
        
    else:
        print("❌ Invalid choice, using Easy Setup...")
        packages = [
            "easyocr>=1.7.0",
            "transformers>=4.25.0", 
            "torch>=1.13.0",
            "pdf2image>=1.16.3",
            "Pillow>=10.0.0"
        ]
    
    for package in packages:
        success = run_command(
            f"{sys.executable} -m pip install {package}",
            f"Installing {package}"
        )
        if not success:
            print(f"⚠️ Failed to install {package}")
            return False
    
    return True


def test_python_imports():
    """Test that Python packages can be imported."""
    print("\n🧪 Testing Python package imports...")
    
    packages_to_test = [
        ("PIL", "from PIL import Image"),
        ("pdf2image", "from pdf2image import convert_from_path"),
        ("pytesseract", "import pytesseract"),
        ("easyocr", "import easyocr"),
        ("transformers", "import transformers"),
        ("torch", "import torch")
    ]
    
    available_backends = []
    for name, import_cmd in packages_to_test:
        try:
            exec(import_cmd)
            print(f"✅ {name}: OK")
            if name in ['pytesseract', 'easyocr', 'transformers']:
                available_backends.append(name)
        except ImportError as e:
            print(f"⚠️ {name}: Not available - {e}")
    
    if available_backends:
        print(f"\n🎉 Available OCR backends: {', '.join(available_backends)}")
        return True
    else:
        print("\n❌ No OCR backends available")
        return False


def detect_tesseract():
    """Try to detect Tesseract installation."""
    print("\n🔍 Detecting Tesseract OCR engine...")
    
    # Try common locations
    possible_paths = []
    
    if platform.system() == "Windows":
        possible_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            r"C:\Users\{}\AppData\Local\Tesseract-OCR\tesseract.exe".format(os.getenv('USERNAME', '')),
        ]
    
    # Check PATH first
    if run_command("tesseract --version", "Testing Tesseract in PATH"):
        print("✅ Tesseract found in system PATH")
        return True
    
    # Check common installation paths
    for path in possible_paths:
        if os.path.exists(path):
            print(f"✅ Found Tesseract at: {path}")
            # Set for pytesseract
            try:
                import pytesseract
                pytesseract.pytesseract.tesseract_cmd = path
                print("✅ Configured pytesseract to use found installation")
                return True
            except ImportError:
                print("⚠️ Found Tesseract but pytesseract not available")
                
    print("❌ Tesseract not found")
    return False


def show_installation_instructions():
    """Show platform-specific installation instructions."""
    system = platform.system()
    
    print(f"\n💡 Tesseract Installation Instructions for {system}:")
    print("=" * 60)
    
    if system == "Windows":
        print("""
🪟 Windows Installation:

Option 1 - Direct Download:
1. Go to: https://github.com/UB-Mannheim/tesseract/wiki
2. Download the latest Windows installer
3. Run the installer (make sure to check 'Add to PATH' option)
4. Restart your command prompt/IDE

Option 2 - Chocolatey:
choco install tesseract

Option 3 - Conda:
conda install -c conda-forge tesseract

Option 4 - Scoop:
scoop install tesseract
""")
    
    elif system == "Darwin":  # macOS
        print("""
🍎 macOS Installation:

Option 1 - Homebrew (recommended):
brew install tesseract
brew install poppler  # For PDF processing

Option 2 - MacPorts:
sudo port install tesseract-<version>

Option 3 - Conda:
conda install -c conda-forge tesseract
""")
    
    elif system == "Linux":
        print("""
🐧 Linux Installation:

Ubuntu/Debian:
sudo apt-get update
sudo apt-get install tesseract-ocr
sudo apt-get install poppler-utils  # For PDF processing

CentOS/RHEL/Fedora:
sudo yum install tesseract  # or dnf install tesseract
sudo yum install poppler-utils

Arch Linux:
sudo pacman -S tesseract
sudo pacman -S poppler

Or use conda:
conda install -c conda-forge tesseract
""")
    
    else:
        print(f"""
❓ Unknown system: {system}

General instructions:
1. Install Tesseract OCR for your operating system
2. Make sure 'tesseract' command is available in PATH
3. For PDF support, also install poppler-utils
4. Test with: tesseract --version
""")


def test_full_ocr_setup():
    """Test the complete OCR setup with enhanced processor."""
    print("\n🚀 Testing Enhanced OCR Setup...")
    
    try:
        # Test enhanced OCR processor
        try:
            from enhanced_ocr_processor import get_ocr_status
            status = get_ocr_status()
        except ImportError:
            # Fallback to original OCR processor
            from ocr_processor import get_ocr_status
            status = get_ocr_status()
        
        print("📊 OCR Status:")
        print(f"  Available: {status['available']}")
        
        if status['available']:
            if 'available_backends' in status:
                print(f"  Available backends: {status['available_backends']}")
                if 'active_backend' in status:
                    print(f"  Active backend: {status['active_backend']}")
            
            print(f"  Supported formats: {status.get('supported_formats', ['pdf'] + ['.png', '.jpg', '.jpeg'])}")
            
            if 'tesseract_version' in status:
                print(f"  Tesseract version: {status['tesseract_version']}")
            
            print("✅ OCR setup is complete and working!")
            return True
        else:
            print(f"  Error: {status.get('error', 'Unknown error')}")
            print("❌ OCR setup incomplete")
            
            if 'installation_help' in status:
                print("\n💡 Installation Help:")
                print(status['installation_help'])
            
            return False
            
    except Exception as e:
        print(f"❌ Error testing OCR setup: {e}")
        return False


def create_test_image():
    """Create a simple test image for OCR testing."""
    print("\n🖼️ Creating test image for OCR...")
    
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a simple test image
        img = Image.new('RGB', (400, 200), color='white')
        draw = ImageDraw.Draw(img)
        
        # Try to use default font
        try:
            # Try to load a better font if available
            if platform.system() == "Windows":
                font = ImageFont.truetype("arial.ttf", 20)
            else:
                font = ImageFont.load_default()
        except:
            font = ImageFont.load_default()
        
        # Draw test text
        test_text = "OCR Test Document\n\nThis is a sample text for testing\nOptical Character Recognition.\n\nNumbers: 12345\nSymbols: !@#$%"
        
        lines = test_text.split('\n')
        y = 20
        for line in lines:
            draw.text((20, y), line, fill='black', font=font)
            y += 25
        
        # Save test image
        docs_dir = Path(__file__).parent.parent / "docs"
        test_image_path = docs_dir / "ocr_test_sample.png"
        img.save(test_image_path)
        
        print(f"✅ Created test image: {test_image_path.name}")
        return True
        
    except Exception as e:
        print(f"❌ Error creating test image: {e}")
        return False


def main():
    """Main installation workflow."""
    print("🚀 OCR Installation Helper")
    print("=" * 50)
    
    print("This script will help you install OCR dependencies for docs-navigator.")
    print("\nSteps:")
    print("1. Install Python packages")
    print("2. Detect/Install Tesseract OCR engine") 
    print("3. Test the complete setup")
    
    input("\nPress Enter to continue...")
    
    # Step 1: Install Python packages
    print("\n" + "="*50)
    print("📦 Step 1: Installing Python packages")
    if not install_python_packages():
        print("❌ Failed to install Python packages")
        return
    
    if not test_python_imports():
        print("❌ Python package imports failed")
        return
    
    # Step 2: Detect Tesseract
    print("\n" + "="*50)
    print("🔍 Step 2: Detecting Tesseract OCR")
    if not detect_tesseract():
        show_installation_instructions()
        print("\n⚠️ Please install Tesseract OCR manually and run this script again.")
        print("💡 Or run: python tests/test_ocr.py to test your setup")
        return
    
    # Step 3: Test complete setup
    print("\n" + "="*50)
    print("🧪 Step 3: Testing complete setup")
    if test_full_ocr_setup():
        print("\n🎉 OCR installation completed successfully!")
        
        # Create test resources
        create_test_image()
        
        print("\n📚 Next steps:")
        print("1. Add image files (.png, .jpg, etc.) to docs/ folder")
        print("2. Add scanned PDF files to docs/ folder")
        print("3. Run: python app_gradio.py to start the interface")
        print("4. Test with: python tests/test_ocr.py")
        print("5. Ask OCR-related questions in the Gradio interface")
        
    else:
        print("\n❌ OCR setup verification failed")
        print("💡 Check the error messages above")
        print("🔧 You may need to install Tesseract OCR manually")


if __name__ == "__main__":
    main()