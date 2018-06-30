import json
import os
from datetime import datetime


class WebprofileManager(object):
    """
    Implements CRUD for Webprofiles in json file.
    """

    def __init__(self, db_filename):
        """
        db_filename - json file with webprofiles
        """
        self.db_filename = db_filename

        if (os.path.exists(self.db_filename) and
                not os.path.isfile(self.db_filename)):
            raise Exception('{} is not file'.format(self.db_filename))

        try:
            with open(self.db_filename) as f:
                self.profiles = json.load(f)
        except FileNotFoundError:
            self.profiles = []

    def create_webprofile(self, vk_id, instagram,
                          country, city, birth_year, sex):
        webprofile = {
            'vk_id': int(vk_id),
            'instagram': instagram,
            'country': country,
            'city': city,
            'birth_year': birth_year,
            'sex': sex,
            'instaphotos': [],
            'vkphotos': []
        }

        self.profiles.append(webprofile)
        return webprofile

    def create_vkphoto(self, vk_id, photo_obj, photo_format, img_path):
        utc = datetime.utcfromtimestamp(photo_obj['date'])
        vkphoto = {
            'photo_id': photo_obj['id'],
            'shortcode': str(vk_id) + '_' + str(photo_obj['id']),
            'url': None,
            'img_path': img_path,
            'likes': photo_obj['likes']['count'],
            'year': utc.year,
            'month': utc.month
        }

        for s in photo_obj['sizes']:
            if s['type'] == photo_format:
                vkphoto['url'] = s['src']
                break

        return vkphoto

    def create_instaphoto(self, post, img_path,
                          max_comments=20, max_likers=20):
        instaphoto = {
            'shortcode': post.shortcode,
            'url': post.url,
            'img_path': img_path,
            'likes': post.likes,
            'year': post.date.year,
            'month': post.date.month,
        }

        if post.likes != 0 and max_likers > 0:
            print('Loading likers...')
            likers = []
            for p in post.get_likes():
                likers.append(p.username)
                if len(likers) >= max_likers:
                    break
            instaphoto['liked_users'] = likers

        if post.comments != 0 and max_comments > 0:
            print('Loading comments...')
            comments = []
            for c in post.get_comments():
                comments.append({'text': c.text,
                                 'username': c.owner.username
                                 })
                if len(comments) >= max_comments:
                    break

            instaphoto['comments'] = comments

        if post.caption is not None:
            instaphoto['caption'] = post.caption

        if post.caption_hashtags != []:
            instaphoto['hashtags'] = post.caption_hashtags

        loc = post.location
        if loc is not None:
            instaphoto['location'] = {'name': loc.slug,
                                      'lat': loc.lat,
                                      'lng': loc.lng
                                      }

        return instaphoto

    def add_or_update_photo(self, webprofile, new_photo, field):
        """
        field - can be 'instaphotos' or 'vkphotos'
        returns index of updated or -1 (last) if appended
        """
        assert field == 'instaphotos' or 'vkphotos', (
            'field can be only instaphotos or vkphotos')

        for i, photo in enumerate(webprofile[field]):
            if photo['shortcode'] == new_photo['shortcode']:
                webprofile[field][i] = new_photo
                return i

        webprofile[field].append(new_photo)
        return -1

    def get_webprofile_by_instagram(self, instagram):
        for p in self.profiles:
            if p['instagram'] == instagram:
                return p

    def save_database(self):
        if os.path.isfile(self.db_filename):
            with open(self.db_filename+'_new.json', 'w') as f:
                json.dump(self.profiles, f)

            os.rename(self.db_filename,
                      self.db_filename+'_old.json')

            os.rename(self.db_filename+'_new.json',
                      self.db_filename)
            os.remove(self.db_filename+'_old.json')
        else:
            with open(self.db_filename, 'w') as f:
                json.dump(self.profiles, f)
