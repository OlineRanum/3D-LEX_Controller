import sys
import yaml

class ViconReader:
    def __init__(self, config_path):
        with open(config_path, 'r') as file:
            self.config = yaml.safe_load(file)
        self.vicon_sdk_path = self.config['vicon_sdk_path']
        self.load_vicon()
        # Additional initialization code can go here

    # Example method to demonstrate access to the SDK path
    def load_vicon(self):
        sys.path.append(self.vicon_sdk_path)
        import vicon_dssdk

    # Add more methods to interact with the Vicon SDK

# Usage
if __name__ == "__main__":
    reader = ViconReader("config.yaml")
    