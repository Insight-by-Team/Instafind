import argparse
import requests
import instaloader
import numpy as np
import os


def main(users_list_file, odir, skip_users, max_count=100):
    os.makedirs(odir, exist_ok=True)

    users = np.loadtxt(users_list_file, dtype=str)

    L = instaloader.Instaloader()
    for i, user in enumerate(users[skip_users:]):
        print('{} [{}\{}]'.format(user, i+1+skip_users, len(users)))
        try:
            profile = instaloader.Profile.from_username(L.context, user)
        except instaloader.ProfileNotExistsException:
            print('{} Not found'.format(user))
            continue

        downloaded = 0
        for post in profile.get_posts():
            if post.is_video:
                continue

            url = post.url
            r = requests.get(url)
            fname = os.path.join(odir, '{}_{:05d}.jpg'.format(user,
                                                              downloaded))
            with open(fname, 'wb') as f:
                f.write(r.content)

            downloaded += 1
            if downloaded >= max_count:
                break


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Downloads n images from users')

    parser.add_argument('users_path', help='path to file with users list')
    parser.add_argument('-n', '--photos_number', default=5, type=int,
                        help='count of photos to download')
    parser.add_argument('-o', '--output_dir', default='photos')
    parser.add_argument('-s', '--skip_first_users', default=0, type=int)

    args = parser.parse_args()

    main(args.users_path, args.output_dir, args.skip_first_users,
         args.photos_number)
