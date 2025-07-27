#!/bin/bash

echo "========================================"
echo "Nightingale 虚拟机部署脚本"
echo "========================================"

# 检测操作系统
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
else
    echo "不支持的操作系统: $OSTYPE"
    exit 1
fi

echo "检测到操作系统: $OS"

# 检查是否为 root 用户
if [[ $EUID -eq 0 ]]; then
    echo "警告: 不建议使用 root 用户运行此脚本"
    read -p "是否继续? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 系统依赖安装
echo "正在安装系统依赖..."

if [[ "$OS" == "linux" ]]; then
    # 检测 Linux 发行版
    if command -v apt-get &> /dev/null; then
        # Ubuntu/Debian
        echo "检测到 Ubuntu/Debian 系统"
        sudo apt-get update
        sudo apt-get install -y python3.8 python3.8-venv python3.8-dev
        sudo apt-get install -y build-essential libffi-dev libssl-dev
        sudo apt-get install -y curl wget git
        
        # 安装 Node.js 18
        curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
        sudo apt-get install -y nodejs
        
    elif command -v yum &> /dev/null; then
        # CentOS/RHEL
        echo "检测到 CentOS/RHEL 系统"
        sudo yum update -y
        sudo yum groupinstall -y "Development Tools"
        sudo yum install -y python3 python3-pip python3-devel
        sudo yum install -y libffi-devel openssl-devel
        sudo yum install -y curl wget git
        
        # 安装 Node.js 18
        curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
        sudo yum install -y nodejs
        
    else
        echo "不支持的 Linux 发行版"
        exit 1
    fi
fi

# 检查 Python 版本
echo "检查 Python 版本..."
python3 --version
if [[ $? -ne 0 ]]; then
    echo "错误: Python3 未安装或版本过低"
    exit 1
fi

# 检查 Node.js 版本
echo "检查 Node.js 版本..."
node --version
if [[ $? -ne 0 ]]; then
    echo "错误: Node.js 未安装或版本过低"
    exit 1
fi

# 升级 pip 和 setuptools
echo "升级 pip 和 setuptools..."
python3 -m pip install --upgrade pip setuptools wheel

# 创建项目目录
echo "创建项目目录..."
mkdir -p ~/nightingale
cd ~/nightingale

# 克隆项目（如果还没有）
if [ ! -d "Nightingale" ]; then
    echo "克隆项目..."
    git clone https://github.com/your-username/Nightingale.git
fi

cd Nightingale

# 设置后端环境
echo "设置后端环境..."
cd backend

# 创建虚拟环境
python3 -m venv venv_stableaudio
python3 -m venv venv_gemini

# 安装 Stable Audio 环境依赖
echo "安装 Stable Audio 环境依赖..."
source venv_stableaudio/bin/activate
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements-stable-audio.txt
deactivate

# 安装 Gemini 环境依赖
echo "安装 Gemini 环境依赖..."
source venv_gemini/bin/activate
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements-gemini-utf8.txt
deactivate

cd ..

# 设置前端环境
echo "设置前端环境..."
cd ambiance-weaver-react

# 安装前端依赖
npm install

# 配置环境变量
if [ ! -f ".env" ]; then
    echo "创建环境变量文件..."
    cp env.example .env
    
    # 获取虚拟机 IP
    VM_IP=$(hostname -I | awk '{print $1}')
    echo "检测到虚拟机 IP: $VM_IP"
    
    # 更新环境变量
    sed -i "s|http://localhost:8000|http://$VM_IP:8000|g" .env
    sed -i "s|http://localhost:8001|http://$VM_IP:8001|g" .env
    sed -i "s|http://localhost:3000|http://$VM_IP:3000|g" .env
    
    echo "环境变量已配置为使用虚拟机 IP: $VM_IP"
fi

cd ..

# 配置防火墙
echo "配置防火墙..."
if command -v ufw &> /dev/null; then
    # Ubuntu/Debian
    sudo ufw allow 8000
    sudo ufw allow 8001
    sudo ufw allow 3000
    sudo ufw allow 22
    sudo ufw --force enable
elif command -v firewall-cmd &> /dev/null; then
    # CentOS/RHEL
    sudo firewall-cmd --permanent --add-port=8000/tcp
    sudo firewall-cmd --permanent --add-port=8001/tcp
    sudo firewall-cmd --permanent --add-port=3000/tcp
    sudo firewall-cmd --reload
fi

echo ""
echo "========================================"
echo "✓ 虚拟机部署完成！"
echo "========================================"
echo ""
echo "下一步操作："
echo "1. 配置 API 密钥:"
echo "   cd backend"
echo "   cp env.example .env"
echo "   # 编辑 .env 文件，添加你的 API 密钥"
echo ""
echo "2. 启动服务:"
echo "   ./start_clean.bat  # Windows"
echo "   # 或手动启动各个服务"
echo ""
echo "3. 访问地址:"
echo "   前端: http://$VM_IP:3000"
echo "   Gemini API: http://$VM_IP:8000"
echo "   Stable Audio: http://$VM_IP:8001"
echo ""
echo "4. 生产环境建议:"
echo "   - 配置 SSL 证书"
echo "   - 设置 Nginx 反向代理"
echo "   - 配置域名解析"
echo "========================================" 