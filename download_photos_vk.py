import argparse
import requests
import vk
import numpy as np
import os
from time import sleep
from webprofile_manager import WebprofileManager


def trim_newline(x):
    if x.endswith("\r\n"):
        return x[:-2]
    if x.endswith("\n") or x.endswith("\r"):
        return x[:-1]
    return x


def main(token_file, webprofile_path, odir, skip_users, post_sleep,
         max_photos=5, photo_format='y'):

    manager = WebprofileManager(webprofile_path)
    profiles = manager.profiles[skip_users:]  # profiles to process

    with open(token_file) as f:
        access_token = trim_newline(f.read())
    session = vk.Session(access_token)
    vkapi = vk.API(session)

    max_requests = 25  # max requests by vkAPI in execute
    with open('./get_urls_template.vkscript') as f:
        code_template = f.read()

    for i in range(0, len(profiles), max_requests):
        batch_profs = profiles[i:i+max_requests]
        print('{} - {} [{}-{} / {}]'.format(batch_profs[0]['vk_id'],
                                            batch_profs[-1]['vk_id'],
                                            i + skip_users + 1,
                                            i + skip_users + 1 + max_requests,
                                            len(manager.profiles)))
        ids = [p['vk_id'] for p in batch_profs]
        photos = vkapi.execute(code=code_template.format(ids=ids,
                                                         n_photos=max_photos),
                               v=5.80)

        for p, p_photos in zip(batch_profs, photos):
            user_dir = os.path.join(odir, str(p['vk_id']))
            os.makedirs(user_dir, exist_ok=True)

            if 'vkphotos' not in p:
                p['vkphotos'] = []

            for photo in p_photos['items']:
                filename = '{}_{}.jpg'.format(p['vk_id'], photo['id'])
                img_path = os.path.join(user_dir, filename)
                vkphoto = manager.create_vkphoto(p['vk_id'],
                                                 photo, photo_format,
                                                 img_path)

                if vkphoto['url'] is None:
                    print('{} doesnt required size, skipped.'.format(
                        vkphoto['shortcode']))
                    continue

                photo_index = manager.add_or_update_photo(p, vkphoto,
                                                          'vkphotos')
                if (photo_index >= 0):
                    print('Existing photo encountered. Stop. {}'.format(
                        p['vk_id']))
                    break

                r = requests.get(vkphoto['url'])
                with open(img_path, 'wb') as f:
                    f.write(r.content)

        print('Saving webprofiles...')
        manager.save_database()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Downloads n images from users')

    parser.add_argument('webprofiles_path',
                        help='path to file with webprofiles')
    parser.add_argument('-tf', '--token_file', required=True)
    parser.add_argument('-mp', '--max_photos', default=5, type=int,
                        help='count of photos to download')
    parser.add_argument('-pf', '--photo_format',
                        choices=['s', 'm', 'x', 'o', 'p',
                                 'q', 'r', 'y', 'z', 'w'],
                        default='y',
                        help='Photo formats (smxopqryzw, default: y)')
    parser.add_argument('-ps', '--post_sleep', default=0.3, type=float,
                        help='Sleep time in seconds between posts '
                             '(default 0.3 by vkAPI)')
    parser.add_argument('-o', '--output_dir', default='photos')
    parser.add_argument('-s', '--skip_first_users', default=0, type=int)

    args = parser.parse_args()

    main(args.token_file,
         args.webprofiles_path, args.output_dir, args.skip_first_users,
         args.post_sleep,
         args.max_photos, args.photo_format)
