GENERATE CMS ID
----------------

Steps:

1. Copy the folder to a machine typically the Director Node (Undercloud Machine) that can reach VSD.

2. From the folder run the following command to generate CMS\_ID:

    ```
       python configure\_vsd\_cms\_id.py --server <vsd-ip-address>:<vsd-port> --serverauth <vsd-username>:<vsd-password> --organization <vsd-organization> --auth\_resource /me --serverssl True --base\_uri /nuage/api/<vsp-version>"
    ```

   Example command : 
    ```
         "python configure_vsd_cms_id.py --server 0.0.0.0:0 --serverauth username:password --organization organization --auth_resource /me --serverssl True --base_uri /nuage/api/v6"
    ```


3 . The CMS ID will be displayed on the terminal as well as a copy of it will be stored in a file "cms\_id.txt" in the same folder.
