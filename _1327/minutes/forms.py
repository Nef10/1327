from django import forms
from django.conf import settings
from django.contrib.auth.models import Group
from django.forms import inlineformset_factory

from _1327.documents.forms import DocumentForm
from _1327.minutes.models import Guest, MinutesDocument


class MinutesDocumentForm(DocumentForm):

	class Meta:
		model = MinutesDocument
		fields = ['title', 'date', 'moderator', 'participants', 'labels', 'state', 'text', 'comment', 'url_title']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields["state"].widget = forms.RadioSelect(choices=MinutesDocument.CHOICES)
		if not self.instance.participants.exists():
			self.initial['participants'] = [user.id for user in Group.objects.get(name=settings.STAFF_GROUP_NAME).user_set.all()]

	@classmethod
	def get_formset_factory(cls):
		return inlineformset_factory(MinutesDocument, Guest, form=GuestForm, can_delete=True, extra=1)

MinutesDocument.Form = MinutesDocumentForm


class GuestForm(forms.ModelForm):
	class Meta:
		model = Guest
		fields = ['name']

Guest.Form = GuestForm
