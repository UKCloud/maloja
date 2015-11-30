#!/usr/bin/env python
#   -*- encoding: UTF-8 -*-

from __future__ import print_function
from __future__ import unicode_literals

from collections import OrderedDict
from collections import namedtuple
import itertools
import unittest
import xml.etree.ElementTree as ET
import xml.sax.saxutils

from maloja.model import yaml_dumps
from maloja.model import yaml_loads

import maloja.surveyor
import maloja.types

namespace = "{http://www.vmware.com/vcloud/v1.5}"
template = """
<?xml version="1.0" encoding="UTF-8"?>
<VAppTemplate xmlns="http://www.vmware.com/vcloud/v1.5" xmlns:ovf="http://schemas.dmtf.org/ovf/envelope/1" goldMaster="false" status="8" name="Windows_2008_R2_STD_50GB_MediumHighMem_v1.0.2" id="urn:vcloud:vm:359b91ab-bdd1-4091-a30f-da18e264d311" href="https://api.vcd.portal.skyscapecloud.com/api/vAppTemplate/vm-359b91ab-bdd1-4091-a30f-da18e264d311" type="application/vnd.vmware.vcloud.vm+xml" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://schemas.dmtf.org/ovf/envelope/1 http://schemas.dmtf.org/ovf/envelope/1/dsp8023_1.1.0.xsd http://www.vmware.com/vcloud/v1.5 http://10.10.6.11/api/v1.5/schema/master.xsd">
    <Link rel="up" href="https://api.vcd.portal.skyscapecloud.com/api/vAppTemplate/vappTemplate-30348aad-0a01-4a3a-a7f2-079e9fea1073" type="application/vnd.vmware.vcloud.vAppTemplate+xml"/>
    <Link rel="storageProfile" href="https://api.vcd.portal.skyscapecloud.com/api/vdcStorageProfile/efb95611-9c69-49fa-8257-a0afdb18f39b" type="application/vnd.vmware.vcloud.vdcStorageProfile+xml"/>
    <Link rel="down" href="https://api.vcd.portal.skyscapecloud.com/api/vAppTemplate/vm-359b91ab-bdd1-4091-a30f-da18e264d311/metadata" type="application/vnd.vmware.vcloud.metadata+xml"/>
    <Link rel="down" href="https://api.vcd.portal.skyscapecloud.com/api/vAppTemplate/vm-359b91ab-bdd1-4091-a30f-da18e264d311/productSections/" type="application/vnd.vmware.vcloud.productSections+xml"/>
    <Description/>
    <NetworkConnectionSection href="https://api.vcd.portal.skyscapecloud.com/api/vAppTemplate/vm-359b91ab-bdd1-4091-a30f-da18e264d311/networkConnectionSection/" type="application/vnd.vmware.vcloud.networkConnectionSection+xml" ovf:required="false">
        <ovf:Info>Specifies the available VM network connections</ovf:Info>
        <PrimaryNetworkConnectionIndex>0</PrimaryNetworkConnectionIndex>
        <NetworkConnection needsCustomization="true" network="none">
            <NetworkConnectionIndex>0</NetworkConnectionIndex>
            <IsConnected>false</IsConnected>
            <MACAddress>00:50:56:01:0a:61</MACAddress>
            <IpAddressAllocationMode>NONE</IpAddressAllocationMode>
        </NetworkConnection>
    </NetworkConnectionSection>
    <GuestCustomizationSection href="https://api.vcd.portal.skyscapecloud.com/api/vAppTemplate/vm-359b91ab-bdd1-4091-a30f-da18e264d311/guestCustomizationSection/" type="application/vnd.vmware.vcloud.guestCustomizationSection+xml" ovf:required="false">
        <ovf:Info>Specifies Guest OS Customization Settings</ovf:Info>
        <Enabled>true</Enabled>
        <ChangeSid>true</ChangeSid>
        <VirtualMachineId>359b91ab-bdd1-4091-a30f-da18e264d311</VirtualMachineId>
        <JoinDomainEnabled>false</JoinDomainEnabled>
        <UseOrgSettings>false</UseOrgSettings>
        <AdminPasswordEnabled>false</AdminPasswordEnabled>
        <AdminPasswordAuto>true</AdminPasswordAuto>
        <AdminAutoLogonEnabled>false</AdminAutoLogonEnabled>
        <AdminAutoLogonCount>0</AdminAutoLogonCount>
        <ResetPasswordRequired>false</ResetPasswordRequired>
        <ComputerName>Windows2008R2</ComputerName>
    </GuestCustomizationSection>
    <VAppScopedLocalId>fb568dd5-fec6-476e-9021-aefb96a52044</VAppScopedLocalId>
    <DateCreated>2013-09-19T22:31:33.127+01:00</DateCreated>
</VAppTemplate>"""

queryresults_xml = """<?xml version="1.0" encoding="UTF-8"?>
<QueryResultRecords xmlns="http://www.vmware.com/vcloud/v1.5" name="vm" page="1" pageSize="25" total="12" href="https://api.vcd.portal.skyscapecloud.com/api/vms/query?page=1&amp;pageSize=25&amp;format=records&amp;filter=(container==https%3A//api.vcd.portal.skyscapecloud.com/api/vApp/vapp-68274d62-ad42-4db3-84ff-50145ec1ec95)" type="application/vnd.vmware.vcloud.query.records+xml" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.vmware.com/vcloud/v1.5 http://10.10.6.12/api/v1.5/schema/master.xsd">
    <Link rel="alternate" href="https://api.vcd.portal.skyscapecloud.com/api/vms/query?page=1&amp;pageSize=25&amp;format=references&amp;filter=(container==https%3A//api.vcd.portal.skyscapecloud.com/api/vApp/vapp-68274d62-ad42-4db3-84ff-50145ec1ec95)" type="application/vnd.vmware.vcloud.query.references+xml"/>
    <Link rel="alternate" href="https://api.vcd.portal.skyscapecloud.com/api/vms/query?page=1&amp;pageSize=25&amp;format=idrecords&amp;filter=(container==https%3A//api.vcd.portal.skyscapecloud.com/api/vApp/vapp-68274d62-ad42-4db3-84ff-50145ec1ec95)" type="application/vnd.vmware.vcloud.query.idrecords+xml"/>
    <VMRecord container="https://api.vcd.portal.skyscapecloud.com/api/vApp/vapp-68274d62-ad42-4db3-84ff-50145ec1ec95" containerName="vApp_4936.572.853fe2_3" guestOs="CentOS 4/5/6/7 (64-bit)" hardwareVersion="8" isBusy="false" isDeleted="false" isDeployed="true" isInMaintenanceMode="false" isPublished="false" isVAppTemplate="false" memoryMB="2048" name="Skyscape_CentOS_6_4_x64_50GB_Tiny_v1.0.1" numberOfCpus="1" status="POWERED_ON" storageProfileName="STANDARD-Any" vdc="https://api.vcd.portal.skyscapecloud.com/api/vdc/8bdd2156-f276-4718-8ea2-21560d89b8e1" href="https://api.vcd.portal.skyscapecloud.com/api/vApp/vm-1617dae0-1391-4b02-8981-3452b5d02314" isVdcEnabled="true" pvdcHighestSupportedHardwareVersion="9" taskStatus="success" task="https://api.vcd.portal.skyscapecloud.com/api/task/2c8a632e-9661-4d23-a60b-7d675062aeba" taskDetails=" " vmToolsVersion="0" networkName="NIC0_NET" taskStatusName="vappInstallTools"/>
    <VMRecord container="https://api.vcd.portal.skyscapecloud.com/api/vApp/vapp-68274d62-ad42-4db3-84ff-50145ec1ec95" containerName="vApp_4936.572.853fe2_3" guestOs="CentOS 4/5/6/7 (64-bit)" hardwareVersion="8" isBusy="false" isDeleted="false" isDeployed="true" isInMaintenanceMode="false" isPublished="false" isVAppTemplate="false" memoryMB="32768" name="Skyscape_CentOS_6_4_x64_50GB_Large_HighMem_v1.0.1-7" numberOfCpus="8" status="POWERED_ON" storageProfileName="STANDARD-Any" vdc="https://api.vcd.portal.skyscapecloud.com/api/vdc/8bdd2156-f276-4718-8ea2-21560d89b8e1" href="https://api.vcd.portal.skyscapecloud.com/api/vApp/vm-39d6f67e-cd3a-40fa-a945-c869571e798f" isVdcEnabled="true" pvdcHighestSupportedHardwareVersion="9" taskStatus="success" task="https://api.vcd.portal.skyscapecloud.com/api/task/4c871eac-c93a-47bf-a2dc-892cd9a8553f" taskDetails=" " vmToolsVersion="0" networkName="NIC0_NET" taskStatusName="vappDeploy"/>
    <VMRecord container="https://api.vcd.portal.skyscapecloud.com/api/vApp/vapp-68274d62-ad42-4db3-84ff-50145ec1ec95" containerName="vApp_4936.572.853fe2_3" guestOs="CentOS 4/5/6/7 (64-bit)" hardwareVersion="8" isBusy="false" isDeleted="false" isDeployed="true" isInMaintenanceMode="false" isPublished="false" isVAppTemplate="false" memoryMB="32768" name="Skyscape_CentOS_6_4_x64_50GB_Large_HighMem_v1.0.1-5" numberOfCpus="8" status="POWERED_ON" storageProfileName="STANDARD-Any" vdc="https://api.vcd.portal.skyscapecloud.com/api/vdc/8bdd2156-f276-4718-8ea2-21560d89b8e1" href="https://api.vcd.portal.skyscapecloud.com/api/vApp/vm-414bf09e-0fc2-466c-97e7-5b321bad1f29" isVdcEnabled="true" pvdcHighestSupportedHardwareVersion="9" taskStatus="success" task="https://api.vcd.portal.skyscapecloud.com/api/task/5c1be8be-5d6c-46ca-bb8d-779d60816865" taskDetails=" " vmToolsVersion="0" networkName="NIC0_NET" taskStatusName="vappDeploy"/>
    <VMRecord container="https://api.vcd.portal.skyscapecloud.com/api/vApp/vapp-68274d62-ad42-4db3-84ff-50145ec1ec95" containerName="vApp_4936.572.853fe2_3" guestOs="CentOS 4/5/6/7 (64-bit)" hardwareVersion="8" isBusy="false" isDeleted="false" isDeployed="true" isInMaintenanceMode="false" isPublished="false" isVAppTemplate="false" memoryMB="32768" name="Skyscape_CentOS_6_4_x64_50GB_Large_HighMem_v1.0.1-6" numberOfCpus="8" status="POWERED_ON" storageProfileName="STANDARD-Any" vdc="https://api.vcd.portal.skyscapecloud.com/api/vdc/8bdd2156-f276-4718-8ea2-21560d89b8e1" href="https://api.vcd.portal.skyscapecloud.com/api/vApp/vm-4512d190-d497-4a23-8033-a34cac18e67f" isVdcEnabled="true" pvdcHighestSupportedHardwareVersion="9" taskStatus="success" task="https://api.vcd.portal.skyscapecloud.com/api/task/455ee0fe-b375-4455-8054-6c7a309d2714" taskDetails=" " vmToolsVersion="0" networkName="NIC0_NET" taskStatusName="vappDeploy"/>
    <VMRecord container="https://api.vcd.portal.skyscapecloud.com/api/vApp/vapp-68274d62-ad42-4db3-84ff-50145ec1ec95" containerName="vApp_4936.572.853fe2_3" guestOs="CentOS 4/5/6/7 (64-bit)" hardwareVersion="8" isBusy="false" isDeleted="false" isDeployed="false" isInMaintenanceMode="false" isPublished="false" isVAppTemplate="false" memoryMB="32768" name="Skyscape_CentOS_6_4_x64_50GB_Large_HighMem_v1.0.1-10" numberOfCpus="8" status="POWERED_OFF" storageProfileName="STANDARD-Any" vdc="https://api.vcd.portal.skyscapecloud.com/api/vdc/8bdd2156-f276-4718-8ea2-21560d89b8e1" href="https://api.vcd.portal.skyscapecloud.com/api/vApp/vm-5ba3f2f1-ef71-49c1-925f-77c25b2912b0" isVdcEnabled="true" pvdcHighestSupportedHardwareVersion="9" taskStatus="error" task="https://api.vcd.portal.skyscapecloud.com/api/task/203d1fb6-e7d1-4d73-81f5-29d881aae5fc" taskDetails="  [ 68048ed0-8e9b-4fd5-b50b-6abd30db4f84 ] Unable to perform this action. Contact your cloud administr..." vmToolsVersion="8389" networkName="NIC0_NET" taskStatusName="vappDeploy"/>
    <VMRecord container="https://api.vcd.portal.skyscapecloud.com/api/vApp/vapp-68274d62-ad42-4db3-84ff-50145ec1ec95" containerName="vApp_4936.572.853fe2_3" guestOs="CentOS 4/5/6/7 (64-bit)" hardwareVersion="8" isBusy="false" isDeleted="false" isDeployed="true" isInMaintenanceMode="false" isPublished="false" isVAppTemplate="false" memoryMB="32768" name="Skyscape_CentOS_6_4_x64_50GB_Large_HighMem_v1.0.1-2" numberOfCpus="8" status="POWERED_ON" storageProfileName="STANDARD-Any" vdc="https://api.vcd.portal.skyscapecloud.com/api/vdc/8bdd2156-f276-4718-8ea2-21560d89b8e1" href="https://api.vcd.portal.skyscapecloud.com/api/vApp/vm-5c9eb6d3-8ad6-4435-b8a6-c5e5da9ad7e4" isVdcEnabled="true" pvdcHighestSupportedHardwareVersion="9" taskStatus="success" task="https://api.vcd.portal.skyscapecloud.com/api/task/1af7f610-2b7e-4d3a-b905-cf5b7a514728" taskDetails=" " vmToolsVersion="0" networkName="NIC0_NET" taskStatusName="vappDeploy"/>
    <VMRecord container="https://api.vcd.portal.skyscapecloud.com/api/vApp/vapp-68274d62-ad42-4db3-84ff-50145ec1ec95" containerName="vApp_4936.572.853fe2_3" guestOs="CentOS 4/5/6/7 (64-bit)" hardwareVersion="8" isBusy="false" isDeleted="false" isDeployed="true" isInMaintenanceMode="false" isPublished="false" isVAppTemplate="false" memoryMB="32768" name="Skyscape_CentOS_6_4_x64_50GB_Large_HighMem_v1.0.1-3" numberOfCpus="8" status="POWERED_ON" storageProfileName="STANDARD-Any" vdc="https://api.vcd.portal.skyscapecloud.com/api/vdc/8bdd2156-f276-4718-8ea2-21560d89b8e1" href="https://api.vcd.portal.skyscapecloud.com/api/vApp/vm-730e796d-43c2-4e07-848c-2969715acaed" isVdcEnabled="true" pvdcHighestSupportedHardwareVersion="9" taskStatus="success" task="https://api.vcd.portal.skyscapecloud.com/api/task/de6d9879-9ba9-4bd4-8492-080ed0311128" taskDetails=" " vmToolsVersion="0" networkName="NIC0_NET" taskStatusName="vappDeploy"/>
    <VMRecord container="https://api.vcd.portal.skyscapecloud.com/api/vApp/vapp-68274d62-ad42-4db3-84ff-50145ec1ec95" containerName="vApp_4936.572.853fe2_3" guestOs="CentOS 4/5/6/7 (64-bit)" hardwareVersion="8" isBusy="false" isDeleted="false" isDeployed="true" isInMaintenanceMode="false" isPublished="false" isVAppTemplate="false" memoryMB="32768" name="Skyscape_CentOS_6_4_x64_50GB_Large_HighMem_v1.0.1-9" numberOfCpus="8" status="POWERED_ON" storageProfileName="STANDARD-Any" vdc="https://api.vcd.portal.skyscapecloud.com/api/vdc/8bdd2156-f276-4718-8ea2-21560d89b8e1" href="https://api.vcd.portal.skyscapecloud.com/api/vApp/vm-8682f419-cfc3-43bf-bc4e-b8d9aa6cabf3" isVdcEnabled="true" pvdcHighestSupportedHardwareVersion="9" taskStatus="success" task="https://api.vcd.portal.skyscapecloud.com/api/task/5cfa02b5-b935-495f-a3d7-84bb87ee824c" taskDetails=" " vmToolsVersion="0" networkName="NIC0_NET" taskStatusName="vappDeploy"/>
    <VMRecord container="https://api.vcd.portal.skyscapecloud.com/api/vApp/vapp-68274d62-ad42-4db3-84ff-50145ec1ec95" containerName="vApp_4936.572.853fe2_3" guestOs="CentOS 4/5/6/7 (64-bit)" hardwareVersion="8" isBusy="false" isDeleted="false" isDeployed="true" isInMaintenanceMode="false" isPublished="false" isVAppTemplate="false" memoryMB="32768" name="Skyscape_CentOS_6_4_x64_50GB_Large_HighMem_v1.0.1" numberOfCpus="8" status="POWERED_ON" storageProfileName="STANDARD-Any" vdc="https://api.vcd.portal.skyscapecloud.com/api/vdc/8bdd2156-f276-4718-8ea2-21560d89b8e1" href="https://api.vcd.portal.skyscapecloud.com/api/vApp/vm-9adf2854-d68a-4f57-905e-1b73b74891b0" isVdcEnabled="true" pvdcHighestSupportedHardwareVersion="9" taskStatus="success" task="https://api.vcd.portal.skyscapecloud.com/api/task/8bfc8a2d-bc95-4792-b489-0b9417da3ec8" taskDetails=" " vmToolsVersion="0" networkName="NIC0_NET" taskStatusName="vappDeploy"/>
    <VMRecord container="https://api.vcd.portal.skyscapecloud.com/api/vApp/vapp-68274d62-ad42-4db3-84ff-50145ec1ec95" containerName="vApp_4936.572.853fe2_3" guestOs="CentOS 4/5/6/7 (64-bit)" hardwareVersion="8" isBusy="false" isDeleted="false" isDeployed="true" isInMaintenanceMode="false" isPublished="false" isVAppTemplate="false" memoryMB="32768" name="Skyscape_CentOS_6_4_x64_50GB_Large_HighMem_v1.0.1-4" numberOfCpus="8" status="POWERED_ON" storageProfileName="STANDARD-Any" vdc="https://api.vcd.portal.skyscapecloud.com/api/vdc/8bdd2156-f276-4718-8ea2-21560d89b8e1" href="https://api.vcd.portal.skyscapecloud.com/api/vApp/vm-9f6560f8-f76a-4c54-8b81-6032ff335056" isVdcEnabled="true" pvdcHighestSupportedHardwareVersion="9" taskStatus="success" task="https://api.vcd.portal.skyscapecloud.com/api/task/1d3454c9-6d2c-4ac5-a75c-c6ac8f411533" taskDetails=" " vmToolsVersion="0" networkName="NIC0_NET" taskStatusName="vappDeploy"/>
    <VMRecord container="https://api.vcd.portal.skyscapecloud.com/api/vApp/vapp-68274d62-ad42-4db3-84ff-50145ec1ec95" containerName="vApp_4936.572.853fe2_3" guestOs="CentOS 4/5/6/7 (64-bit)" hardwareVersion="8" isBusy="false" isDeleted="false" isDeployed="true" isInMaintenanceMode="false" isPublished="false" isVAppTemplate="false" memoryMB="32768" name="Skyscape_CentOS_6_4_x64_50GB_Large_HighMem_v1.0.1-8" numberOfCpus="8" status="POWERED_ON" storageProfileName="STANDARD-Any" vdc="https://api.vcd.portal.skyscapecloud.com/api/vdc/8bdd2156-f276-4718-8ea2-21560d89b8e1" href="https://api.vcd.portal.skyscapecloud.com/api/vApp/vm-c926f275-0244-4f5e-bd73-b3b56048c84d" isVdcEnabled="true" pvdcHighestSupportedHardwareVersion="9" taskStatus="success" task="https://api.vcd.portal.skyscapecloud.com/api/task/cec2df7a-0f49-436e-8b1e-d3928991c48d" taskDetails=" " vmToolsVersion="0" networkName="NIC0_NET" taskStatusName="vappDeploy"/>
    <VMRecord container="https://api.vcd.portal.skyscapecloud.com/api/vApp/vapp-68274d62-ad42-4db3-84ff-50145ec1ec95" containerName="vApp_4936.572.853fe2_3" guestOs="CentOS 4/5/6/7 (64-bit)" hardwareVersion="8" isBusy="false" isDeleted="false" isDeployed="false" isInMaintenanceMode="false" isPublished="false" isVAppTemplate="false" memoryMB="32768" name="Skyscape_CentOS_6_4_x64_50GB_Large_HighMem_v1.0.1-1" numberOfCpus="8" status="POWERED_OFF" storageProfileName="STANDARD-Any" vdc="https://api.vcd.portal.skyscapecloud.com/api/vdc/8bdd2156-f276-4718-8ea2-21560d89b8e1" href="https://api.vcd.portal.skyscapecloud.com/api/vApp/vm-f8ba1690-0537-4569-9227-899c67479834" isVdcEnabled="true" pvdcHighestSupportedHardwareVersion="9" taskStatus="error" task="https://api.vcd.portal.skyscapecloud.com/api/task/cea92703-441a-42ac-b9ce-35176d70cb79" taskDetails="  [ 559ee502-2063-49df-b10e-2300ac943d15 ] Unable to perform this action. Contact your cloud administr..." vmToolsVersion="8389" networkName="NIC0_NET" taskStatusName="vappDeploy"/>
</QueryResultRecords>"""

vm_xml = """<Vm xmlns="http://www.vmware.com/vcloud/v1.5" xmlns:ovf="http://schemas.dmtf.org/ovf/envelope/1" xmlns:vssd="http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_VirtualSystemSettingData" xmlns:rasd="http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_ResourceAllocationSettingData" xmlns:vmw="http://www.vmware.com/schema/ovf" xmlns:ovfenv="http://schemas.dmtf.org/ovf/environment/1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" needsCustomization="false" deployed="true" status="4" name="Skyscape_CentOS_6_4_x64_50GB_Tiny_v1.0.1" id="urn:vcloud:vm:1617dae0-1391-4b02-8981-3452b5d02314" href="https://api.vcd.portal.skyscapecloud.com/api/vApp/vm-1617dae0-1391-4b02-8981-3452b5d02314" type="application/vnd.vmware.vcloud.vm+xml" xsi:schemaLocation="http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_VirtualSystemSettingData http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2.22.0/CIM_VirtualSystemSettingData.xsd http://www.vmware.com/schema/ovf http://www.vmware.com/schema/ovf http://schemas.dmtf.org/ovf/envelope/1 http://schemas.dmtf.org/ovf/envelope/1/dsp8023_1.1.0.xsd http://schemas.dmtf.org/ovf/environment/1 http://schemas.dmtf.org/ovf/envelope/1/dsp8027_1.1.0.xsd http://www.vmware.com/vcloud/v1.5 http://10.10.6.14/api/v1.5/schema/master.xsd http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_ResourceAllocationSettingData http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2.22.0/CIM_ResourceAllocationSettingData.xsd">
    <Link rel="power:powerOff" href="https://api.vcd.portal.skyscapecloud.com/api/vApp/vm-1617dae0-1391-4b02-8981-3452b5d02314/power/action/powerOff"/>
    <Link rel="power:reboot" href="https://api.vcd.portal.skyscapecloud.com/api/vApp/vm-1617dae0-1391-4b02-8981-3452b5d02314/power/action/reboot"/>
    <Link rel="power:reset" href="https://api.vcd.portal.skyscapecloud.com/api/vApp/vm-1617dae0-1391-4b02-8981-3452b5d02314/power/action/reset"/>
    <Link rel="power:shutdown" href="https://api.vcd.portal.skyscapecloud.com/api/vApp/vm-1617dae0-1391-4b02-8981-3452b5d02314/power/action/shutdown"/>
    <Link rel="power:suspend" href="https://api.vcd.portal.skyscapecloud.com/api/vApp/vm-1617dae0-1391-4b02-8981-3452b5d02314/power/action/suspend"/>
    <Link rel="undeploy" href="https://api.vcd.portal.skyscapecloud.com/api/vApp/vm-1617dae0-1391-4b02-8981-3452b5d02314/action/undeploy" type="application/vnd.vmware.vcloud.undeployVAppParams+xml"/>
    <Link rel="edit" href="https://api.vcd.portal.skyscapecloud.com/api/vApp/vm-1617dae0-1391-4b02-8981-3452b5d02314" type="application/vnd.vmware.vcloud.vm+xml"/>
    <Link rel="down" href="https://api.vcd.portal.skyscapecloud.com/api/vApp/vm-1617dae0-1391-4b02-8981-3452b5d02314/metadata" type="application/vnd.vmware.vcloud.metadata+xml"/>
    <Link rel="down" href="https://api.vcd.portal.skyscapecloud.com/api/vApp/vm-1617dae0-1391-4b02-8981-3452b5d02314/productSections/" type="application/vnd.vmware.vcloud.productSections+xml"/>
    <Link rel="screen:thumbnail" href="https://api.vcd.portal.skyscapecloud.com/api/vApp/vm-1617dae0-1391-4b02-8981-3452b5d02314/screen"/>
    <Link rel="screen:acquireTicket" href="https://api.vcd.portal.skyscapecloud.com/api/vApp/vm-1617dae0-1391-4b02-8981-3452b5d02314/screen/action/acquireTicket"/>
    <Link rel="screen:acquireMksTicket" href="https://api.vcd.portal.skyscapecloud.com/api/vApp/vm-1617dae0-1391-4b02-8981-3452b5d02314/screen/action/acquireMksTicket" type="application/vnd.vmware.vcloud.mksTicket+xml"/>
    <Link rel="media:insertMedia" href="https://api.vcd.portal.skyscapecloud.com/api/vApp/vm-1617dae0-1391-4b02-8981-3452b5d02314/media/action/insertMedia" type="application/vnd.vmware.vcloud.mediaInsertOrEjectParams+xml"/>
    <Link rel="media:ejectMedia" href="https://api.vcd.portal.skyscapecloud.com/api/vApp/vm-1617dae0-1391-4b02-8981-3452b5d02314/media/action/ejectMedia" type="application/vnd.vmware.vcloud.mediaInsertOrEjectParams+xml"/>
    <Link rel="disk:attach" href="https://api.vcd.portal.skyscapecloud.com/api/vApp/vm-1617dae0-1391-4b02-8981-3452b5d02314/disk/action/attach" type="application/vnd.vmware.vcloud.diskAttachOrDetachParams+xml"/>
    <Link rel="disk:detach" href="https://api.vcd.portal.skyscapecloud.com/api/vApp/vm-1617dae0-1391-4b02-8981-3452b5d02314/disk/action/detach" type="application/vnd.vmware.vcloud.diskAttachOrDetachParams+xml"/>
    <Link rel="installVmwareTools" href="https://api.vcd.portal.skyscapecloud.com/api/vApp/vm-1617dae0-1391-4b02-8981-3452b5d02314/action/installVMwareTools"/>
    <Link rel="snapshot:create" href="https://api.vcd.portal.skyscapecloud.com/api/vApp/vm-1617dae0-1391-4b02-8981-3452b5d02314/action/createSnapshot" type="application/vnd.vmware.vcloud.createSnapshotParams+xml"/>
    <Link rel="reconfigureVm" href="https://api.vcd.portal.skyscapecloud.com/api/vApp/vm-1617dae0-1391-4b02-8981-3452b5d02314/action/reconfigureVm" name="Skyscape_CentOS_6_4_x64_50GB_Tiny_v1.0.1" type="application/vnd.vmware.vcloud.vm+xml"/>
    <Link rel="up" href="https://api.vcd.portal.skyscapecloud.com/api/vApp/vapp-68274d62-ad42-4db3-84ff-50145ec1ec95" type="application/vnd.vmware.vcloud.vApp+xml"/>
    <Description/>
    <ovf:VirtualHardwareSection xmlns:vcloud="http://www.vmware.com/vcloud/v1.5" ovf:transport="" vcloud:href="https://api.vcd.portal.skyscapecloud.com/api/vApp/vm-1617dae0-1391-4b02-8981-3452b5d02314/virtualHardwareSection/" vcloud:type="application/vnd.vmware.vcloud.virtualHardwareSection+xml">
        <ovf:Info>Virtual hardware requirements</ovf:Info>
        <ovf:System>
            <vssd:ElementName>Virtual Hardware Family</vssd:ElementName>
            <vssd:InstanceID>0</vssd:InstanceID>
            <vssd:VirtualSystemIdentifier>Skyscape_CentOS_6_4_x64_50GB_Tiny_v1.0.1</vssd:VirtualSystemIdentifier>
            <vssd:VirtualSystemType>vmx-08</vssd:VirtualSystemType>
        </ovf:System>
        <ovf:Item>
            <rasd:Address>00:50:56:01:aa:99</rasd:Address>
            <rasd:AddressOnParent>0</rasd:AddressOnParent>
            <rasd:AutomaticAllocation>true</rasd:AutomaticAllocation>
            <rasd:Connection vcloud:ipAddress="192.168.2.100" vcloud:primaryNetworkConnection="true" vcloud:ipAddressingMode="POOL">NIC0_NET</rasd:Connection>
            <rasd:Description>E1000 ethernet adapter on "NIC0_NET"</rasd:Description>
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
            <rasd:ResourceSubType>lsilogic</rasd:ResourceSubType>
            <rasd:ResourceType>6</rasd:ResourceType>
        </ovf:Item>
        <ovf:Item>
            <rasd:AddressOnParent>0</rasd:AddressOnParent>
            <rasd:Description>Hard disk</rasd:Description>
            <rasd:ElementName>Hard disk 1</rasd:ElementName>
            <rasd:HostResource vcloud:capacity="51200" vcloud:busSubType="lsilogic" vcloud:busType="6"/>
            <rasd:InstanceID>2000</rasd:InstanceID>
            <rasd:Parent>2</rasd:Parent>
            <rasd:ResourceType>17</rasd:ResourceType>
        </ovf:Item>
        <ovf:Item>
            <rasd:Address>1</rasd:Address>
            <rasd:Description>IDE Controller</rasd:Description>
            <rasd:ElementName>IDE Controller 1</rasd:ElementName>
            <rasd:InstanceID>3</rasd:InstanceID>
            <rasd:ResourceType>5</rasd:ResourceType>
        </ovf:Item>
        <ovf:Item>
            <rasd:AddressOnParent>0</rasd:AddressOnParent>
            <rasd:AutomaticAllocation>true</rasd:AutomaticAllocation>
            <rasd:Description>CD/DVD Drive</rasd:Description>
            <rasd:ElementName>CD/DVD Drive 1</rasd:ElementName>
            <rasd:HostResource/>
            <rasd:InstanceID>3002</rasd:InstanceID>
            <rasd:Parent>3</rasd:Parent>
            <rasd:ResourceSubType>vmware.cdrom.iso</rasd:ResourceSubType>
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
        <ovf:Item vcloud:href="https://api.vcd.portal.skyscapecloud.com/api/vApp/vm-1617dae0-1391-4b02-8981-3452b5d02314/virtualHardwareSection/cpu" vcloud:type="application/vnd.vmware.vcloud.rasdItem+xml">
            <rasd:AllocationUnits>hertz * 10^6</rasd:AllocationUnits>
            <rasd:Description>Number of Virtual CPUs</rasd:Description>
            <rasd:ElementName>1 virtual CPU(s)</rasd:ElementName>
            <rasd:InstanceID>4</rasd:InstanceID>
            <rasd:Reservation>0</rasd:Reservation>
            <rasd:ResourceType>3</rasd:ResourceType>
            <rasd:VirtualQuantity>1</rasd:VirtualQuantity>
            <rasd:Weight>0</rasd:Weight>
            <vmw:CoresPerSocket ovf:required="false">1</vmw:CoresPerSocket>
            <Link rel="edit" href="https://api.vcd.portal.skyscapecloud.com/api/vApp/vm-1617dae0-1391-4b02-8981-3452b5d02314/virtualHardwareSection/cpu" type="application/vnd.vmware.vcloud.rasdItem+xml"/>
        </ovf:Item>
        <ovf:Item vcloud:href="https://api.vcd.portal.skyscapecloud.com/api/vApp/vm-1617dae0-1391-4b02-8981-3452b5d02314/virtualHardwareSection/memory" vcloud:type="application/vnd.vmware.vcloud.rasdItem+xml">
            <rasd:AllocationUnits>byte * 2^20</rasd:AllocationUnits>
            <rasd:Description>Memory Size</rasd:Description>
            <rasd:ElementName>2048 MB of memory</rasd:ElementName>
            <rasd:InstanceID>5</rasd:InstanceID>
            <rasd:Reservation>0</rasd:Reservation>
            <rasd:ResourceType>4</rasd:ResourceType>
            <rasd:VirtualQuantity>2048</rasd:VirtualQuantity>
            <rasd:Weight>0</rasd:Weight>
            <Link rel="edit" href="https://api.vcd.portal.skyscapecloud.com/api/vApp/vm-1617dae0-1391-4b02-8981-3452b5d02314/virtualHardwareSection/memory" type="application/vnd.vmware.vcloud.rasdItem+xml"/>
        </ovf:Item>
        <Link rel="edit" href="https://api.vcd.portal.skyscapecloud.com/api/vApp/vm-1617dae0-1391-4b02-8981-3452b5d02314/virtualHardwareSection/" type="application/vnd.vmware.vcloud.virtualHardwareSection+xml"/>
        <Link rel="down" href="https://api.vcd.portal.skyscapecloud.com/api/vApp/vm-1617dae0-1391-4b02-8981-3452b5d02314/virtualHardwareSection/cpu" type="application/vnd.vmware.vcloud.rasdItem+xml"/>
        <Link rel="edit" href="https://api.vcd.portal.skyscapecloud.com/api/vApp/vm-1617dae0-1391-4b02-8981-3452b5d02314/virtualHardwareSection/cpu" type="application/vnd.vmware.vcloud.rasdItem+xml"/>
        <Link rel="down" href="https://api.vcd.portal.skyscapecloud.com/api/vApp/vm-1617dae0-1391-4b02-8981-3452b5d02314/virtualHardwareSection/memory" type="application/vnd.vmware.vcloud.rasdItem+xml"/>
        <Link rel="edit" href="https://api.vcd.portal.skyscapecloud.com/api/vApp/vm-1617dae0-1391-4b02-8981-3452b5d02314/virtualHardwareSection/memory" type="application/vnd.vmware.vcloud.rasdItem+xml"/>
        <Link rel="down" href="https://api.vcd.portal.skyscapecloud.com/api/vApp/vm-1617dae0-1391-4b02-8981-3452b5d02314/virtualHardwareSection/disks" type="application/vnd.vmware.vcloud.rasdItemsList+xml"/>
        <Link rel="edit" href="https://api.vcd.portal.skyscapecloud.com/api/vApp/vm-1617dae0-1391-4b02-8981-3452b5d02314/virtualHardwareSection/disks" type="application/vnd.vmware.vcloud.rasdItemsList+xml"/>
        <Link rel="down" href="https://api.vcd.portal.skyscapecloud.com/api/vApp/vm-1617dae0-1391-4b02-8981-3452b5d02314/virtualHardwareSection/media" type="application/vnd.vmware.vcloud.rasdItemsList+xml"/>
        <Link rel="down" href="https://api.vcd.portal.skyscapecloud.com/api/vApp/vm-1617dae0-1391-4b02-8981-3452b5d02314/virtualHardwareSection/networkCards" type="application/vnd.vmware.vcloud.rasdItemsList+xml"/>
        <Link rel="edit" href="https://api.vcd.portal.skyscapecloud.com/api/vApp/vm-1617dae0-1391-4b02-8981-3452b5d02314/virtualHardwareSection/networkCards" type="application/vnd.vmware.vcloud.rasdItemsList+xml"/>
        <Link rel="down" href="https://api.vcd.portal.skyscapecloud.com/api/vApp/vm-1617dae0-1391-4b02-8981-3452b5d02314/virtualHardwareSection/serialPorts" type="application/vnd.vmware.vcloud.rasdItemsList+xml"/>
        <Link rel="edit" href="https://api.vcd.portal.skyscapecloud.com/api/vApp/vm-1617dae0-1391-4b02-8981-3452b5d02314/virtualHardwareSection/serialPorts" type="application/vnd.vmware.vcloud.rasdItemsList+xml"/>
    </ovf:VirtualHardwareSection>
    <ovf:OperatingSystemSection xmlns:vcloud="http://www.vmware.com/vcloud/v1.5" ovf:id="101" vcloud:href="https://api.vcd.portal.skyscapecloud.com/api/vApp/vm-1617dae0-1391-4b02-8981-3452b5d02314/operatingSystemSection/" vcloud:type="application/vnd.vmware.vcloud.operatingSystemSection+xml" vmw:osType="centos64Guest">
        <ovf:Info>Specifies the operating system installed</ovf:Info>
        <ovf:Description>CentOS 4/5/6/7 (64-bit)</ovf:Description>
        <Link rel="edit" href="https://api.vcd.portal.skyscapecloud.com/api/vApp/vm-1617dae0-1391-4b02-8981-3452b5d02314/operatingSystemSection/" type="application/vnd.vmware.vcloud.operatingSystemSection+xml"/>
    </ovf:OperatingSystemSection>
    <NetworkConnectionSection href="https://api.vcd.portal.skyscapecloud.com/api/vApp/vm-1617dae0-1391-4b02-8981-3452b5d02314/networkConnectionSection/" type="application/vnd.vmware.vcloud.networkConnectionSection+xml" ovf:required="false">
        <ovf:Info>Specifies the available VM network connections</ovf:Info>
        <PrimaryNetworkConnectionIndex>0</PrimaryNetworkConnectionIndex>
        <NetworkConnection needsCustomization="false" network="NIC0_NET">
            <NetworkConnectionIndex>0</NetworkConnectionIndex>
            <IpAddress>192.168.2.100</IpAddress>
            <IsConnected>true</IsConnected>
            <MACAddress>00:50:56:01:aa:99</MACAddress>
            <IpAddressAllocationMode>POOL</IpAddressAllocationMode>
        </NetworkConnection>
        <Link rel="edit" href="https://api.vcd.portal.skyscapecloud.com/api/vApp/vm-1617dae0-1391-4b02-8981-3452b5d02314/networkConnectionSection/" type="application/vnd.vmware.vcloud.networkConnectionSection+xml"/>
    </NetworkConnectionSection>
    <GuestCustomizationSection href="https://api.vcd.portal.skyscapecloud.com/api/vApp/vm-1617dae0-1391-4b02-8981-3452b5d02314/guestCustomizationSection/" type="application/vnd.vmware.vcloud.guestCustomizationSection+xml" ovf:required="false">
        <ovf:Info>Specifies Guest OS Customization Settings</ovf:Info>
        <Enabled>true</Enabled>
        <ChangeSid>false</ChangeSid>
        <VirtualMachineId>1617dae0-1391-4b02-8981-3452b5d02314</VirtualMachineId>
        <JoinDomainEnabled>false</JoinDomainEnabled>
        <UseOrgSettings>false</UseOrgSettings>
        <AdminPasswordEnabled>false</AdminPasswordEnabled>
        <AdminPasswordAuto>true</AdminPasswordAuto>
        <AdminAutoLogonEnabled>false</AdminAutoLogonEnabled>
        <AdminAutoLogonCount>0</AdminAutoLogonCount>
        <ResetPasswordRequired>false</ResetPasswordRequired>
        <ComputerName>SkyscapeCen-001</ComputerName>
        <Link rel="edit" href="https://api.vcd.portal.skyscapecloud.com/api/vApp/vm-1617dae0-1391-4b02-8981-3452b5d02314/guestCustomizationSection/" type="application/vnd.vmware.vcloud.guestCustomizationSection+xml"/>
    </GuestCustomizationSection>
    <RuntimeInfoSection xmlns:vcloud="http://www.vmware.com/vcloud/v1.5" vcloud:href="https://api.vcd.portal.skyscapecloud.com/api/vApp/vm-1617dae0-1391-4b02-8981-3452b5d02314/runtimeInfoSection" vcloud:type="application/vnd.vmware.vcloud.virtualHardwareSection+xml">
        <ovf:Info>Specifies Runtime info</ovf:Info>
    </RuntimeInfoSection>
    <SnapshotSection href="https://api.vcd.portal.skyscapecloud.com/api/vApp/vm-1617dae0-1391-4b02-8981-3452b5d02314/snapshotSection" type="application/vnd.vmware.vcloud.snapshotSection+xml" ovf:required="false">
        <ovf:Info>Snapshot information section</ovf:Info>
    </SnapshotSection>
    <VAppScopedLocalId>Skyscape_CentOS_6_4_x64_50GB_Tiny_v1.0.1</VAppScopedLocalId>
    <ovfenv:Environment xmlns:ns10="http://www.vmware.com/schema/ovfenv" ovfenv:id="" ns10:vCenterId="vm-113593">
        <ovfenv:PlatformSection>
            <ovfenv:Kind>VMware ESXi</ovfenv:Kind>
            <ovfenv:Version>5.5.0</ovfenv:Version>
            <ovfenv:Vendor>VMware, Inc.</ovfenv:Vendor>
            <ovfenv:Locale>en</ovfenv:Locale>
        </ovfenv:PlatformSection>
        <ovfenv:PropertySection>
            <ovfenv:Property ovfenv:key="vCloud_UseSysPrep" ovfenv:value="None"/>
            <ovfenv:Property ovfenv:key="vCloud_bitMask" ovfenv:value="1"/>
            <ovfenv:Property ovfenv:key="vCloud_bootproto_0" ovfenv:value="static"/>
            <ovfenv:Property ovfenv:key="vCloud_computerName" ovfenv:value="SkyscapeCen-001"/>
            <ovfenv:Property ovfenv:key="vCloud_dns1_0" ovfenv:value=""/>
            <ovfenv:Property ovfenv:key="vCloud_dns2_0" ovfenv:value=""/>
            <ovfenv:Property ovfenv:key="vCloud_gateway_0" ovfenv:value="192.168.2.1"/>
            <ovfenv:Property ovfenv:key="vCloud_ip_0" ovfenv:value="192.168.2.100"/>
            <ovfenv:Property ovfenv:key="vCloud_macaddr_0" ovfenv:value="00:50:56:01:aa:99"/>
            <ovfenv:Property ovfenv:key="vCloud_markerid" ovfenv:value="2e8b0b74-4b25-43d4-839a-16963c1012de"/>
            <ovfenv:Property ovfenv:key="vCloud_netmask_0" ovfenv:value="255.255.255.0"/>
            <ovfenv:Property ovfenv:key="vCloud_numnics" ovfenv:value="1"/>
            <ovfenv:Property ovfenv:key="vCloud_primaryNic" ovfenv:value="0"/>
            <ovfenv:Property ovfenv:key="vCloud_reconfigToken" ovfenv:value="569753022"/>
            <ovfenv:Property ovfenv:key="vCloud_resetPassword" ovfenv:value="0"/>
            <ovfenv:Property ovfenv:key="vCloud_suffix_0" ovfenv:value=""/>
        </ovfenv:PropertySection>
        <ve:EthernetAdapterSection xmlns:ve="http://www.vmware.com/schema/ovfenv" xmlns="http://schemas.dmtf.org/ovf/environment/1" xmlns:oe="http://schemas.dmtf.org/ovf/environment/1">
            <ve:Adapter ve:mac="00:50:56:01:aa:99" ve:network="vxw-dvs-196-virtualwire-3812-sid-5449-dvs.VCDVSNIC0_NET-9e4bcfb7-529b-4b37-955b-" ve:unitNumber="7"/>
   
        </ve:EthernetAdapterSection>
    </ovfenv:Environment>
    <VmCapabilities href="https://api.vcd.portal.skyscapecloud.com/api/vApp/vm-1617dae0-1391-4b02-8981-3452b5d02314/vmCapabilities/" type="application/vnd.vmware.vcloud.vmCapabilitiesSection+xml">
        <Link rel="edit" href="https://api.vcd.portal.skyscapecloud.com/api/vApp/vm-1617dae0-1391-4b02-8981-3452b5d02314/vmCapabilities/" type="application/vnd.vmware.vcloud.vmCapabilitiesSection+xml"/>
        <MemoryHotAddEnabled>false</MemoryHotAddEnabled>
        <CpuHotAddEnabled>false</CpuHotAddEnabled>
    </VmCapabilities>
    <StorageProfile href="https://api.vcd.portal.skyscapecloud.com/api/vdcStorageProfile/f096e740-60c0-4e69-8f55-71cea40e44c3" name="STANDARD-Any" type="application/vnd.vmware.vcloud.vdcStorageProfile+xml"/>
</Vm>"""

vdc = """
name:
href:
"""

vapp = """
name: 'vapp name'
href:
creationDate:
isdeployed:
isEnabled:
isExpired:
isInMaintenanceMode:
ownerName:
status:
"""

vm_yaml = """
name: "Test data"
href:
guestOs: Ubuntu 12.04 LTS
hardwareVersion: 8
cpu:
memoryMB:
networkcards:
- name:
harddisks:
- name:
  capacity:
  bustype:
cd:
  description:
floppydisk:
  description: Floppy Drive 1
  media:
isBusy:
isDeleted:
isDeployed:
isInMaintenanceMode:
isPublished:
status:
storageProfileName:
vmToolsVersion:
networkconnections:
- name: NIC0_NET
  ip: 192.168.10.41
  isConnected: true
  macAddress: "00:50:56:01:aa:99"
ipAddressAllocationMode:
guestcustomization:
  enabled:
  changesid:
"""

class DataObject:

    _defaults = []

    @staticmethod
    def typecast(val):
        if val in ("true", "false"):
            return val == "true"
        try:
            if val.isdigit():
                return int(val)
        except AttributeError:
            return val
        else:
            return val

    def __init__(self, **kwargs):
        data = self._defaults + list(kwargs.items())
        for k, v in data:
            setattr(self, k, v)

    def feed_xml(self, tree, *args, **kwargs):
        fields = [k for k, v in self._defaults]
        attribs = ((attr, tree.attrib.get(attr)) for attr in tree.attrib if attr in fields)
        body = ((elem.tag, elem.text) for elem in tree if elem.tag in fields)
        for k, v in itertools.chain(attribs, body):
            setattr(self, k, self.typecast(v))
        return self

class Vm(DataObject):

    NetworkConnection = namedtuple(
        "NetworkConnection", ["name", "ip", "isConnected", "macAddress"]
    )

    _defaults = [
        ("guestOs", None),
        ("hardwareVersion", None),
        ("cpu", None),
        ("memoryMB", None),
        ("networkcards", []),
        ("harddisks", []),
        ("cd", None),
        ("floppydisk", None),
        ("isBusy", None),
        ("isDeleted", None),
        ("isDeployed", None),
        ("isInMaintenanceMode", None),
        ("isPublished", None),
        ("status", None),
        ("storageProfileName", None),
        ("vmToolsVersion", None),
        ("networkconnections", []),
        ("ipAddressAllocationMode", None),
        ("guestcustomization", None)
    ]

    def __init__(self, **kwargs):
        seq, typ = ("networkconnections", Vm.NetworkConnection)
        if seq in kwargs:
            kwargs[seq] = [typ(**{k: self.typecast(v) for k, v in i.items()}) for i in kwargs[seq]]

        super().__init__(**kwargs)

    def feed_xml(self, tree, ns="{http://www.vmware.com/vcloud/v1.5}"):
        if tree.tag in (ns + "VMRecord", ):
            super().feed_xml(tree, ns="{http://www.vmware.com/vcloud/v1.5}")
        if tree.tag == ns + "Vm":
            self.networkconnections = [
                Vm.NetworkConnection(
                    i.attrib["network"],
                    i.find(ns + "IpAddress").text,
                    True if i.find(ns + "IsConnected").text == "true" else False,
                    i.find(ns + "MACAddress").text)
                for i in tree.iter(ns + "NetworkConnection")]
        return self


class VmTests(unittest.TestCase):

    def test_feed_query_results(self):
        ns = "{http://www.vmware.com/vcloud/v1.5}"
        tree = ET.fromstring(queryresults_xml)
        record = next(tree.iter(ns + "VMRecord"))
        obj = Vm()
        self.assertIs(None, obj.guestOs)
        self.assertIs(obj, obj.feed_xml(record))
        self.assertEqual("STANDARD-Any", obj.storageProfileName)
        self.assertEqual(8, obj.hardwareVersion)
        self.assertEqual("CentOS 4/5/6/7 (64-bit)", obj.guestOs)

    def test_feed_vm(self):
        ns = "{http://www.vmware.com/vcloud/v1.5}"
        tree = ET.fromstring(vm_xml)
        obj = Vm()
        self.assertIs(obj, obj.feed_xml(tree))
        self.assertEqual(1, len(obj.networkconnections))

    def test_load_yaml(self):
        data = yaml_loads(vm_yaml)
        obj = Vm(**data)
        self.assertEqual(1, len(obj.networkconnections))
        self.assertIsInstance(obj.networkconnections[0], Vm.NetworkConnection)
