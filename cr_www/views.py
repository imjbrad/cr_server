__author__ = 'jordanbradley'
from rest_framework import views, generics, status, response, mixins, permissions as rest_permissions
from rest_framework import exceptions as rest_exceptions
from django import forms
import mandrill

class BetaAccessRequestForm(forms.Form):
    name = forms.CharField()
    email = forms.EmailField()
    introduction = forms.CharField()
    journalist_check = forms.BooleanField(required=False)

class RequestBetaAccess(generics.CreateAPIView):
    permission_classes = (rest_permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        form = BetaAccessRequestForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            introduction = form.cleaned_data['introduction']
            journalist_check = form.cleaned_data['journalist_check']

            mandrill_client = mandrill.Mandrill('ciRNiFQFVBPqRI1YSmQ2Vw')
            message = {
                "html": '<h3>'+name+'</h3><h3>'+email+'</h3><div>'+introduction+'</div><br><strong>Do you write for a news website or blog?</strong>'+('Yes' if journalist_check else 'No'),
                "subject": "Beta Access Request",
                "from_email": email,
                "from_name": name,
                "to": [{
                        "email": "jbradley@mica.edu",
                        "name": "Jordan Bradley",
                        "type": "to"
                    }],
                "headers": {
                    "Reply-To": email
                }
            }

            try:
                result = mandrill_client.messages.send(message=message, async=False)
                #pass
            except mandrill.Error, e:
                raise rest_exceptions.APIException(e)

            return response.Response(status=status.HTTP_201_CREATED)

        raise rest_exceptions.APIException("Invalid Submisssion")