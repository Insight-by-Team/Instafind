import json


class WebprofileManager(object):
    """
    Implements CRUD for Webprofiles in json file.
    """

    def __init__(self, db_filename):
        """
        db_filename - json file with webprofiles
        """
        self.db_filename = db_filename

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
            'instaphotos': []
        }

        self.profiles.append(webprofile)
        return webprofile

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

        if post.likes != 0:
            likers = []
            for p in post.get_likes():
                likers.append(p.username)
                if len(likers) >= max_likers:
                    break
            instaphoto['liked_users'] = likers

        if post.comments != 0:
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

    def add_or_update_photo(self, webprofile, instaphoto):
        for i, photo in enumerate(webprofile['instaphotos']):
            if photo['shortcode'] == instaphoto['shortcode']:
                webprofile['instaphotos'][i] = instaphoto
                return

        webprofile['instaphotos'].append(instaphoto)

    def get_webprofile_by_instagram(self, instagram):
        for p in self.profiles:
            if p['instagram'] == instagram:
                return p

    def save_database(self, new_filename=None):
        if new_filename is not None:
            self.db_filename = new_filename

        with open(self.db_filename, 'w') as f:
            json.dump(self.profiles, f)
