import argparse
import requests
import instaloader
import numpy as np
import os
from webprofile_manager import WebprofileManager


def main(login, passw, webprofile_path, odir, skip_users,
         max_posts=5, max_followers=20,
         max_comments=20, max_likers=20,
         stop_if_post_exists=False):

    manager = WebprofileManager(webprofile_path)

    # Login to instagram
    print('Login in..')
    L = instaloader.Instaloader(sleep=True)
    try:
        L.context.login(login, passw)
    except instaloader.ConnectionException:
        raise Exception('Failed to login')

    # Process each profile
    for i, p in enumerate(manager.profiles[skip_users:]):
        print('{} [{}\{}]'.format(p['instagram'], i+1+skip_users,
                                  len(manager.profiles)))

        # Load and check profile
        try:
            inst_profile = instaloader.Profile.from_username(
                L.context, p['instagram'])
        except instaloader.ProfileNotExistsException:
            print('{} not found'.format(p['instagram']))
            manager.profiles.remove(p)
            continue

        if inst_profile.is_private:
            print('{} private profile'.format(p['instagram']))
            manager.profiles.remove(p)
            continue

        # Create user dir
        user_dir = os.path.join(odir, p['instagram'])
        os.makedirs(user_dir, exist_ok=True)

        # Load followers
        print('Loading followers...')
        followers = []
        for f in inst_profile.get_followers():
            followers.append(f.username)
            if len(followers) >= max_followers:
                break
        p['instafollowers'] = followers

        # Load posts
        print('Loading posts...')
        downloaded = 0
        for post in inst_profile.get_posts():
            print('[{}\{}]'.format(downloaded,
                                   min(max_posts, inst_profile.mediacount)))
            if post.is_video:
                continue

            filename = '{}_{}.jpg'.format(p['instagram'], post.shortcode)
            img_path = os.path.join(user_dir, filename)
            instaphoto = manager.create_instaphoto(post, img_path,
                                                   max_comments)
            if (manager.add_or_update_photo(p, instaphoto) >= 0 and
                    stop_if_post_exists):
                print('Existing post encountered. Stop.')
                break

            r = requests.get(instaphoto['url'])
            with open(img_path, 'wb') as f:
                f.write(r.content)

            downloaded += 1
            if downloaded >= max_posts:
                break

        print('Saving webprofiles...')
        manager.save_database()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Downloads n images from users')

    parser.add_argument('webprofiles_path',
                        help='path to file with webprofiles')
    parser.add_argument('-u', '--username', required=True)
    parser.add_argument('-p', '--password', required=True)
    parser.add_argument('-mp', '--max_posts', default=5, type=int,
                        help='count of photos to download')
    parser.add_argument('-mf', '--max_followers', default=20, type=int)
    parser.add_argument('-mc', '--max_comments', default=20, type=int)
    parser.add_argument('-ml', '--max_likers', default=20, type=int)
    parser.add_argument('-spe', '--stop_if_post_exists',
                        default=False, action='store_true')
    parser.add_argument('-o', '--output_dir', default='photos')
    parser.add_argument('-s', '--skip_first_users', default=0, type=int)

    args = parser.parse_args()

    main(args.username, args.password,
         args.webprofiles_path, args.output_dir, args.skip_first_users,
         args.max_posts, args.max_followers,
         args.max_comments, args.max_likers,
         args.stop_if_post_exists)
