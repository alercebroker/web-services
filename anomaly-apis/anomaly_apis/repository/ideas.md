The domains are a set of abstract classes and method that the repositortys
must provide to the app.

The other files are implementations of the domain for certain data sources.

# whats espected from the domain

- function to get a paginated list of parsed objects (the model for objects is in object)
    - search params oid, score1 (tuple), score2(tuple), score 3(tuple), first mjd(tuple), ndets(tuple)
    - the search param can be used to order
- function to get single object fron the source.
    - search param just the oid

# issues to consider in the future
- the query of object model will return more attributes
- those attributes will be used to filter and order the response.