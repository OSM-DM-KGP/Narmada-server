# Narmada-server

Backend server for Narmada calls

The server side uses NodeJS framework and is written in Javascript. Nginx is used as an HTTP server to make the frontend accessible to the public. However, the NLP-related extraction tasks are handled better in Python. So a part of the server-side has been hosted with Flask, a micro web framework in Python. The Flask server makes API calls to the deep learning classifiers, featuring BERT, which returns the output. The output is further reflected in the frontend. The server sends information requested by the user interface via _RESTful API_, which supports cached responses on the frontend and enables the system to be scalable, thus allowing more users to use this service. 

API endpoints are publicly available, which would allow programmatic access to the server's functionalities. The major services provided are:

* **Fetching information** i.e. needs, availabilites and matches. Filtering by multiple conditions (such as matched or not, containing a particular resource) is also possible.

    ```
    GET /get?type=Need&isCompleted=false

    isCompleted: false / true {Completed already or not}
    skip: Skips first x results (int, default=0)
    text: Resource must contain this text (default absent)
    type: Need / Availability

    Response: array of jsons
    ```

* **Matching needs and availabilities** For a provided need / availability, top 20 matches are suggested based on resource similarity.

    ```
    GET /match?type=Need&id=591987020924260354

    id: id of resource that needs to be matched
    type: type of current resource that seeks matches

    Response: array of jsons
    ```

* **Elevating matched status** -- Whenever a suitable match is found for a need/ availability, the corresponding pair is marked as _Matched_, implying these cannot be matched again. Once the Match has been assigned to a volunteer, and is completed, the sys-admin can mark this match as _Completed_, which moves both these resources from the dashboard to the Completed Resources view.

    ```
    PUT /makeMatch?id1=X&id2=Y
    id1, id2: ids of two items that should be matched
    Currently does not have server side validation

    PUT /markCompleted?id1=X&id2=Y
    id1, id2: ids of two items that should be matched
    Currently does not have server side validation

    Response: Status code 201
    ```

* **Parsing and adding new information** -- The system allows creation of new need/availability for a provided text. This is achieved by parsing all information - resources, contact, location, quantity and source from the said text and returning these fields.

```
POST /parse?text=This is some text
text: Tweet text that should be parsed

Response: See request params for next call
```

```
POST /new
Params:
{ "lang": "en",
  "text": "Food as rice service",
  "Classification": "Need",
  "isCompleted": false,
  "Matched": -1,
  "Locations":
   { "Assam, India": { "lat": 26.0737044, "long": 83.18594580000001 } },
  "Resources": { "Food": "rice"},
  "Contact": { "Email": [], "Phone number": [] } 
	
}

Response: Status code 201
```