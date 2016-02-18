..  Titling
    ##++::==~~--''``

Design file
:::::::::::

After you run a Maloja survey, you'll find a representation of your virtual infrastructure
in your output directory (typically named `.maloja`).

These files keep all the attributes of your Organisations, Templates, Vms etc in YAML
format.

You can paste the contents of these files together to describe to Maloja what
infrastructure you want it to build. Save it as your `design file`.

In order to build a new VApp, a design file contains:

    * One Vdc
    * One or more Networks
    * A Template for the VApp
    * Optionally, one or more Vms to add into the VApp
    * Optionally, a configuration for a Gateway

You need to present these items as a YAML list, which means that each is indented once and
preceded by a '-' character.

Example
=======

.. literalinclude:: ../test/issue_025-03.yaml
   :language: yaml

Plan command
============

You can check your design file with Maloja's `plan` command::

    maloja @options.private plan --input=my_design.yaml
    
The output will verify the objects in the file::

    2016-02-18 10:02:00,626 INFO    maloja|Using project proj_f9rb9m99.
    2016-02-18 10:02:00,676 INFO    maloja.planner|Vdc 'Skyscape Python Development (IL2-PROD-STANDARD)' is parent Vdc.
    2016-02-18 10:02:00,676 INFO    maloja.planner|Network 'USER_NET' is public network.
    2016-02-18 10:02:00,686 INFO    maloja.planner|Network 'Demo Network'  is private network.
    2016-02-18 10:02:00,686 INFO    maloja.planner|Template 'Demo Website' provides VApp template.
    2016-02-18 10:02:00,686 INFO    maloja.planner|Vm 'Web' to be created.
    2016-02-18 10:02:00,696 INFO    maloja.planner|Vm 'App' to be created.
    2016-02-18 10:02:00,696 INFO    maloja.planner|Vm 'DB' to be created.
    2016-02-18 10:02:00,696 INFO    maloja.planner|Gateway 'nft002bfi2' to modify rules.
    2016-02-18 10:02:00,706 INFO    maloja.planner|Approved 8 objects of 8
    2016-02-18 10:02:00,706 INFO    maloja.planner|OK.

Build command
=============

Once you're happy with the details of your design file, you can apply the `build` command
to get it made::

    maloja @options.private build --input=my_design.yaml

Inspect command
===============

Use the `inspect` command to check the results of a `build`. Pass in the design file you used and the
name of an entity to check::

    maloja @options.private inspect --input=my_design.yaml --name=my_asset_name

In this example, we passed in the name of a VApp we created. The non-complying items are marked
with `WARNINGS`::

    2016-02-18 10:10:04,349 INFO    maloja|Using project proj_f9rb9m99.
    Enter your API password:
    2016-02-18 10:10:13,159 INFO    maloja.planner|Vdc 'Skyscape Python Development (IL2-PROD-STANDARD)' is parent Vdc.
    2016-02-18 10:10:13,159 INFO    maloja.planner|Network 'USER_NET' is public network.
    2016-02-18 10:10:13,159 INFO    maloja.planner|Network 'Demo Network'  is private network.
    2016-02-18 10:10:13,159 INFO    maloja.planner|Template 'Demo Website' provides VApp template.
    2016-02-18 10:10:13,169 INFO    maloja.planner|Vm 'Web' to be created.
    2016-02-18 10:10:13,169 INFO    maloja.planner|Vm 'App' to be created.
    2016-02-18 10:10:13,169 INFO    maloja.planner|Vm 'DB' to be created.
    2016-02-18 10:10:13,179 INFO    maloja.planner|Gateway 'nft002bfi2' to modify rules.
    2016-02-18 10:10:13,179 INFO    maloja.planner|Approved 8 objects of 8
    2016-02-18 10:10:20,259 INFO    maloja.inspector.check_orgvdcnetwork|Network 'USER_NET' OK.
    2016-02-18 10:10:20,659 WARNING maloja.inspector.check_vapp|Found name: 'Skyscape_CentOS_6_4_x64_50GB_Tiny_v1.0.1', expected 'Demo Website'.
    2016-02-18 10:10:22,589 WARNING maloja.inspector.check_vms|VApp contains extra VMs.
    2016-02-18 10:10:24,049 WARNING maloja.inspector.check_vms|Found name: 'b064e3070ffd4e719be6560365b1bd79', expected 'App'.
    2016-02-18 10:10:25,989 WARNING maloja.inspector.check_vms|Found name: '2c92974018344be680aefe218c721049', expected 'DB'.
    2016-02-18 10:10:28,429 WARNING maloja.inspector.check_vms|Found name: 'Skyscape_CentOS_6_4_x64_50GB_Tiny_v1.0.1', expected 'DB'.
    2016-02-18 10:10:30,789 WARNING maloja.inspector.check_vms|Found name: '8f5184e531824b0883d9300c1e23918f', expected 'Web'.
    2016-02-18 10:10:32,819 INFO    maloja.inspector.check_gateway|Gateway 'nft002bfi2' OK.

