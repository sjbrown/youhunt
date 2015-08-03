import json

from django import forms

class InviteForm(forms.Form):
    invite_json = forms.CharField(label='Invite JSON', max_length=100*1024)

    def clean_invite_json(self):
        jdata = self.cleaned_data['invite_json']
        try:
            print 'Trying to loads the jdata', jdata
            json_data = json.loads(jdata)
        except Exception as e:
            print 'JSON PARSE FAIL', e
            raise forms.ValidationError("Invalid JSON data in invite_json")
        return jdata
