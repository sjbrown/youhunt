import json

from django import forms

def clean_json(cleaned_data, key):
    jdata = cleaned_data[key]
    try:
        print 'Trying to loads the jdata', jdata
        json_data = json.loads(jdata)
    except Exception as e:
        print 'JSON PARSE FAIL', e
        raise forms.ValidationError("Invalid JSON data in %s" % key)
    return jdata

class InviteForm(forms.Form):
    invite_json = forms.CharField(label='Invite JSON', max_length=100*1024)

    def clean_invite_json(self):
        return clean_json(self.cleaned_data, 'invite_json')


class AcceptMissionForm(forms.Form):
    accept_json = forms.CharField(label='Accept JSON', max_length=100*1024)

    def clean_accept_json(self):
        return clean_json(self.cleaned_data, 'accept_json')
