import os

class FileManager:
    def __init__(self):
        self.file_name = "filelist.txt"
        # Get the directory one level up from the current working directory
        parent_directory = os.path.dirname(os.getcwd())
        # Set the file path to the 'outputs' subdirectory within the parent directory
        self.file_path = os.path.join(parent_directory, "outputs", self.file_name)

        # Ensure the 'outputs' directory exists
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

        # Create the file at initialization
        with open(self.file_path, 'a') as file:
            pass  

    def save_gloss(self, gloss):
        with open(self.file_path, 'a') as file:
            file.write(gloss + '\n')
