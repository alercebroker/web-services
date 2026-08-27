

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

    - Problema con clasificador, esto esta mencionado en Search_objects endpoint.

    - Cambios en oid tipo str, el valor de un oid str cambia al transformarlo a int.
    ValueError: Invalid ZTF object ID: 36028941602879580

    - La funcion encode de ztf no reconoce el oid 36028941602879580, es un error al transformar. 
    Una posible razon puede ser que solo acepta oid con el formato 'ZTFxxxxxx'.
    
    - Timeout en consulta sobre bdd, la razon es porque el indice (clasificador, class, ranking == 1) no se encuentra en
    el schema 'multisurvey_ztf'.

side_objects

    - Refactorizar endpoint, es el mismo codigo de list_object solo con un template distinto.


## Lightcurve API

Oid para testear: 36028941596001817

### Fix endpoints


lightcurve

    - Error de transformacion de object ztf, esto es mencionado en los problemas de list_object.

    - Llamada a bdd, la tabla ztf_dectection no tiene la columna sid debido a una actualizacion del repo pipeline. 
    La solucion consiste en actualizar 'db_plugins' junto con los imports en el repo 'multisurvey'.

    Cambiar import de 'db_plugins.db.sql.models' a 'db_plugins.db.sql.models_pipeline'.


periodogram

    - La tabla ztf forced photometry no tiene en sus atributos psfFlux, esto causa problema para procesar los datos de fp. 


external_sources

    - El listado de objects sobre DR se vuelve a reinciar dejando los checklist marcados.


dr_detections

    - Funciona.


download

    - Funciona.