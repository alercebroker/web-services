This API gives access to ALeRCE Annotated ZTF API, with corrected magnitudes, objects statistics and the object data. 

The following is a list of all the routes you can use to query our database. They are organized by resource which means similar queries are grouped. Usually a resource group has two or more routes, one for retreiving a single resource and one for retreiving a list.

When clicking on a route you get a list of the parameters received by this route and the different response codes and their content with a detailed description of each field under `model`. You can also click the `Try it out` button to interactively test each route.

### Guided example
To retreive one object information you can use the `objects` resource.
1. Open the `objects` group
   You can see that there is a route for getting all objects given specified parameters which is the "root" path under the `objects` resource: `/objects/`, and also a route for getting a single object by object id: `/object/{id}`. This pattern is used for all resources, where you can query a list of resources using the "root" path and a single resource using the `/{id}` path.
2. Now click on the `/objects/{id}` resource.
   In the expanded content you can see the parameters section with the `id` parameter that also shows required.
   Below that, you can see the responses section that shows this route has 2 reponse codes: 200 for success and 404 for when the object isn't found. 
   In the success code you can also see an example response which is a json with all the fields and generic values. To know what is the meaning of each field you can click the `Model` tab.
   **You can also check all the available models at the bottom of the page.**
3. Click the `Try it out` button and add an object id to the `id` parameter.
   Use this oid for a test: ZTF20aaelulu
4. Click the `execute` button and wait for it to finish.
   You will get the response body with the information of the object you just searched. Additionally you get the curl command of the query and the request url so you can get an idea of how the querystring is built.
