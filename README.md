# Whodis
Entity Resolution API

Whodis provides an interface into an entity resolution system.

--------------------
## API
Entity resolution queries ("Who is this?") can be executed through the `resolve` endpoint

Entity resolution queries can be POSTed to `resolve` with a request body including:
  -- "api_key" : the value of your api_key
  -- "body" : JSON event-like query object ("this?")
  optional:
  -- "resolution" : the desired resolution level (0-1000, 1000 is highest resolution, 0 is default)
  -- "privacy" : the desired amount of privacy in the query response (-1000 to 1000)

-----------
## Privacy
  Whodis allows privacy to be included as noise in query responses in two ways.
  
  First, privacy can be added or removed from a single query with the 'privacy' parameter in the request body.
  
  Second, privacy can be injected into specific entities.
  Future query responses containing these entities will have additional privacy.

------------

Whodis is a free, public infrastructure project supported by donations from people like you.
