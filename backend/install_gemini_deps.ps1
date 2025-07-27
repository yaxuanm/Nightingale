# Gemini虚拟环境依赖安装脚本
# 使用方法: .\install_gemini_deps.ps1

Write-Host "🚀 开始安装Gemini虚拟环境依赖..." -ForegroundColor Green

# 检查是否在虚拟环境中
if (-not $env:VIRTUAL_ENV) {
    Write-Host "⚠️  警告: 未检测到虚拟环境，请先激活venv_gemini" -ForegroundColor Yellow
    Write-Host "运行: venv_gemini\Scripts\Activate.ps1" -ForegroundColor Cyan
    exit 1
}

Write-Host "✓ 虚拟环境已激活: $env:VIRTUAL_ENV" -ForegroundColor Green

# 升级pip
Write-Host "📦 升级pip..." -ForegroundColor Cyan
python -m pip install --upgrade pip

# 安装核心依赖
Write-Host "📦 安装核心依赖..." -ForegroundColor Cyan
pip install protobuf==4.25.8 numpy==2.2.6 fastapi==0.111.0 uvicorn==0.24.0

# 安装Google AI包
Write-Host "🤖 安装Google AI包..." -ForegroundColor Cyan
pip install google-generativeai==0.8.5 google-genai==1.24.0

# 安装数据库包
Write-Host "🗄️  安装数据库包..." -ForegroundColor Cyan
pip install supabase==2.17.0

# 安装音频处理包
Write-Host "🎵 安装音频处理包..." -ForegroundColor Cyan
pip install pydub==0.25.1 soundfile==0.13.1 librosa==0.11.0

# 安装AI/ML包
Write-Host "🧠 安装AI/ML包..." -ForegroundColor Cyan
pip install torch==2.7.1

# 安装工具包
Write-Host "🛠️  安装工具包..." -ForegroundColor Cyan
pip install python-dotenv==1.0.0 requests==2.32.4 pillow==11.3.0 tqdm==4.67.1

# 安装其他依赖
Write-Host "📚 安装其他依赖包..." -ForegroundColor Cyan
pip install aiohappyeyeballs==2.6.1 aiohttp==3.12.14 aiosignal==1.4.0 annotated-types==0.7.0 anyio==4.9.0 attrs==25.3.0 audioread==3.0.1 backports.tarfile==1.2.0 cachetools==5.5.2 certifi==2025.6.15 cffi==1.17.1 charset-normalizer==3.4.2 click==8.2.1 click-log==0.4.0 colorama==0.4.6 contourpy==1.3.2 cycler==0.12.1 decorator==5.2.1 deprecation==2.1.0 docutils==0.21.2 dotty-dict==1.3.1 edge-tts==7.0.2 filelock==3.18.0 fonttools==4.58.5 frozenlist==1.7.0 fsspec==2025.5.1 gitdb==4.0.12 GitPython==3.1.44 google-ai-generativelanguage==0.6.15 google-api-core==2.25.1 google-api-python-client==2.174.0 google-auth==2.40.3 google-auth-httplib2==0.2.0 googleapis-common-protos==1.70.0 gotrue==2.12.3 grpcio==1.73.1 grpcio-status==1.62.3 h11==0.16.0 httpcore==1.0.9 httplib2==0.22.0 httpx==0.28.1 idna==3.10 importlib_metadata==8.7.0 invoke==1.7.3 jaraco.classes==3.4.0 jaraco.context==6.0.1 jaraco.functools==4.2.1 Jinja2==3.1.6 joblib==1.5.1 keyring==25.6.0 kiwisolver==1.4.8 lazy_loader==0.4 llvmlite==0.44.0 MarkupSafe==3.0.2 matplotlib==3.10.3 more-itertools==10.7.0 mpmath==1.3.0 msgpack==1.1.1 multidict==6.6.3 networkx==3.5 nh3==0.2.21 noisereduce==3.0.3 numba==0.61.2 packaging==25.0 pkginfo==1.12.1.2 platformdirs==4.3.8 pooch==1.8.2 postgrest==1.1.1 propcache==0.3.2 proto-plus==1.26.1 pyasn1==0.6.1 pyasn1_modules==0.4.2 pycparser==2.22 pydantic==2.11.7 pydantic_core==2.33.2 Pygments==2.19.2 pyparsing==3.2.3 python-dateutil==2.9.0.post0 python-gitlab==3.15.0 python-multipart==0.0.20 python-semantic-release==7.33.2 pywin32-ctypes==0.2.3 readme_renderer==44.0 realtime==2.6.0 requests-toolbelt==1.0.0 rfc3986==1.5.0 rsa==4.9.1 scikit-learn==1.7.0 scipy==1.16.0 semver==2.13.0 setuptools==65.5.0 six==1.17.0 smmap==5.0.2 sniffio==1.3.1 soxr==0.5.0.post1 srt==3.5.3 starlette==0.37.2 storage3==0.12.0 StrEnum==0.4.15 supafunc==0.10.1 sympy==1.14.0 tabulate==0.9.0 tenacity==8.5.0 threadpoolctl==3.6.0 tomlkit==0.13.3 twine==3.8.0 typing_extensions==4.14.1 typing-inspection==0.4.1 uritemplate==4.2.0 urllib3==2.5.0 websockets==13.0 wheel==0.45.1 yarl==1.20.1 zipp==3.23.0

Write-Host "✅ 所有依赖安装完成！" -ForegroundColor Green
Write-Host "🧪 运行测试: python quick_test_gemini.py" -ForegroundColor Cyan 