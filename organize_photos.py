import os
import shutil
import argparse
import numpy as np


def main(input_folder, output_folder):
    users = []
    for filename in os.listdir(input_folder):
        username = filename[:-10]

        filepath = os.path.join(input_folder, filename)
        if os.path.isfile(filepath):
            output_path = os.path.join(output_folder, username)
            os.makedirs(output_path, exist_ok=True)
            shutil.move(filepath, output_path)

            users.append([output_path, username])

    users = np.array(users)
    np.savetxt(os.path.join(output_folder, 'all.csv'),
               users, fmt='%s', delimiter=',')
    np.savetxt(os.path.join(output_folder, 'users.csv'),
               np.unique(users[:, 1]), fmt='%s')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                description='Reorganize photos into folders by user')

    parser.add_argument('-i', '--input_folder', default='.')
    parser.add_argument('-o', '--output_folder',
                        help='If not specified then as input_folder')
    args = parser.parse_args()

    if args.output_folder is None:
        args.output_folder = args.input_folder

    main(args.input_folder, args.output_folder)
