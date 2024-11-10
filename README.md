# 📱 iPhone Remote Control

A web-based application for controlling iOS devices remotely using libimobiledevice.

## ✨ Features
- 📱 Device information and details
- 🔋 Real-time battery status monitoring
- 🌐 Network information and statistics
- 🔄 Device restart and shutdown controls
- 🔒 Secure remote SSH connection

## 🛠️ Prerequisites
- Python 3.8 or higher
- libimobiledevice (required for iOS device communication)
- Git

### Installing libimobiledevice
#### On macOS:
```bash
brew install libimobiledevice
```

#### On Ubuntu/Debian:
```bash
sudo apt-get install libimobiledevice6 libimobiledevice-utils
```

#### On Windows:
Download and install from [libimobiledevice-windows](https://github.com/libimobiledevice-win32/imobiledevice-net)

## 🚀 Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/iphone-remote-control.git
cd iphone-remote-control
```

2. Create and activate virtual environment (recommended):
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

## 📱 Usage

1. Connect your iPhone via USB cable
2. Trust the computer on your iPhone if prompted
3. Run the application:
```bash
python iphone_control.py
```
4. Open your web browser and navigate to:
```
http://localhost:5000
```

## 🔧 Troubleshooting

### Common Issues:
- 🚫 **Device not detected**: Make sure your iPhone is properly connected and trusted
- ⚠️ **libimobiledevice errors**: Verify that libimobiledevice is correctly installed
- 🔒 **Permission issues**: Run with sudo/admin rights if necessary

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## ⭐ Support

If you find this project helpful, please give it a star!

