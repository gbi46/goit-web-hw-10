class DatabaseSwitchMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if "use_mongo" not in request.session:
            request.session["use_mongo"] = True
        return self.get_response(request)
