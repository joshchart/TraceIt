from datetime import datetime
from locust import FastHttpUser, task, between 
import random
import time

class FastAPIUser(FastHttpUser):
    wait_time = between(3, 7)
    
    def on_start(self):
        self.device_id = self.register_device()
        if self.device_id:
            self.update_device_location() 
            time.sleep(2)  # Adding a delay to ensure the location update is processed


    def register_device(self):
        # Helper function to register a device and return the device ID 
        device_data = {"user_id": f"user-{random.randint(1, 1000)}", "device_name": f"Device-{random.randint(1, 1000)}"}
        response = self.client.post("/api/v1/devices", json=device_data)
        if response.status_code == 201:
            device_id = response.json()['device_id']
            return device_id
        else:
            print(f"Failed to register device: {response.status_code} - {response.text}")
            return None

    @task
    def update_device_location(self):
        if self.device_id:
            location_data = {
                "latitude": random.uniform(-90, 90),
                "longitude": random.uniform(-180, 180),
                "timestamp": datetime.now().isoformat()
            }
            response = self.client.post(f"/api/v1/devices/{self.device_id}/locations", json=location_data)
            if response.status_code != 200:
                print(f"Failed to update location: {response.status_code} - {response.text}")
                return None
        else:
            print("No device ID available.")

    @task
    def get_current_location(self):
        if self.device_id:
            response = self.client.get(f"/api/v1/devices/{self.device_id}/location")
            if response.status_code != 200:
                print(f"Failed to get current location: {response.status_code} - {response.text}")
        else:
            print("No device ID available.")

    @task 
    def get_device_info(self):
        if self.device_id:
            response = self.client.get(f"/api/v1/devices/{self.device_id}")
            if response.status_code != 200:
                print(f"Failed to get device info: {response.status_code} - {response.text}")
        else:
            print("No device ID available.")

    @task
    def list_devices(self):
        response = self.client.get(f"/api/v1/devices")
        if response.status_code != 200:
            print(f"Failed to list devices: {response.status_code} - {response.text}")
