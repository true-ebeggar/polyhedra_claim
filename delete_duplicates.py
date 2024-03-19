import os

directory = os.path.dirname(os.path.abspath(__file__))

for filename in os.listdir(directory):
    if filename.endswith('.txt'):
        file_path = os.path.join(directory, filename)

        with open(file_path, 'r') as file:
            lines = file.readlines()

        unique_lines = list(dict.fromkeys(lines))
        with open(file_path, 'w') as file:
            file.writelines(unique_lines)

        print(f"Processed file: {filename}")

print("Duplicate lines removed from all text files.")