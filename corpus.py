import os

class CorpusGen:
    def __init__(self, initial_folder: str, generated_folder: str):
        self.initial_folder = initial_folder
        self.generated_folder = generated_folder

    def find_matched_segments(self):
        """Yield paths of matched segment files."""
        initial_files = {f: os.path.join(self.initial_folder, f) for f in os.listdir(self.initial_folder) if f.startswith('segment_') and f.endswith('.txt')}
        
        for initial_file in initial_files:
            segment_number = initial_file.split('_')[1].split('.')[0]
            generated_file = f'gen_segment_{segment_number}.txt'
            generated_file_path = os.path.join(self.generated_folder, generated_file)

            if os.path.exists(generated_file_path):
                print('CorpusGen found similar files:')
                print(f'  Initial: {initial_file}')
                print(f'  Generated: {generated_file}')
                yield initial_files[initial_file], generated_file_path
