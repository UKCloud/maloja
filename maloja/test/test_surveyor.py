#!/usr/bin/env python
#   -*- encoding: UTF-8 -*-

from __future__ import print_function
from __future__ import unicode_literals

import textwrap
import unittest

import ruamel.yaml

import maloja.surveyor
import maloja.types

class OrgSurveyTests(unittest.TestCase):
    xml = textwrap.dedent("""<?xml version="1.0" encoding="UTF-8"?><Org
        xmlns="http://www.vmware.com/vcloud/v1.5"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        href="https://vcloud.example.com/api/org/7b832bc5-3d65-45a2-8d35-da28388ab80a"
        id="urn:vcloud:org:7b832bc5-3d65-45a2-8d35-da28388ab80a"
        name="Default"
        type="application/vnd.vmware.vcloud.org+xml"
        xsi:schemaLocation="http://www.vmware.com/vcloud/v1.5 http://https://vcloud.example.com/api/v1.5/schema/master.xsd">
        <Link
            href="https://vcloud.example.com/api/vdc/afaafb99-228c-4838-ad07-5bf3aa649d42"
            name="Default vDC"
            rel="down"
            type="application/vnd.vmware.vcloud.vdc+xml"/>
        <Link
            href="https://vcloud.example.com/api/tasksList/7b832bc5-3d65-45a2-8d35-da28388ab80a"
            rel="down"
            type="application/vnd.vmware.vcloud.tasksList+xml"/>
        <Link
            href="https://vcloud.example.com/api/catalog/39867ab4-04e0-4b13-b468-08abcc1de810"
            name="Default catalog"
            rel="down"
            type="application/vnd.vmware.vcloud.catalog+xml"/>
        <Link
            href="https://vcloud.example.com/api/org/7b832bc5-3d65-45a2-8d35-da28388ab80a/catalog/39867ab4-04e0-4b13-b468-08abcc1de810/controlAccess/"
            rel="down"
            type="application/vnd.vmware.vcloud.controlAccess+xml"/>
        <Link
            href="https://vcloud.example.com/api/org/7b832bc5-3d65-45a2-8d35-da28388ab80a/catalog/39867ab4-04e0-4b13-b468-08abcc1de810/action/controlAccess"
            rel="controlAccess"
            type="application/vnd.vmware.vcloud.controlAccess+xml"/>
        <Link
            href="https://vcloud.example.com/api/admin/org/7b832bc5-3d65-45a2-8d35-da28388ab80a/catalogs"
            rel="add"
            type="application/vnd.vmware.admin.catalog+xml"/>
        <Link
            href="https://vcloud.example.com/api/network/1fcc8a15-340d-43cc-a200-76c2cbbe70ba"
            name="VM Network"
            rel="down"
            type="application/vnd.vmware.vcloud.orgNetwork+xml"/>
        <Link
            href="https://vcloud.example.com/api/supportedSystemsInfo/"
            rel="down"
            type="application/vnd.vmware.vcloud.supportedSystemsInfo+xml"/>
        <Link
            href="https://vcloud.example.com/api/org/7b832bc5-3d65-45a2-8d35-da28388ab80a/metadata"
            rel="down"
            type="application/vnd.vmware.vcloud.metadata+xml"/>
        <Description>Default organization description</Description>
        <Tasks>
            <Task
                cancelRequested="false"
                endTime="2013-02-14T13:12:08.617+02:00"
                expiryTime="2013-05-15T13:12:08.617+03:00"
                href="https://vcloud.example.com/api/task/de88f868-8402-4a66-aa7b-18a45223d640"
                id="urn:vcloud:task:de88f868-8402-4a66-aa7b-18a45223d640"
                name="task"
                operation="External processing finished Organization Default(7b832bc5-3d65-45a2-8d35-da28388ab80a)"
                operationName="jobCustom"
                serviceNamespace="ServiceNamespace"
                startTime="2013-02-14T13:12:08.617+02:00"
                status="error"
                type="application/vnd.vmware.vcloud.task+xml">
                <Link
                    href="https://vcloud.example.com/api/task/de88f868-8402-4a66-aa7b-18a45223d640"
                    name="task"
                    rel="edit"
                    type="application/vnd.vmware.vcloud.task+xml"/>
                <Owner
                    href="https://vcloud.example.com/api/admin/org/7b832bc5-3d65-45a2-8d35-da28388ab80a"
                    name="Default"
                    type="application/vnd.vmware.admin.organization+xml"/>
                <Error
                    majorErrorCode="500"
                    message="The task is still in progress."
                    minorErrorCode="INTERNAL_SERVER_ERROR"
                    stackTrace="The task is still in progress."/>
                <User
                    href="https://vcloud.example.com/api/admin/user/007a5dfd-32b4-42dd-813b-bfef3da70cb5"
                    name="user"
                    type="application/vnd.vmware.admin.user+xml"/>
                <Organization
                    href="https://vcloud.example.com/api/org/7b832bc5-3d65-45a2-8d35-da28388ab80a"
                    name="Default"
                    type="application/vnd.vmware.vcloud.org+xml"/>
                <Progress>20</Progress>
                <Details>The task is still in progress.</Details>
            </Task>
        </Tasks>
        <FullName>Default Organization</FullName>
    </Org>
    """)

    def test_simple(self):
        obj = next(maloja.surveyor.survey_loads(OrgSurveyTests.xml), None)
        self.assertIsInstance(obj, maloja.types.Org)
        self.assertEqual("Default", obj.name)
        self.assertEqual("Default Organization", obj.fullName)
        self.assertEqual(
            "https://vcloud.example.com/api/org/7b832bc5-3d65-45a2-8d35-da28388ab80a",
            obj.href)
        self.assertEqual(
            "application/vnd.vmware.vcloud.org+xml",
            obj.type)
