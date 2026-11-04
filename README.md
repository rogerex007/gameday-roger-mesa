# Todo empieza con un evento — kit inicial

Este kit corresponde a la misión 02 del Game Pack AWS Event-Driven. Incluye la
infraestructura Terraform base para estudiarla y preparar su validación.
Las funciones Python son ejercicios pendientes de las siguientes misiones;
no procesan órdenes todavía. No contiene las pruebas ni las soluciones oficiales.

## Sube el kit desde tu navegador

1. Descomprime el ZIP. Sube su **contenido**, no el archivo ZIP ni la carpeta
   contenedora que pueda crear tu descompresor.
2. En GitHub, crea un repositorio en tu cuenta, por ejemplo `gameday-tu-nombre`.
   Para esta primera prueba debe ser público: Arena aún no tiene acceso a repos
   privados. No incluyas información personal ni secretos. Inicialízalo con un
   README para que aparezca el menú de archivos.
3. Abre **Add file → Upload files** y arrastra las carpetas `.github` y
   `game-packs`, junto con los archivos de la raíz de este kit. Activa mostrar
   archivos ocultos en tu explorador (en Linux, Ctrl+H) para ver `.github` y
   `.gitignore`. Guarda los cambios con **Commit changes** en `main`.
   Si GitHub propone una rama nueva, integra el cambio antes de enviar tu entrega.
4. Comprueba que la raíz de GitHub contiene `.github/` y `game-packs/`.
   Evita rutas como `kit/game-packs/` o `aws-event-driven/game-packs/`.
   Si ya tenías un repositorio vinculado, conserva ese repositorio y revisa los
   archivos antes de reemplazarlos. Subir el kit no elimina tu antigua carpeta
   `terraform/`: la ruta utilizada por el reto es la que aparece abajo.
5. Vuelve a Arena y vincula la URL HTTPS de ese repositorio en la misión 02.
6. En GitHub, abre el historial de commits, entra al commit que acabas de crear
   y usa **Copy full SHA**. Pega sus 40 caracteres en Arena y registra la entrega.

No necesitas instalar Git, Terraform ni AWS CLI en tu computador para estos pasos.
La estructura del repositorio debe quedar así:

```text
.github/workflows/terraform-lab.yml
.gitignore
README.md
LICENSE
ARENA-KIT.json
game-packs/aws-event-driven/
  terraform/
    main.tf
    variables.tf
    versions.tf
    outputs.tf
    terraform.tfvars.example
    .build/.gitkeep
  functions/
    orders/handler.py
    payments/handler.py
    inventory/handler.py
```

## Qué debes revisar en la misión 02

- Identifica el recorrido HTTP → Orders → EventBridge → SQS → Payments/Inventory.
- Ubica las tablas de DynamoDB, los permisos IAM y las colas de mensajes fallidos.
- Revisa las variables de Terraform y el prefijo único que asignará el instructor.
- Conserva `use_floci=true`. No agregues claves AWS ni ejecutes `terraform apply`
  en tu computador; el laboratorio se ejecutará en el entorno autorizado.
- Las tres funciones levantan `NotImplementedError` a propósito. Su implementación
  corresponde a las misiones 03 y 04.

## Estado actual de la evaluación

Arena comprueba automáticamente el commit y los archivos requeridos. Encontrar
los archivos no completa la misión ni concede los puntos de validación:
el runner aislado para Terraform todavía no está habilitado. El punto por
vincular el repositorio se registra por separado.

El workflow incluido se ejecuta manualmente desde **Actions → Revision inicial
del laboratorio → Run workflow**. Solo revisa formato y estructura Terraform;
no hace plan/apply ni verifica el comportamiento de las funciones. Sus resultados
no son una validación oficial de Arena. Los runners de laboratorio no se
registran directamente en los repositorios personales.

`ARENA-KIT.json` identifica la versión del kit y los hashes de los archivos
originales; puedes modificar el código para resolver los ejercicios.

Ayuda de GitHub: [subir archivos y carpetas desde el navegador](https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository).
