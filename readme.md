### System enviroment and Installation:
    - This script been tested in Linux enviroment with python 3.10.6
       sudo apt install python3-virtualenv
    - Getting start: 
        $ git clone https://github.com/leimpengpeng/hwc-migration-script.git
        
        $ cd hwc-migration-script
        $ virtualenv venv -> create vm enviroment
        $ source venv/bin/activate -> activate virtual enviroment 

        
        $ pip3 install -r requirements.txt 
### Enviroment setup:
    Please contact owner : for .env setup
### OMS task group migration: 
    1. Generate list of url_file for migrate
                $ python3 migrate generate_url_list
        Output: key_list directiory is generated with the urls_list of file to migrate
    2. Upload the list to bucket:
                $ python3 migrate upload_urls_obj
        output: Uploaded key_list to a bucket called "URL_LISTS_SRC_BUCKET"

    3. Start migration task with: 
            $ python3 migrate oms_tasks <region-code>
        eg: 
            $ python3 migrate oms_tasks ap-southeast-3 // for singappre
            $ python3 migrate oms_tasks cn-east-3 // for ShangHai

