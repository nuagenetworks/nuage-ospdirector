Steps:

Clone this repo onto the undercloud director   

```
git clone https://github.com/nuagenetworks/nuage-ospdirector.git
cd nuage-ospdirector
git checkout OSPD13
cd tripleo-heat-templates-diff/
```

<b>For Non AVRS integration,</b>

Run either `sudo ./apply_patch.py` or `sudo python apply_patch.py` to patch the changes.   

<b>For AVRS integration,</b>

Run either `sudo ./apply_patch.py avrs` or  `sudo python apply_patch.py avrs` to patch the changes.


Verify that all the changes are applied. Ensure that there are no "Hunk #1 FAILED" errors. There might be "hunk ignored" warnings (based on running version) which can be ignored.   

Multiple versions are supported by the script: openstack-tripleo-heat-templates-8.0.2-4.el7ost.noarch, openstack-tripleo-heat-templates-8.0.2-43.el7ost.noarch, openstack-tripleo-heat-templates-8.0.4-20.el7ost.noarch, openstack-tripleo-heat-templates-8.0.7-4.el7ost.noarch, openstack-tripleo-heat-templates-8.0.7-21.el7ost.noarch and openstack-tripleo-heat-templates-8.2.0-6.2.el7ost.noarch

