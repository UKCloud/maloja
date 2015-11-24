#!/usr/bin/env python
#   -*- encoding: UTF-8 -*-

from __future__ import print_function
from __future__ import unicode_literals

import textwrap
import unittest
import xml.etree.ElementTree as ET

import ruamel.yaml

import maloja.surveyor
import maloja.types

class CatalogSurveyTests(unittest.TestCase):
    xml = textwrap.dedent("""<?xml version="1.0" encoding="UTF-8"?><Catalog
    xmlns="http://www.vmware.com/vcloud/v1.5"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    href="https://vcloud.example.com/api/catalog/39867ab4-04e0-4b13-b468-08abcc1de810"
    id="urn:vcloud:catalog:39867ab4-04e0-4b13-b468-08abcc1de810"
    name="Default catalog"
    type="application/vnd.vmware.vcloud.catalog+xml"
    xsi:schemaLocation="http://www.vmware.com/vcloud/v1.5 http://https://vcloud.example.com/api/v1.5/schema/master.xsd">
    <Link
        href="https://vcloud.example.com/api/org/7b832bc5-3d65-45a2-8d35-da28388ab80a"
        rel="up"
        type="application/vnd.vmware.vcloud.org+xml"/>
    <Link
        href="https://vcloud.example.com/api/catalog/39867ab4-04e0-4b13-b468-08abcc1de810/metadata"
        rel="down"
        type="application/vnd.vmware.vcloud.metadata+xml"/>
    <Link
        href="https://vcloud.example.com/api/catalog/39867ab4-04e0-4b13-b468-08abcc1de810/catalogItems"
        rel="add"
        type="application/vnd.vmware.vcloud.catalogItem+xml"/>
    <Link
        href="https://vcloud.example.com/api/catalog/39867ab4-04e0-4b13-b468-08abcc1de810/action/upload"
        rel="add"
        type="application/vnd.vmware.vcloud.media+xml"/>
    <Link
        href="https://vcloud.example.com/api/catalog/39867ab4-04e0-4b13-b468-08abcc1de810/action/upload"
        rel="add"
        type="application/vnd.vmware.vcloud.uploadVAppTemplateParams+xml"/>
    <Link
        href="https://vcloud.example.com/api/catalog/39867ab4-04e0-4b13-b468-08abcc1de810/action/copy"
        rel="copy"
        type="application/vnd.vmware.vcloud.copyOrMoveCatalogItemParams+xml"/>
    <Link
        href="https://vcloud.example.com/api/catalog/39867ab4-04e0-4b13-b468-08abcc1de810/action/move"
        rel="move"
        type="application/vnd.vmware.vcloud.copyOrMoveCatalogItemParams+xml"/>
    <Link
        href="https://vcloud.example.com/api/catalog/39867ab4-04e0-4b13-b468-08abcc1de810/action/captureVApp"
        rel="add"
        type="application/vnd.vmware.vcloud.captureVAppParams+xml"/>
    <Description>Default catalog</Description>
    <CatalogItems>
        <CatalogItem
            href="https://vcloud.example.com/api/catalogItem/016ed9ac-c9cc-4455-bcfb-1393edcae000"
            id="016ed9ac-c9cc-4455-bcfb-1393edcae000"
            name="imported"
            type="application/vnd.vmware.vcloud.catalogItem+xml"/>
    </CatalogItems>
    <IsPublished>false</IsPublished>
    <DateCreated>2013-02-11T15:46:40.170+02:00</DateCreated>
    <VersionNumber>39</VersionNumber>
    </Catalog>""")

    def test_xml(self):
        obj = next(maloja.surveyor.survey_loads(CatalogSurveyTests.xml), None)
        self.assertIsInstance(obj, maloja.types.Catalog)
        self.assertEqual("Default catalog", obj.name)
        self.assertEqual(
            "https://vcloud.example.com/api/catalog/39867ab4-04e0-4b13-b468-08abcc1de810",
            obj.href)
        self.assertEqual(
            "application/vnd.vmware.vcloud.catalog+xml",
            obj.type)
        tree = ET.fromstring(OrgSurveyTests.xml)
        vdcs = maloja.surveyor.find_xpath(
            "./*/[@type='application/vnd.vmware.vcloud.vdc+xml']", tree)


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

    def test_xml(self):
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
        tree = ET.fromstring(OrgSurveyTests.xml)
        vdcs = maloja.surveyor.find_xpath(
            "./*/[@type='application/vnd.vmware.vcloud.vdc+xml']", tree)

    def test_yaml(self):
        txt = textwrap.dedent("""
            !!python/object/new:maloja.types.Org [Default, application/vnd.vmware.vcloud.org+xml,
            'https://vcloud.example.com/api/org/7b832bc5-3d65-45a2-8d35-da28388ab80a',
            Default Organization]""").strip()
        obj = ruamel.yaml.load(txt)
        self.assertIsInstance(obj, maloja.types.Org)
        self.assertEqual("Default", obj.name)
        self.assertEqual("Default Organization", obj.fullName)
        self.assertEqual(
            "https://vcloud.example.com/api/org/7b832bc5-3d65-45a2-8d35-da28388ab80a",
            obj.href)
        self.assertEqual(
            "application/vnd.vmware.vcloud.org+xml",
            obj.type)

class VAppSurveyTests(unittest.TestCase):

    xml = textwrap.dedent("""<?xml version="1.0" encoding="UTF-8"?><VApp
    xmlns="http://www.vmware.com/vcloud/v1.5"
    xmlns:ovf="http://schemas.dmtf.org/ovf/envelope/1"
    xmlns:rasd="http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_ResourceAllocationSettingData"
    xmlns:vmext="http://www.vmware.com/vcloud/extension/v1.5"
    xmlns:vmw="http://www.vmware.com/schema/ovf"
    xmlns:vssd="http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_VirtualSystemSettingData"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    deployed="false"
    href="https://vcloud.example.com/api/vApp/vapp-bba47763-0ce1-45b9-8470-ea29ba58c52f"
    id="urn:vcloud:vapp:bba47763-0ce1-45b9-8470-ea29ba58c52f"
    name="importedVapp"
    ovfDescriptorUploaded="true"
    status="8"
    type="application/vnd.vmware.vcloud.vApp+xml"
    xsi:schemaLocation="http://www.vmware.com/vcloud/extension/v1.5 http://https://vcloud.example.com/api/v1.5/schema/vmwextensions.xsd http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_VirtualSystemSettingData http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2.22.0/CIM_VirtualSystemSettingData.xsd http://www.vmware.com/schema/ovf http://www.vmware.com/schema/ovf http://schemas.dmtf.org/ovf/envelope/1 http://schemas.dmtf.org/ovf/envelope/1/dsp8023_1.1.0.xsd http://www.vmware.com/vcloud/v1.5 http://https://vcloud.example.com/api/v1.5/schema/master.xsd http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_ResourceAllocationSettingData http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2.22.0/CIM_ResourceAllocationSettingData.xsd">
    <Link
        href="https://vcloud.example.com/api/vApp/vapp-bba47763-0ce1-45b9-8470-ea29ba58c52f/power/action/powerOn"
        rel="power:powerOn"/>
    <Link
        href="https://vcloud.example.com/api/vApp/vapp-bba47763-0ce1-45b9-8470-ea29ba58c52f/action/deploy"
        rel="deploy"
        type="application/vnd.vmware.vcloud.deployVAppParams+xml"/>
    <Link
        href="https://vcloud.example.com/api/network/82af5cfc-1f17-40b5-bc19-e8122a599ad2"
        name="VM Network"
        rel="down"
        type="application/vnd.vmware.vcloud.vAppNetwork+xml"/>
    <Link
        href="https://vcloud.example.com/api/vApp/vapp-bba47763-0ce1-45b9-8470-ea29ba58c52f/controlAccess/"
        rel="down"
        type="application/vnd.vmware.vcloud.controlAccess+xml"/>
    <Link
        href="https://vcloud.example.com/api/vApp/vapp-bba47763-0ce1-45b9-8470-ea29ba58c52f/action/controlAccess"
        rel="controlAccess"
        type="application/vnd.vmware.vcloud.controlAccess+xml"/>
    <Link
        href="https://vcloud.example.com/api/vApp/vapp-bba47763-0ce1-45b9-8470-ea29ba58c52f/action/recomposeVApp"
        rel="recompose"
        type="application/vnd.vmware.vcloud.recomposeVAppParams+xml"/>
    <Link
        href="https://vcloud.example.com/api/vApp/vapp-bba47763-0ce1-45b9-8470-ea29ba58c52f/action/enterMaintenanceMode"
        rel="enterMaintenanceMode"/>
    <Link
        href="https://vcloud.example.com/api/vdc/afaafb99-228c-4838-ad07-5bf3aa649d42"
        rel="up"
        type="application/vnd.vmware.vcloud.vdc+xml"/>
    <Link
        href="https://vcloud.example.com/api/vApp/vapp-bba47763-0ce1-45b9-8470-ea29ba58c52f"
        rel="edit"
        type="application/vnd.vmware.vcloud.vApp+xml"/>
    <Link
        href="https://vcloud.example.com/api/vApp/vapp-bba47763-0ce1-45b9-8470-ea29ba58c52f"
        rel="remove"/>
    <Link
        href="https://vcloud.example.com/api/vApp/vapp-bba47763-0ce1-45b9-8470-ea29ba58c52f/action/enableDownload"
        rel="enable"/>
    <Link
        href="https://vcloud.example.com/api/vApp/vapp-bba47763-0ce1-45b9-8470-ea29ba58c52f/action/disableDownload"
        rel="disable"/>
    <Link
        href="https://vcloud.example.com/api/vApp/vapp-bba47763-0ce1-45b9-8470-ea29ba58c52f/owner"
        rel="down"
        type="application/vnd.vmware.vcloud.owner+xml"/>
    <Link
        href="https://vcloud.example.com/api/vApp/vapp-bba47763-0ce1-45b9-8470-ea29ba58c52f/metadata"
        rel="down"
        type="application/vnd.vmware.vcloud.metadata+xml"/>
    <Link
        href="https://vcloud.example.com/api/vApp/vapp-bba47763-0ce1-45b9-8470-ea29ba58c52f/ovf"
        rel="ovf"
        type="text/xml"/>
    <Link
        href="https://vcloud.example.com/api/vApp/vapp-bba47763-0ce1-45b9-8470-ea29ba58c52f/productSections/"
        rel="down"
        type="application/vnd.vmware.vcloud.productSections+xml"/>
    <Link
        href="https://vcloud.example.com/api/vApp/vapp-bba47763-0ce1-45b9-8470-ea29ba58c52f/action/createSnapshot"
        rel="snapshot:create"
        type="application/vnd.vmware.vcloud.createSnapshotParams+xml"/>
    <Description/>
    <LeaseSettingsSection
        href="https://vcloud.example.com/api/vApp/vapp-bba47763-0ce1-45b9-8470-ea29ba58c52f/leaseSettingsSection/"
        ovf:required="false"
        type="application/vnd.vmware.vcloud.leaseSettingsSection+xml">
        <ovf:Info>Lease settings section</ovf:Info>
        <Link
            href="https://vcloud.example.com/api/vApp/vapp-bba47763-0ce1-45b9-8470-ea29ba58c52f/leaseSettingsSection/"
            rel="edit"
            type="application/vnd.vmware.vcloud.leaseSettingsSection+xml"/>
        <DeploymentLeaseInSeconds>604800</DeploymentLeaseInSeconds>
        <StorageLeaseInSeconds>2592000</StorageLeaseInSeconds>
        <StorageLeaseExpiration>2013-03-16T13:18:35.237+02:00</StorageLeaseExpiration>
    </LeaseSettingsSection>
    <ovf:StartupSection
        xmlns:vcloud="http://www.vmware.com/vcloud/v1.5"
        vcloud:href="https://vcloud.example.com/api/vApp/vapp-bba47763-0ce1-45b9-8470-ea29ba58c52f/startupSection/"
        vcloud:type="application/vnd.vmware.vcloud.startupSection+xml">
        <ovf:Info>VApp startup section</ovf:Info>
        <ovf:Item
            ovf:id="importedVapp"
            ovf:order="0"
            ovf:startAction="powerOn"
            ovf:startDelay="0"
            ovf:stopAction="guestShutdown"
            ovf:stopDelay="0"/>
        <Link
            href="https://vcloud.example.com/api/vApp/vapp-bba47763-0ce1-45b9-8470-ea29ba58c52f/startupSection/"
            rel="edit"
            type="application/vnd.vmware.vcloud.startupSection+xml"/>
    </ovf:StartupSection>
    <ovf:NetworkSection
        xmlns:vcloud="http://www.vmware.com/vcloud/v1.5"
        vcloud:href="https://vcloud.example.com/api/vApp/vapp-bba47763-0ce1-45b9-8470-ea29ba58c52f/networkSection/"
        vcloud:type="application/vnd.vmware.vcloud.networkSection+xml">
        <ovf:Info>The list of logical networks</ovf:Info>
        <ovf:Network
            ovf:name="VM Network">
            <ovf:Description>new description</ovf:Description>
        </ovf:Network>
    </ovf:NetworkSection>
    <NetworkConfigSection
        href="https://vcloud.example.com/api/vApp/vapp-bba47763-0ce1-45b9-8470-ea29ba58c52f/networkConfigSection/"
        ovf:required="false"
        type="application/vnd.vmware.vcloud.networkConfigSection+xml">
        <ovf:Info>The configuration parameters for logical networks</ovf:Info>
        <Link
            href="https://vcloud.example.com/api/vApp/vapp-bba47763-0ce1-45b9-8470-ea29ba58c52f/networkConfigSection/"
            rel="edit"
            type="application/vnd.vmware.vcloud.networkConfigSection+xml"/>
        <NetworkConfig
            networkName="VM Network">
            <Link
                href="https://vcloud.example.com/api/admin/network/82af5cfc-1f17-40b5-bc19-e8122a599ad2/action/reset"
                rel="repair"/>
            <Description>new description</Description>
            <Configuration>
                <IpScopes>
                    <IpScope>
                        <IsInherited>false</IsInherited>
                        <Gateway>192.168.254.1</Gateway>
                        <Netmask>255.255.255.0</Netmask>
                        <IsEnabled>true</IsEnabled>
                        <IpRanges>
                            <IpRange>
                                <StartAddress>192.168.254.100</StartAddress>
                                <EndAddress>192.168.254.199</EndAddress>
                            </IpRange>
                        </IpRanges>
                    </IpScope>
                </IpScopes>
                <FenceMode>isolated</FenceMode>
                <RetainNetInfoAcrossDeployments>false</RetainNetInfoAcrossDeployments>
            </Configuration>
            <IsDeployed>false</IsDeployed>
        </NetworkConfig>
    </NetworkConfigSection>
    <SnapshotSection
        href="https://vcloud.example.com/api/vApp/vapp-bba47763-0ce1-45b9-8470-ea29ba58c52f/snapshotSection"
        ovf:required="false"
        type="application/vnd.vmware.vcloud.snapshotSection+xml">
        <ovf:Info>Snapshot information section</ovf:Info>
    </SnapshotSection>
    <DateCreated>2013-02-14T13:14:23.850+02:00</DateCreated>
    <Owner
        type="application/vnd.vmware.vcloud.owner+xml">
        <User
            href="https://vcloud.example.com/api/admin/user/51e86769-9e2d-4edc-af4e-5d3606494cbf"
            name="system"
            type="application/vnd.vmware.admin.user+xml"/>
    </Owner>
    <InMaintenanceMode>false</InMaintenanceMode>
    <Children>
        <Vm
            deployed="false"
            href="https://vcloud.example.com/api/vApp/vm-89c84bd6-c6f2-4e4c-8a7d-c44a3489e2e4"
            id="urn:vcloud:vm:89c84bd6-c6f2-4e4c-8a7d-c44a3489e2e4"
            name="importedVapp"
            needsCustomization="false"
            status="8"
            type="application/vnd.vmware.vcloud.vm+xml">
            <VCloudExtension
                required="false">
                <vmext:VmVimInfo>
                    <vmext:VmVimObjectRef>
                        <vmext:VimServerRef
                            href="https://vcloud.example.com/api/admin/extension/vimServer/5b2f648b-9da7-4d7b-8212-6ed8a83f2102"
                            name="ConfigWizard Configured vCenter"
                            type="application/vnd.vmware.admin.vmwvirtualcenter+xml"/>
                        <vmext:MoRef>vm-277</vmext:MoRef>
                        <vmext:VimObjectType>VIRTUAL_MACHINE</vmext:VimObjectType>
                    </vmext:VmVimObjectRef>
                    <vmext:DatastoreVimObjectRef>
                        <vmext:VimServerRef
                            href="https://vcloud.example.com/api/admin/extension/vimServer/5b2f648b-9da7-4d7b-8212-6ed8a83f2102"
                            name="ConfigWizard Configured vCenter"
                            type="application/vnd.vmware.admin.vmwvirtualcenter+xml"/>
                        <vmext:MoRef>datastore-42</vmext:MoRef>
                        <vmext:VimObjectType>DATASTORE</vmext:VimObjectType>
                    </vmext:DatastoreVimObjectRef>
                    <vmext:HostVimObjectRef>
                        <vmext:VimServerRef
                            href="https://vcloud.example.com/api/admin/extension/vimServer/5b2f648b-9da7-4d7b-8212-6ed8a83f2102"
                            name="ConfigWizard Configured vCenter"
                            type="application/vnd.vmware.admin.vmwvirtualcenter+xml"/>
                        <vmext:MoRef>host-118</vmext:MoRef>
                        <vmext:VimObjectType>HOST</vmext:VimObjectType>
                    </vmext:HostVimObjectRef>
                    <vmext:VirtualDisksMaxChainLength>3</vmext:VirtualDisksMaxChainLength>
                </vmext:VmVimInfo>
            </VCloudExtension>
            <Link
                href="https://vcloud.example.com/api/vApp/vm-89c84bd6-c6f2-4e4c-8a7d-c44a3489e2e4/power/action/powerOn"
                rel="power:powerOn"/>
            <Link
                href="https://vcloud.example.com/api/vApp/vm-89c84bd6-c6f2-4e4c-8a7d-c44a3489e2e4/action/deploy"
                rel="deploy"
                type="application/vnd.vmware.vcloud.deployVAppParams+xml"/>
            <Link
                href="https://vcloud.example.com/api/vApp/vm-89c84bd6-c6f2-4e4c-8a7d-c44a3489e2e4"
                rel="edit"
                type="application/vnd.vmware.vcloud.vm+xml"/>
            <Link
                href="https://vcloud.example.com/api/vApp/vm-89c84bd6-c6f2-4e4c-8a7d-c44a3489e2e4"
                rel="remove"/>
            <Link
                href="https://vcloud.example.com/api/vApp/vm-89c84bd6-c6f2-4e4c-8a7d-c44a3489e2e4/metadata"
                rel="down"
                type="application/vnd.vmware.vcloud.metadata+xml"/>
            <Link
                href="https://vcloud.example.com/api/vApp/vm-89c84bd6-c6f2-4e4c-8a7d-c44a3489e2e4/complianceResult"
                rel="down"
                type="application/vnd.vmware.vm.complianceResult+xml"/>
            <Link
                href="https://vcloud.example.com/api/vApp/vm-89c84bd6-c6f2-4e4c-8a7d-c44a3489e2e4/productSections/"
                rel="down"
                type="application/vnd.vmware.vcloud.productSections+xml"/>
            <Link
                href="https://vcloud.example.com/api/vApp/vm-89c84bd6-c6f2-4e4c-8a7d-c44a3489e2e4/screen"
                rel="screen:thumbnail"/>
            <Link
                href="https://vcloud.example.com/api/vApp/vm-89c84bd6-c6f2-4e4c-8a7d-c44a3489e2e4/media/action/insertMedia"
                rel="media:insertMedia"
                type="application/vnd.vmware.vcloud.mediaInsertOrEjectParams+xml"/>
            <Link
                href="https://vcloud.example.com/api/vApp/vm-89c84bd6-c6f2-4e4c-8a7d-c44a3489e2e4/media/action/ejectMedia"
                rel="media:ejectMedia"
                type="application/vnd.vmware.vcloud.mediaInsertOrEjectParams+xml"/>
            <Link
                href="https://vcloud.example.com/api/vApp/vm-89c84bd6-c6f2-4e4c-8a7d-c44a3489e2e4/disk/action/attach"
                rel="disk:attach"
                type="application/vnd.vmware.vcloud.diskAttachOrDetachParams+xml"/>
            <Link
                href="https://vcloud.example.com/api/vApp/vm-89c84bd6-c6f2-4e4c-8a7d-c44a3489e2e4/disk/action/detach"
                rel="disk:detach"
                type="application/vnd.vmware.vcloud.diskAttachOrDetachParams+xml"/>
            <Link
                href="https://vcloud.example.com/api/vApp/vm-89c84bd6-c6f2-4e4c-8a7d-c44a3489e2e4/action/consolidate"
                rel="consolidate"/>
            <Link
                href="https://vcloud.example.com/api/vApp/vm-89c84bd6-c6f2-4e4c-8a7d-c44a3489e2e4/action/relocate"
                rel="relocate"
                type="application/vnd.vmware.vcloud.relocateVmParams+xml"/>
            <Link
                href="https://vcloud.example.com/api/vApp/vm-89c84bd6-c6f2-4e4c-8a7d-c44a3489e2e4/action/checkCompliance"
                rel="checkCompliance"/>
            <Link
                href="https://vcloud.example.com/api/vApp/vm-89c84bd6-c6f2-4e4c-8a7d-c44a3489e2e4/action/createSnapshot"
                rel="snapshot:create"
                type="application/vnd.vmware.vcloud.createSnapshotParams+xml"/>
            <Link
                href="https://vcloud.example.com/api/vApp/vm-89c84bd6-c6f2-4e4c-8a7d-c44a3489e2e4/action/reconfigureVm"
                name="importedVapp"
                rel="reconfigureVm"
                type="application/vnd.vmware.vcloud.vm+xml"/>
            <Link
                href="https://vcloud.example.com/api/vApp/vapp-bba47763-0ce1-45b9-8470-ea29ba58c52f"
                rel="up"
                type="application/vnd.vmware.vcloud.vApp+xml"/>
            <Description/>
            <ovf:VirtualHardwareSection
                xmlns:vcloud="http://www.vmware.com/vcloud/v1.5"
                ovf:transport=""
                vcloud:href="https://vcloud.example.com/api/vApp/vm-89c84bd6-c6f2-4e4c-8a7d-c44a3489e2e4/virtualHardwareSection/"
                vcloud:type="application/vnd.vmware.vcloud.virtualHardwareSection+xml">
                <ovf:Info>Virtual hardware requirements</ovf:Info>
                <ovf:System>
                    <vssd:ElementName>Virtual Hardware Family</vssd:ElementName>
                    <vssd:InstanceID>0</vssd:InstanceID>
                    <vssd:VirtualSystemIdentifier>importedVapp</vssd:VirtualSystemIdentifier>
                    <vssd:VirtualSystemType>vmx-08</vssd:VirtualSystemType>
                </ovf:System>
                <ovf:Item>
                    <rasd:Address>00:50:56:8d:7f:21</rasd:Address>
                    <rasd:AddressOnParent>0</rasd:AddressOnParent>
                    <rasd:AutomaticAllocation>false</rasd:AutomaticAllocation>
                    <rasd:Connection
                        vcloud:ipAddressingMode="DHCP"
                        vcloud:primaryNetworkConnection="true">VM Network</rasd:Connection>
                    <rasd:Description>E1000 ethernet adapter on "VM Network"</rasd:Description>
                    <rasd:ElementName>Network adapter 0</rasd:ElementName>
                    <rasd:InstanceID>1</rasd:InstanceID>
                    <rasd:ResourceSubType>E1000</rasd:ResourceSubType>
                    <rasd:ResourceType>10</rasd:ResourceType>
                </ovf:Item>
                <ovf:Item>
                    <rasd:Address>0</rasd:Address>
                    <rasd:Description>SCSI Controller</rasd:Description>
                    <rasd:ElementName>SCSI Controller 0</rasd:ElementName>
                    <rasd:InstanceID>2</rasd:InstanceID>
                    <rasd:ResourceSubType>lsilogicsas</rasd:ResourceSubType>
                    <rasd:ResourceType>6</rasd:ResourceType>
                </ovf:Item>
                <ovf:Item>
                    <rasd:AddressOnParent>0</rasd:AddressOnParent>
                    <rasd:Description>Hard disk</rasd:Description>
                    <rasd:ElementName>Hard disk 1</rasd:ElementName>
                    <rasd:HostResource
                        vcloud:busSubType="lsilogicsas"
                        vcloud:busType="6"
                        vcloud:capacity="40"/>
                    <rasd:InstanceID>2000</rasd:InstanceID>
                    <rasd:Parent>2</rasd:Parent>
                    <rasd:ResourceType>17</rasd:ResourceType>
                </ovf:Item>
                <ovf:Item>
                    <rasd:Address>0</rasd:Address>
                    <rasd:Description>IDE Controller</rasd:Description>
                    <rasd:ElementName>IDE Controller 0</rasd:ElementName>
                    <rasd:InstanceID>3</rasd:InstanceID>
                    <rasd:ResourceType>5</rasd:ResourceType>
                </ovf:Item>
                <ovf:Item>
                    <rasd:AddressOnParent>1</rasd:AddressOnParent>
                    <rasd:AutomaticAllocation>false</rasd:AutomaticAllocation>
                    <rasd:Description>CD/DVD Drive</rasd:Description>
                    <rasd:ElementName>CD/DVD Drive 1</rasd:ElementName>
                    <rasd:HostResource/>
                    <rasd:InstanceID>3002</rasd:InstanceID>
                    <rasd:Parent>3</rasd:Parent>
                    <rasd:ResourceType>15</rasd:ResourceType>
                </ovf:Item>
                <ovf:Item>
                    <rasd:AddressOnParent>0</rasd:AddressOnParent>
                    <rasd:AutomaticAllocation>false</rasd:AutomaticAllocation>
                    <rasd:Description>Floppy Drive</rasd:Description>
                    <rasd:ElementName>Floppy Drive 1</rasd:ElementName>
                    <rasd:HostResource/>
                    <rasd:InstanceID>8000</rasd:InstanceID>
                    <rasd:ResourceType>14</rasd:ResourceType>
                </ovf:Item>
                <ovf:Item
                    vcloud:href="https://vcloud.example.com/api/vApp/vm-89c84bd6-c6f2-4e4c-8a7d-c44a3489e2e4/virtualHardwareSection/cpu"
                    vcloud:type="application/vnd.vmware.vcloud.rasdItem+xml">
                    <rasd:AllocationUnits>hertz * 10^6</rasd:AllocationUnits>
                    <rasd:Description>Number of Virtual CPUs</rasd:Description>
                    <rasd:ElementName>1 virtual CPU(s)</rasd:ElementName>
                    <rasd:InstanceID>4</rasd:InstanceID>
                    <rasd:Reservation>0</rasd:Reservation>
                    <rasd:ResourceType>3</rasd:ResourceType>
                    <rasd:VirtualQuantity>1</rasd:VirtualQuantity>
                    <rasd:Weight>0</rasd:Weight>
                    <vmw:CoresPerSocket
                        ovf:required="false">1</vmw:CoresPerSocket>
                    <Link
                        href="https://vcloud.example.com/api/vApp/vm-89c84bd6-c6f2-4e4c-8a7d-c44a3489e2e4/virtualHardwareSection/cpu"
                        rel="edit"
                        type="application/vnd.vmware.vcloud.rasdItem+xml"/>
                </ovf:Item>
                <ovf:Item
                    vcloud:href="https://vcloud.example.com/api/vApp/vm-89c84bd6-c6f2-4e4c-8a7d-c44a3489e2e4/virtualHardwareSection/memory"
                    vcloud:type="application/vnd.vmware.vcloud.rasdItem+xml">
                    <rasd:AllocationUnits>byte * 2^20</rasd:AllocationUnits>
                    <rasd:Description>Memory Size</rasd:Description>
                    <rasd:ElementName>4096 MB of memory</rasd:ElementName>
                    <rasd:InstanceID>5</rasd:InstanceID>
                    <rasd:Reservation>0</rasd:Reservation>
                    <rasd:ResourceType>4</rasd:ResourceType>
                    <rasd:VirtualQuantity>4096</rasd:VirtualQuantity>
                    <rasd:Weight>0</rasd:Weight>
                    <Link
                        href="https://vcloud.example.com/api/vApp/vm-89c84bd6-c6f2-4e4c-8a7d-c44a3489e2e4/virtualHardwareSection/memory"
                        rel="edit"
                        type="application/vnd.vmware.vcloud.rasdItem+xml"/>
                </ovf:Item>
                <Link
                    href="https://vcloud.example.com/api/vApp/vm-89c84bd6-c6f2-4e4c-8a7d-c44a3489e2e4/virtualHardwareSection/"
                    rel="edit"
                    type="application/vnd.vmware.vcloud.virtualHardwareSection+xml"/>
                <Link
                    href="https://vcloud.example.com/api/vApp/vm-89c84bd6-c6f2-4e4c-8a7d-c44a3489e2e4/virtualHardwareSection/cpu"
                    rel="down"
                    type="application/vnd.vmware.vcloud.rasdItem+xml"/>
                <Link
                    href="https://vcloud.example.com/api/vApp/vm-89c84bd6-c6f2-4e4c-8a7d-c44a3489e2e4/virtualHardwareSection/cpu"
                    rel="edit"
                    type="application/vnd.vmware.vcloud.rasdItem+xml"/>
                <Link
                    href="https://vcloud.example.com/api/vApp/vm-89c84bd6-c6f2-4e4c-8a7d-c44a3489e2e4/virtualHardwareSection/memory"
                    rel="down"
                    type="application/vnd.vmware.vcloud.rasdItem+xml"/>
                <Link
                    href="https://vcloud.example.com/api/vApp/vm-89c84bd6-c6f2-4e4c-8a7d-c44a3489e2e4/virtualHardwareSection/memory"
                    rel="edit"
                    type="application/vnd.vmware.vcloud.rasdItem+xml"/>
                <Link
                    href="https://vcloud.example.com/api/vApp/vm-89c84bd6-c6f2-4e4c-8a7d-c44a3489e2e4/virtualHardwareSection/disks"
                    rel="down"
                    type="application/vnd.vmware.vcloud.rasdItemsList+xml"/>
                <Link
                    href="https://vcloud.example.com/api/vApp/vm-89c84bd6-c6f2-4e4c-8a7d-c44a3489e2e4/virtualHardwareSection/disks"
                    rel="edit"
                    type="application/vnd.vmware.vcloud.rasdItemsList+xml"/>
                <Link
                    href="https://vcloud.example.com/api/vApp/vm-89c84bd6-c6f2-4e4c-8a7d-c44a3489e2e4/virtualHardwareSection/media"
                    rel="down"
                    type="application/vnd.vmware.vcloud.rasdItemsList+xml"/>
                <Link
                    href="https://vcloud.example.com/api/vApp/vm-89c84bd6-c6f2-4e4c-8a7d-c44a3489e2e4/virtualHardwareSection/networkCards"
                    rel="down"
                    type="application/vnd.vmware.vcloud.rasdItemsList+xml"/>
                <Link
                    href="https://vcloud.example.com/api/vApp/vm-89c84bd6-c6f2-4e4c-8a7d-c44a3489e2e4/virtualHardwareSection/networkCards"
                    rel="edit"
                    type="application/vnd.vmware.vcloud.rasdItemsList+xml"/>
                <Link
                    href="https://vcloud.example.com/api/vApp/vm-89c84bd6-c6f2-4e4c-8a7d-c44a3489e2e4/virtualHardwareSection/serialPorts"
                    rel="down"
                    type="application/vnd.vmware.vcloud.rasdItemsList+xml"/>
                <Link
                    href="https://vcloud.example.com/api/vApp/vm-89c84bd6-c6f2-4e4c-8a7d-c44a3489e2e4/virtualHardwareSection/serialPorts"
                    rel="edit"
                    type="application/vnd.vmware.vcloud.rasdItemsList+xml"/>
            </ovf:VirtualHardwareSection>
            <ovf:OperatingSystemSection
                xmlns:vcloud="http://www.vmware.com/vcloud/v1.5"
                ovf:id="102"
                vcloud:href="https://vcloud.example.com/api/vApp/vm-89c84bd6-c6f2-4e4c-8a7d-c44a3489e2e4/operatingSystemSection/"
                vcloud:type="application/vnd.vmware.vcloud.operatingSystemSection+xml"
                vmw:osType="windows7Server64Guest">
                <ovf:Info>Specifies the operating system installed</ovf:Info>
                <ovf:Description>Microsoft Windows Server 2008 R2 (64-bit)</ovf:Description>
                <Link
                    href="https://vcloud.example.com/api/vApp/vm-89c84bd6-c6f2-4e4c-8a7d-c44a3489e2e4/operatingSystemSection/"
                    rel="edit"
                    type="application/vnd.vmware.vcloud.operatingSystemSection+xml"/>
            </ovf:OperatingSystemSection>
            <NetworkConnectionSection
                href="https://vcloud.example.com/api/vApp/vm-89c84bd6-c6f2-4e4c-8a7d-c44a3489e2e4/networkConnectionSection/"
                ovf:required="false"
                type="application/vnd.vmware.vcloud.networkConnectionSection+xml">
                <ovf:Info>Specifies the available VM network connections</ovf:Info>
                <PrimaryNetworkConnectionIndex>0</PrimaryNetworkConnectionIndex>
                <NetworkConnection
                    needsCustomization="true"
                    network="VM Network">
                    <NetworkConnectionIndex>0</NetworkConnectionIndex>
                    <IsConnected>false</IsConnected>
                    <MACAddress>00:50:56:8d:7f:21</MACAddress>
                    <IpAddressAllocationMode>DHCP</IpAddressAllocationMode>
                </NetworkConnection>
                <Link
                    href="https://vcloud.example.com/api/vApp/vm-89c84bd6-c6f2-4e4c-8a7d-c44a3489e2e4/networkConnectionSection/"
                    rel="edit"
                    type="application/vnd.vmware.vcloud.networkConnectionSection+xml"/>
            </NetworkConnectionSection>
            <GuestCustomizationSection
                href="https://vcloud.example.com/api/vApp/vm-89c84bd6-c6f2-4e4c-8a7d-c44a3489e2e4/guestCustomizationSection/"
                ovf:required="false"
                type="application/vnd.vmware.vcloud.guestCustomizationSection+xml">
                <ovf:Info>Specifies Guest OS Customization Settings</ovf:Info>
                <Enabled>false</Enabled>
                <ChangeSid>false</ChangeSid>
                <VirtualMachineId>89c84bd6-c6f2-4e4c-8a7d-c44a3489e2e4</VirtualMachineId>
                <JoinDomainEnabled>false</JoinDomainEnabled>
                <UseOrgSettings>false</UseOrgSettings>
                <AdminPasswordEnabled>false</AdminPasswordEnabled>
                <AdminPasswordAuto>true</AdminPasswordAuto>
                <AdminAutoLogonEnabled>false</AdminAutoLogonEnabled>
                <AdminAutoLogonCount>0</AdminAutoLogonCount>
                <ResetPasswordRequired>false</ResetPasswordRequired>
                <ComputerName>importedVap-001</ComputerName>
                <Link
                    href="https://vcloud.example.com/api/vApp/vm-89c84bd6-c6f2-4e4c-8a7d-c44a3489e2e4/guestCustomizationSection/"
                    rel="edit"
                    type="application/vnd.vmware.vcloud.guestCustomizationSection+xml"/>
            </GuestCustomizationSection>
            <RuntimeInfoSection
                xmlns:vcloud="http://www.vmware.com/vcloud/v1.5"
                vcloud:href="https://vcloud.example.com/api/vApp/vm-89c84bd6-c6f2-4e4c-8a7d-c44a3489e2e4/runtimeInfoSection"
                vcloud:type="application/vnd.vmware.vcloud.virtualHardwareSection+xml">
                <ovf:Info>Specifies Runtime info</ovf:Info>
            </RuntimeInfoSection>
            <SnapshotSection
                href="https://vcloud.example.com/api/vApp/vm-89c84bd6-c6f2-4e4c-8a7d-c44a3489e2e4/snapshotSection"
                ovf:required="false"
                type="application/vnd.vmware.vcloud.snapshotSection+xml">
                <ovf:Info>Snapshot information section</ovf:Info>
            </SnapshotSection>
            <VAppScopedLocalId>importedVapp</VAppScopedLocalId>
            <VmCapabilities
                href="https://vcloud.example.com/api/vApp/vm-89c84bd6-c6f2-4e4c-8a7d-c44a3489e2e4/vmCapabilities/"
                type="application/vnd.vmware.vcloud.vmCapabilitiesSection+xml">
                <Link
                    href="https://vcloud.example.com/api/vApp/vm-89c84bd6-c6f2-4e4c-8a7d-c44a3489e2e4/vmCapabilities/"
                    rel="edit"
                    type="application/vnd.vmware.vcloud.vmCapabilitiesSection+xml"/>
                <MemoryHotAddEnabled>false</MemoryHotAddEnabled>
                <CpuHotAddEnabled>false</CpuHotAddEnabled>
            </VmCapabilities>
            <StorageProfile
                href="https://vcloud.example.com/api/vdcStorageProfile/b520e879-71de-4d47-b2e1-e092aab97f61"
                name="*"
                type="application/vnd.vmware.vcloud.vdcStorageProfile+xml"/>
        </Vm>
    </Children>
    </VApp>""")

    def test_xml(self):
        obj = next(maloja.surveyor.survey_loads(VAppSurveyTests.xml), None)
        self.assertIsInstance(obj, maloja.types.App)
        self.assertEqual("importedVapp", obj.name)
        self.assertEqual(
            "https://vcloud.example.com/api/vApp/vapp-bba47763-0ce1-45b9-8470-ea29ba58c52f",
            obj.href)
        self.assertEqual(
            "application/vnd.vmware.vcloud.vApp+xml",
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

    def test_xml(self):
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