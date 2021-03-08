import os
import json
import requests
from urllib.parse import quote

from scrapy.exporters import JsonItemExporter


PUSHBULLET_TOKEN = 'push bullet token here'
CHANNEL_TAG = 'channel tag here'


def send_sms(message, password=None):
    SEND_SMS_RO_URL_TEMPLATE = (
        'https://api.sendsms.ro/json?action=message_send&'
        'username=candale.andrei&'
        'password={}&'.format(password)
        'to={number}&'
        'text={message}&'
        'from=Candale'
    )

    people = (
        ('Person here', '0741234567'),
    )

    for name, phone_number in people:
        requests.get(
            SEND_SMS_RO_URL_TEMPLATE.format(number=phone_number, message=message))


class NonDuplicateItemExporter(JsonItemExporter):

    def __init__(self, file, **kwargs):
        if os.path.exists('uids.txt'):
            with open('uids.txt', 'r') as f:
                self.uids = list(map(lambda x: x.strip(), f))
        else:
            self.uids = []

        self.uids_file = open('uids.txt', 'a')
        super().__init__(file, **kwargs)

    def finish_exporting(self):
        self.uids_file.close()
        super().finish_exporting()

    def export_item(self, item):
        if item['uid'] in self.uids:
            return

        self.uids.append(item['uid'])
        self.uids_file.write(item['uid'] + '\n')

        body = f"""
Price: {item['price']}
Has backyard: {item['has_backyard']}
URL: {item['url']}
Description
===========
{item['description']}
"""

        response = requests.post(
            'https://api.pushbullet.com/v2/pushes',
            headers={
                'Access-Token': PUSHBULLET_TOKEN,
                'Content-Type': 'application/json',
            },
            data=json.dumps({
                'body': body,
                'title': '[{}] - {}'.format(item['price'], item['title']),
                'type': 'note',
                'channel_tag': CHANNEL_TAG
            })
        )

        if response.status_code != 200:
            print('ERROR PUSHBULLET: {}'.format(response.content.decode()))

        send_sms('[{}] - {}'.format(item['price'], item['url']))

        return super().export_item(item)
