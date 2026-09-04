# Adaptación de APIs para ZTF

## Object API

OID para testear: `36028941602879580`

### Fix endpoints

**Search_objects**

- El listado de clasificadores solo regresa a los que están relacionados con LSST. La razón es porque el survey está hardcodeado.  
  Revisar la función `get_all_classifiers()`.

**object_information**

- El endpoint y el template funcionan con ZTF.

**Classes_select**

- Refactor. Se puede eliminar este endpoint debido a que no procesa los datos, solo ordena datos.

**list_object**

- Problema con clasificador, se menciona en el endpoint `Search_objects`.

- Cambios en OID tipo `str`. El valor de un OID `str` cambia al transformarlo a `int`.

  `ValueError: Invalid ZTF object ID: 36028941602879580`

- Timeout en consulta sobre BDD. La razón es porque el índice `(clasificador, class, ranking == 1)` no se encuentra en el schema `multisurvey_ztf`.

**Observación:** Al ingresar el OID en la request, tiene que ir con el siguiente formato: `'ZTFxxxxx'` respecto a ZTF.  
Ingresar un OID de la siguiente manera: `'36028941602879580'` genera un error en la request.

**side_objects**

- Refactorizar endpoint. Es el mismo código de `list_object`, solo con un template distinto.


## Lightcurve API

OID para testear: `36028941596001817`

### Fix endpoints

**lightcurve**

- Llamada a BDD. La tabla `ztf_detection` no tiene la columna `sid` debido a una actualización del repo `pipeline`.  
  La solución consiste en actualizar `db_plugins` junto con los imports en el repo `multisurvey`.

- Cambiar import de `db_plugins.db.sql.models` a `db_plugins.db.sql.models_pipeline`.

**Observación:** Al ingresar el OID en la request, tiene que ir con el siguiente formato: `'ZTFxxxxx'` respecto a ZTF.  
Ingresar un OID de la siguiente manera: `'36028941602879580'` genera un error en la request.

**periodogram**

- La tabla `ztf_forced_photometry` no tiene entre sus atributos `psfFlux`. Esto causa problemas para procesar los datos de FP.

**external_sources**

- El listado de objetos sobre DR se vuelve a reiniciar, dejando los checklists marcados.

**dr_detections**

- Funciona.

**download**

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
```


## Services

Listado de los servicios que se verán afectados por los cambios a implementar:

1. Explorer

2. Cliente de Python

3. SN Hunter