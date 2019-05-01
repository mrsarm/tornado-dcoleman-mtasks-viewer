#!/usr/bin/env python3
import logging
import os
from tornado.escape import json_decode
from tornado.httpclient import AsyncHTTPClient, HTTPClientError
from tornado.ioloop import IOLoop
from tornado.web import *


endpoint = os.getenv("DCOLEMAN_ENDPOINT", "http://localhost:8000/api/v1")
title = "Django Coleman - Task Viewer | {}".format
mtasks_url = (endpoint + "/tasks/{}/").format


class BaseHandler(RequestHandler):
    def error(self, status, msg="Unexpected Error", exc_info=None):
        if exc_info:
            logging.error("Unexpected error %s", exc_info.__class__.__name__, exc_info=exc_info)
        self.set_status(status)
        return self.render("error.html", title=title(msg), error=msg)


class MainHandler(BaseHandler):
    async def get(self, task_number):
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
        return self.render("index.html",
                           title=title(f"Task #{task_number}"),
                           order=order,
                           state=state,
                           assigned_to=assigned_to)

    def get_assigned_to(self, user):
        if not user:
            return ""
        full_name = " ".join(
            filter(None, (user.get("first_name"), user.get("last_name")))
        )
        return full_name if full_name else user["username"]


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
