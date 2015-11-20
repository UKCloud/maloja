#!/usr/bin/env python
#   -*- encoding: UTF-8 -*-

import logging

class Surveyor:

    @staticmethod
    def on_org_list(path, session, response):
        log = logging.getLogger("maloja.surveyor.on_org_list")
        # TODO: Use session to schedule navigation of API with own callbacks
        log.debug(path)
        log.debug(response.text)
