import os
from django import forms
from django.conf import settings
from .models import Prescription, PrescriptionStatus

class PrescriptionUploadForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ['uploaded_file', 'patient_name', 'doctor_name', 'clinic_hospital', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Any dosage instructions or remarks from your doctor'}),
        }

    def clean_uploaded_file(self):
        file = self.cleaned_data.get('uploaded_file')
        if not file:
            raise forms.ValidationError("Please select a file to upload.")

        ext = os.path.splitext(file.name)[1].lower()
        if ext not in settings.ALLOWED_PRESCRIPTION_EXTENSIONS:
            raise forms.ValidationError(f"Unsupported file format. Please upload {', '.join(settings.ALLOWED_PRESCRIPTION_EXTENSIONS)} files.")

        if file.size > settings.MAX_UPLOAD_SIZE:
            raise forms.ValidationError(f"File size exceeds 5MB limit. Please upload a smaller file.")

        return file


class PrescriptionReviewForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ['status', 'rejection_reason', 'notes']
        widgets = {
            'rejection_reason': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Required if rejected (e.g. illegible signature, expired date, wrong medication)'}),
            'notes': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Clinical remarks or dosage verified'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        reason = cleaned_data.get('rejection_reason')

        if status == PrescriptionStatus.REJECTED and not reason:
            self.add_error('rejection_reason', "You must provide a reason for rejecting the prescription.")

        return cleaned_data
