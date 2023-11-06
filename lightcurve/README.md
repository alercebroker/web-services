# ALeRCE Lightcurve API
## For developers
Run with `poetry run uvicorn api.api:app`
## HTMX endpoint
The htmx returned by this API's htmx endpoint emits the following events:
|       Event      |      Detail content     |     Level     |
|:----------------:|:-----------------------:|:-------------:|
| onDetectionClick | Clicked detection index | document.body |

