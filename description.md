This API gives access to ALeRCE Annotated Alerts API, with corrected magnitudes, objects statistics and the object data. 

The following is a list of all the routes that can be used to query the database. They are organized by resource, meaning that similar queries are grouped.

When clicking on a route a list of the parameters accepted by this route, the different possible response codes and their content, with a detailed description of each field under `model`, is displayed. Clicking on the `Try it out` button it is possible to interactively test each route.

### Guided example
To retrieve object information, use the `objects` resource.
1. Open the `objects` group.
   Here there is a route (the "root" path under the `objects` resource: `/objects/`) for getting all objects given specified parameters.
   There is also a route for getting a single object by its ALeRCE ID: `/objects/{id}`. This pattern is used in several resources.
2. Click on the `/objects/{id}` resource.
   In the expanded content appears the parameters section with the `id` parameter, which is highlighted as required.
   Below, in the responses section, it shows that there are 2 possible response codes: 200 for success and 404 if the object isn't found. 
   In the success section there's also an `Example Value`, in this case a JSON with all its fields and generic values. 
   The meaning of each field can be found by clicking the `Model` tab.
   **All the available models are also described at the bottom of the page.**
3. Click the `Try it out` button and add an ALeRCE ID to the `id` parameter.
   Use this ID for a test: AL22mkfmiqypfgitk.
4. Click the `Execute` button and wait for the response.
   The response body should have the information of the object above. 
   Additionally, it shows the curl command of the query and the request URL.
