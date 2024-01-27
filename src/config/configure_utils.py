import sys
import yaml

class SetUp:
    def __init__(self, config_path):
        with open(config_path, 'r') as file:
            self.args = yaml.safe_load(file)
        self.vicon_sdk_path = self.args['vicon_sdk_path']
        self.hotkeys = self.args.get('keys', {}) 

        self.__load_vicon()
        self.__load_hotkeys()

    def __load_vicon(self):
        sys.path.append(self.vicon_sdk_path)

    def __load_hotkeys(self):
        self.start_key = self.hotkeys.get('start', 'default_start_key')  
        self.stop_key = self.hotkeys.get('stop', 'default_stop_key')  
        self.save_key = self.hotkeys.get('save', 'default_save_key')  
        print(f"Start key: {self.start_key}, Stop key: {self.stop_key}, Save key: {self.save_key}")


if __name__ == "__main__":
    reader = SetUp("config.yaml")
    