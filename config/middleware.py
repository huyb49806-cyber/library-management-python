class CorsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == "OPTIONS":
            from django.http import HttpResponse
            response = HttpResponse()
            self._set_headers(request, response)
            return response

        response = self.get_response(request)
        self._set_headers(request, response)
        return response

    def _set_headers(self, request, response):
        origin = request.headers.get("Origin", "*")
        response["Access-Control-Allow-Origin"] = origin if origin else "*"
        response["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With, Accept, Origin"
        response["Access-Control-Allow-Credentials"] = "true"
