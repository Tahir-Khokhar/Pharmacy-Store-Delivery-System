from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from apps.prescriptions.models import Prescription, PrescriptionStatus

User = get_user_model()

class PrescriptionVerificationTests(TestCase):
    def setUp(self):
        self.customer = User.objects.create_user(username='rxpatient', email='patient@test.com', password='pass', role='CUSTOMER')
        self.pharmacist = User.objects.create_user(username='rxpharma', email='pharma@test.com', password='pass', role='PHARMACIST')
        self.prescription_file = SimpleUploadedFile(
            'rx_document.pdf',
            b'%PDF-1.4 Mock PDF Data for clinical verification',
            content_type='application/pdf'
        )

    def test_prescription_upload_and_status(self):
        rx = Prescription.objects.create(
            customer=self.customer,
            uploaded_file=self.prescription_file,
            doctor_name='Dr. House',
            clinic_hospital='Princeton Plainsboro',
            status=PrescriptionStatus.PENDING
        )
        self.assertIsNotNone(rx.prescription_number)
        self.assertTrue(rx.prescription_number.startswith('RX-'))
        self.assertEqual(rx.status, PrescriptionStatus.PENDING)
        self.assertFalse(rx.is_approved)

    def test_pharmacist_approval(self):
        rx = Prescription.objects.create(
            customer=self.customer,
            uploaded_file=self.prescription_file,
            status=PrescriptionStatus.PENDING
        )
        rx.status = PrescriptionStatus.APPROVED
        rx.verified_by = self.pharmacist
        rx.save()
        self.assertTrue(rx.is_approved)
        self.assertEqual(rx.verified_by, self.pharmacist)
