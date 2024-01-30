import os
import sys
import shutil

class FileManager:
    def __init__(self, output_dir):
        self.create_directory(output_dir)


    def save_gloss(self, gloss):
        with open(self.file_path, 'a') as file:
            file.write(gloss + '\n')

    def clean_dir(self, directory_path):
        try:
            for root, dirs, files in os.walk(directory_path, topdown=False):
                for file in files:
                    file_path = os.path.join(root, file)
                    os.remove(file_path)
                for dir in dirs:
                    dir_path = os.path.join(root, dir)
                    shutil.rmtree(dir_path)
            print(f"All files and subdirectories in '{directory_path}' have been removed.")
        except Exception as e:
            print(f"An error occurred: {e}")


    def create_directory(self, directory_path, subdir = False):
        """ Creates dir if does not exist
        """
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
            print(f"Directory '{directory_path}' created successfully.")
        else:
            if subdir:
                self.prompt_yes_no(directory_path)

 
    def prompt_yes_no(self, directory_path):
        while True:
            response = input(f"Directory already exist, delete old data (yes/no): ").lower().strip()
            if response in ['yes', 'no']:
                if response == 'yes':
                    self.clean_dir(directory_path)
                    print(f"Directory '{directory_path}' already exists, and has been cleaned.")
                elif response == 'no':
                    print('Please manage directory manually to not overwrite data')
                    exit()
            else:
                print("Please answer with 'yes' or 'no'.")