import argparse
import requests
import re
import os


def getQueryId(http_page):
    base = 'https://www.instagram.com/'
    pattern = r'static/bundles/base/ProfilePageContainer\.js/.*?\.js'

    js_url = re.search(pattern, http_page).group(0)

    r = requests.get(base + js_url)
    if r.status_code == 200:
        js_code = r.content.decode('utf-8')
        return re.search(r'queryId:"(.*?)"', js_code).group(1)
    else:
        r.raise_for_status()


def main(username, n, resolution, output_dir):
    user_dir = os.path.join(output_dir, username)
    url = 'https://instagram.com/{}/'.format(username)
    pattern = (r'"src":"([^"]*?.jpg)"'
               '\,"config_width":{0}'
               '\,"config_height":{0}'.format(resolution))

    os.makedirs(user_dir, exist_ok=True)

    r = requests.get(url)
    if r.status_code == 200:
        http_page = r.content.decode('utf-8')

        # queryId = getQueryId(http_page)
        # id = re.search(r'"id":"(.*?)"', http_page).group(1)
        # after = re.search(r'"end_cursor":"(.*?)"', http_page).group(1)

        # variables = '{{"id":"{}","first":{},"after":"{}"}}'.format(id, n,
        #                                                            after)
        # params = {'query_hash': queryId,
        #           'variables': variables}
        # imgs_r = requests.get('https://www.instagram.com/graphql/query',
        #                       params=params,
        #                       cookies=r.cookies)

        # print(imgs_r.url)
        # print(imgs_r.status_code)
        # print(imgs_r.content.decode('utf-8'))
        # return 3

        matches = re.findall(pattern, http_page)
        n = min(n, len(matches))
        for i, img_url in enumerate(matches[:n]):
            print('Downloading [{}\{}]'.format(i, n))

            img_r = requests.get(img_url)
            with open(os.path.join(user_dir,
                                   '{}.jpg'.format(i)), 'wb') as f:
                f.write(img_r.content)
    else:
        r.raise_for_status()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download specified'
                                                 'users photos.')

    parser.add_argument('username')
    parser.add_argument('-n', '--photos_num', default=100, type=int,
                        help='Number of photos to be downloaded'
                        '(default: 100)')
    parser.add_argument('-r', '--photos_resolution', default=640, type=int,
                        help='Resolution of photos (default: 640)')
    parser.add_argument('-o', '--output_dir', default='.')

    args = parser.parse_args()
    main(args.username, args.photos_num, args.photos_resolution,
         args.output_dir)
