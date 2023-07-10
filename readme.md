##### OMS task group migration: 
    1. Generate list of file to migrate
        $ python3 migrate generate_url_list
        Output: key_list directiory is generated with the urls_list of file to migrate
    2. Upload the list to bucket:
        $ python3 migrate upload_urls_obj
        output: Uploaded key_list to a bucket called "URL_LISTS_SRC_BUCKET"

    3. Start migration task with: 
        $ python3 migrate oms_tasks <region-code>
        eg: 
            $ python3 migrate oms_tasks ap-southeast-3 //for singappre
            $ python3 migrate oms_tasks cn-east-3 // for ShangHai
$ 
