from flask import Flask, request
import logging
import json
import random

app = Flask(__name__)
import translate
from geo import get_geo_info, get_distance

logging.basicConfig(level=logging.INFO, filename='app.log',
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')

Session_data = {}
current_status = "start"
current_dialog = "start"
dialog_sport = None
flag = False
flag_end_football = False
score_ronaldo = 0
question_1 = False
question_2 = False
question_3 = False
question_4 = False
question_5 = False
flag_leo = False
flag_info_ney = False
not_test_ron = 1
knowledge_about_ney = ["очень знаменитый", "хороший футболист", "играет в PSG",
                       "играет в ПСЖ"]
topic_alisa = ["talk_sport", "translate", "gallery", "city"]


@app.route('/post', methods=['POST'])
def main():
    logging.info('Request: %r', request.json)

    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }

    main_dialog(response, request.json)

    logging.info('Request: %r', response)

    return json.dumps(response)


def main_dialog(res, req):
    global current_status, current_dialog, Session_data, dialog_sport, flag, flag_end_football, \
        score_ronaldo, question_1, question_2, question_3, question_4, question_5, not_test_ron, knowledge_about_ney, \
        flag_leo, flag_info_ney, topic_alisa

    user_id = req['session']['user_id']
    if current_dialog == "start":
        if req['session']['new']:
            res['response']['text'] = 'Привет! Ты запустил данный навык, нажми на кнопку "Помощь" и узнай, что я умею.' \
                                      ' О чем хочешь поговорить?'
            current_status = "start_question"
            Session_data[user_id] = {
                'suggests': [
                    "Давай о спорте.",
                    "Просто поболтать.",
                    "Вопросы по городам.",
                    "Покажи города.",
                    "Не знаю, выбери сама.",
                    "Помощь.",
                ],
                'username': "Пользователь"
            }
            Session_data[user_id]['quest'] = ['Как погода?', 'Как тебя зовут?', 'Тебе много лет?',
                                              'Чем занимаешься?', "Какая ваша любимая книга?", "Кто ваш любимый автор?",
                                              "Вы бы выбрали ум или внешность?",
                                              "По шкале от 1 - 10 насколько забавны ваши шутки?"]

            res['response']['buttons'] = get_suggests(user_id)
            return
        if current_status == "start_question" and req['request']['original_utterance'].lower() not in \
                ['давай о спорте.', 'просто поболтать.', 'вопросы по городам.', 'покажи города.',
                 'не знаю, выбери сама.', 'помощь.']:
            res['response']['text'] = 'Я тебя не поняла, повтори ещё раз.'
            Session_data[user_id] = {
                'suggests': [
                    "Давай о спорте.",
                    "Просто поболтать.",
                    "Вопросы по городам.",
                    "Покажи города.",
                    "Не знаю, выбери сама.",
                    "Помощь.",
                ],
                'username': "Пользователь"
            }
            Session_data[user_id]['quest'] = ['Как погода?', 'Как тебя зовут?', 'Тебе много лет?',
                                              'Чем занимаешься?', "Какая ваша любимая книга?", "Кто ваш любимый автор?",
                                              "Вы бы выбрали ум или внешность?",
                                              "По шкале от 1 - 10 насколько забавны ваши шутки?"]

            res['response']['buttons'] = get_suggests(user_id)
            return
        if current_status == "start_question":
            if req['request']['original_utterance'].lower() in ['помощь.']:
                res['response'][
                    'text'] = 'Я умею выполнять несколько команд:"Давай о спорте"-я могу поддержать небольшой' \
                              ' диалог по теме спорта,"Просто поболтать"- я могу поспрашивать' \
                              ' тебя о чем-нибудь,"Вопросы по городам"-я' \
                              ' могу рассказать тебе в какой стране находится город, если ты введешь' \
                              ' 1 город, если введешь 2, то скажу рсстояние между ними,"Покажи города"-могу' \
                              ' показать известных мне городов,"' \
                              'Не знаю, выбери сама"-выберу сама тему для разговора.'
                Session_data[user_id] = {
                    'suggests': [
                        "Давай о спорте.",
                        "Просто поболтать.",
                        "Вопросы по городам.",
                        "Покажи города.",
                        "Не знаю, выбери сама.",
                        "Помощь.",
                    ],
                    'username': "Пользователь"
                }
                Session_data[user_id]['quest'] = ['Как погода?', 'Как тебя зовут?', 'Тебе много лет?',
                                                  'Чем занимаешься?', "Какая ваша любимая книга?",
                                                  "Кто ваш любимый автор?",
                                                  "Вы бы выбрали ум или внешность?",
                                                  "По шкале от 1 - 10 насколько забавны ваши шутки?"]

                res['response']['buttons'] = get_suggests(user_id)
                return
        if current_status == "start_question":
            if req['request']['original_utterance'].lower() in ['давай о спорте.', 'спорт.', 'спорте', 'спорте.',
                                                                'давай о спорте.', 'давай о спорте', 'спортом',
                                                                'спортом.']:
                current_status = "talk_sport"
                res['response']['text'] = 'Отлично! О каком спорте поговорим?'
                Session_data[user_id] = {
                    'suggests': [
                        "Футбол",
                        "Баскетбол.",
                        "Хоккей.",
                    ],
                    'username': "Пользователь"
                }

                res['response']['buttons'] = get_suggests(user_id)
                return
        if current_status == "talk_sport" and dialog_sport == None and req['request'][
            'original_utterance'].lower() not in \
                ['футбол', 'баскетбол.', 'хоккей.']:
            res['response']['text'] = 'Я тебя не поняла, повтори ещё раз.'
            Session_data[user_id] = {
                'suggests': [
                    "Футбол",
                    "Баскетбол.",
                    "Хоккей.",
                ],
                'username': "Пользователь"
            }

            res['response']['buttons'] = get_suggests(user_id)
            return
        if current_status == "talk_sport" and dialog_sport == 'football' and req['request'][
            'original_utterance'].lower() not in \
                ['месси.', 'роналду.', 'неймар.']:
            res['response']['text'] = 'Я тебя не поняла, повтори ещё раз.'
            Session_data[user_id] = {
                'suggests': [
                    "Месси.",
                    "Роналду.",
                    "Неймар.",
                ],
                'username': "Пользователь"
            }

            res['response']['buttons'] = get_suggests(user_id)
            return
        if current_status == "talk_sport":
            if req['request']['original_utterance'].lower() in ['футбол', 'футболе.', 'футболом', 'футбол.',
                                                                'футболе.', 'Футболом.']:
                res['response']['text'] = 'Этот спорт мне нравится больше всего. Кто твой любимый футболист?'
                dialog_sport = 'football'
                Session_data[user_id] = {
                    'suggests': [
                        "Месси.",
                        "Роналду.",
                        "Неймар.",
                    ],
                    'username': "Пользователь"

                }

                res['response']['buttons'] = get_suggests(user_id)
                return
            if dialog_sport == 'football':
                if req['request']['original_utterance'].lower() in ['месси', 'месси.', 'лео.', 'лео', 'лионель',
                                                                    'лионель.', 'лионель месси.''лионель месси',
                                                                    'меси.', 'меси']:
                    res['response'][
                        'text'] = 'Мне он тоже нравится больше всех. Он просто' \
                                  ' гений. Хочешь покажу его самое красивое фото?'
                    dialog_sport = 'football_messi'
                    Session_data[user_id] = {
                        'suggests': [
                            "Да, давай.",
                            "Нет, не надо.",
                        ],
                        'username': "Пользователь"

                    }

                    res['response']['buttons'] = get_suggests(user_id)
                    return
            if dialog_sport == 'football_messi':
                if req['request']['original_utterance'].lower() in ['да', 'давай.', 'почему бы и нет', 'ага', 'угу',
                                                                    'да, давай.']:
                    res['response']['text'] = 'Тогда напиши:"ЛеоМесси"'
                    flag_leo = True
                    return
                if not flag_leo and req['request']['original_utterance'].lower() not in ['да', 'давай.',
                                                                                         'почему бы и нет', 'ага',
                                                                                         'угу',
                                                                                         'да, давай.']:
                    current_status = "start"
                    current_dialog = "start"
                    res['response']['text'] = 'Тогда давай переключим тему.'
                    Session_data[user_id] = {
                        'suggests': [
                            "Просто поболтать.",
                            "Вопросы по городам.",
                            "Покажи города.",
                            "Не знаю, выбери сама.",
                            "Помощь.",
                        ],
                        'username': "Пользователь"
                    }
                    Session_data[user_id]['quest'] = ['Как погода?', 'Как тебя зовут?', 'Тебе много лет?',
                                                      'Чем занимаешься?', "Какая ваша любимая книга?",
                                                      "Кто ваш любимый автор?",
                                                      "Вы бы выбрали ум или внешность?",
                                                      "По шкале от 1 - 10 насколько забавны ваши шутки?"]

                    res['response']['buttons'] = get_suggests(user_id)
                    return

                if dialog_sport == 'football_messi' and flag_leo and not flag and not flag_end_football:
                    res['response']['card'] = {}
                    res['response']['card']['type'] = 'BigImage'
                    res['response']['card']['title'] = 'Месси. Понравилось?'
                    res['response']['card']['image_id'] = '1652229/5ba76fc57d55506fdb93'
                    res['response']['text'] = 'Понравилось?'
                    flag = False
                    flag_end_football = True
                    Session_data[user_id] = {
                        'suggests': [
                            "Да.",
                            "Нет.",
                        ],
                        'username': "Пользователь"

                    }

                    res['response']['buttons'] = get_suggests(user_id)
                    return
                if dialog_sport == 'football_messi' and flag_end_football:
                    if req['request']['original_utterance'].lower() in ['да.', 'да', 'ага', 'угу', 'очень',
                                                                        'еще бы']:
                        res['response']['text'] = 'Я старалась:) Давай сменим тему.'
                        current_status = "start_question"
                        current_dialog = "start"
                        Session_data[user_id] = {
                            'suggests': [
                                "Просто поболтать.",
                                "Вопросы по городам.",
                                "Покажи города.",
                                "Не знаю, выбери сама.",
                                "Помощь.",
                            ],
                            'username': "Пользователь"
                        }
                        Session_data[user_id]['quest'] = ['Как погода?', 'Как тебя зовут?', 'Тебе много лет?',
                                                          'Чем занимаешься?', "Какая ваша любимая книга?",
                                                          "Кто ваш любимый автор?",
                                                          "Вы бы выбрали ум или внешность?",
                                                          "По шкале от 1 - 10 насколько забавны ваши шутки?"]

                        res['response']['buttons'] = get_suggests(user_id)
                        return
                    if dialog_sport == 'football_messi' and flag_end_football:
                        if req['request']['original_utterance'].lower() in ['нет.', 'нет', 'не-а', 'ноу', 'не очень']:
                            res['response']['text'] = 'Всем не угодишь, а я ведь старалась:( Давай сменим тему.'
                            current_status = "start_question"
                            current_dialog = "start"
                            Session_data[user_id] = {
                                'suggests': [
                                    "Просто поболтать.",
                                    "Вопросы по городам.",
                                    "Покажи города.",
                                    "Не знаю, выбери сама.",
                                    "Помощь.",
                                ],
                                'username': "Пользователь"
                            }
                            Session_data[user_id]['quest'] = ['Как погода?', 'Тебе много лет?',
                                                              'Чем занимаешься?',
                                                              "Какая ваша любимая книга?",
                                                              "Кто ваш любимый автор?",
                                                              "Вы бы выбрали ум или внешность?",
                                                              "По шкале от 1 - 10 насколько забавны ваши шутки?"]

                            res['response']['buttons'] = get_suggests(user_id)
                            return
            if dialog_sport == 'football':
                if req['request']['original_utterance'].lower() in ['роналду', 'роналду.', 'криш.', 'криро',
                                                                    'криштиану',
                                                                    'криштиану роналду.']:
                    dialog_sport = 'football_ronaldo'
                    res['response'][
                        'text'] = 'На мой взгляд, Лео лучше, но о нём я тоже смогу поддержать разговор. Хочешь' \
                                  ' узнать о том, как хорошо ты о нем знаешь?'
                    Session_data[user_id] = {
                        'suggests': [
                            "Да, давай.",
                            "Нет, не хочу.",
                        ],
                        'username': "Пользователь"

                    }

                    res['response']['buttons'] = get_suggests(user_id)
                    return
            if current_status == "talk_sport" and dialog_sport == 'football_ronaldo':
                if req['request']['original_utterance'].lower() in ['да, давай.', 'да',
                                                                    'ага.',
                                                                    'ага',
                                                                    'угу',
                                                                    'угу.']:
                    res['response'][
                        'text'] = 'Хорошо. В тесте будет 5 вопрос, за каждый правильный дается один балл,' \
                                  ' за каждый неправильный снимается балл. Первый вопрос: В каком' \
                                  ' году Роналдо стал выступать за Манчестер Юнайтед?'
                    question_1 = True
                    not_test_ron = 0
                    dialog_sport = 'football_ronaldo_test'
                    Session_data[user_id] = {
                        'suggests': [
                            "2003",
                            "2009",
                            "2018",
                            "он там не выступал",
                        ],
                        'username': "Пользователь"

                    }

                    res['response']['buttons'] = get_suggests(user_id)
                    return
                if req['request']['original_utterance'].lower() not in ['да, давай.', 'да',
                                                                        'ага.',
                                                                        'ага',
                                                                        'угу',
                                                                        'угу.']:
                    res['response'][
                        'text'] = 'Большего' \
                                  ' о нём я не знаю, поэтому давай переключать тему.'
                    current_status = "start_question"
                    Session_data[user_id] = {
                        'suggests': [
                            "Просто поболтать.",
                            "Вопросы по городам.",
                            "Покажи города.",
                            "Не знаю, выбери сама.",
                        ],
                        'username': "Пользователь"
                    }
                    Session_data[user_id]['quest'] = ['Как погода?', 'Тебе много лет?',
                                                      'Чем занимаешься?',
                                                      "Какая ваша любимая книга?",
                                                      "Кто ваш любимый автор?",
                                                      "Вы бы выбрали ум или внешность?",
                                                      "По шкале от 1 - 10 насколько забавны ваши шутки?"]

                    res['response']['buttons'] = get_suggests(user_id)
                    return

            if question_1 and dialog_sport == 'football_ronaldo_test' and req['request'][
                'original_utterance'].lower() in [
                '2003', 'две тысячи третий', 'две тысячи третьем', 'две тысячи третьем году',
            ]:
                score_ronaldo += 1
                res['response'][
                    'text'] = 'Это правильный ответ. Переходим ко 2 вопросу. Сколько лет он выступал' \
                              ' за этот клуб?'
                Session_data[user_id] = {
                    'suggests': [
                        "6",
                        "8",
                        "9",
                        "он и сейчас там выступает",
                    ],
                    'username': "Пользователь"

                }
                question_1 = False
                question_2 = True

                res['response']['buttons'] = get_suggests(user_id)
                return
            if question_1 and dialog_sport == 'football_ronaldo_test' and req['request'][
                'original_utterance'].lower() not in [
                '2003', 'две тысячи третий', 'две тысячи третьем', 'две тысячи третьем году',
            ]:
                if score_ronaldo > 0:
                    score_ronaldo -= 1
                else:
                    score_ronaldo = 0
                res['response'][
                    'text'] = 'Это неправильный ответ. Переходим ко 2 вопросу. Сколько лет он выступал' \
                              ' за этот клуб?'
                Session_data[user_id] = {
                    'suggests': [
                        "6",
                        "8",
                        "9",
                        "он и сейчас там выступает",
                    ],
                    'username': "Пользователь"

                }

                question_1 = False
                question_2 = True

                res['response']['buttons'] = get_suggests(user_id)
                return
            if question_2 and req['request'][
                'original_utterance'].lower() in [
                '6', 'шесть', 'шесть лет', 'лет шесть',
            ]:
                score_ronaldo += 1
                res['response'][
                    'text'] = 'Это правильный ответ. Переходим ко 3 вопросу.Сколько золотых мячей он выиграл?'
                Session_data[user_id] = {
                    'suggests': [
                        "4",
                        "5",
                        "6",
                        "Ни одного",
                    ],
                    'username': "Пользователь"

                }
                question_2 = False
                question_3 = True

                res['response']['buttons'] = get_suggests(user_id)
                return
            if question_2 and req['request'][
                'original_utterance'].lower() not in [
                '6', 'шесть', 'шесть лет', 'лет шесть',
            ]:
                if score_ronaldo > 0:
                    score_ronaldo -= 1
                else:
                    score_ronaldo = 0
                res['response'][
                    'text'] = 'Это неправильный ответ. Переходим ко 3 вопросу.Сколько золотых мячей он выиграл?'
                Session_data[user_id] = {
                    'suggests': [
                        "4",
                        "5",
                        "6",
                        "Ни одного",
                    ],
                    'username': "Пользователь"

                }
                question_2 = False
                question_3 = True

                res['response']['buttons'] = get_suggests(user_id)
                return
            if question_3 and req['request'][
                'original_utterance'].lower() in [
                '5', 'пять', 'пять лет', 'лет пять',
            ]:
                score_ronaldo += 1
                res['response'][
                    'text'] = 'Это правильный ответ. Переходим ко 4 вопросу. В каком году он выиграл первый ЗМ?'
                Session_data[user_id] = {
                    'suggests': [
                        "2006",
                        "2016",
                        "2009",
                        "2008",
                    ],
                    'username': "Пользователь"

                }
                question_3 = False
                question_4 = True

                res['response']['buttons'] = get_suggests(user_id)
                return
            if question_3 and req['request'][
                'original_utterance'].lower() not in [
                '5', 'пять', 'пять лет', 'лет пять',
            ]:
                if score_ronaldo > 0:
                    score_ronaldo -= 1
                else:
                    score_ronaldo = 0
                res['response'][
                    'text'] = 'Это неправильный ответ. Переходим ко 4 вопросу. В каком году он выиграл первый ЗМ?'
                Session_data[user_id] = {
                    'suggests': [
                        "2006",
                        "2016",
                        "2009",
                        "2008",
                    ],
                    'username': "Пользователь"

                }
                question_3 = False
                question_4 = True

                res['response']['buttons'] = get_suggests(user_id)
                return
            if question_4 and req['request'][
                'original_utterance'].lower() not in [
                '2008', 'две тысячи восьмой', 'в две тысячи восьмом', 'две тысячи восьмой год',
            ]:
                if score_ronaldo > 0:
                    score_ronaldo -= 1
                else:
                    score_ronaldo = 0
                res['response'][
                    'text'] = 'Это неправильный ответ. Переходим ко 5 вопросу. Где этот игрок играет сейчас?'
                Session_data[user_id] = {
                    'suggests': [
                        "Реал Мадрид",
                        "Ювентус",
                        "Барселона",
                        "Манчестер Юнайтед",
                    ],
                    'username': "Пользователь"

                }
                question_4 = False
                question_5 = True

                res['response']['buttons'] = get_suggests(user_id)
                return
            if question_4 and req['request'][
                'original_utterance'].lower() in [
                '2008', 'две тысячи восьмой', 'в две тысячи восьмом', 'две тысячи восьмой год',
            ]:
                score_ronaldo += 1
                res['response'][
                    'text'] = 'Это правильный ответ. Переходим ко 5 вопросу. Где этот игрок играет сейчас?'
                Session_data[user_id] = {
                    'suggests': [
                        "Реал Мадрид",
                        "Ювентус",
                        "Барселона",
                        "Манчестер Юнайтед",
                    ],
                    'username': "Пользователь"

                }
                question_4 = False
                question_5 = True

                res['response']['buttons'] = get_suggests(user_id)
                return
            if question_5 and req['request'][
                'original_utterance'].lower() in [
                'Ювентус', 'Юве', 'В Ювентусе', 'В Юве',
            ]:
                score_ronaldo += 1
                res['response'][
                    'text'] = 'Это правильный ответ. Вот твои баллы: ' + str(
                    score_ronaldo) + 'Ты доволен результатами?'
                Session_data[user_id] = {
                    'suggests': [
                        "Да, очень",
                        "Нет",
                    ],
                    'username': "Пользователь"

                }
                question_5 = False

                res['response']['buttons'] = get_suggests(user_id)
                return
            if question_5 and req['request'][
                'original_utterance'].lower() not in [
                'Ювентус', 'Юве', 'В Ювентусе', 'В Юве',
            ]:
                if score_ronaldo > 0:
                    score_ronaldo -= 1
                else:
                    score_ronaldo = 0
                res['response'][
                    'text'] = 'Это неправильный ответ. Вот твои баллы: ' + str(
                    score_ronaldo) + 'Ты доволен результатами?'
                Session_data[user_id] = {
                    'suggests': [
                        "Да, очень",
                        "Нет",
                    ],
                    'username': "Пользователь"

                }
                question_5 = False
                not_test_ron = 5
                res['response']['buttons'] = get_suggests(user_id)
                return
            if not_test_ron == 5:
                if req['request']['original_utterance'].lower() in [
                    'да, очень', 'да', 'очень', 'ага',
                ]:
                    res['response'][
                        'text'] = 'Отлично, поздравляю, ты молодец! Большего' \
                                  ' о нём я не знаю, поэтому давай переключать тему.'
                    current_status = "start_question"
                    current_dialog = "start"
                    Session_data[user_id] = {
                        'suggests': [
                            "Просто поболтать.",
                            "Вопросы по городам.",
                            "Покажи города.",
                            "Не знаю, выбери сама.",
                            "Помощь.",
                        ],
                        'username': "Пользователь"
                    }
                    Session_data[user_id]['quest'] = ['Как погода?', 'Тебе много лет?',
                                                      'Чем занимаешься?', "Какая ваша любимая книга?",
                                                      "Кто ваш любимый автор?",
                                                      "Вы бы выбрали ум или внешность?",
                                                      "По шкале от 1 - 10 насколько забавны ваши шутки?"]

                    res['response']['buttons'] = get_suggests(user_id)
                    return
            if dialog_sport == 'football':
                if req['request']['original_utterance'].lower() in ['неймар', 'неймар.', 'ней.']:
                    dialog_sport = 'football_neymar'
                    res['response'][
                        'text'] = 'Его я знаю плохо. Расскажи ' \
                                  'мне что-нибудь о нем в нескольких сообщениях. Надеюсь ты сможешь' \
                                  ' сообщить что-то новое :)'
                    Session_data[user_id] = {
                        'suggests': [
                            "Ну давай попробую.",
                            "Я не смогу что-то вспомнить.",
                        ],
                        'username': "Пользователь"

                    }

                    res['response']['buttons'] = get_suggests(user_id)
                    return
            if dialog_sport == 'football_neymar':
                if not flag_info_ney and req['request']['original_utterance'].lower() in ['ну давай попробую.',
                                                                                          'давай.',
                                                                                          'сейчас попробую']:
                    flag_info_ney = True
                    res['response'][
                        'text'] = 'Я тебя внимательно слушаю'
                    return
                if not flag_info_ney and req['request']['original_utterance'].lower() not in ['ну давай попробую.',
                                                                                              'давай.',
                                                                                              'сейчас попробую'] or \
                        req['request']['original_utterance'].lower() in ['я не смогу что-то вспомнить.', 'нет.',
                                                                         'не хочу']:
                    res['response'][
                        'text'] = 'Очень жаль, я надеялась на тебя. Тогда давай поговорим о чём-нибудь другом.'
                    current_status = "start_question"
                    current_dialog = "start"
                    Session_data[user_id] = {
                        'suggests': [
                            "Просто поболтать.",
                            "Вопросы по городам.",
                            "Покажи города.",
                            "Не знаю, выбери сама.",
                            "Помощь.",
                        ],
                        'username': "Пользователь"
                    }
                    Session_data[user_id]['quest'] = ['Как погода?', 'Тебе много лет?',
                                                      'Чем занимаешься?',
                                                      "Какая ваша любимая книга?",
                                                      "Кто ваш любимый автор?",
                                                      "Вы бы выбрали ум или внешность?",
                                                      "По шкале от 1 - 10 насколько забавны ваши шутки?"]

                    res['response']['buttons'] = get_suggests(user_id)
                    return
                if any([i_know(alisa, req['request']['original_utterance'].lower()) for alisa in
                        knowledge_about_ney]) and flag_info_ney:
                    res['response'][
                        'text'] = 'Ну обо всем об этом я знала. Вот, что я узнала от тебя: "' + str(". ".join(
                        knowledge_about_ney)) + '" Спасибо, что рассказал мне о нем,' \
                                                ' было интересно тебя послушать. Давай ещё о' \
                                                ' чём-нибудь поговорим.'
                    current_status = "start_question"
                    current_dialog = "start"
                    Session_data[user_id] = {
                        'suggests': [
                            "Просто поболтать.",
                            "Вопросы по городам.",
                            "Покажи города.",
                            "Не знаю, выбери сама.",
                            "Помощь.",
                        ],
                        'username': "Пользователь"
                    }
                    Session_data[user_id]['quest'] = ['Как погода?', 'Тебе много лет?',
                                                      'Чем занимаешься?', "Какая ваша любимая книга?",
                                                      "Кто ваш любимый автор?",
                                                      "Вы бы выбрали ум или внешность?",
                                                      "По шкале от 1 - 10 насколько забавны ваши шутки?"]

                    res['response']['buttons'] = get_suggests(user_id)
                    return
                if not any([i_know(alisa, req['request']['original_utterance'].lower()) for alisa in
                            knowledge_about_ney]):
                    res['response'][
                        'text'] = 'Ого первый раз об этом услышала, продолжай, мне очень интересно.'
                    knowledge_about_ney.append(req['request']['original_utterance'].lower())
                    return
        if current_status == "talk_sport":
            if current_status == "talk_sport" and dialog_sport == 'basketball' and req['request'][
                'original_utterance'].lower() \
                    not in ['давай.', 'нет.']:
                res['response']['text'] = 'Я тебя не поняла, повтори ещё раз.'
                res['response']['buttons'] = [{
                    "title": "Давай.",
                    "url": "https://yandex.ru/search/?text=баскетбол",
                    "hide": True
                }, {
                    "title": "Нет.",
                    "hide": True
                }]
                return
            if req['request']['original_utterance'].lower() in ['баскетбол', 'баскетболе.', 'баскетболом', 'баскетбол.',
                                                                'баскетболе.', 'баскетболом.']:
                res['response']['text'] = 'Я в нём очень мало разбираюсь.' \
                                          ' Все, что я пока могу, это вывести тебе турнирую таблицу на данный момент.'
                dialog_sport = 'basketball'

                res['response']['buttons'] = [{
                    "title": "Давай.",
                    "url": "https://yandex.ru/search/?text=баскетбол",
                    "hide": True
                }, {
                    "title": "Нет.",
                    "hide": True
                }]
                return

            if current_status == "talk_sport" and dialog_sport == 'basketball':
                if req['request']['original_utterance'].lower() in ['давай.', 'давай', 'да', 'да.',
                                                                    'покажи.', 'покажи']:
                    res['response']['text'] = 'Там вот такие результаты. Было интересно?'
                return
            if req['request']['original_utterance'].lower() in ['нет.']:
                res['response']['text'] = 'Тогда сменим тему.'
                current_status = "start_question"
                current_dialog = "start"
                Session_data[user_id] = {
                    'suggests': [
                        "Просто поболтать.",
                        "Вопросы по городам.",
                        "Покажи города.",
                        "Не знаю, выбери сама.",
                        "Помощь.",
                    ],
                    'username': "Пользователь"
                }
                Session_data[user_id]['quest'] = ['Как погода?', 'Тебе много лет?',
                                                  'Чем занимаешься?', "Какая ваша любимая книга?",
                                                  "Кто ваш любимый автор?",
                                                  "Вы бы выбрали ум или внешность?",
                                                  "По шкале от 1 - 10 насколько забавны ваши шутки?"]

                res['response']['buttons'] = get_suggests(user_id)
                return

        if current_status == "talk_sport":
            if req['request']['original_utterance'].lower() in ['хоккей', 'хоккее.', 'хоккей', 'хоккей.']:
                res['response']['text'] = 'Извини, об этом спорте я ничего не знаю.'
            current_status = "start_question"
            current_dialog = "start"
            Session_data[user_id] = {
                'suggests': [
                    "Просто поболтать.",
                    "Вопросы по городам.",
                    "Покажи города.",
                    "Не знаю, выбери сама.",
                    "Помощь.",
                ],
                'username': "Пользователь"
            }
            Session_data[user_id]['quest'] = ['Как погода?', 'Тебе много лет?',
                                              'Чем занимаешься?', "Какая ваша любимая книга?",
                                              "Кто ваш любимый автор?",
                                              "Вы бы выбрали ум или внешность?",
                                              "По шкале от 1 - 10 насколько забавны ваши шутки?"]

            res['response']['buttons'] = get_suggests(user_id)
            return
    if current_status == "start_question" and req['request']['original_utterance'].lower() in [
        'не знаю, выбери сама.', 'не знаю.', 'выбери сама',
        'а что сама предложишь.',
        'давай о спорте.', 'давай о спорте', 'спортом',
        'спортом.']:
        current_status = "random_topic"
    if current_status == "random_topic":
        current = random.choice(topic_alisa)
        if current == "translate":
            res['response'][
                'text'] = 'Давай я тогда тебе что-нибудь переведу, переводить буду с ' + lang
            current_dialog = current
            current_status = 'start_translite'
            return
        if current == "gallery":
            res['response'][
                'text'] = 'Давай я покажу фотографии городов, о которых я слышала,' \
                          ' говори название, а я скажу знаю я его или нет.'
            current_dialog = current
            current_status = current
            return
        if current == "city":
            res['response'][
                'text'] = 'Давай расскажу про города тебе.'
            current_dialog = current
            current_status = current
            return
        if current == "talk_sport":
            res['response'][
                'text'] = 'Давай поговорим о спорте. Выбери о каком:"Футбол","Баскетбол","Хоккей"'
            current_status = current
            Session_data[user_id] = {
                'suggests': [
                    "Футбол",
                    "Баскетбол.",
                    "Хоккей.",
                ],
                'username': "Пользователь"
            }

            res['response']['buttons'] = get_suggests(user_id)
            return

    if req['request']['original_utterance'].lower() in ['просто поболтать.']:
        current_dialog = "talk"

    if current_dialog == "talk":
        if len(Session_data[user_id]['quest']) < 1:
            res['response']['text'] = 'Не знаю, о чем еще спросить'
            current_status = "start_question"
            current_dialog = "start"
            Session_data[user_id] = {
                'suggests': [
                    "Давай о спорте.",
                    "Вопросы по городам.",
                    "Покажи города.",
                    "Не знаю, выбери сама.",
                    "Помощь.",
                ],
                'username': "Пользователь"
            }
            Session_data[user_id]['quest'] = ['Как погода?', 'Тебе много лет?',
                                              'Чем занимаешься?', "Какая ваша любимая книга?",
                                              "Кто ваш любимый автор?",
                                              "Вы бы выбрали ум или внешность?",
                                              "По шкале от 1 - 10 насколько забавны ваши шутки?"]

            res['response']['buttons'] = get_suggests(user_id)
            return
        res['response'][
            'text'] = 'Окей. Что делаешь'
        st_q = ['Интересно', 'Понятно', 'Ясно', 'Хорошо', 'Ммм', 'Неплохо', 'Хорошо']
        c_q = random.choice(Session_data[user_id]['quest'])
        Session_data[user_id]['quest'].remove(c_q)
        res['response']['text'] = random.choice(st_q) + '. ' + c_q

        return

    if current_dialog == "talk" and req['request']['original_utterance'].lower() in ['хватит']:
        res['response'][
            'text'] = 'Было приятно пообщаться) О чём ещё поговорим?'
        Session_data[user_id] = {
            'suggests': [
                "Давай о спорте.",
                "Вопросы по городам.",
                "Покажи города.",
                "Не знаю, выбери сама.",
                "Помощь.",
            ],
            'username': "Пользователь"
        }
        Session_data[user_id]['quest'] = ['Как погода?', 'Тебе много лет?',
                                          'Чем занимаешься?',
                                          "Какая ваша любимая книга?",
                                          "Кто ваш любимый автор?",
                                          "Вы бы выбрали ум или внешность?",
                                          "По шкале от 1 - 10 насколько забавны ваши шутки?"]

        res['response']['buttons'] = get_suggests(user_id)
        return
    if req['request']['original_utterance'].lower() in ['вопросы по городам.']:
        current_dialog = "city"
        res['response'][
            'text'] = 'Отлично! Я могу сказать в какой стране город или сказать расстояние между городами!'

        return
    if current_dialog == "city":
        cities = get_cities(req)
        if req['request']['original_utterance'].lower() in ['хватит']:
            res['response'][
                'text'] = 'Надеюсь тебе понравилось. Выбирай новую тему.'
            current_dialog = "start"
            current_status = "start_question"
            Session_data[user_id] = {
                'suggests': [
                    "Давай о спорте.",
                    "Просто поболтать.",
                    "Покажи города.",
                    "Не знаю, выбери сама.",
                    "Помощь.",
                ],
                'username': "Пользователь"
            }
            Session_data[user_id]['quest'] = ['Как погода?', 'Как тебя зовут?', 'Тебе много лет?',
                                              'Чем занимаешься?', "Какая ваша любимая книга?", "Кто ваш любимый автор?",
                                              "Вы бы выбрали ум или внешность?",
                                              "По шкале от 1 - 10 насколько забавны ваши шутки?"]

            res['response']['buttons'] = get_suggests(user_id)
            return

        if len(cities) == 0:

            res['response']['text'] = 'Ты не написал название не одного города!'

        elif len(cities) == 1:

            res['response']['text'] = 'Этот город в стране - ' + get_geo_info(cities[0], 'country')

        elif len(cities) == 2:

            distance = get_distance(get_geo_info(cities[0], 'coordinates'), get_geo_info(cities[1], 'coordinates'))
            res['response']['text'] = 'Расстояние между этими городами: ' + str(round(distance)) + ' км.'

        else:

            res['response']['text'] = 'Слишком много городов!'
        return
    if req['request']['original_utterance'].lower() in ['переведи текст.', 'переведи', 'переводчик',
                                                        'нужно перевести']:
        current_dialog = "translate"
        res['response']['text'] = 'Отлично! Что нужно перевести?'
        Session_data[user_id]['suggests'] = [
            "Русский-английский",
            "Английский-русский"
        ]
        res['response']['text'] = Session_data[user_id]['username'] + '. Выбери язык'
        res['response']['buttons'] = get_suggests(user_id)
        current_dialog = 'translate'
        current_status = 'start_translite'

        return

    if req['request']['original_utterance'].lower() in ['покажи города.']:
        current_dialog = "gallery"
        res['response']['text'] = 'Отлично!'
        Session_data[user_id]['suggests'] = [
            "Тамбов",
            "Москва",
            "Воронеж"
        ]
        res['response']['text'] = Session_data[user_id]['username'] + ', Какой город показать?'
        res['response']['buttons'] = get_suggests(user_id)
        current_status = 'start'
        current_dialog = 'gallery'

        return
    if current_dialog == "translate":
        translite_dialog(res, req)
        return
    if current_dialog == 'gallery':
        gallery_dialog(res, req)
        return


def i_know(alisa, user):
    s = 0
    alisa = alisa.lower().split()
    user = user.lower().split()
    for a in alisa:
        for u in user:
            if a == u:
                s += 1
    if s > 2:
        return True
    return False


lang = "ru-en"


def translite_dialog(res, req):
    global current_status, current_dialog, Session_data, lang
    user_id = req['session']['user_id']
    if current_status == "start":
        if req['request']['original_utterance'] == "Русский-английский":

            lang = 'ru-en'

        else:
            lang = 'en-ru'
        res['response']['text'] = Session_data[user_id]['username'] + " скажи текст"
        current_status = 'start_translite'
        return

    if 'хватит' in req['request']['original_utterance'].lower():
        res['response']['text'] = "Была рада помочь. О чём ещё поболтаем?"
        current_status = "start_question"
        Session_data[user_id] = {
            'suggests': [
                "Давай о спорте.",
                "Вопросы по городам.",
                "Покажи города.",
                "Не знаю, выбери сама.",
                "Помощь.",
            ],
            'username': "Пользователь"
        }
        Session_data[user_id]['quest'] = ['Как погода?', 'Тебе много лет?',
                                          'Чем занимаешься?',
                                          "Какая ваша любимая книга?",
                                          "Кто ваш любимый автор?",
                                          "Вы бы выбрали ум или внешность?",
                                          "По шкале от 1 - 10 насколько забавны ваши шутки?"]

        res['response']['buttons'] = get_suggests(user_id)
        return
    if current_status == 'start_translite':
        res['response']['text'] = "Перевод: " + translate.translate(req['request']['original_utterance'], lang)[0]
        current_status = 'start_translite'
        return


def gallery_dialog(res, req):
    global current_status, current_dialog, Session_data
    if current_dialog == "gallery":
        cities = {
            'тамбов':
                '1030494/15ee1b701a627af980e2'
            ,
            'леомесси':
                '1652229/5ba76fc57d55506fdb93'
            ,
            'москва':
                '1521359/53fc3bb34e2483f6794a'
            ,
            'воронеж':
                '1521359/0b2c34dc9f54dc235084'
            ,
            'нью-йорк':
                '1652229/728d5c86707054d4745f'
            ,
            'париж':
                '1652229/f77136c2364eb90a3ea8'

        }
        user_id = req['session']['user_id']

        city = req['request']['original_utterance'].lower()
        if city == "хватит":
            current_dialog = "start"
            current_status = "start"
            res['response']['text'] = 'Ок'
            current_status = "start_question"
            Session_data[user_id] = {
                'suggests': [
                    "Давай о спорте.",
                    "Вопросы по городам.",
                    "Просто поболтать.",
                    "Не знаю, выбери сама.",
                    "Помощь.",
                ],
                'username': "Пользователь"
            }
            Session_data[user_id]['quest'] = ['Как погода?', 'Тебе много лет?',
                                              'Чем занимаешься?',
                                              "Какая ваша любимая книга?",
                                              "Кто ваш любимый автор?",
                                              "Вы бы выбрали ум или внешность?",
                                              "По шкале от 1 - 10 насколько забавны ваши шутки?"]

            res['response']['buttons'] = get_suggests(user_id)
            return
        if city in cities:
            res['response']['card'] = {}
            res['response']['card']['type'] = 'BigImage'
            res['response']['card']['title'] = 'Этот город я знаю.'
            res['response']['card']['image_id'] = cities[city]
            res['response']['text'] = req['request']['original_utterance']
        else:
            res['response']['text'] = 'Первый раз слышу об этом городе.'
        return
    else:
        return


def city_dialog(res, req):
    user_id = req['session']['user_id']
    if req['session']['new']:
        res['response']['text'] = 'Привет! Я могу сказать в какой стране город или сказать расстояние между городами!'
        return
    cities = get_cities(req)
    if len(cities) == 0:
        res['response']['text'] = 'Ты не написал название не одного города!'
    elif len(cities) == 1:
        res['response']['text'] = 'Этот город в стране - ' + get_geo_info(cities[0], 'country')
    elif len(cities) == 2:
        distance = get_distance(get_geo_info(cities[0], 'coordinates'), get_geo_info(cities[1], 'coordinates'))
        res['response']['text'] = 'Расстояние между этими городами: ' + str(round(distance)) + ' км.'
    else:
        res['response']['text'] = 'Слишком много городов!'


def get_cities(req):
    cities = []
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.GEO':
            if 'city' in entity['value'].keys():
                cities.append(entity['value']['city'])
    return cities


def get_first_name(req):
    for entity in req['request']['nlu']['entities']:
        if entity['type'] == 'YANDEX.FIO':
            return entity['value'].get('first_name', None)


def get_suggests(user_id):
    session = Session_data[user_id]
    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests']
    ]
    Session_data[user_id] = session

    return suggests


if __name__ == '__main__':
    app.run()
