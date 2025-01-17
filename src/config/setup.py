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
        self.__load_optical_camera_configs()
        self.__load_obs_config()

    def __load_vicon(self):
        self.vicon_sdk_path = self.args['vicon_sdk_path']
        sys.path.append(self.vicon_sdk_path)
        self.vicon_package_paths = self.args['vicon_package_paths']
        for path in self.vicon_package_paths:
            sys.path.append(path)

    def __load_hotkeys(self):
        self.hotkeys = self.args.get('keys', {}) 
        self.start_key = self.hotkeys.get('start', 'default_start_key')  
        self.stop_key = self.hotkeys.get('stop', 'default_stop_key')  
        self.save_key = self.hotkeys.get('save', 'default_save_key')  
        self.battery_key = self.hotkeys.get('battery', 'default_battery_key')  
        self.quit_key = self.hotkeys.get('quit', 'default_quit_key')  
        # print(f"Start key: {self.start_key}, Stop key: {self.stop_key}, Save key: {self.save_key}, Battery key: {self.battery_key}, Quit key: {self.quit_key}")

    def __load_host_info(self):
        # Live Link Face
        self.llf_udp_ip = self.args['llf_udp_ip']
        self.llf_udp_port = self.args['llf_udp_port']
        # Local computer 
        self.target_ip = self.args['target_ip']
        self.target_port = self.args['target_port']
        self.receive_csv_port = self.args['receive_csv_port']
        self.receive_video_port = self.args['receive_video_port']

        self.tcp_iphone_port = self.args['tcp_iphone_port']
        self.controller_port = self.args['controller_port']
        self.shogun_hostname = self.args['shogun_hostname']
        self.shogun_port = self.args['shogun_port']

        self.websock_ip = self.args['websock_ip']
        self.websock_port = self.args['websock_port']

    def __load_paths(self):
        self.output_dir = self.args['output_dir']
        self.llf_csv_save_path = self.args['llf_save_path_csv']
        self.llf_video_save_path = self.args['llf_save_path_video']

    def __load_optical_camera_configs(self):
        self.camera_names = []
        self.camera_mic_names = []
        self.camera_save_paths = []
        # Check how many optical cameras there are and save them to the camera list

        cur_camera = 1
        while 'camera_name_' + str(cur_camera) in self.args:
            self.camera_names.append(self.args['camera_name_' + str(cur_camera)])
            self.camera_mic_names.append(self.args['camera_mic_name_' + str(cur_camera)])
            self.camera_save_paths.append(self.args['camera_save_path_' + str(cur_camera)])
            cur_camera += 1

    def __load_obs_config(self):
        self.obs_host = self.args['obs_host']
        self.obs_port = self.args['obs_port']
        self.obs_password = self.args.get('obs_password', None)
        self.obs_buffer_folder = self.args['obs_buffer_folder']
        self.obs_save_folder = self.args['obs_save_folder']

if __name__ == "__main__":
    reader = SetUp("config.yaml")
    