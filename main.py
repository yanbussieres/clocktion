from datetime import datetime
from notion.block import TodoBlock
import re

import requests
from flask import Flask, request
import urllib.request
import json
from notion.client import NotionClient


app = Flask(__name__)

CLIENT = NotionClient(
    token_v2= < YOURAPITOKEN > )


@app.route('/', methods=['POST', 'GET'])
def home():
    return "Clocktion, Braver"


@app.route('/receive/timer_stop', methods=['POST'])
def receive():
    data = request.get_json()
    # clockify format looks like this : 'PT16H50M43S'
    cardboard_related = data.get('project')

    if cardboard_related:
        duration_clockify = data['project']['duration']
        cardboard_title = data['project']['name']
        description = data['description']
        duration_hh_mm_ss = re.findall(r'\d+', duration_clockify)

        if len(duration_hh_mm_ss) == 3:
            duration_hh = int(
                duration_hh_mm_ss[0]) + int(duration_hh_mm_ss[1])/60
        elif len(duration_hh_mm_ss) == 2:
            duration_hh = int(duration_hh_mm_ss[0])/60

        cv = CLIENT.get_collection_view(
            < 'URI_TO_BOARD_YOU_WANT_TO_MODIFY' > )

        # TODO: Querying all the cards from the collection view. We could reduce workload by having this info in a DB
        result = cv.default_query().execute()

        is_board_exists = False
        for row in result:
            if cardboard_title.startswith(row.name) and row.name is not "":
                is_board_exists = True
                board_id = row.id
                _update_board_time_tracking(board_id, duration_hh)
                _update_board_description(board_id, description)

        if not is_board_exists:
            # TODO: Create a card in the board OR send an email and remind to associate time With Project
            pass

    return "board has been updated"


def _update_board_time_tracking(board_id, duration_hh):
    page = CLIENT.get_block(board_id)
    page.temps = duration_hh


def _update_board_description(board_id, description):
    datetime_now = datetime.now().strftime("%d/%m/%y, %Hh:%Mm")
    page = CLIENT.get_block(board_id)
    if description != "":
        new_child = page.children.add_new(
            TodoBlock, title=f'SubTask done on: {datetime_now}, :{description}')
    else:
        new_child = page.children.add_new(
            TodoBlock, title=f'SubTask done on: {datetime_now} with NO description... please be a gentleman and track your time correctly ^^')


if __name__ == '__main__':
    app.run()
