from django import forms
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from guardian.shortcuts import get_perms_for_model, assign_perm, remove_perm

from .models import Attachment, Document


class StrippedCharField(forms.CharField):
	"""
		CharField that saves trimmed strings
	"""

	def to_python(self, value):
		super(StrippedCharField, self).to_python(value)
		if value is None:
			return None
		return value.strip()


class DocumentForm(forms.ModelForm):
	url_title = StrippedCharField(label=_('URL'), max_length=255, required=True)
	comment = StrippedCharField(label=_('Comment'), max_length=255, required=True)

	class Meta:
		model = Document
		fields = ['title', 'text', 'comment', 'url_title']

	FORBIDDEN_URLS = ["admin", "login", "logout", "documents", "minutes", "polls"]
	def clean_url_title(self):
		super().clean()
		url_title = self.cleaned_data['url_title']
		if url_title in self.FORBIDDEN_URLS:
			raise ValidationError(_('The URL used for this page is not allowed.'))
		if Document.objects.filter(url_title=url_title).exclude(id=self.instance.id).exists():
			raise ValidationError(_('The URL used for this page is already taken.'))
		return url_title

Document.Form = DocumentForm


class PermissionForm(forms.Form):
	"""
		Form that can be used to change permissions of a document object
	"""

	change_permission = forms.BooleanField(required=False)
	delete_permission = forms.BooleanField(required=False)
	view_permission = forms.BooleanField(required=False)
	group_name = forms.CharField(required=False)

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields["group_name"].widget = forms.HiddenInput()

	def save(self, model):
		group = Group.objects.get(name=self.cleaned_data["group_name"])
		possible_permissions = get_perms_for_model(model)
		for permission in possible_permissions:
			if "change" in str(permission):
				if self.cleaned_data["change_permission"]:
					assign_perm(permission.codename, group, model)
				else:
					remove_perm(permission.codename, group, model)
			elif "delete" in str(permission):
				if self.cleaned_data["delete_permission"]:
					assign_perm(permission.codename, group, model)
				else:
					remove_perm(permission.codename, group, model)
			elif "view" in str(permission):
				if self.cleaned_data["view_permission"]:
					assign_perm(permission.codename, group, model)
				else:
					remove_perm(permission.codename, group, model)


class AttachmentForm(forms.ModelForm):
	displayname = StrippedCharField(max_length=255, required=False)

	class Meta:
		model = Attachment
		exclude = ('document', 'index')
