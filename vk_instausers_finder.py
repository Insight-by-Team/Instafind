import requests
import json
from time import sleep
from webprofile_manager import WebprofileManager


def make_request(method, params, access_token, v='5.75'):
    params['access_token'] = access_token
    params['v'] = v
    return requests.get('https://api.vk.com/method/{}'.format(method), params)


def get_instagrams(user_ids, access_token):
    params = {'user_ids': ', '.join(user_ids),
              'fields': 'connections'}
    r = make_request('users.get', params, access_token)

    responses = json.loads(r.content.decode('utf-8'))['response']

    return list(filter(lambda x: 'instagram' in x.keys(), responses))


def search_users(country_id, city_id, birth_year, sex,
                 access_token, count=1000):
    params = {'q': '', 'count': count, 'fields': 'connections',
              'country': country_id, 'city': city_id,
              'birth_year': birth_year, 'sex': sex}

    r = make_request('users.search', params, access_token)
    print(r.status_code)

    users = json.loads(r.content.decode('utf-8'))['response']['items']

    return users


def main():
    with open('data/token') as f:
        access_token = f.readline()[:-1]

    manager = WebprofileManager('data/webprofiles.json')

    countries = [['1', 'Russia'],
                 ['2', 'Ukraine'],
                 ['3', 'Belarus']]
    con_cities = []
    for c in ['ru', 'ua', 'by']:
        with open('data/{}_cities.json'.format(c)) as f:
            cities = json.load(f)['response']['items']
            con_cities.append(cities)

    for i, [country_id, country_title] in enumerate(countries):
        for city in con_cities[i]:
            city_id = city['id']
            print(city['title'])

            for b_year in range(1980, 2003):
                print(b_year, end=' ')

                for sex_id, sex_letter in [[1, 'w'], [2, 'm']]:
                    wait_secs = 5
                    sleep(wait_secs)
                    users = search_users(
                        country_id, city_id, b_year, sex_id, access_token)

                    while len(users) == 0:
                        print('Blocked.. Waiting {} seconds'.format(wait_secs))
                        sleep(wait_secs)
                        users = search_users(
                            country_id, city_id, b_year, sex_id, access_token)
                        wait_secs *= 2

                    instausers = list(filter(lambda x: 'instagram' in x.keys(),
                                             users))

                    for user in instausers:
                        manager.create_webprofile(user['id'],
                                                  user['instagram'],
                                                  country_title, city['title'],
                                                  b_year, sex_letter)
                    # filename = 'instausers/{}_{}_{}.json'.format(country_id,
                    #                                              city_id,
                    #                                              b_year)
                    # with open(filename, 'w') as f:
                    #     json.dump(instausers, f)

                    print(len(instausers))
                    manager.save_database()


if __name__ == '__main__':
    main()
