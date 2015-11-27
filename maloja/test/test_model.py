#!/usr/bin/env python
#   -*- encoding: UTF-8 -*-

from __future__ import print_function
from __future__ import unicode_literals

from collections import OrderedDict
from collections import namedtuple
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

vm = """
name: 'vm name'
href:
guestOs: ''
hardwareVersion:
hardware:
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
    media:
  floppydisk:
    description:
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
- name:
  ip:
  isConnected:
  macAddress:
ipAddressAllocationMode:
guestcustomization:
  enabled:
  changesid:
"""

class DataObject:

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

class Vm(DataObject):

    NetworkConnection = namedtuple(
        "NetworkConnection", ["name", "ip", "isConnected", "macAddress"]
    )

    @classmethod
    def from_xml(cls, tree):
        #ns = "http://www.vmware.com/vcloud/v1.5"
        data = OrderedDict([
            ("name", tree.attrib.get("name")),
            ("href", tree.attrib.get("href"))
        ])
        data["networkConnections"] = [
            cls.NetworkConnection(
                i.attrib["network"],
                #i.find("IpAddress").text,
                None, None, None)
            for i in tree.iter("NetworkConnection")]
        """
        guestOs: ''
        hardwareVersion:
        hardware:
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
            media:
          floppydisk:
            description:
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
        - name:
          ip:
          isConnected:
          macAddress:
        ipAddressAllocationMode:
        guestcustomization:
          enabled:
          changesid:
        """
        return cls(**data)


def survey_loads(xml, types={}):
    """
    TODO: Move back into surveyor.

    """
    ET.register_namespace("", "http://www.vmware.com/vcloud/v1.5")
    namespace = "{http://www.vmware.com/vcloud/v1.5}"
    tree = ET.fromstring(xml)
    typ = (types or {
        namespace + "VApp": maloja.types.App,
        namespace + "Catalog": maloja.types.Catalog,
        namespace + "Vm": maloja.types.Node,
        namespace + "Org": maloja.types.Org,
        namespace + "VAppTemplate": maloja.types.Template,
        namespace + "Vdc": maloja.types.Vdc
    }).get(tree.tag)
    try:
        yield typ.from_xml(tree)
    except AttributeError:
        attribs = (tree.attrib.get(f, None) for f in typ._fields)
        body = (
            item.text if item is not None else None
            for item in [
                tree.find(namespace + f[0].capitalize() + f[1:]) for f in typ._fields
            ]
        )
        data = (b if b is not None else a for a, b in zip(attribs, body))
        yield typ(*data)

class ParseTests(unittest.TestCase):

    def test_parse(self):
        types = {
            namespace + "VApp": maloja.types.App,
            namespace + "Catalog": maloja.types.Catalog,
            namespace + "Vm": Vm,
            namespace + "Org": maloja.types.Org,
            namespace + "VAppTemplate": maloja.types.Template,
            namespace + "Vdc": maloja.types.Vdc
        }
        print(vars(next(survey_loads(vm_xml, types))))

class YAMLTests(unittest.TestCase):

    def test_read_vm(self):
        mapping = yaml_loads(vm)
        #print(yaml_dumps(mapping))

    @unittest.skip("Pending model design.")
    def test_simple(self):
        inp = """\
        # example
        name:
          # details
          family: Smith   # very common
          given: Alice    # one of the siblings
        """

        code = yaml_loads(inp)
        code['name']['given'] = 'Bob'

        print(yaml_dumps(code), end='')
