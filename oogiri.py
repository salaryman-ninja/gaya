# -*- coding: utf-8 -*-
import os
import sys
import time
import hashlib
import base64

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext import db
# <= python 2.5 needed
from django.utils import simplejson as json

import models
import model_json


class ContentRequestHandler(webapp.RequestHandler):
    def post(self):
        i_dict = json.loads(self.request.body)
        #iDictionary = {}
        #for item in iData:
        #    iDictionary[item['name']] = item['value']
        o_dict = {}
        #if not i_dict.has_key('state') or not i_dict.has_key('question_id'):
        #    (state, question_id) = (None, None)
        #else:
        #    (state, question_id) = (i_dict['state'], i_dict['question_id'])
        #(state, question_id) = next_state(state, question_id)
        if i_dict.has_key('oogiri_name') and i_dict['oogiri_name'] != None:
            (o_dict['oogiri_name'], o_dict['oogiri_hash']) = name_and_hash(i_dict['oogiri_name'])

        # set next state
        if not i_dict.has_key('state') or i_dict['state'] == None:
            state = 0
        elif i_dict['state'] == 0:
            next_question = get_next_question(o_dict['oogiri_name'], o_dict['oogiri_hash'], None)
            state = 1
        elif i_dict['state'] == 1:
            state = 2
        else:
            next_question = get_next_question(o_dict['oogiri_name'], o_dict['oogiri_hash'], i_dict['question_key'])
            if next_question == None:
                state = 3
            else:
                state = 1
        o_dict['state'] = state

        if state == 0:
            vote_query = models.Vote.all()
            voted_dict = {}
            for vote in vote_query:
                key = (vote.answer.oogiri_name, vote.answer.oogiri_hash)
                if not voted_dict.has_key(key):
                    voted_dict[key] = {
                        'count':0,
                        'oogiri_name':vote.answer.oogiri_name,
                        'oogiri_hash':vote.answer.oogiri_hash,
                        'update_datetime':vote.answer.update_datetime
                        }
                voted_dict[key]['count'] += 1
            o_dict['voted_counts'] = sorted(voted_dict.values(), key = lambda dict: dict['update_datetime'], reverse = True)
        elif state == 1:
            o_dict['question'] = next_question
        elif state == 2:
            o_dict['question'] = models.Question.get(i_dict['question_key'])
            answer_query = models.Answer.all()
            answer_query.filter('question =', o_dict['question'])
            answer_query.order('-update_datetime')
            answer_list = []
            for answer in answer_query:
                if answer.oogiri_name != o_dict['oogiri_name'] or answer.oogiri_hash != o_dict['oogiri_hash']:
                    answer.oogiri_name = None
                    answer.oogiri_hash = None
                answer_list.append(answer)
            o_dict['answers'] = answer_list
        elif state == 3:
            answer_query = models.Answer.all()
            voted_dict = {}
            for answer in answer_query:
                key = (answer.oogiri_name, answer.oogiri_hash)
                if not voted_dict.has_key(key):
                    voted_dict[key] = {'count':0}
                vote_query = answer.vote_set
                vote_query.filter('oogiri_name = ', o_dict['oogiri_name'])
                vote_query.filter('oogiri_hash = ', o_dict['oogiri_hash'])
                voted_dict[key]['count'] += vote_query.count()
            # sort
            voted_count_list = [{
                'oogiri_name':key[0],
                'oogiri_hash':key[1],
                'count':value['count']
                } for key, value in voted_dict.iteritems()]
            o_dict['voted_counts'] = sorted(voted_count_list, key = lambda dict: dict['count'], reverse = True)
        o_dict_json = model_json.JSONEncoder().encode(o_dict)
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(o_dict_json)

class AnswerRequestHandler(webapp.RequestHandler):
    def post(self):
        i_dict = json.loads(self.request.body)
        question_key = db.Key(i_dict['question_key'])
        if i_dict.has_key('key'):
            key = db.Key(i_dict['key'])
            answer = models.Answer.get(key)
            if answer.question.key() != question_key:
                # answer key is old
                question = models.Question.get(question_key)
                answer = models.Answer(question = question)
        else:
            question = models.Question.get(question_key)
            answer = models.Answer(question = question)
        answer.content = i_dict['content']
        (answer.oogiri_name, answer.oogiri_hash) = name_and_hash(i_dict['oogiri_name'])
        answer.put()
        o_dict_json = model_json.JSONEncoder().encode(answer)
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(o_dict_json)

class VoteRequestHandler(webapp.RequestHandler):
    def post(self):
        i_dict = json.loads(self.request.body)
        answer_key = db.Key(i_dict['answer_key'])
        answer = models.Answer.get(answer_key)
        vote = models.Vote(answer = answer)
        (vote.oogiri_name, vote.oogiri_hash) = name_and_hash(i_dict['oogiri_name'])
        vote.put()
        o_dict_json = model_json.JSONEncoder().encode(vote)
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(o_dict_json)


def name_and_hash(oogiri_name):
    name_array = oogiri_name.split('#', 1)
    oogiri_name = name_array[0]
    oogiri_hash = trip(name_array[1]) if len(name_array) > 1 else None
    return (oogiri_name, oogiri_hash)

def trip(unicode):
    # make 12-char trip
    digest = hashlib.sha1(unicode.encode('utf_8')).digest()
    return base64.b64encode(digest, './')[:12]


def main():
    application = webapp.WSGIApplication([
        ('/oogiri/content', ContentRequestHandler),
        ('/oogiri/answer', AnswerRequestHandler),
        ('/oogiri/vote', VoteRequestHandler),
        ], debug = True)
    util.run_wsgi_app(application)

def state():
    current_time = time.time()
    current_state = int(current_time % (interval_time * 3) / interval_time) + 1
    current_state = 3
    remaining_time = int(interval_time - current_time % interval_time)
    return (current_state, remaining_time)

def next_state(state, question_id):
    if state == 0:
        return (1, 'id:1')
    if state == 1:
        return (2, question_id)
    if state == 2:
        if question_id == 'id:5':
            return (3, None)
        else:
            ids = question_id.split(':', 1)
            ids[1] = str(int(ids[1]) + 1)
            return (1, ':'.join(ids))
    return (0, None)

def get_next_question(oogiri_name, oogiri_hash, question_key):
    if question_key == None:
        query = models.Answer.all();
        query.filter('oogiri_name = ', oogiri_name)
        query.filter('oogiri_hash = ', oogiri_hash)
        query.order('-update_datetime')
        answer = query.get()
        if answer == None:
            last_question = None
        else:
            last_question = answer.question
    else:
        last_question = models.Question.get(question_key)

    if last_question == None:
        next_question = models.Question.get_by_key_name('id:1')
    else:
        ids = last_question.key().name().split(':', 1)
        ids[1] = str(int(ids[1]) + 1)
        key_name = ':'.join(ids)
        next_question = models.Question.get_by_key_name(key_name)
        if next_question == None and question_key == None:
            # starting second round
            next_question = models.Question.get_by_key_name('id:1')

    return next_question


if __name__ == '__main__':
    main()
