import os
import shutil
import argparse


def main(input_folder, output_folder):
    for filename in os.listdir(input_folder):
        username = filename[:-10]

        filepath = os.path.join(input_folder, filename)
        if os.path.isfile(filepath):    
            output_path = os.path.join(output_folder, username)
            os.makedirs(output_path, exist_ok=True)
            shutil.move(filepath, output_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                description='Reorganize photos into folders by user')

    parser.add_argument('-i', '--input_folder', default='.')
    parser.add_argument('-o', '--output_folder', default='.')

    args = parser.parse_args()
    main(args.input_folder, args.output_folder)