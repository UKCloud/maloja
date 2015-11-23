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

class VdcSurveyTests(unittest.TestCase):
    xml = textwrap.dedent("""<?xml version="1.0" encoding="UTF-8"?><Vdc
    xmlns="http://www.vmware.com/vcloud/v1.5"
    xmlns:vmext="http://www.vmware.com/vcloud/extension/v1.5"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    href="https://vcloud.example.com/api/vdc/afaafb99-228c-4838-ad07-5bf3aa649d42"
    id="urn:vcloud:vdc:afaafb99-228c-4838-ad07-5bf3aa649d42"
    name="Default vDC"
    status="1"
    type="application/vnd.vmware.vcloud.vdc+xml"
    xsi:schemaLocation="http://www.vmware.com/vcloud/extension/v1.5 http://https://vcloud.example.com/api/v1.5/schema/vmwextensions.xsd http://www.vmware.com/vcloud/v1.5 http://https://vcloud.example.com/api/v1.5/schema/master.xsd">
    <VCloudExtension
        required="false">
        <vmext:VimObjectRef>
            <vmext:VimServerRef
                href="https://vcloud.example.com/api/admin/extension/vimServer/5b2f648b-9da7-4d7b-8212-6ed8a83f2102"
                name="VC"
                type="application/vnd.vmware.admin.vmwvirtualcenter+xml"/>
            <vmext:MoRef>resgroup-194</vmext:MoRef>
            <vmext:VimObjectType>RESOURCE_POOL</vmext:VimObjectType>
        </vmext:VimObjectRef>
    </VCloudExtension>
    <Link
        href="https://vcloud.example.com/api/org/7b832bc5-3d65-45a2-8d35-da28388ab80a"
        rel="up"
        type="application/vnd.vmware.vcloud.org+xml"/>
    <Link
        href="https://vcloud.example.com/api/vdc/afaafb99-228c-4838-ad07-5bf3aa649d42/metadata"
        rel="down"
        type="application/vnd.vmware.vcloud.metadata+xml"/>
    <Link
        href="https://vcloud.example.com/api/vdc/afaafb99-228c-4838-ad07-5bf3aa649d42/action/uploadVAppTemplate"
        rel="add"
        type="application/vnd.vmware.vcloud.uploadVAppTemplateParams+xml"/>
    <Link
        href="https://vcloud.example.com/api/vdc/afaafb99-228c-4838-ad07-5bf3aa649d42/media"
        rel="add"
        type="application/vnd.vmware.vcloud.media+xml"/>
    <Link
        href="https://vcloud.example.com/api/vdc/afaafb99-228c-4838-ad07-5bf3aa649d42/action/instantiateOvf"
        rel="add"
        type="application/vnd.vmware.vcloud.instantiateOvfParams+xml"/>
    <Link
        href="https://vcloud.example.com/api/vdc/afaafb99-228c-4838-ad07-5bf3aa649d42/action/instantiateVAppTemplate"
        rel="add"
        type="application/vnd.vmware.vcloud.instantiateVAppTemplateParams+xml"/>
    <Link
        href="https://vcloud.example.com/api/vdc/afaafb99-228c-4838-ad07-5bf3aa649d42/action/cloneVApp"
        rel="add"
        type="application/vnd.vmware.vcloud.cloneVAppParams+xml"/>
    <Link
        href="https://vcloud.example.com/api/vdc/afaafb99-228c-4838-ad07-5bf3aa649d42/action/cloneVAppTemplate"
        rel="add"
        type="application/vnd.vmware.vcloud.cloneVAppTemplateParams+xml"/>
    <Link
        href="https://vcloud.example.com/api/vdc/afaafb99-228c-4838-ad07-5bf3aa649d42/action/cloneMedia"
        rel="add"
        type="application/vnd.vmware.vcloud.cloneMediaParams+xml"/>
    <Link
        href="https://vcloud.example.com/api/vdc/afaafb99-228c-4838-ad07-5bf3aa649d42/action/captureVApp"
        rel="add"
        type="application/vnd.vmware.vcloud.captureVAppParams+xml"/>
    <Link
        href="https://vcloud.example.com/api/vdc/afaafb99-228c-4838-ad07-5bf3aa649d42/action/composeVApp"
        rel="add"
        type="application/vnd.vmware.vcloud.composeVAppParams+xml"/>
    <Link
        href="https://vcloud.example.com/api/vdc/afaafb99-228c-4838-ad07-5bf3aa649d42/disk"
        rel="add"
        type="application/vnd.vmware.vcloud.diskCreateParams+xml"/>
    <Link
        href="https://vcloud.example.com/api/admin/vdc/afaafb99-228c-4838-ad07-5bf3aa649d42/edgeGateways"
        rel="edgeGateways"
        type="application/vnd.vmware.vcloud.query.records+xml"/>
    <Link
        href="https://vcloud.example.com/api/admin/vdc/afaafb99-228c-4838-ad07-5bf3aa649d42/networks"
        rel="add"
        type="application/vnd.vmware.vcloud.orgVdcNetwork+xml"/>
    <Link
        href="https://vcloud.example.com/api/admin/vdc/afaafb99-228c-4838-ad07-5bf3aa649d42/networks"
        rel="orgVdcNetworks"
        type="application/vnd.vmware.vcloud.query.records+xml"/>
    <Description>Default vDC</Description>
    <Tasks>
        <Task
            cancelRequested="false"
            endTime="2013-02-14T13:13:00.333+02:00"
            expiryTime="2013-05-15T13:12:59.990+03:00"
            href="https://vcloud.example.com/api/task/2510f3ab-4a12-4c69-834f-bbfd442ff374"
            id="urn:vcloud:task:2510f3ab-4a12-4c69-834f-bbfd442ff374"
            name="task"
            operation="Updated Storage Profiles for Virtual Datacenter (afaafb99-228c-4838-ad07-5bf3aa649d42)"
            operationName="vdcUpdateStorageProfiles"
            serviceNamespace="com.vmware.vcloud"
            startTime="2013-02-14T13:12:59.990+02:00"
            status="error"
            type="application/vnd.vmware.vcloud.task+xml">
            <Owner
                href="https://vcloud.example.com/api/admin/vdc/afaafb99-228c-4838-ad07-5bf3aa649d42"
                name=""
                type="application/vnd.vmware.admin.vdc+xml"/>
            <Error
                majorErrorCode="400"
                message="The request has duplicate VDC storage profile &quot;profile&quot;."
                minorErrorCode="BAD_REQUEST"
                stackTrace="com.vmware.vcloud.api.presentation.service.BadRequestException: The request has duplicate VDC storage profile &quot;profile&quot;.  at com.vmware.vcloud.api.presentation.service.impl.VdcServiceAdapterImpl.updateVdcStorageClassesTask(VdcServiceAdapterImpl.java:672)  at com.vmware.vcloud.api.presentation.service.impl.VdcServiceAdapterImpl.executeTask(VdcServiceAdapterImpl.java:2071)  at com.vmware.vcloud.backendbase.management.system.TaskServiceImpl$4.doInSecurityContext(TaskServiceImpl.java:1341)  at com.vmware.vcloud.backendbase.management.system.TaskServiceImpl$4.doInSecurityContext(TaskServiceImpl.java:1336)  at com.vmware.vcloud.backendbase.management.system.TaskServiceImpl$SecurityContextTemplate.executeForOrgAndUser(TaskServiceImpl.java:1702)  at com.vmware.vcloud.backendbase.management.system.TaskServiceImpl.execute(TaskServiceImpl.java:1336)  at com.vmware.vcloud.backendbase.management.system.TaskServiceImpl.dispatchByStatus(TaskServiceImpl.java:1258)  at com.vmware.vcloud.backendbase.management.system.TaskServiceImpl.dispatchTask(TaskServiceImpl.java:1137)  at com.vmware.vcloud.backendbase.management.system.LocalTask.run(LocalTask.java:88)  at java.util.concurrent.ThreadPoolExecutor.runWorker(ThreadPoolExecutor.java:1110)  at java.util.concurrent.ThreadPoolExecutor$Worker.run(ThreadPoolExecutor.java:603)  at java.lang.Thread.run(Thread.java:722) "/>
            <User
                href="https://vcloud.example.com/api/admin/user/1260efee-6915-494c-8afa-84e7e6d8a310"
                name="system"
                type="application/vnd.vmware.admin.user+xml"/>
            <Organization
                href="https://vcloud.example.com/api/org/7b832bc5-3d65-45a2-8d35-da28388ab80a"
                name="Default"
                type="application/vnd.vmware.vcloud.org+xml"/>
            <Details>  The request has duplicate VDC storage profile "profile".</Details>
        </Task>
    </Tasks>
    <AllocationModel>AllocationVApp</AllocationModel>
    <ComputeCapacity>
        <Cpu>
            <Units>MHz</Units>
            <Allocated>0</Allocated>
            <Limit>0</Limit>
            <Reserved>0</Reserved>
            <Used>0</Used>
            <Overhead>0</Overhead>
        </Cpu>
        <Memory>
            <Units>MB</Units>
            <Allocated>0</Allocated>
            <Limit>0</Limit>
            <Reserved>0</Reserved>
            <Used>0</Used>
            <Overhead>0</Overhead>
        </Memory>
    </ComputeCapacity>
    <ResourceEntities>
        <ResourceEntity
            href="https://vcloud.example.com/api/vAppTemplate/vappTemplate-fa813d19-3936-4099-bff9-e0ad8d1e34bb"
            name="NewCatalogItem"
            type="application/vnd.vmware.vcloud.vAppTemplate+xml"/>
        <ResourceEntity
            href="https://vcloud.example.com/api/vApp/vapp-bba47763-0ce1-45b9-8470-ea29ba58c52f"
            name="importedVapp"
            type="application/vnd.vmware.vcloud.vApp+xml"/>
        <ResourceEntity
            href="https://vcloud.example.com/api/disk/5d9c3d46-c992-49a5-913d-a617d7331618"
            name="diskName"
            type="application/vnd.vmware.vcloud.disk+xml"/>
        <ResourceEntity
            href="https://vcloud.example.com/api/disk/7140e20e-8596-467a-ac10-4cfee7d1a220"
            name="diskName"
            type="application/vnd.vmware.vcloud.disk+xml"/>
        <ResourceEntity
            href="https://vcloud.example.com/api/disk/bb8f4df6-128e-4ffd-a6ed-9241829e382f"
            name="diskName"
            type="application/vnd.vmware.vcloud.disk+xml"/>
        <ResourceEntity
            href="https://vcloud.example.com/api/disk/c0bb36b3-60e2-45c3-a784-1ca2d02a0315"
            name="diskName"
            type="application/vnd.vmware.vcloud.disk+xml"/>
    </ResourceEntities>
    <AvailableNetworks>
        <Network
            href="https://vcloud.example.com/api/network/1fcc8a15-340d-43cc-a200-76c2cbbe70ba"
            name="VM Network"
            type="application/vnd.vmware.vcloud.network+xml"/>
    </AvailableNetworks>
    <Capabilities>
        <SupportedHardwareVersions>
            <SupportedHardwareVersion>vmx-04</SupportedHardwareVersion>
            <SupportedHardwareVersion>vmx-07</SupportedHardwareVersion>
            <SupportedHardwareVersion>vmx-08</SupportedHardwareVersion>
        </SupportedHardwareVersions>
    </Capabilities>
    <NicQuota>0</NicQuota>
    <NetworkQuota>1024</NetworkQuota>
    <UsedNetworkCount>0</UsedNetworkCount>
    <VmQuota>0</VmQuota>
    <IsEnabled>true</IsEnabled>
    <VdcStorageProfiles>
        <VdcStorageProfile
            href="https://vcloud.example.com/api/vdcStorageProfile/b520e879-71de-4d47-b2e1-e092aab97f61"
            name="*"
            type="application/vnd.vmware.vcloud.vdcStorageProfile+xml"/>
        <VdcStorageProfile
            href="https://vcloud.example.com/api/vdcStorageProfile/eb6aacbd-f0d8-4a07-8248-1de28151e98f"
            name="profile"
            type="application/vnd.vmware.vcloud.vdcStorageProfile+xml"/>
    </VdcStorageProfiles>
    </Vdc>""")

    def test_simple(self):
        obj = next(maloja.surveyor.survey_loads(VdcSurveyTests.xml), None)
        self.assertIsInstance(obj, maloja.types.Vdc)
        self.assertEqual("Default vDC", obj.name)
        self.assertEqual("Default vDC", obj.description)
        self.assertEqual(
            "https://vcloud.example.com/api/vdc/afaafb99-228c-4838-ad07-5bf3aa649d42",
            obj.href)
        self.assertEqual(
            "application/vnd.vmware.vcloud.vdc+xml",
            obj.type)
