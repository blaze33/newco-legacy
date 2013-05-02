from django.http import HttpResponseRedirect, HttpResponsePermanentRedirect


class AjaxRedirectMiddleware(object):
    def process_response(self, request, response):
        if request.is_ajax():
            if type(response) == HttpResponseRedirect:
                response.status_code = 278
        return response


class MyMiddleware(object):
    def process_request(self, request):
        host = request.get_host()
        old_url = [host, request.path]
        new_host = "http://newco-prod.herokuapp.com"

        if 'google009a062b2cd3a7e6.html' in request.path:
            return
        if "newco-project" in old_url[0]:
            return HttpResponsePermanentRedirect(new_host + request.path)
        # No redirects required.
        return
