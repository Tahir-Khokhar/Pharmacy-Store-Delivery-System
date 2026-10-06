from decimal import Decimal
import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.files.base import ContentFile
from apps.accounts.models import User, UserRole, Address, Profile
from apps.products.models import Category, Product, DosageForm, Wishlist
from apps.inventory.models import Batch, StockTransaction, TransactionType, BatchStatus
from apps.cart.models import Cart, CartItem
from apps.prescriptions.models import Prescription, PrescriptionStatus
from apps.orders.models import Order, OrderItem, OrderStatus, PaymentMethod, PaymentStatus
from apps.payments.models import Payment
from apps.deliveries.models import Delivery, DeliveryStatus
from apps.reviews.models import Review
from apps.notifications.models import Notification, NotificationType

class Command(BaseCommand):
    help = 'Seeds complete, realistic clinical pharmacy data for PharmaCare.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting PharmaCare Database Seeding..."))

        # 1. Demo Users
        users_data = [
            ('admin', 'admin@pharmacare.local', 'admin123', UserRole.ADMIN, 'Alex', 'Vance', '+15551000', True),
            ('pharmacist', 'pharma@pharmacare.local', 'pharma123', UserRole.PHARMACIST, 'Dr. Sarah', 'Jenkins', '+15551001', False),
            ('inventory', 'inventory@pharmacare.local', 'inven123', UserRole.INVENTORY_MANAGER, 'Marcus', 'Stone', '+15551002', False),
            ('delivery', 'delivery@pharmacare.local', 'deliver123', UserRole.DELIVERY_STAFF, 'David', 'Miller', '+15551003', False),
            ('customer', 'customer@pharmacare.local', 'customer123', UserRole.CUSTOMER, 'Emily', 'Watson', '+15551004', False),
        ]

        users = {}
        for username, email, password, role, fname, lname, phone, is_super in users_data:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'role': role,
                    'first_name': fname,
                    'last_name': lname,
                    'phone': phone,
                    'is_staff': is_super or role in [UserRole.ADMIN, UserRole.PHARMACIST, UserRole.INVENTORY_MANAGER],
                    'is_superuser': is_super
                }
            )
            if created or not user.check_password(password):
                user.set_password(password)
                user.save()
            users[username] = user
            self.stdout.write(f"  User: {username} ({role}) ready.")

        # Customer Addresses
        customer = users['customer']
        addr1, _ = Address.objects.get_or_create(
            user=customer,
            title='Home',
            defaults={
                'full_name': 'Emily Watson',
                'phone': '+1 (555) 234-5678',
                'address_line': '442 Blossom Heights, Apt 3B',
                'area': 'Meadowlands',
                'city': 'Metro City',
                'province': 'NY',
                'postal_code': '10001',
                'landmark': 'Next to Central Park East',
                'is_default': True
            }
        )
        addr2, _ = Address.objects.get_or_create(
            user=customer,
            title='Office',
            defaults={
                'full_name': 'Emily Watson',
                'phone': '+1 (555) 234-5678',
                'address_line': '700 Financial Plaza, Floor 14',
                'area': 'Downtown',
                'city': 'Metro City',
                'province': 'NY',
                'postal_code': '10005',
                'landmark': 'Opposite City Center Mall',
                'is_default': False
            }
        )

        # 2. Categories
        categories_data = [
            ('Antibiotics & Antimicrobials', 'antibiotics', 'Prescription antibiotics, antibacterials and antimicrobial therapies.', 'bi-capsule'),
            ('Pain Relief & Anti-inflammatory', 'pain-relief', 'Analgesics, NSAIDs, antipyretics, and joint pain relief solutions.', 'bi-bandaid'),
            ('Cardiovascular & Blood Pressure', 'cardiovascular', 'Heart medications, antihypertensives, cholesterol regulators, and statins.', 'bi-heart-pulse'),
            ('Respiratory & Allergy', 'respiratory', 'Antihistamines, inhalers, cough syrups, and asthma management.', 'bi-lungs'),
            ('Gastrointestinal & Digestive', 'digestive-health', 'Antacids, proton pump inhibitors, laxatives, and gut health probiotics.', 'bi-shield-plus'),
            ('Diabetes & Endocrinology', 'diabetes-care', 'Blood glucose monitoring, insulin accessories, and metabolic support.', 'bi-droplet-half'),
            ('Vitamins & Supplements', 'vitamins-supplements', 'Dietary supplements, multivitamins, minerals, and immunity boosters.', 'bi-sun'),
            ('Medical Devices & Diagnostics', 'medical-devices', 'Blood pressure monitors, thermometers, nebulizers, and pulse oximeters.', 'bi-speedometer'),
            ('First Aid & Wound Care', 'first-aid', 'Sterile bandages, antiseptics, surgical tape, and emergency trauma kits.', 'bi-hospital'),
        ]

        categories = {}
        for name, slug, desc, icon in categories_data:
            cat, _ = Category.objects.get_or_create(
                slug=slug,
                defaults={'name': name, 'description': desc, 'icon': icon, 'active': True}
            )
            categories[slug] = cat

        # 3. Products
        today = timezone.now().date()
        products_data = [
            {
                'name': 'Amoxicillin Trihydrate',
                'slug': 'amoxicillin-500mg-gsk',
                'sku': 'MED-AMOX-500',
                'generic_name': 'Amoxicillin',
                'brand': 'Amoxil (GSK)',
                'category': categories['antibiotics'],
                'dosage_form': DosageForm.CAPSULE,
                'strength': '500mg',
                'description': 'Amoxicillin is a broad-spectrum penicillin antibiotic used to treat bacterial infections of the ear, nose, throat, urinary tract, and skin. Always complete the entire prescribed course.',
                'short_description': 'Broad-spectrum antibiotic for bacterial infections.',
                'price': Decimal('16.50'),
                'discount_price': Decimal('13.99'),
                'tax_rate': Decimal('5.00'),
                'stock_quantity': 45,
                'min_stock_level': 10,
                'unit': 'Box of 20 capsules',
                'manufacturer': 'GlaxoSmithKline Pharmaceuticals',
                'batch_number': 'AMX-2026-90',
                'expiry_date': today + datetime.timedelta(days=450),
                'prescription_required': True,
                'featured': True,
            },
            {
                'name': 'Azithromycin USP',
                'slug': 'azithromycin-250mg-pfizer',
                'sku': 'MED-AZITH-250',
                'generic_name': 'Azithromycin',
                'brand': 'Zithromax (Pfizer)',
                'category': categories['antibiotics'],
                'dosage_form': DosageForm.TABLET,
                'strength': '250mg',
                'description': 'Azithromycin is a macrolide antibiotic effective against respiratory infections, pneumonia, and strep throat. Requires medical practitioner review.',
                'short_description': 'Convenient once-daily macrolide antibiotic pack.',
                'price': Decimal('24.00'),
                'discount_price': Decimal('19.50'),
                'tax_rate': Decimal('5.00'),
                'stock_quantity': 30,
                'min_stock_level': 8,
                'unit': 'Pack of 6 tablets (Z-Pak)',
                'manufacturer': 'Pfizer Laboratories',
                'batch_number': 'PFZ-AZ-881',
                'expiry_date': today + datetime.timedelta(days=365),
                'prescription_required': True,
                'featured': True,
            },
            {
                'name': 'Ibuprofen Rapid Release',
                'slug': 'ibuprofen-400mg-advil',
                'sku': 'MED-IBU-400',
                'generic_name': 'Ibuprofen',
                'brand': 'Advil Liqui-Gels',
                'category': categories['pain-relief'],
                'dosage_form': DosageForm.CAPSULE,
                'strength': '400mg',
                'description': 'Targeted fast relief for headaches, dental pain, backache, muscular strains, arthritis, and fever. Over-the-counter safe medication.',
                'short_description': 'Fast-acting anti-inflammatory and pain reliever.',
                'price': Decimal('9.99'),
                'discount_price': None,
                'tax_rate': Decimal('5.00'),
                'stock_quantity': 120,
                'min_stock_level': 15,
                'unit': 'Bottle of 40 liquid capsules',
                'manufacturer': 'Haleon Consumer Health',
                'batch_number': 'ADV-400-019',
                'expiry_date': today + datetime.timedelta(days=600),
                'prescription_required': False,
                'featured': True,
            },
            {
                'name': 'Paracetamol Extra Strength',
                'slug': 'paracetamol-500mg-panadol',
                'sku': 'MED-PARA-500',
                'generic_name': 'Paracetamol / Acetaminophen',
                'brand': 'Panadol ActiFast',
                'category': categories['pain-relief'],
                'dosage_form': DosageForm.TABLET,
                'strength': '500mg',
                'description': 'Gentle on stomach antipyretic and analgesic. Formulated for fast absorption to combat acute body aches and fever.',
                'short_description': 'Stomach-gentle relief for pain and fever.',
                'price': Decimal('6.50'),
                'discount_price': Decimal('5.25'),
                'tax_rate': Decimal('5.00'),
                'stock_quantity': 200,
                'min_stock_level': 20,
                'unit': 'Pack of 24 tablets',
                'manufacturer': 'GSK Consumer Healthcare',
                'batch_number': 'PND-500-112',
                'expiry_date': today + datetime.timedelta(days=720),
                'prescription_required': False,
                'featured': True,
            },
            {
                'name': 'Atorvastatin Calcium',
                'slug': 'atorvastatin-20mg-lipitor',
                'sku': 'MED-ATOR-20',
                'generic_name': 'Atorvastatin',
                'brand': 'Lipitor (Viatris)',
                'category': categories['cardiovascular'],
                'dosage_form': DosageForm.TABLET,
                'strength': '20mg',
                'description': 'HMG-CoA reductase inhibitor that reduces LDL cholesterol and triglycerides in blood while elevating protective HDL levels.',
                'short_description': 'Cardiovascular lipid regulator for cholesterol balance.',
                'price': Decimal('32.00'),
                'discount_price': Decimal('27.00'),
                'tax_rate': Decimal('5.00'),
                'stock_quantity': 55,
                'min_stock_level': 10,
                'unit': 'Box of 30 tablets',
                'manufacturer': 'Viatris Inc.',
                'batch_number': 'LIP-020-55',
                'expiry_date': today + datetime.timedelta(days=500),
                'prescription_required': True,
                'featured': True,
            },
            {
                'name': 'Amlodipine Besylate',
                'slug': 'amlodipine-5mg-norvasc',
                'sku': 'MED-AMLO-5',
                'generic_name': 'Amlodipine',
                'brand': 'Norvasc',
                'category': categories['cardiovascular'],
                'dosage_form': DosageForm.TABLET,
                'strength': '5mg',
                'description': 'Calcium channel blocker used to treat arterial hypertension and prevent chronic chest angina. Relaxes coronary and peripheral vascular walls.',
                'short_description': 'Daily blood pressure and coronary angina therapy.',
                'price': Decimal('14.00'),
                'discount_price': None,
                'tax_rate': Decimal('5.00'),
                'stock_quantity': 8,  # LOW STOCK SAMPLE!
                'min_stock_level': 10,
                'unit': 'Box of 30 tablets',
                'manufacturer': 'Pfizer Global Health',
                'batch_number': 'NOR-005-77',
                'expiry_date': today + datetime.timedelta(days=320),
                'prescription_required': True,
                'featured': False,
            },
            {
                'name': 'Salbutamol Inhaler (Albuterol)',
                'slug': 'salbutamol-100mcg-ventolin',
                'sku': 'MED-VENT-100',
                'generic_name': 'Salbutamol Sulphate',
                'brand': 'Ventolin Evohaler',
                'category': categories['respiratory'],
                'dosage_form': DosageForm.INHALER,
                'strength': '100mcg/actuation',
                'description': 'Fast-acting bronchodilator for immediate relief of asthma symptoms, bronchospasm, and chronic obstructive pulmonary disease (COPD).',
                'short_description': 'Emergency bronchodilator relief inhaler (200 doses).',
                'price': Decimal('22.50'),
                'discount_price': Decimal('18.99'),
                'tax_rate': Decimal('5.00'),
                'stock_quantity': 40,
                'min_stock_level': 10,
                'unit': '200 Actuations Inhaler Device',
                'manufacturer': 'GlaxoSmithKline Respiratory',
                'batch_number': 'VNT-100-88',
                'expiry_date': today + datetime.timedelta(days=400),
                'prescription_required': True,
                'featured': True,
            },
            {
                'name': 'Cetirizine Hydrochloride',
                'slug': 'cetirizine-10mg-zyrtec',
                'sku': 'MED-CET-10',
                'generic_name': 'Cetirizine',
                'brand': 'Zyrtec Allergy',
                'category': categories['respiratory'],
                'dosage_form': DosageForm.TABLET,
                'strength': '10mg',
                'description': 'Second-generation non-drowsy antihistamine for hay fever, pet dander allergies, urticaria hives, and seasonal allergic rhinitis.',
                'short_description': '24-hour non-drowsy allergy symptom relief.',
                'price': Decimal('12.99'),
                'discount_price': None,
                'tax_rate': Decimal('5.00'),
                'stock_quantity': 90,
                'min_stock_level': 15,
                'unit': 'Pack of 30 tablets',
                'manufacturer': 'Johnson & Johnson Healthcare',
                'batch_number': 'ZYR-010-34',
                'expiry_date': today + datetime.timedelta(days=700),
                'prescription_required': False,
                'featured': False,
            },
            {
                'name': 'Omeprazole Delayed-Release',
                'slug': 'omeprazole-20mg-prilosec',
                'sku': 'MED-OMEP-20',
                'generic_name': 'Omeprazole',
                'brand': 'Prilosec OTC',
                'category': categories['digestive-health'],
                'dosage_form': DosageForm.CAPSULE,
                'strength': '20mg',
                'description': 'Proton pump inhibitor (PPI) that decreases stomach acid production. Treats GERD, persistent heartburn, and gastric ulcers.',
                'short_description': '24-hour heartburn and acid reflux protection.',
                'price': Decimal('18.00'),
                'discount_price': Decimal('15.50'),
                'tax_rate': Decimal('5.00'),
                'stock_quantity': 75,
                'min_stock_level': 12,
                'unit': 'Box of 28 capsules',
                'manufacturer': 'AstraZeneca Pharmaceuticals',
                'batch_number': 'OMP-2026-44',
                'expiry_date': today + datetime.timedelta(days=45),  # EXPIRING SOON SAMPLE!
                'prescription_required': False,
                'featured': True,
            },
            {
                'name': 'Metformin Hydrochloride',
                'slug': 'metformin-500mg-glucophage',
                'sku': 'MED-MET-500',
                'generic_name': 'Metformin',
                'brand': 'Glucophage',
                'category': categories['diabetes-care'],
                'dosage_form': DosageForm.TABLET,
                'strength': '500mg',
                'description': 'First-line biguanide medication for the management of type 2 diabetes. Improves insulin sensitivity and lowers hepatic glucose synthesis.',
                'short_description': 'Core glucose management for Type 2 Diabetes.',
                'price': Decimal('11.50'),
                'discount_price': None,
                'tax_rate': Decimal('5.00'),
                'stock_quantity': 80,
                'min_stock_level': 15,
                'unit': 'Box of 50 tablets',
                'manufacturer': 'Merck Healthcare',
                'batch_number': 'GLU-500-19',
                'expiry_date': today + datetime.timedelta(days=620),
                'prescription_required': True,
                'featured': False,
            },
            {
                'name': 'Vitamin C + Zinc Liposomal',
                'slug': 'vitamin-c-1000mg-zinc',
                'sku': 'SUP-VITC-1000',
                'generic_name': 'Ascorbic Acid + Zinc Citrate',
                'brand': 'ImmunoShield Gold',
                'category': categories['vitamins-supplements'],
                'dosage_form': DosageForm.SUPPLEMENT,
                'strength': '1000mg + 15mg Zinc',
                'description': 'High-potency antioxidant immune defense formula. Enhances natural collagen production, cellular repair, and seasonal resilience.',
                'short_description': 'High absorption immune & antioxidant booster.',
                'price': Decimal('15.99'),
                'discount_price': Decimal('12.99'),
                'tax_rate': Decimal('5.00'),
                'stock_quantity': 150,
                'min_stock_level': 20,
                'unit': 'Bottle of 60 veggie capsules',
                'manufacturer': 'PureWellness BioScience',
                'batch_number': 'IMM-C-2026',
                'expiry_date': today + datetime.timedelta(days=800),
                'prescription_required': False,
                'featured': True,
            },
            {
                'name': 'Digital Blood Pressure Monitor',
                'slug': 'omron-bp-monitor-upper-arm',
                'sku': 'DEV-OMRON-BP',
                'generic_name': 'Sphygmomanometer',
                'brand': 'Omron Healthcare M3',
                'category': categories['medical-devices'],
                'dosage_form': DosageForm.DEVICE,
                'strength': 'Upper Arm Cuff',
                'description': 'Clinically validated automatic upper-arm digital blood pressure monitor with irregular heartbeat detection and dual-user memory.',
                'short_description': 'Clinically validated automatic upper-arm monitor.',
                'price': Decimal('64.99'),
                'discount_price': Decimal('54.99'),
                'tax_rate': Decimal('5.00'),
                'stock_quantity': 25,
                'min_stock_level': 5,
                'unit': '1 Diagnostic Kit & Cuff',
                'manufacturer': 'Omron Healthcare Co.',
                'batch_number': 'OMR-M3-991',
                'expiry_date': None,
                'prescription_required': False,
                'featured': True,
            },
            {
                'name': 'Complete Sterile First Aid Kit',
                'slug': 'emergency-first-aid-kit-120pc',
                'sku': 'DEV-FAK-120',
                'generic_name': 'Emergency Medical Trauma Supplies',
                'brand': 'MedGuard Clinical',
                'category': categories['first-aid'],
                'dosage_form': DosageForm.CARE,
                'strength': '120 Pieces Emergency Kit',
                'description': 'Hard-shell trauma case equipped with sterile compresses, cleansing wipes, burn dressings, EMT shears, tourniquet, and waterproof bandages.',
                'short_description': '120-piece waterproof trauma & family emergency kit.',
                'price': Decimal('29.99'),
                'discount_price': None,
                'tax_rate': Decimal('5.00'),
                'stock_quantity': 60,
                'min_stock_level': 10,
                'unit': '1 Compact Hard Case',
                'manufacturer': 'MedGuard Safety Gear',
                'batch_number': 'FAK-120-99',
                'expiry_date': today + datetime.timedelta(days=900),
                'prescription_required': False,
                'featured': False,
            },
        ]

        products = {}
        for pdata in products_data:
            prod, _ = Product.objects.get_or_create(
                slug=pdata['slug'],
                defaults=pdata
            )
            products[prod.slug] = prod

            # Create corresponding Batch record
            if prod.batch_number and prod.expiry_date:
                batch, _ = Batch.objects.get_or_create(
                    product=prod,
                    batch_number=prod.batch_number,
                    defaults={
                        'expiry_date': prod.expiry_date,
                        'initial_quantity': prod.stock_quantity + 20,
                        'current_quantity': prod.stock_quantity,
                        'supplier': prod.manufacturer,
                        'cost_per_unit': prod.price * Decimal('0.55'),
                        'status': BatchStatus.ACTIVE
                    }
                )

        self.stdout.write(f"  {len(products)} products and batches registered.")

        # 4. Sample Prescriptions
        mock_pdf_content = ContentFile(b'%PDF-1.4 Mock Prescription Document for Emily Watson', name='rx_emily_watson.pdf')
        rx_approved, _ = Prescription.objects.get_or_create(
            prescription_number='RX-2026-9041',
            defaults={
                'customer': customer,
                'uploaded_file': mock_pdf_content,
                'patient_name': 'Emily Watson',
                'doctor_name': 'Dr. Robert Mitchell, MD',
                'clinic_hospital': 'St. Jude Heart & Health Clinic',
                'status': PrescriptionStatus.APPROVED,
                'verified_by': users['pharmacist'],
                'verified_at': timezone.now() - datetime.timedelta(days=2),
                'notes': 'Verified: Patient authorized for Atorvastatin 20mg 30-day course.'
            }
        )

        mock_pending_content = ContentFile(b'%PDF-1.4 Mock Pending Rx for Emily Watson', name='rx_pending_watson.pdf')
        rx_pending, _ = Prescription.objects.get_or_create(
            prescription_number='RX-2026-9042',
            defaults={
                'customer': customer,
                'uploaded_file': mock_pending_content,
                'patient_name': 'Emily Watson',
                'doctor_name': 'Dr. Lisa Cuddy, Pulmonologist',
                'clinic_hospital': 'Metro General Pulmonary Unit',
                'status': PrescriptionStatus.PENDING,
                'notes': 'Patient requested Ventolin Inhaler renewal.'
            }
        )

        # 5. Sample Completed Order (Delivered)
        order1, ord1_created = Order.objects.get_or_create(
            order_number='ORD-2026-1001',
            defaults={
                'customer': customer,
                'shipping_address': addr1,
                'shipping_address_snapshot': f"{addr1.full_name}\n{addr1.address_line}\n{addr1.city}, {addr1.postal_code}",
                'subtotal': Decimal('40.99'),
                'tax': Decimal('2.05'),
                'delivery_fee': Decimal('4.99'),
                'grand_total': Decimal('48.03'),
                'payment_method': PaymentMethod.ONLINE,
                'payment_status': PaymentStatus.PAID,
                'order_status': OrderStatus.DELIVERED,
                'requires_prescription': True,
                'prescription': rx_approved,
                'customer_notes': 'Please ring apartment 3B upon arrival.'
            }
        )
        if ord1_created:
            OrderItem.objects.create(
                order=order1,
                product=products['atorvastatin-20mg-lipitor'],
                product_name_snapshot='Atorvastatin Calcium 20mg',
                sku_snapshot='MED-ATOR-20',
                quantity=1,
                unit_price=Decimal('27.00'),
                tax=Decimal('1.35'),
                subtotal=Decimal('27.00'),
                prescription_required=True
            )
            OrderItem.objects.create(
                order=order1,
                product=products['amoxicillin-500mg-gsk'],
                product_name_snapshot='Amoxicillin 500mg',
                sku_snapshot='MED-AMOX-500',
                quantity=1,
                unit_price=Decimal('13.99'),
                tax=Decimal('0.70'),
                subtotal=Decimal('13.99'),
                prescription_required=True
            )
            Payment.objects.create(
                order=order1,
                transaction_id='TXN-2026-9901',
                payment_method='ONLINE',
                amount=order1.grand_total,
                status='PAID',
                paid_at=timezone.now() - datetime.timedelta(days=2),
                gateway_response='AuthCode: AUTH-ONLINE-88219 (APPROVED)'
            )
            Delivery.objects.create(
                order=order1,
                tracking_number='TRK-2026-001',
                delivery_staff=users['delivery'],
                delivery_address=order1.shipping_address_snapshot,
                status=DeliveryStatus.DELIVERED,
                assigned_at=timezone.now() - datetime.timedelta(days=2),
                delivered_at=timezone.now() - datetime.timedelta(days=1),
                recipient_name='Emily Watson',
                delivery_notes='Signed and delivered safely at apartment door.'
            )

        # 6. Sample In-Progress Order (Out for Delivery)
        order2, ord2_created = Order.objects.get_or_create(
            order_number='ORD-2026-1002',
            defaults={
                'customer': customer,
                'shipping_address': addr1,
                'shipping_address_snapshot': f"{addr1.full_name}\n{addr1.address_line}\n{addr1.city}, {addr1.postal_code}",
                'subtotal': Decimal('64.98'),
                'tax': Decimal('3.25'),
                'delivery_fee': Decimal('0.00'),  # Free over $50
                'grand_total': Decimal('68.23'),
                'payment_method': PaymentMethod.COD,
                'payment_status': PaymentStatus.PENDING,
                'order_status': OrderStatus.OUT_FOR_DELIVERY,
                'requires_prescription': False,
                'customer_notes': 'Call phone upon doorstep arrival.'
            }
        )
        if ord2_created:
            OrderItem.objects.create(
                order=order2,
                product=products['omron-bp-monitor-upper-arm'],
                product_name_snapshot='Digital Blood Pressure Monitor',
                sku_snapshot='DEV-OMRON-BP',
                quantity=1,
                unit_price=Decimal('54.99'),
                tax=Decimal('2.75'),
                subtotal=Decimal('54.99'),
                prescription_required=False
            )
            OrderItem.objects.create(
                order=order2,
                product=products['ibuprofen-400mg-advil'],
                product_name_snapshot='Ibuprofen Rapid Release',
                sku_snapshot='MED-IBU-400',
                quantity=1,
                unit_price=Decimal('9.99'),
                tax=Decimal('0.50'),
                subtotal=Decimal('9.99'),
                prescription_required=False
            )
            Payment.objects.create(
                order=order2,
                transaction_id='TXN-2026-9902',
                payment_method='COD',
                amount=order2.grand_total,
                status='PENDING'
            )
            Delivery.objects.create(
                order=order2,
                tracking_number='TRK-2026-002',
                delivery_staff=users['delivery'],
                delivery_address=order2.shipping_address_snapshot,
                status=DeliveryStatus.OUT_FOR_DELIVERY,
                assigned_at=timezone.now() - datetime.timedelta(hours=3),
                out_for_delivery_at=timezone.now() - datetime.timedelta(hours=1),
                delivery_notes='Courier on vehicle run. Collect cash upon receipt.'
            )

        # 7. Wishlist Items
        Wishlist.objects.get_or_create(user=customer, product=products['vitamin-c-1000mg-zinc'])
        Wishlist.objects.get_or_create(user=customer, product=products['emergency-first-aid-kit-120pc'])

        # 8. Verified Reviews
        Review.objects.get_or_create(
            customer=customer,
            product=products['amoxicillin-500mg-gsk'],
            defaults={
                'rating': 5,
                'review': 'Authentic packaging with tamper seal. Delivered rapidly right after pharmacist verified my prescription.',
                'approved': True
            }
        )
        Review.objects.get_or_create(
            customer=customer,
            product=products['ibuprofen-400mg-advil'],
            defaults={
                'rating': 5,
                'review': 'Fast pain relief and original product. Great convenience having it delivered home.',
                'approved': True
            }
        )

        # 9. Sample Notifications
        Notification.objects.get_or_create(
            user=customer,
            title="Prescription Approved",
            defaults={
                'message': "Your prescription RX-2026-9041 was reviewed and approved by Dr. Sarah Jenkins (Pharmacist).",
                'notification_type': NotificationType.PRESCRIPTION_APPROVED,
                'is_read': True
            }
        )
        Notification.objects.get_or_create(
            user=customer,
            title="Courier Out for Delivery",
            defaults={
                'message': "Courier David Miller is on the road with Order #ORD-2026-1002. Tracking #TRK-2026-002.",
                'notification_type': NotificationType.ORDER_SHIPPED,
                'is_read': False
            }
        )

        self.stdout.write(self.style.SUCCESS("PharmaCare sample pharmacy seed data successfully installed!"))
