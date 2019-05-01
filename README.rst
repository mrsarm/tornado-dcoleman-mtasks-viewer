.. image:: docs/source/_static/img/dcoleman-viewer.png
   :scale: 50 %

(Tornado) Django Coleman Viewer
===============================

**IN PROGRESS**: Simple web application to view task orders from
`Django Coleman <https://github.com/mrsarm/django-coleman>`_,
built with `Tornado Framework <https://www.tornadoweb.org/en/stable/>`_.

This is just a PoC using Tornado web framework and
Python 3+ async programming, and Django Coleman as API,
it's not a full featured, production ready application.


Requirements
------------

* Python 3.6+
* Tornado framework installed (tested with version 6)
* Django Coleman running at the URL pointed
  by the ``DCOLEMAN_ENDPOINT`` environment
  variable (by default it uses ``http://localhost:8000/api/v1``)


Install and Run
---------------

Install ``tornado`` with::

   $ pip3 install tornado

(use virtual environments!)

Run with::

   $ ./app.py

Run changing the Django Coleman endpoint with::

   $ DCOLEMAN_ENDPOINT=http://HOSTNAME/api/v1 ./app.py


Access the application
----------------------

If the order number is *123*, the URL is: http://localhost:8888/123


About
-----

**Project**: https://github.com/mrsarm/tornado-dcoleman-mtasks-viewer

**Authors**: (2019) Mariano Ruiz <mrsarm@gmail.com>

**License**: AGPL-v3
