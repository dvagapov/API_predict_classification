import json
import sys
import os.path
import psycopg2.extras
import psycopg2
import re

from prediction.predict import predict
from threading import Event
from psycopg2 import sql

from flask import Flask, make_response, request, g
from flask_restx import Resource, Api, reqparse
from flask_httpauth import HTTPTokenAuth

app = Flask(__name__)
api = Api(app)
auth = HTTPTokenAuth(scheme='Token')

def connect_db():
    conn = psycopg2.connect(dbname=os.environ.get('PG_DB'), user=os.environ.get('PG_USER'), 
                                password=os.environ.get('PG_PASS'), host=os.environ.get('PG_HOST'))
    return conn

# Auth check token
@auth.verify_token
def verify_token(token):
    if not (token):
        return False
    conn = connect_db()
    with conn.cursor() as cursor:
        cursor.execute('SELECT COALESCE( (SELECT User_ID FROM login_user WHERE token = %s LIMIT 1) , 0) a', (token, ))
        user_id = cursor.fetchone()
        if int(user_id[0]) > 0:
            g.current_user = str(user_id[0])
            return True

    return False

# Ping-pong    
@api.route('/ping')
class Ping(Resource):
    def get(self):
        return {
            'status': 'success  ',
            'message': 'pong!'
        }, 200

parser = reqparse.RequestParser(bundle_errors=True)
parser.add_argument('f1', required=True,  action='append', help="f1 cannot be blank")
parser.add_argument('f2', required=True,  action='append', help="f2 cannot be blank")
parser.add_argument('f3', required=True,  action='append', help="f3 cannot be blank")

@api.route('/classify') # @api.expect(parser)
class Classify(Resource):
    '''
        Get 3 params: f1:float, f2:float, f3:string
        
        Return: json
        
        Example:
            $ curl -X POST http://localhost:5000/classify -H 'Authorization: Token tokenTest1' -d "f1=1.212&f2=2.223&f3=B"
            output: { "predicted_class": "1.0", "status": "OK"}
    '''
    @auth.login_required
    def post(self):
        response = ''
        args = parser.parse_args()
        error_res = '{"status": "ERROR", "error_message": "MSG"}'
        try:
            f1 = str(args['f1'][0])
            f2 = str(args['f2'][0])
            f3 = str.upper(str(args['f3'][0]))
            
            # f1 check
            if re.match(r'^-?\d+(?:\.\d+)?$', f1) is None:
                error = "f1 is not a float."
                response = make_response(error_res.replace('MSG',error), 421)

            # f2 check
            if re.match(r'^-?\d+(?:\.\d+)?$', f2) is None:
                error = "f2 is not a float."
                response = make_response(error_res.replace('MSG',error), 422)
                
            # f3 check
            if f3 not in ['','A','B','C','D','E']:
                error = "f3 should be in ['','A','B','C','D','E']"
                response = make_response(error_res.replace('MSG',error), 423)
            
            if response != '':
                conn = connect_db()
                with conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor) as cursor:
                    conn.autocommit = True
                    insert = sql.SQL('INSERT INTO predict_err_logs (f1, f2, f3, err) VALUES {}').format(
                        sql.SQL(',').join(map(sql.Literal, list([(f1, f2, f3, error)])))
                    )
                    cursor.execute(insert)
                response = make_response(error_res.replace('MSG',error), 423)
                return response

            # predict
            f1 = float(args['f1'][0])
            f2 = float(args['f2'][0])
            f3 = str.upper(str(args['f3'][0]))

            res_int = predict(f1, f2, f3)
            status = 'OK'
            
            # check prediction in two most recently logged requests
            conn = connect_db()
            with conn.cursor() as cursor:
                cursor.execute('SELECT predict FROM predict_logs ORDER BY TS DESC LIMIT 2')
                predict_logs = cursor.fetchall()
                
                flag = True
                if predict_logs is not None :
                    for recently_predict in predict_logs:
                        if int(recently_predict[0]) != int(res_int)  and recently_predict[0] is not None :
                            flag = False
                    if flag:
                        status = 'WARNING'

            print('resp 1')
            response = make_response('{ "predicted_class": "' + str(res_int) + '", "status": "' + status + '"}')
            
            conn = connect_db()
            with conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor) as cursor:
                conn.autocommit = True
                cursor.execute('INSERT INTO predict_logs (f1, f2, f3, predict) VALUES (%s, %s, %s, %s);',(f1, f2, f3, int(res_int)))
                cursor.execute('UPDATE predict_logs_cnt SET cnt = cnt + 1 WHERE f3 = %s',(f3,))

            return response

        except Exception as error :
            error_res = '{"status": "ERROR", "error_message": "' + str(error) + '"}'
            response = make_response(error_res, 420)
            return response

# Ping-pong    
@api.route('/stats')
class Stats(Resource):
    '''
        Get 3 params: f1:float, f2:float, f3:string
        Return: int
        
        Example:
            $ curl http://localhost:5000/stats -H 'Authorization: Token tokenTest1'
            output: {"mean_f1": 0.25, "mean_f2": 0.33, "most_frequent_f3": "A"}
    '''
    @auth.login_required
    def get(self):
        try:
            conn = connect_db()
            with conn.cursor() as cursor:
                cursor.execute('SELECT avg(f1) mean_f1, avg(f2) mean_f2, cnt.f3 f3_cnt FROM predict_logs as p, (SELECT f3 FROM predict_logs_cnt ORDER BY cnt DESC LIMIT 1) cnt GROUP BY cnt.f3 LIMIT 1')
                stats = cursor.fetchone()
                response = make_response('{"mean_f1": ' + str(stats[0]) + ', "mean_f2": ' + str(stats[1]) + ', "most_frequent_f3": "' + stats[2] + '"}', 200)
                return response

        except Exception as error :
            error_res = '{"status": "ERROR", "error_message": "' + str(error) + '"}'
            response = make_response(error_res, 420)
            return response

if __name__ == '__main__':
    app.run(debug=True)