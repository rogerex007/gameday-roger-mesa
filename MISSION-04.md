# Misión 04 — Duplicados, fallos, DLQ y recuperación

Conserva Orders, Payments e Inventory de la misión 03 y añade el workflow
`.github/workflows/lab-integration-tests.yml`. Este kit no reemplaza tus handlers.
Los contratos de la misión 03 siguen vigentes; esta misión añade pruebas de
resiliencia y un receptor de operaciones de negocio simuladas.

## Operación observable

Una fila de idempotencia no demuestra que evitaste repetir un pago. En esta
misión, después de aceptar una orden como nueva, Payments e Inventory deben
registrar su operación mediante un POST a la URL que el juez entrega en
`OPERATIONS_URL`. Envía JSON con exactamente estos campos:

```json
{"service":"payments","orderId":"identificador-de-la-orden"}
```

Inventory utiliza `"service":"inventory"`. El receptor devuelve HTTP 201.
Cada POST representa un pago o una reserva simulada y se cuenta, incluso si es
un duplicado. No cobra dinero ni modifica inventario real. El registro pertenece
al juez y los handlers no pueden consultarlo, borrarlo ni reiniciarlo.

Puedes usar la biblioteca estándar, dentro del camino que ejecuta la operación
por primera vez, después de una escritura condicional aceptada:

```python
import json
import os
import urllib.request

operations_url = os.getenv("OPERATIONS_URL")
if operations_url:
    request = urllib.request.Request(
        operations_url,
        data=json.dumps({"service": "payments", "orderId": order_id}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=3) as response:
        if response.status != 201:
            raise RuntimeError("No se registró la operación simulada")
```

Adapta `service` para Inventory. En misión 03 no se proporciona esa variable y
puedes omitir esta llamada. No uses logs como evidencia de la operación.

## Duplicados

Conserva la clave `(eventId=orderId, service=payments|inventory)` y utiliza una
escritura condicional para aceptar una orden nueva. Un `messageId` o ID de
EventBridge puede cambiar en una nueva entrega: no debe definir la operación.

Cuando DynamoDB indique que la operación ya está registrada, reconoce el mensaje
como procesado, sin otro POST a `OPERATIONS_URL`. El juez entrega dos copias con
IDs de transporte distintos y comprueba su registro propio de operaciones.

## Fallos parciales

Procesa los registros del lote y devuelve en `batchItemFailures` únicamente los
`messageId` fallidos. Un registro inválido no debe impedir procesar los válidos:

```json
{"batchItemFailures":[{"itemIdentifier":"messageId-del-registro-inválido"}]}
```

No incluyas el identificador de orden en lugar del de mensaje. Los duplicados ya
procesados no son fallos y no deben aparecer en esa lista.

## Incidente y recuperación

Con `FAIL_PAYMENTS=true`, Payments debe lanzar una excepción o reportar el mensaje
como fallido **antes** de guardar idempotencia o ejecutar la operación. Inventory
debe continuar funcionando. El juez no elimina los mensajes fallidos; SQS los
reintenta y su política nativa los envía a la DLQ.

El laboratorio usa `maxReceiveCount=2` y visibilidad de 1 segundo para acortar la
prueba; no son valores recomendados para producción. No configures colas desde
tus handlers: el juez prepara y controla las políticas.

Después, el juez desactiva el fallo y vuelve a entregar el cuerpo del mensaje de
la DLQ. Debe procesarse correctamente una vez. Otra copia posterior debe ser un
éxito sin repetir el pago. El juez gestiona las recepciones y los acuses según el
resultado de los handlers; no ejecuta el servicio Lambda ni sus event mappings.

## Entrega

Con el evento abierto y misión 04 activa, conserva `ARENA_EVENT_ID` y la GitHub
App, y ejecuta **Actions → Evaluar misión 04 en Arena → Run workflow**. También
se dispara al cambiar el laboratorio o este workflow en la rama predeterminada.
Un nuevo commit genera una nueva entrega; para reintentar el mismo commit fallido
activa `retry` o usa **Re-run jobs** en la ejecución fallida (máximo cinco
intentos). Aprobar concede 30 puntos una sola vez.
Los workflows de otras misiones pueden dispararse por el mismo push y rechazar
la entrega porque su misión no está activa; revisa el de misión 04.

## Alcance

Las pruebas usan Floci y procesos Python sin privilegios en una VM sin red externa.
Los duplicados se prueban con entregas secuenciales y dentro de un mismo lote.
No se aplican tus archivos Terraform, no se despliegan Lambdas ni se usan AWS real
o pagos reales. La prueba no demuestra exactamente-una-vez en producción ni
atomicidad entre una escritura DynamoDB y un servicio externo: una caída entre
la marca de idempotencia y la operación requiere un diseño adicional, como un
outbox o una máquina de estados. El incidente de este reto ocurre antes de ambos.
