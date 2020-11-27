from django import forms


class ServerForm(forms.Form):
    name = forms.CharField()
    ip = forms.GenericIPAddressField()
    user_root = forms.CharField()
    user_single = forms.CharField()
    password_root = forms.CharField()
    password_single = forms.CharField()

    def add_server(self):
        pass
