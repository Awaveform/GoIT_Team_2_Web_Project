from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi


class CustomFastAPI(FastAPI):
    def openapi(self):
        if self.openapi_schema:
            return self.openapi_schema
        openapi_schema = get_openapi(
            title=self.title,
            version=self.version,
            openapi_version=self.openapi_version,
            description=self.description,
            routes=self.routes,
        )

        # Add security definitions
        openapi_schema["components"]["securitySchemes"] = {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
            }
        }

        # Add security requirements
        openapi_schema["security"] = [{"BearerAuth": []}]

        return openapi_schema
