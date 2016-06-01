GENERATE CMS ID
----------------

Steps:

1. Copy the folder to a machine that can reach VSD

2. From the folder run the following command to generate CMS\_ID:

   "python configure\_vsd\_cms\_id.py --server <vsd_ip_address>:<vsd_port> --serverauth <vsd_username>:<vsd_password> --organization <vsd_organization> --auth\_resource /me --serverssl True --base\_uri /nuage/api/<vsp_version (3.2/4.0)>"

   example command : 
     "python configure_vsd_cms_id.py --server 0.0.0.0:0 --serverauth username:password --organization organization --auth_resource /me --serverssl True --base_uri /nuage/api/v3_2"

3. The CMS ID will be displayed on the terminal as well as a copy of it will be stored in a file "cms\_id.txt" in the same folder.
