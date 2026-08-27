# Adaptacion de API's para ztf

## Object API

Oid para testear: 36028941602879580

### Fix endpoints

Seach_objects

    - El listado de clasificadores solo regresa a los que estan relacionados con LSST, la razon es porque el survey esta hardcodeado. 
    Revisar la funcion get_all_classifiers().

object_information

    - El endpoint y el template funciona con ZTF.

Classes_select

    - Refactor, se puede eliminar este endpoint debido a que no procesa los datos, solo ordena datos.

list_object

    - Problema con clasificador, se menciona en Search_objects endpoint.

    - Cambios en oid tipo str, el valor de un oid str cambia al transformarlo a int.
    ValueError: Invalid ZTF object ID: 36028941602879580
    
    - Timeout en consulta sobre bdd, la razon es porque el indice (clasificador, class, ranking == 1) no se encuentra en
    el schema 'multisurvey_ztf'.

    Observacion: Al ingresar el oid en la request tiene que ir con el siguiente formato 'ZTFxxxxx' respecto a ztf.
    Ingresar un oid de la siguiente manera '36028941602879580' genera error en la request.

side_objects

    - Refactorizar endpoint, es el mismo codigo de list_object solo con un template distinto.


## Lightcurve API

Oid para testear: 36028941596001817

### Fix endpoints


lightcurve

    - Llamada a bdd, la tabla ztf_dectection no tiene la columna sid debido a una actualizacion del repo pipeline. 
    La solucion consiste en actualizar 'db_plugins' junto con los imports en el repo 'multisurvey'.

    Cambiar import de 'db_plugins.db.sql.models' a 'db_plugins.db.sql.models_pipeline'.

    Observacion: Al ingresar el oid en la request tiene que ir con el siguiente formato 'ZTFxxxxx' respecto a ztf.
    Ingresar un oid de la siguiente manera '36028941602879580' genera error en la request.


periodogram

    - La tabla ztf forced photometry no tiene en sus atributos psfFlux, esto causa problema para procesar los datos de fp. 


external_sources

    - El listado de objects sobre DR se vuelve a reinciar dejando los checklist marcados.


dr_detections

    - Funciona.


download

    - Funciona.


## Magstats api
### Fix field types in model:
File: multisurveys-apis/src/magstat_api/models/magstats.py

Change the type of this fields to float
```
    dmdt_first: Optional[int] = None
    dm_first: Optional[int] = None
    sigmadm_first: Optional[int] = None
    ...
    dt_first: Optional[int] = None
    maglast: Optional[int] = None
    magfirst: Optional[int] = None
```


## Add the ztf string id to marset if into the endpoint. Using core idmapper idemapper decode id
File: multisurveys-apis/src/object_api/routes/rest.py, multisurveys-apis/src/object_api/routes/htmx.py
using
```
from ..services.idmapper.idmapper import encode_ids
in the routes functions to decode the id.