# Misión 03 — Publica y procesa una orden

Completa los tres `handler(event, context)` en los archivos del kit inicial:

- `game-packs/aws-event-driven/functions/orders/handler.py`
- `game-packs/aws-event-driven/functions/payments/handler.py`
- `game-packs/aws-event-driven/functions/inventory/handler.py`

Este ZIP solo añade esta guía y `.github/workflows/app-integration-tests.yml`.
Conserva tus archivos Terraform y tus soluciones. No necesitas instalar librerías
en tu computador: el laboratorio incluye Python y boto3 1.38.18.

## Contrato de Orders

El evento tiene forma de petición de API Gateway: `body` contiene JSON y
`isBase64Encoded` indica si primero debes decodificarlo. El JSON incluye
`orderId`, `customerId` y `total`. El juez utiliza valores distintos en dos órdenes.

1. Guarda una orden en la tabla indicada por `ORDERS_TABLE`, con clave `orderId`.
   Conserva `customerId` y `total` (número DynamoDB); agrega `status="CREATED"`
   y `createdAt` (fecha como string).
2. Publica el evento en `EVENT_BUS_NAME` mediante EventBridge `put_events`:
   `Source="com.cloudopsarena.orders"`, `DetailType="OrderCreated"` y `Detail`
   con JSON que conserve `orderId`, `customerId` y `total`.
3. Comprueba errores de publicación. Devuelve `statusCode=201` y `body` JSON
   con al menos `orderId` y `status="CREATED"`.

## Contrato de Payments e Inventory

Cada handler recibe `Records`, una lista de mensajes SQS. Cada registro tiene
`messageId` y `body`; este último es JSON de EventBridge, cuyo objeto `detail`
contiene la orden. Procesa todos los registros del lote.

Registra el procesamiento en la tabla `IDEMPOTENCY_TABLE`, con clave compuesta:

- `eventId`: `orderId` de la orden (string).
- `service`: `payments` o `inventory`, según el consumidor (string).
- Guarda además `orderId` (string).

Devuelve `{"batchItemFailures": []}` cuando todos los mensajes válidos se
procesen. Usar `ConditionExpression="attribute_not_exists(eventId)"` permite
preparar la idempotencia; sus pruebas de duplicados, fallos y DLQ corresponden a
la misión 04 y no se evalúan todavía.

## Clientes AWS del laboratorio

Usa boto3 con `AWS_ENDPOINT_URL` y `AWS_REGION` proporcionados por el juez.
Las tablas y el bus también llegan por variables; no fijes sus nombres en código.
`AWS_ACCESS_KEY_ID` y `AWS_SECRET_ACCESS_KEY` contienen credenciales ficticias
locales. `FAIL_PAYMENTS=false` en esta misión. No agregues credenciales reales,
dependencias externas, Docker ni acceso a internet.

## Entrega desde GitHub Actions

Agrega el workflow incluido, conserva la variable `ARENA_EVENT_ID` del evento y
la autorización existente de la GitHub App. Con el evento abierto y la misión 03
activa, usa **Actions → Evaluar misión 03 en Arena → Run workflow** en la rama
predeterminada. Los cambios posteriores también disparan el workflow. El de
misión 02 puede indicar que esa misión no está activa; consulta el de misión 03.

Sigue las etapas en Arena o Actions. Si corriges el código, entrega un nuevo commit.
Para reintentar el mismo commit fallido o bloqueado activa `retry` (máximo cinco
intentos). Aprobar concede 20 puntos una sola vez.

## Qué se comprueba

El juez prepara DynamoDB, un bus y una regla EventBridge, y dos colas SQS dentro
de Floci en una VM sin red externa. Invoca Orders con JSON normal y base64,
verifica las órdenes persistidas y los mensajes que EventBridge entrega a ambas
colas. Después invoca los consumidores con los lotes SQS reales y verifica los
registros de procesamiento. No basta con devolver una respuesta de éxito.

Los handlers se ejecutan como procesos Python sin privilegios. Esta prueba no
utiliza el servicio Lambda, API Gateway ni event source mappings; no hace apply
del Terraform del participante ni acredita despliegues AWS. La VM y todos sus
recursos se eliminan al finalizar.
