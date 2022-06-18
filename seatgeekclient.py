import requests
import config
import logging

class SeatGeekClient():
    key = None
    id = None
    base_url = 'http://api.seatgeek.com/2/'

    def __init__(self, client_id, api_key):
        self.key = api_key
        self.id = client_id
    
    def get_events(self, artists, location):
        return_dict = dict()
        for artist in artists:
            artist_stripped = artist.replace('&', '')
            artist_dashed = artist_stripped.replace(' ', '-')
            if location == None:
                request_url = self.base_url + 'events?performers.slug=' + artist_dashed + '&client_id=' + self.id
            else:
                request_url = self.base_url + 'events?performers.slug=' + artist_dashed + '&venue.city=' + location + '&client_id=' + self.id
            response = requests.get(request_url)
            response_json = response.json()
            if len(response_json['events']) > 0:
                return_dict[artist] = []
                for event in response_json['events']:
                    concert_info = dict()
                    concert_info['name'] = event['title']
                    concert_info['date'] = event['datetime_local']
                    concert_info['venue'] = event['venue']['name']
                    concert_info['city'] = event['venue']['city']
                    concert_info['state'] = event['venue']['state']
                    concert_info['url'] = event['url']
                    return_dict[artist].append(concert_info)
        return return_dict      