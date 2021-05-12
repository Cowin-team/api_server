# API Server

## Instructions to run API Server

1. Make sure to have Python3.
2. Clone the repo and cd into it.  
    `git clone https://github.com/Cowin-team/api_server.git && cd api_server`
3. Create a virtual environment to keep global python clean  
    `python -m venv env`
4. Activate the environment  
    `source env/bin/activate`
5. Install the required packages  
    `pip install -r requirements.txt`
6. Install redis  
    Linux:  
        `sudo apt-get install redis-server`  
    Mac:  
        `brew install redis  
        brew services start redis`
7. Run the server  
    `python api.py`
   
## APIs
1. API to fetch all the resources supported by the app  
    URL: *http://35.223.206.45/resource/get*  
    Method: GET  
    Response:
    ```
    {
        "Kanyakumari": [
            "beds"
        ],
        "Karur": [
            "beds"
        ],
        "ariyalur": [
            "beds"
        ],
        "asgard": [
            "beds"
        ],
        "chengalpattu": [
            "beds"
        ],
        "chennai": [
            "beds",
            "oxygen"
        ],
        "coimbatore": [
            "beds",
            "oxygen"
        ],
        ......
    }
2.  API to fetch the resource values   
    Request URL: *http://35.223.206.45/sheet/fetch?city=chennai&resource=oxygen*  
    Method: GET  
    Response (same as "values" from google sheet apis): 
    ```
    [
        [
            "Barath Oxygen ",
            "",
            "",
            "",
            "https://www.google.com/maps/place/Bharath+Oxygen+Company/@13.1130195,80.1780218,15z/data=!4m2!3m1!1s0x0:0x83d43ca4184a24b9?sa=X&ved=2ahUKEwjwlK7BgrLwAhXEvZ4KHYwSDZoQ_BIwCnoECBQQAw",
            "",
            "yes",
            "",
            "",
            "",
            "",
            "9444003856, 8778731935"
        ]....
    ]
   
