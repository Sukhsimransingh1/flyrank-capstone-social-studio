warning: in the working copy of 'app/main.py', LF will be replaced by CRLF the next time Git touches it
[1mdiff --git a/app/main.py b/app/main.py[m
[1mindex 3203d13..8489d32 100644[m
[1m--- a/app/main.py[m
[1m+++ b/app/main.py[m
[36m@@ -7,8 +7,9 @@[m [mfrom app.api.routes.variants import router as variants_router[m
 from app.core.config import settings[m
 from app.db.session import Base, check_database_connection, engine[m
 from app.models.post import Post  # noqa: F401[m
[32m+[m[32mfrom app.models.publish import PublishRecord  # noqa: F401[m
 from app.models.variant import Variant  # noqa: F401[m
[31m-[m
[32m+[m[32mfrom app.api.routes.publish import router as publish_router[m
 [m
 @asynccontextmanager[m
 async def lifespan(app: FastAPI):[m
[36m@@ -24,6 +25,7 @@[m [mapp = FastAPI([m
 )[m
 [m
 app.include_router(posts_router)[m
[32m+[m[32mapp.include_router(publish_router)[m
 app.include_router(variants_router)[m
 [m
 [m
[1mdiff --git a/app/models/__init__.py b/app/models/__init__.py[m
[1mindex 9eb801f..b59fc53 100644[m
[1m--- a/app/models/__init__.py[m
[1m+++ b/app/models/__init__.py[m
[36m@@ -1,7 +1,9 @@[m
 from app.models.post import Post[m
[32m+[m[32mfrom app.models.publish import PublishRecord[m
 from app.models.variant import Variant[m
 [m
 __all__ = [[m
     "Post",[m
     "Variant",[m
[32m+[m[32m    "PublishRecord",[m
 ][m
\ No newline at end of file[m
