"""
Verificar que permisos tiene el usuario de API en OCI.
Usamos el SDK para introspeccionar.
"""
import oci
from app.core.config import settings

cfg = settings.oci
key_content = settings.OCI_KEY_CONTENT
literal_n = chr(92) + chr(110)
real_nl = chr(10)
if literal_n in key_content and real_nl not in key_content:
    key_content = key_content.replace(literal_n, real_nl)

oci_config = {
    "tenancy": cfg["tenancy"],
    "user": cfg["user"],
    "fingerprint": cfg["fingerprint"],
    "key_content": key_content,
    "region": cfg["region"],
}

print("=== Configuración OCI ===")
print(f"Tenancy: {cfg['tenancy']}")
print(f"User: {cfg['user']}")
print(f"Fingerprint: {cfg['fingerprint']}")
print(f"Region: {cfg['region']}")
print(f"Namespace: {cfg['namespace']}")
print(f"Bucket: {cfg['bucket']}")
print()

# Crear cliente de Identity para ver los grupos y permisos del usuario
identity = oci.identity.IdentityClient(oci_config)

# Obtener info del usuario
try:
    user_info = identity.get_user(cfg["user"]).data
    print("=== Info del Usuario ===")
    print(f"Nombre: {user_info.name}")
    print(f"Estado: {user_info.lifecycle_state}")
    print(f"Tipo: {user_info.user_type}")
except Exception as e:
    print(f"Error obteniendo usuario: {e}")

# Obtener grupos del usuario
try:
    groups = identity.list_user_group_memberships(
        compartment_id=cfg["tenancy"],
        user_id=cfg["user"]
    ).data
    print(f"\n=== Grupos del Usuario ({len(groups)} grupos) ===")
    for g in groups:
        print(f"  - {g.group_name} (ID: {g.group_id})")
except Exception as e:
    print(f"Error obteniendo grupos: {e}")

# Obtener políticas que aplican al usuario
print(f"\n=== Políticas (policies) del tenancy ===")
try:
    policies = identity.list_policies(
        compartment_id=cfg["tenancy"]
    ).data
    for p in policies:
        if p.lifecycle_state == "ACTIVE":
            print(f"\nPolicy: {p.name}")
            print(f"Statements:")
            for stmt in p.statements:
                if any(term in stmt.lower() for term in ['object', 'storage', 'bucket', 'allow']):
                    print(f"  - {stmt}")
except Exception as e:
    print(f"Error obteniendo políticas: {e}")

# Ahora probar acceso directo al bucket (sin listar buckets)
print("\n=== Test acceso directo al bucket ===")
object_storage = oci.object_storage.ObjectStorageClient(oci_config)

# Intentar obtener el namespace (esto suele funcionar)
try:
    ns = object_storage.get_namespace().data
    print(f"Namespace (GET): {ns}")
except Exception as e:
    print(f"Error get_namespace: {e}")

# Intentar listar objetos directamente (sin listar buckets primero)
try:
    objects = object_storage.list_objects(
        namespace_name=cfg["namespace"],
        bucket_name=cfg["bucket"]
    ).data
    print(f"Objetos en bucket: {len(objects.objects)}")
    for obj in objects.objects[:5]:
        print(f"  - {obj.name} ({obj.size} bytes)")
except Exception as e:
    print(f"Error list_objects: {e}")
    if hasattr(e, 'status'):
        print(f"  HTTP Status: {e.status}")
    if hasattr(e, 'code'):
        print(f"  OCI Code: {e.code}")
    if hasattr(e, 'message'):
        print(f"  Message: {e.message}")
