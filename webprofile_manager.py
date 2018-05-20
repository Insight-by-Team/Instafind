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

    def create_instaphoto(self, shortcode, url, path, likes):
        instaphoto = {
            'shortcode': shortcode,
            'url': url,
            'path': path,
            'likes': likes
        }

        return instaphoto

    def get_webprofile_by_instagram(self, instagram):
        for p in self.profiles:
            if p['instagram'] == instagram:
                return p

    def save_database(self, new_filename=None):
        if new_filename is not None:
            self.db_filename = new_filename

        with open(self.db_filename, 'w') as f:
            json.dump(self.profiles, f)
