#!/usr/bin/env python3
import logging
import os
import datetime
from tornado.escape import json_decode
from tornado.httpclient import AsyncHTTPClient, HTTPClientError
from tornado.ioloop import IOLoop
from tornado.web import *
from hashlib import sha1


endpoint   = os.getenv('DCOLEMAN_ENDPOINT', 'http://localhost:8000/api/v1')
salt       = os.getenv('DCOLEMAN_TASKS_VIEWER_HASH_SALT', '1two3')
title      = "Django Coleman - Task Viewer | {}".format
mtasks_url = (endpoint + "/tasks/{}/").format
master_t   = os.getenv('DCOLEMAN_MASTER_TOKEN', 'porgs')      # A master token to access to any order,
                                                              # REPLACE in production or leave it blank to disable

class BaseHandler(RequestHandler):
    def error(self, status, msg="Unexpected Error", exc_info=None):
        if exc_info:
            logging.error("Unexpected error %s", exc_info.__class__.__name__, exc_info=exc_info)
        self.set_status(status)
        return self.render("error.html", title=title(msg), error=msg)


class MainHandler(BaseHandler):
    async def get(self, task_number):
        token = self.get_argument("t", None)
        if not token:
            return self.error(401, "Unauthorized Access")
        if not self.is_valid_token(task_number, token):
            return self.error(401, "Invalid Authorization Code")
        http_client = AsyncHTTPClient()
        try:
            response = await http_client.fetch(mtasks_url(task_number))
        except HTTPClientError as e:
            if e.code == 404:
                return self.error(404, "Order Not Found")
            else:
                return self.error(400, exc_info=e)
        except Exception as e:
            return self.error(500, exc_info=e)
        order = json_decode(response.body)
        state = order['state']
        assigned_to = self.get_assigned_to(order.get('user'))
        created_at = self.get_created_at(order.get('created_at'))
        deadline = self.get_deadline(order.get('deadline'))
        return self.render("index.html",
                           title=title(f"Task #{task_number}"),
                           order=order,
                           created_at=created_at,
                           deadline=deadline,
                           state=state,
                           assigned_to=assigned_to)

    def get_assigned_to(self, user):
        if not user:
            return ""
        full_name = " ".join(
            filter(None, (user.get("first_name"), user.get("last_name")))
        )
        return full_name if full_name else user["username"]

    def get_created_at(self, created_at):
        if not created_at:
            return ""
        return datetime.datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%S.%fZ") \
                                .strftime("%B %d, %Y")

    def get_deadline(self, deadline):
        if not deadline:
            return ""
        return datetime.datetime.strptime(deadline, "%Y-%m-%d") \
                                .strftime("%B %d, %Y")

    def is_valid_token(self, order_number, token_url):
        """
        Verifies whether the token is valid or not.
        It uses the same algorithm used by Django Coleman to
        generates the token using as input a salt code and
        the Order Number

        See: ``mtasks.models.Task#get_tasks_viewer_url`` from the
             Django Coleman project
        """
        if master_t and token_url == master_t:  # Master Token is Magic !
            return True
        pk = int(order_number)      # Removes the leading zeros
        token = "{}-{}".format(salt, pk)
        token = sha1(token.encode('utf-8')).hexdigest()
        return token == token_url


class NotFoundHandler(BaseHandler):
    def prepare(self):  # for all methods
        return self.error(404, "Resource Not Found")


def make_app():
    return Application([
        (r"/([0-9]+)", MainHandler),
    ], default_handler_class=NotFoundHandler)


if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    IOLoop.current().start()
