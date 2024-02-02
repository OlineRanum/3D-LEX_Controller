import sys
import yaml

class SetUp:
    def __init__(self, config_path):
        with open(config_path, 'r') as file:
            self.args = yaml.safe_load(file)
        
        self.__load_vicon()
        self.__load_hotkeys()
        self.__load_host_info()
        self.__load_paths()

    def __load_vicon(self):
        self.vicon_sdk_path = self.args['vicon_sdk_path']
        sys.path.append(self.vicon_sdk_path)

    def __load_hotkeys(self):
        self.hotkeys = self.args.get('keys', {}) 
        self.start_key = self.hotkeys.get('start', 'default_start_key')  
        self.stop_key = self.hotkeys.get('stop', 'default_stop_key')  
        self.save_key = self.hotkeys.get('save', 'default_save_key')  
        self.battery_key = self.hotkeys.get('battery', 'default_battery_key')  
        self.quit_key = self.hotkeys.get('quit', 'default_quit_key')  
        print(f"Start key: {self.start_key}, Stop key: {self.stop_key}, Save key: {self.save_key}, Battery key: {self.battery_key}, Quit key: {self.quit_key}")

    def __load_host_info(self):
        # Live Link Face
        self.llf_udp_ip = self.args['llf_udp_ip']
        self.llf_udp_port = self.args['llf_udp_port']
        # Local computer 
        self.target_ip = self.args['target_ip']
        self.target_port = self.args['target_port']

    def __load_paths(self):
        self.output_dir = self.args['output_dir']



if __name__ == "__main__":
    reader = SetUp("config.yaml")
    