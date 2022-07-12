#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
from abc import ABCMeta, abstractmethod
import json
from datetime import datetime
import logging
import hashlib
import uuid
from optparse import OptionParser
from http.server import HTTPServer, BaseHTTPRequestHandler
from http import HTTPStatus
from scoring import get_score, get_interests

SALT = "Otus"
ADMIN_LOGIN = "admin"
ADMIN_SALT = "42"
ERRORS = {
    HTTPStatus.BAD_REQUEST.value: "Bad Request",
    HTTPStatus.FORBIDDEN.value: "Forbidden",
    HTTPStatus.NOT_FOUND.value: "Not Found",
    HTTPStatus.INVALID_REQUEST.value: "Invalid Request",
    HTTPStatus.INTERNAL_ERROR.value: "Internal Server Error",
}
UNKNOWN = 0
MALE = 1
FEMALE = 2
GENDERS = {
    UNKNOWN: "unknown",
    MALE: "male",
    FEMALE: "female",
}
#
EMPTY_VALUES = (None, '', [], (), {})
LIMIT_AGE = 70


class FieldABC(metaclass=ABCMeta):
    def __init__(self, required=False, nullable=True):
        self.required = required
        self.nullable = nullable

    @abstractmethod
    # return validated field or raise ValueError
    def validate(self, value):
        raise NotImplementedError('Parse_and_validate method not implemented')


class CharField(FieldABC):
    def validate(self, value):
        if isinstance(value, str):
            return value
        raise ValueError('Field is not string')


class ArgumentsField(FieldABC):
    def validate(self, value):
        if isinstance(value, dict):
            return value
        raise ValueError('Field is not dictionary')


class EmailField(CharField):
    def validate(self, value):
        value = super().validate(value)
        if not re.match(r'(.+@.+)', value):
            raise ValueError('Email field is not valid')
        return value


class PhoneField(FieldABC):
    def validate(self, value):
        if not re.match(r'(^7[\d]{10}$)', str(value)):
            raise ValueError('Phone field is not valid')
        return value


class DateField(FieldABC):
    def validate(self, value):
        try:
            datetime.strptime(str(value), '%d.%m.%Y')
        except:
            raise ValueError('Date field is not valid')
        return value


class BirthDayField(FieldABC):
    def validate(self, value):
        current_date = datetime.now()
        try:
            birth_date = datetime.strptime(str(value), '%d.%m.%Y')
        except:
            raise ValueError('BirthDay field is not valid')
        if (current_date.year - birth_date.year) > LIMIT_AGE:
            raise ValueError(f'Age must not exceed {LIMIT_AGE} years')
        return value


class GenderField(FieldABC):
    def validate(self, value):
        if value not in GENDERS:
            raise ValueError('Gender field is not valid')
        return value


class ClientIDsField(FieldABC):
    def validate(self, values):
        if not isinstance(values, list):
            raise ValueError('Client ids field is not valid')
        for value in values:
            if not isinstance(value, int):
                raise ValueError('Client ids field is not valid')
        return values


class RequestMeta(type):
    # gather correct fields in collection
    def __new__(meta, name, bases, attrs):
        fields_list = []
        for key, value in attrs.items():
            if isinstance(value, FieldABC):
                fields_list.append((key, value))
        cls = super().__new__(meta, name, bases, attrs)
        cls.fields_list = fields_list
        return cls


class Request(metaclass=RequestMeta):
    def __init__(self, request):
        self.request = request
        self.non_empty_fields = []
        self.errors_list = []
        self.code = HTTPStatus.OK.value

    def is_valid(self):
        if not isinstance(self.request, dict):
            self.errors_list.append('Request must be dictionary')
            self.code = HTTPStatus.INVALID_REQUEST.value
        for field_name, field_value in self.fields_list:
            if field_name not in self.request.keys() and field_value.required:
                self.errors_list.append(f'Field {field_name} is required')
                self.code = HTTPStatus.INVALID_REQUEST.value
            if field_name in self.request.keys():
                if self.request[field_name] not in EMPTY_VALUES:
                    self.non_empty_fields.append(field_name)
                    field_value.validate(self.request[field_name])
            if not field_value.nullable and self.request[field_name] in EMPTY_VALUES:
                self.errors_list.append(f'Field {field_name} must not be empty')
                self.code = HTTPStatus.INVALID_REQUEST.value
        if self.errors_list:
            return False
        return True


class ClientsInterestsRequest(Request):
    client_ids = ClientIDsField(required=True)
    date = DateField(required=False, nullable=True)

    def get_response(self, ctx, store):
        response = {}
        n_ids = 0
        clt_ids_list = self.request['clients_ids']
        for clt_id in clt_ids_list:
            response[str(clt_id)] = get_interests(store, clt_id)
            n_ids += 1
        ctx['nclients'] = n_ids
        return response, self.code


class OnlineScoreRequest(Request):
    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=False, nullable=True)

    def is_valid(self):
        has_pair = False
        super().is_valid()
        val_pairs = [['email', 'phone'], ['first_name', 'last_name'], ['gender', 'birthday']]
        for pair in val_pairs:
            if set(pair).issubset(self.non_empty_fields):
                has_pair = True
        if not has_pair:
            self.errors_list.append('''At least one pair of field:
                                    email-phone, 
                                    first_name-last_name, 
                                    gender-birthday must be not empty''')
            self.code = HTTPStatus.INVALID_REQUEST.value
        if self.errors_list:
            return False
        return True

    def get_response(self, ctx, store, **request):
        ctx['has'] = self.non_empty_fields
        if is_admin:
            score = 43
        else:
            score = get_score(store, **request)
        return {'score': score}, self.code


class MethodRequest(Request):
    account = CharField(required=False, nullable=True)
    login = CharField(required=True, nullable=True)
    token = CharField(required=True, nullable=True)
    arguments = ArgumentsField(required=True, nullable=True)
    method = CharField(required=True, nullable=False)

    @property
    def is_admin(self):
        return self.login == ADMIN_LOGIN


def check_auth(request):
    if request.is_admin:
        digest = hashlib.sha512(datetime.datetime.now().strftime("%Y%m%d%H") + ADMIN_SALT).hexdigest()
    else:
        digest = hashlib.sha512(request.account + request.login + SALT).hexdigest()
    if digest == request.token:
        return True
    return False


def method_handler(request, ctx, store):
    # validate request
    basic_request = MethodRequest(**request['body'])
    if not basic_request.is_valid():
        return basic_request.errors_list, basic_request.code
    # if token is invalid, return Forbidden status
    if not check_auth(request['body']):
        return "Forbidden", HTTPStatus.FORBIDDEN.value
    # analyze request method

    # online_score method
    if request['body']['method'] == 'online_score':
        arg_request = OnlineScoreRequest(**request['body']['arguments'])
        if not arg_request.is_valid():
            return arg_request.errors_list, arg_request.code
        return arg_request.get_response(ctx,
                                        store,
                                        basic_request.is_admin,
                                        **request['body']['arguments'])
    # clients_interests method
    elif request['body']['method'] == 'clients_interests':
        arg_request = ClientsInterestsRequesе(**request['body']['arguments'])
        if not arg_request.is_valid():
            return arg_request.errors_list, arg_request.code
        return arg_request.get_response(ctx,
                                        store)


class MainHTTPHandler(BaseHTTPRequestHandler):
    router = {
        "method": method_handler
    }
    store = None

    def get_request_id(self, headers):
        return headers.get('HTTP_X_REQUEST_ID', uuid.uuid4().hex)

    def do_POST(self):
        response, code = {}, HTTPStatus.OK.value
        context = {"request_id": self.get_request_id(self.headers)}
        request = None
        try:
            data_string = self.rfile.read(int(self.headers['Content-Length']))
            request = json.loads(data_string)
        except:
            code = HTTPStatus.BAD_REQUEST.value

        if request:
            path = self.path.strip("/")
            logging.info("%s: %s %s" % (self.path, data_string, context["request_id"]))
            if path in self.router:
                try:
                    response, code = self.router[path]({"body": request, "headers": self.headers}, context, self.store)
                except Exception as e:
                    logging.exception("Unexpected error: %s" % e)
                    code = HTTPStatus.INTERNAL_ERROR.value
            else:
                code = HTTPStatus.NOT_FOUND.value

        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if code not in ERRORS:
            r = {"response": response, "code": code}
        else:
            r = {"error": response or ERRORS.get(code, "Unknown Error"), "code": code}
        context.update(r)
        logging.info(context)
        self.wfile.write(json.dumps(r))
        return


def logging_init(logging_file):
    # initialize script logging
    logging.basicConfig(filename=logging_file,
                        format='[%(asctime)s] %(levelname).1s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=logging.INFO)


if __name__ == "__main__":
    op = OptionParser()
    op.add_option("-p", "--port", action="store", type=int, default=8080)
    op.add_option("-l", "--log", action="store", default=None)
    (opts, args) = op.parse_args()
    try:
        logging_init(opts.log)
    except Exception:
        logging_init(None)
    server = HTTPServer(("localhost", opts.port), MainHTTPHandler)
    logging.info("Starting server at %s" % opts.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
