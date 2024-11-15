import sys
sys.path.append(r"C:\Program Files\Vicon\ShogunPost1.12\SDK\Win64")

try:
    import ViconShogunPostSDK
except ImportError as e:
    print(f"ImportError: {str(e)}")
    sys.exit(1)

# Define the class for connecting to Shogun Post
class ViconShogunPost(object):
    def __init__(self, address="localhost", port=805):
        self._Client = ViconShogunPostSDK.Client3.TheClient
        self.Connect(address, port)

    def __del__(self):
        if self._Client.IsConnected():
            self._Client.Disconnect()

    def Connect(self, address, port=805):
        if self._Client.IsConnected():
            self._Client.Disconnect()

        result = self._Client.Connect(address, port)
        if result.Error():  # This line might not be needed if Connect returns a boolean or similar
            raise ConnectionError("Failed to connect to Shogun Post.")

        if not self._Client.IsConnected():
            raise ConnectionError("Unable to connect to ShogunPost application.")

    def GetFrameCount(self):
        frame_count = self._Client.GetFrameCount()
        if frame_count is None:
            raise RuntimeError("Failed to get frame count.")
        return frame_count

    def OpenFile(self, path):
        result = self._Client.LoadFile(path)
        if not result:
            raise RuntimeError("Failed to open file.")
        return result
    
    def CloseFile(self):
        result = self._Client.NewScene()
        if result.Error():
            raise RuntimeError("Failed to close file.")
        return result
    
    def GetSceneName(self):
        result = self._Client.GetSceneName()
        if result.Error():
            raise RuntimeError("Failed to get scene name.")
        return result.Name.Value()
    
    def ExportFile(self, filePath):
        hsl = f"""select "Solving";
                SelectChildren_Add_All;
                saveFile -s "{filePath}";
                """
        return self._Client.HSL(hsl)
    
    def rotate180(self):
        hsl = """select "ValkyrieTest01";
                setTime 1;
                setKey "Rotation.Z" 180.000000 -onMod ValkyrieTest01;
                """
        return self._Client.HSL(hsl)
    
    def setPAL100(self):
        hsl = """setFrameRate "pal" 100.000000;"""
        return self._Client.HSL(hsl)

# # Example usage, setting pal
# shogun_post = ViconShogunPost()
# shogun_post.setPAL100()
