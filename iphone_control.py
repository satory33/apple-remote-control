import subprocess
import time
from typing import Optional
from flask import Flask, render_template, jsonify, request
import socket
import paramiko
from threading import Thread

class iPhoneController:
    def __init__(self, remote_host=None, remote_user=None, remote_password=None):
        self.device_id = None
        self.remote_host = remote_host
        self.remote_user = remote_user
        self.remote_password = remote_password
        self.ssh_client = None
        
    def connect_remote(self) -> bool:
        """Connect to remote server via SSH"""
        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh_client.connect(
                self.remote_host,
                username=self.remote_user,
                password=self.remote_password
            )
            print("SSH connection established")
            return True
        except Exception as e:
            print(f"SSH connection error: {e}")
            return False

    def execute_remote_command(self, command: str) -> tuple:
        """Execute command on remote server"""
        if not self.ssh_client:
            return None, "No SSH connection"
        try:
            stdin, stdout, stderr = self.ssh_client.exec_command(command)
            return stdout.read().decode(), stderr.read().decode()
        except Exception as e:
            return None, str(e)

    def get_device_id(self) -> Optional[str]:
        if self.remote_host:
            output, error = self.execute_remote_command('idevice_id -l')
            if output:
                devices = output.strip().split('\n')
                return devices[0] if devices and devices[0] else None
        else:
            result = subprocess.run(['idevice_id', '-l'], capture_output=True, text=True)
            if result.stdout:
                devices = result.stdout.strip().split('\n')
                return devices[0] if devices and devices[0] else None
        return None

    def get_device_info(self) -> dict:
        """Get device information"""
        try:
            if self.remote_host:
                output, error = self.execute_remote_command('ideviceinfo')
                if error:
                    return {'error': error}
                result_output = output
            else:
                result = subprocess.run(['ideviceinfo'], capture_output=True, text=True)
                result_output = result.stdout

            info = {}
            for line in result_output.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    clean_value = value.strip()
                    if clean_value and clean_value != "N/A":
                        info[key.strip()] = clean_value
                    
            sorted_info = {}
            priority_keys = [
                'DeviceName', 'ProductType', 'ProductVersion', 
                'BuildVersion', 'CPUArchitecture', 'HardwareModel',
                'DeviceColor', 'DeviceClass', 'UniqueDeviceID',
                'SerialNumber', 'WiFiAddress', 'BluetoothAddress'
            ]
            
            for key in priority_keys:
                if key in info:
                    sorted_info[key] = info[key]
            
            for key in sorted(info.keys()):
                if key not in sorted_info:
                    sorted_info[key] = info[key]
                    
            return sorted_info
        except Exception as e:
            print(f"Error getting device information: {e}")
            return {'error': str(e)}

    def get_battery_info(self) -> dict:
        """Get battery information"""
        try:
            if self.remote_host:
                output, error = self.execute_remote_command('ideviceinfo -q com.apple.mobile.battery')
            else:
                result = subprocess.run(['ideviceinfo', '-q', 'com.apple.mobile.battery'],
                                     capture_output=True, text=True)
                output = result.stdout
                error = result.stderr

            if error:
                return {'error': error}

            battery_info = {}
            for line in output.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    if key == 'BatteryCurrentCapacity':
                        battery_info['Battery Level'] = f"{value}%"
                    elif key == 'BatteryIsCharging':
                        battery_info['Charging'] = 'Yes' if value.lower() == 'true' else 'No'
                    elif key == 'ExternalConnected':
                        battery_info['Power Connected'] = 'Yes' if value.lower() == 'true' else 'No'
                    elif key == 'FullyCharged':
                        battery_info['Fully Charged'] = 'Yes' if value.lower() == 'true' else 'No'
                    else:
                        battery_info[key] = value

            return battery_info
        except Exception as e:
            return {'error': str(e)}

    def restart_device(self) -> bool:
        """Restart the device"""
        try:
            if self.remote_host:
                output, error = self.execute_remote_command('idevicediagnostics restart')
                return not error
            else:
                subprocess.run(['idevicediagnostics', 'restart'], check=True)
                return True
        except Exception as e:
            print(f"Error restarting device: {e}")
            return False

    def shutdown_device(self) -> bool:
        """Shutdown the device"""
        try:
            if self.remote_host:
                output, error = self.execute_remote_command('idevicediagnostics shutdown')
                return not error
            else:
                subprocess.run(['idevicediagnostics', 'shutdown'], check=True)
                return True
        except Exception as e:
            print(f"Error shutting down device: {e}")
            return False

    def get_network_info(self) -> dict:
        """Get network information"""
        try:
            if self.remote_host:
                output, error = self.execute_remote_command('ideviceinfo -q com.apple.mobile.wireless_lockdown')
            else:
                result = subprocess.run(['ideviceinfo', '-q', 'com.apple.mobile.wireless_lockdown'],
                                     capture_output=True, text=True)
                output = result.stdout
                error = result.stderr

            if error:
                return {'error': error}

            network_info = {}
            for line in output.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    network_info[key.strip()] = value.strip()

            return network_info
        except Exception as e:
            return {'error': str(e)}

# Flask application
app = Flask(__name__)
controller = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/connect', methods=['POST'])
def connect():
    global controller
    data = request.json
    controller = iPhoneController(
        remote_host=data.get('host'),
        remote_user=data.get('username'),
        remote_password=data.get('password')
    )
    success = controller.connect_remote()
    return jsonify({'success': success})

@app.route('/api/device_info')
def device_info():
    if controller:
        return jsonify(controller.get_device_info())
    return jsonify({'error': 'No connection'})

@app.route('/api/battery', methods=['GET'])
def battery_info():
    if not controller:
        return jsonify({'error': 'No connection'})
    return jsonify(controller.get_battery_info())

@app.route('/api/restart', methods=['POST'])
def restart():
    if not controller:
        return jsonify({'error': 'No connection'})
    success = controller.restart_device()
    return jsonify({
        'success': success,
        'error': 'Failed to restart device' if not success else None
    })

@app.route('/api/shutdown', methods=['POST'])
def shutdown():
    if not controller:
        return jsonify({'error': 'No connection'})
    success = controller.shutdown_device()
    return jsonify({
        'success': success,
        'error': 'Failed to shutdown device' if not success else None
    })

@app.route('/api/network', methods=['GET'])
def get_network():
    if not controller:
        return jsonify({'error': 'No connection'})
    return jsonify(controller.get_network_info())

def main():
    app.run(host='0.0.0.0', port=5000)

if __name__ == "__main__":
    main() 