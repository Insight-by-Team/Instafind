import requests
import json
from time import sleep

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


def search_users(country_id, city_id, age, access_token, count=1000):
    params = {'q': '', 'count': count, 'fields': 'connections',
              'country': country_id, 'city': city_id,
              'age_from': age, 'age_to': age}

    r = make_request('users.search', params, access_token)
    print(r.status_code)

    users = json.loads(r.content.decode('utf-8'))['response']['items']

    return users


def main():
    with open('data/token') as f:
        access_token = f.readline()

    countries = ['1', '2', '3']  # ru, ua, by
    con_cities = []
    for c in ['ru', 'ua', 'by']:
        with open('data/{}_cities.json'.format(c)) as f:
            cities = json.load(f)['response']['items']
            con_cities.append(cities)

    all_victims = []
    for i, country_id in enumerate(countries):
        for city in con_cities[i]:
            city_id = city['id']
            print(city['title'])

            for age in range(15, 31):
                print(age, end=' ')
                sleep(1)
                users = search_users(country_id, city_id, age, access_token)

                instausers = list(filter(lambda x: 'instagram' in x.keys(),
                                         users))

                filename = 'instausers/{}_{}_{}.json'.format(country_id,
                                                             city_id,
                                                             age)
                with open(filename, 'w') as f:
                    json.dump(instausers, f)

                print(len(instausers))
                all_victims += instausers

    with open('instausers/all.json', 'w') as f:
        json.dump(all_victims, f)


if __name__ == '__main__':
    main()
