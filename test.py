import requests
import json

BASE = 'https://api.hatchways.io/assessment/blog/posts'
BASE_API = 'http://localhost:5000'


def test_api(testing_text='history,tech', sortBy = 'likes', direction = 'desc'):

    response_ping = requests.get(BASE_API + '/api/ping')
    print('api/ping result:')
    print(json.loads(response_ping.text))

    if response_ping.status_code == 400:
            return 0

    if ',' in testing_text:
        tags = testing_text.split(',')
    else:
        tags = testing_text

    response = requests.get(BASE_API + '/api/posts', {'tags': testing_text, 'sortBy': sortBy, 'direction': direction})

    print('api/posts result:')
    if sortBy not in ['id', 'reads', 'likes', 'popularity', None]:
        print(json.loads(response.text))
        return 0
    
    if direction not in ['asc', 'desc', None]:
        print(json.loads(response.text))
        return 0

    #validate_text query from the source
    validate_text = []

    for i in tags:
        validate = requests.get(BASE, {'tag': i})
        validate_text.append(json.loads(validate.text))

    result_text = json.loads(response.text)

    #check if the result list has duplicate
    check_no_duplicate = True
    for i in result_text['posts']:
        count = 0
        for j in result_text['posts']:
            if i==j:
                count += 1
        if count > 1:
            check_no_duplicate = False

    if check_no_duplicate:
        print('No duplicate records')
    else:
        print('Have duplicate records')

    #check for correct items in result list
    check_correct_items = True
    for i in validate_text:
        for j in range(len(result_text['posts'])):
            if result_text['posts'][j] in i['posts']:
                i['posts'].remove(result_text['posts'][j])

    for i in range(len(validate_text)):
        if len(validate_text[i]['posts']) != 0:
            check_correct_items = False

    if check_correct_items:
        print('order is correct')
    else:
        print('order is not correct')

    #check for correct order in result list
    check_correct_order = True
    #since default value of sortBy is 'id' and direction is 'asc'
    if sortBy == None:
        sortBy = 'id'
    if direction == None:
        direction = 'asc'
    for i in range(len(result_text['posts'])-1):
        if direction == 'asc':
            if result_text['posts'][i][sortBy] > result_text['posts'][i+1][sortBy]:
                check_correct_order = False
        else:
            if result_text['posts'][i][sortBy] < result_text['posts'][i+1][sortBy]:
                check_correct_order = False

    if check_correct_order:
        print('order is correct')
    else:
        print('order is not correct')

    #result
    if check_no_duplicate and check_correct_items and check_correct_order:
        print('Everything is OK')
    else:
        print('Something is not correct')

if __name__ == '__main__':
    #custom test
    testing_text_arr = [['tech'], ['history'], ['tech, history'], ['tech, history, health'], ['tech']]
    sortBy_arr = ['likes', 'id', 'reads', 'popularitylol', None]
    direction_arr = ['asc', 'desc', 'ascs', 'desc', None]

    test_api()

    for i in range(len(testing_text_arr)):
        test = test_api(testing_text=testing_text_arr[i], sortBy=sortBy_arr[i], direction=direction_arr[i])