"""
Database seed script for development.

This script creates initial test data for the SamadhanX platform.
It is IDEMPOTENT - safe to run multiple times.
"""

import sys
from pathlib import Path

# Add the backend directory to path
backend_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import date, datetime, timedelta
import random

from app.db.database import SessionLocal
from app.models import *
from app.models.enums import *
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


class Seeder:
    """Database seeder class."""
    
    def __init__(self, db: Session):
        self.db = db
        self.created_ids = {}
    
    def run(self):
        """Run all seed operations."""
        print("🌱 Starting database seed...")
        
        try:
            self.seed_roles()
            self.seed_users()
            self.seed_expertise()
            self.seed_categories()
            self.seed_universities()
            self.seed_industry_partners()
            self.seed_challenges()
            self.seed_projects()
            
            self.db.commit()
            print("✅ Database seeded successfully!")
            
        except Exception as e:
            self.db.rollback()
            print(f"❌ Error seeding database: {e}")
            raise
    
    def seed_roles(self):
        """Seed system roles."""
        print("  Creating roles...")
        
        roles_data = [
            (UserRole.CITIZEN, "Citizen who can submit challenges"),
            (UserRole.GOVERNMENT_OFFICER, "Government official who validates challenges"),
            (UserRole.UNIVERSITY_ADMIN, "University administrator"),
            (UserRole.FACULTY, "Faculty member at a university"),
            (UserRole.STUDENT, "Student at a university"),
            (UserRole.INDUSTRY, "Industry partner"),
            (UserRole.MENTOR, "Mentor for projects"),
            (UserRole.CSR, "Corporate Social Responsibility representative"),
            (UserRole.RESEARCHER, "Researcher"),
            (UserRole.PLATFORM_ADMIN, "Platform administrator"),
        ]
        
        for role_name, description in roles_data:
            existing = self.db.execute(
                select(Role).where(Role.name == role_name)
            ).scalar_one_or_none()
            
            if not existing:
                role = Role(name=role_name, description=description)
                self.db.add(role)
                self.db.flush()
                print(f"    ✓ Created role: {role_name}")
            else:
                print(f"    ⏭ Role already exists: {role_name}")
    
    def seed_users(self):
        """Seed test users."""
        print("  Creating users...")
        
        # Get roles
        roles = {
            role.name: role
            for role in self.db.execute(select(Role)).scalars().all()
        }
        
        users_data = [
            # Citizens
            {
                "name": "Rajesh Kumar",
                "email": "rajesh.kumar@example.com",
                "phone": "+919876543210",
                "roles": [UserRole.CITIZEN],
                "profile_type": "citizen"
            },
            {
                "name": "Priya Sharma",
                "email": "priya.sharma@example.com",
                "phone": "+919876543211",
                "roles": [UserRole.CITIZEN],
                "profile_type": "citizen"
            },
            {
                "name": "Amit Singh",
                "email": "amit.singh@example.com",
                "phone": "+919876543212",
                "roles": [UserRole.CITIZEN],
                "profile_type": "citizen"
            },
            # Government Officers
            {
                "name": "Dr. Sunita Devi",
                "email": "sunita.devi@jharkhand.gov.in",
                "phone": "+919876543220",
                "roles": [UserRole.GOVERNMENT_OFFICER],
                "profile_type": "government",
                "employee_id": "JH2023001",
                "department": "Department of Science and Technology",
                "designation": "Joint Secretary"
            },
            {
                "name": "Ramesh Mahato",
                "email": "ramesh.mahato@jharkhand.gov.in",
                "phone": "+919876543221",
                "roles": [UserRole.GOVERNMENT_OFFICER],
                "profile_type": "government",
                "employee_id": "JH2023002",
                "department": "Department of Rural Development",
                "designation": "Director"
            },
            # University Admin
            {
                "name": "Prof. Anjali Verma",
                "email": "anjali.verma@bitmesra.ac.in",
                "phone": "+919876543230",
                "roles": [UserRole.UNIVERSITY_ADMIN],
                "profile_type": None
            },
            {
                "name": "Dr. Suresh Oraon",
                "email": "suresh.oraon@nitmsr.ac.in",
                "phone": "+919876543231",
                "roles": [UserRole.UNIVERSITY_ADMIN],
                "profile_type": None
            },
            # Platform Admin
            {
                "name": "System Administrator",
                "email": "admin@samadhanx.gov.in",
                "phone": "+919876543240",
                "roles": [UserRole.PLATFORM_ADMIN],
                "profile_type": None
            },
        ]
        
        self.created_ids['users'] = {}
        
        for user_data in users_data:
            existing = self.db.execute(
                select(User).where(User.email == user_data["email"])
            ).scalar_one_or_none()
            
            if not existing:
                user = User(
                    name=user_data["name"],
                    email=user_data["email"],
                    phone=user_data.get("phone"),
                    password_hash=hash_password("Password@123"),
                    account_status=AccountStatus.ACTIVE
                )
                self.db.add(user)
                self.db.flush()
                
                # Add roles
                for role_name in user_data["roles"]:
                    role = roles[role_name]
                    user_role = UserRoleAssociation(user_id=user.id, role_id=role.id)
                    self.db.add(user_role)
                
                # Add profile types
                if user_data.get("profile_type") == "citizen":
                    citizen = Citizen(user_id=user.id)
                    self.db.add(citizen)
                elif user_data.get("profile_type") == "government":
                    gov = GovernmentOfficer(
                        user_id=user.id,
                        employee_id=user_data["employee_id"],
                        department=user_data["department"],
                        designation=user_data["designation"]
                    )
                    self.db.add(gov)
                
                self.db.flush()
                self.created_ids['users'][user_data["email"]] = user.id
                print(f"    ✓ Created user: {user_data['name']}")
            else:
                self.created_ids['users'][user_data["email"]] = existing.id
                print(f"    ⏭ User already exists: {user_data['name']}")
    
    def seed_expertise(self):
        """Seed expertise areas."""
        print("  Creating expertise areas...")
        
        expertise_data = [
            ("AI/ML", "Technology"),
            ("IoT", "Technology"),
            ("Robotics", "Technology"),
            ("Computer Vision", "Technology"),
            ("GIS", "Technology"),
            ("Embedded Systems", "Technology"),
            ("Data Science", "Technology"),
            ("Cybersecurity", "Technology"),
            ("Mobile Development", "Technology"),
            ("Web Development", "Technology"),
            ("Agricultural Engineering", "Agriculture"),
            ("Precision Farming", "Agriculture"),
            ("Crop Science", "Agriculture"),
            ("Water Engineering", "Water"),
            ("Hydrology", "Water"),
            ("Irrigation Systems", "Water"),
            ("Civil Engineering", "Infrastructure"),
            ("Environmental Science", "Environment"),
            ("Renewable Energy", "Energy"),
            ("Solar Technology", "Energy"),
            ("Public Health", "Healthcare"),
            ("Telemedicine", "Healthcare"),
            ("Medical Devices", "Healthcare"),
            ("Electronics", "Technology"),
            ("Mechanical Engineering", "Engineering"),
            ("Biotechnology", "Science"),
            ("Business Management", "Business"),
            ("Social Science", "Social"),
            ("Rural Development", "Social"),
            ("Waste Management", "Environment"),
        ]
        
        self.created_ids['expertise'] = {}
        
        for name, category in expertise_data:
            existing = self.db.execute(
                select(Expertise).where(Expertise.name == name)
            ).scalar_one_or_none()
            
            if not existing:
                expertise = Expertise(
                    name=name,
                    category=category,
                    description=f"{name} expertise in {category}"
                )
                self.db.add(expertise)
                self.db.flush()
                self.created_ids['expertise'][name] = expertise.id
                print(f"    ✓ Created expertise: {name}")
            else:
                self.created_ids['expertise'][name] = existing.id
    
    def seed_categories(self):
        """Seed challenge categories."""
        print("  Creating categories...")
        
        categories_data = [
            # Primary categories
            ("Education", None),
            ("Healthcare", None),
            ("Agriculture", None),
            ("Water Management", None),
            ("Sanitation", None),
            ("Environment", None),
            ("Energy", None),
            ("Urban Infrastructure", None),
            ("Accessibility", None),
            ("Public Administration", None),
            ("Rural Livelihoods", None),
            ("Disaster Management", None),
        ]
        
        self.created_ids['categories'] = {}
        
        for name, parent in categories_data:
            existing = self.db.execute(
                select(Category).where(Category.name == name, Category.parent_id == None)
            ).scalar_one_or_none()
            
            if not existing:
                category = Category(name=name, description=f"{name} related challenges")
                self.db.add(category)
                self.db.flush()
                self.created_ids['categories'][name] = category.id
                print(f"    ✓ Created category: {name}")
            else:
                self.created_ids['categories'][name] = existing.id
        
        # Subcategories
        subcategories = [
            ("Irrigation", "Agriculture"),
            ("Crop Protection", "Agriculture"),
            ("Farm Technology", "Agriculture"),
            ("Drinking Water", "Water Management"),
            ("Water Conservation", "Water Management"),
            ("Wastewater", "Water Management"),
            ("Rural Healthcare", "Healthcare"),
            ("Diagnostics", "Healthcare"),
            ("Telemedicine", "Healthcare"),
            ("Waste Management", "Environment"),
            ("Pollution Control", "Environment"),
            ("Biodiversity", "Environment"),
        ]
        
        for name, parent_name in subcategories:
            parent_id = self.created_ids['categories'].get(parent_name)
            if parent_id:
                existing = self.db.execute(
                    select(Category).where(Category.name == name, Category.parent_id == parent_id)
                ).scalar_one_or_none()
                
                if not existing:
                    category = Category(name=name, parent_id=parent_id, description=f"{name} under {parent_name}")
                    self.db.add(category)
                    self.db.flush()
                    print(f"    ✓ Created subcategory: {name}")
    
    def seed_universities(self):
        """Seed Jharkhand universities."""
        print("  Creating universities...")
        
        universities_data = [
            {
                "name": "Birla Institute of Technology, Mesra",
                "code": "BIT_MESRA",
                "type": UniversityType.DEEMED,
                "description": "Premier technical university in Jharkhand",
                "address": "Mesra, Ranchi",
                "district": "Ranchi",
                "website": "https://www.bitmesra.ac.in",
                "latitude": 23.4163,
                "longitude": 85.4397,
                "departments": ["Computer Science", "Electronics", "Civil Engineering", "Mechanical Engineering"],
                "expertise": ["AI/ML", "IoT", "Robotics", "Data Science", "Cybersecurity"],
                "facilities": ["IoT Lab", "AI Lab", "Robotics Lab", "Fabrication Lab"]
            },
            {
                "name": "National Institute of Technology, Jamshedpur",
                "code": "NIT_JSR",
                "type": UniversityType.CENTRAL,
                "description": "National Institute of Technology in Jamshedpur",
                "address": "Adityapur, Jamshedpur",
                "district": "East Singhbhum",
                "website": "https://www.nitjsr.ac.in",
                "latitude": 22.7767,
                "longitude": 86.1468,
                "departments": ["Computer Science", "Electronics", "Mechanical Engineering", "Civil Engineering"],
                "expertise": ["AI/ML", "IoT", "Data Science", "Civil Engineering"],
                "facilities": ["Innovation Lab", "Research Center", "Computational Lab"]
            },
            {
                "name": "Ranchi University",
                "code": "RU_RANCHI",
                "type": UniversityType.STATE,
                "description": "State university in Ranchi",
                "address": "Morabadi, Ranchi",
                "district": "Ranchi",
                "website": "https://www.ranchiuniversity.ac.in",
                "latitude": 23.3747,
                "longitude": 85.3337,
                "departments": ["Social Science", "Environmental Science", "Rural Development"],
                "expertise": ["Social Science", "Environmental Science", "Rural Development"],
                "facilities": ["Research Lab", "Library"]
            },
            {
                "name": "Central University of Jharkhand",
                "code": "CUJ",
                "type": UniversityType.CENTRAL,
                "description": "Central University of Jharkhand",
                "address": "Brambe, Ranchi",
                "district": "Ranchi",
                "website": "https://www.cuj.ac.in",
                "latitude": 23.4241,
                "longitude": 85.2520,
                "departments": ["Environmental Science", "Biotechnology", "Social Work"],
                "expertise": ["Environmental Science", "Biotechnology", "Rural Development"],
                "facilities": ["Environmental Lab", "Research Center"]
            },
            {
                "name": "Jharkhand Rai University",
                "code": "JRU",
                "type": UniversityType.PRIVATE,
                "description": "Private university in Jharkhand",
                "address": "Kamre, Ranchi",
                "district": "Ranchi",
                "website": "https://www.jru.edu.in",
                "latitude": 23.3441,
                "longitude": 85.3096,
                "departments": ["Engineering", "Management", "Agriculture"],
                "expertise": ["Agricultural Engineering", "Business Management"],
                "facilities": ["Incubation Centre", "Innovation Hub"]
            },
        ]
        
        self.created_ids['universities'] = {}
        self.created_ids['departments'] = {}
        self.created_ids['faculty'] = []
        self.created_ids['students'] = []
        
        for univ_data in universities_data:
            existing = self.db.execute(
                select(University).where(University.code == univ_data["code"])
            ).scalar_one_or_none()
            
            if not existing:
                university = University(
                    name=univ_data["name"],
                    code=univ_data["code"],
                    type=univ_data["type"],
                    description=univ_data["description"],
                    address=univ_data["address"],
                    district=univ_data["district"],
                    state="Jharkhand",
                    website=univ_data.get("website"),
                    latitude=univ_data.get("latitude"),
                    longitude=univ_data.get("longitude"),
                    verification_status=VerificationStatus.VERIFIED
                )
                self.db.add(university)
                self.db.flush()
                
                # Add departments
                for dept_name in univ_data.get("departments", []):
                    dept = Department(
                        university_id=university.id,
                        name=dept_name,
                        description=f"{dept_name} department"
                    )
                    self.db.add(dept)
                    self.db.flush()
                    self.created_ids['departments'][f"{univ_data['code']}_{dept_name}"] = dept.id
                
                # Add university expertise
                for exp_name in univ_data.get("expertise", []):
                    exp_id = self.created_ids['expertise'].get(exp_name)
                    if exp_id:
                        univ_exp = UniversityExpertise(
                            university_id=university.id,
                            expertise_id=exp_id,
                            proficiency_score=random.uniform(0.6, 0.9),
                            evidence_count=random.randint(5, 20)
                        )
                        self.db.add(univ_exp)
                
                # Add facilities
                for fac_name in univ_data.get("facilities", []):
                    facility = Facility(
                        university_id=university.id,
                        name=fac_name,
                        type="Laboratory",
                        description=f"{fac_name} facility",
                        capacity=random.randint(20, 50),
                        availability_status=AvailabilityStatus.AVAILABLE
                    )
                    self.db.add(facility)
                
                self.db.flush()
                self.created_ids['universities'][univ_data["code"]] = university.id
                print(f"    ✓ Created university: {univ_data['name']}")
            else:
                self.created_ids['universities'][univ_data["code"]] = existing.id
                print(f"    ⏭ University already exists: {univ_data['name']}")
        
        # Add faculty and students
        self._seed_university_people()
    
    def _seed_university_people(self):
        """Seed faculty and students."""
        print("  Creating faculty and students...")
        
        # Get roles
        roles = {
            role.name: role
            for role in self.db.execute(select(Role)).scalars().all()
        }
        
        universities = list(self.created_ids['universities'].values())
        
        # Create faculty
        faculty_data = [
            "Dr. Rakesh Kumar",
            "Prof. Meena Gupta",
            "Dr. Sunil Prasad",
            "Dr. Kavita Singh",
            "Prof. Anil Kumar Mahto",
        ]
        
        for name in faculty_data:
            email = name.lower().replace(" ", ".").replace("dr.", "").replace("prof.", "") + "@university.ac.in"
            
            existing_user = self.db.execute(
                select(User).where(User.email == email)
            ).scalar_one_or_none()
            
            if not existing_user:
                user = User(
                    name=name,
                    email=email,
                    phone=f"+9198765432{random.randint(50,99)}",
                    password_hash=hash_password("Password@123"),
                    account_status=AccountStatus.ACTIVE
                )
                self.db.add(user)
                self.db.flush()
                
                # Add role
                role = roles[UserRole.FACULTY]
                user_role = UserRoleAssociation(user_id=user.id, role_id=role.id)
                self.db.add(user_role)
                
                # Create faculty profile
                univ_id = random.choice(universities)
                faculty = Faculty(
                    user_id=user.id,
                    university_id=univ_id,
                    designation=random.choice(["Professor", "Associate Professor", "Assistant Professor"]),
                    bio=f"Experienced faculty member with expertise in technology and innovation.",
                    availability_status=AvailabilityStatus.AVAILABLE
                )
                self.db.add(faculty)
                self.db.flush()
                
                # Add faculty expertise
                expertise_list = random.sample(list(self.created_ids['expertise'].values()), 3)
                for exp_id in expertise_list:
                    fac_exp = FacultyExpertise(
                        faculty_id=faculty.id,
                        expertise_id=exp_id,
                        proficiency_score=random.uniform(0.6, 0.95)
                    )
                    self.db.add(fac_exp)
                
                self.created_ids['faculty'].append(faculty.id)
                print(f"    ✓ Created faculty: {name}")
        
        # Create students
        student_names = [
            "Rahul Kumar", "Anita Sharma", "Vikash Singh", "Priyanka Devi",
            "Ajay Mahto", "Sneha Kumari", "Ravi Kumar", "Pooja Singh",
            "Deepak Prasad", "Neha Gupta"
        ]
        
        for name in student_names:
            email = name.lower().replace(" ", ".") + "@student.ac.in"
            
            existing_user = self.db.execute(
                select(User).where(User.email == email)
            ).scalar_one_or_none()
            
            if not existing_user:
                user = User(
                    name=name,
                    email=email,
                    phone=f"+9198765433{random.randint(0,99):02d}",
                    password_hash=hash_password("Password@123"),
                    account_status=AccountStatus.ACTIVE
                )
                self.db.add(user)
                self.db.flush()
                
                # Add role
                role = roles[UserRole.STUDENT]
                user_role = UserRoleAssociation(user_id=user.id, role_id=role.id)
                self.db.add(user_role)
                
                # Create student profile
                univ_id = random.choice(universities)
                student = Student(
                    user_id=user.id,
                    university_id=univ_id,
                    course=random.choice(["B.Tech", "M.Tech", "B.Sc", "M.Sc"]),
                    year=random.randint(1, 4),
                    skills={"programming": ["Python", "Java"], "tools": ["Git", "Docker"]}
                )
                self.db.add(student)
                self.db.flush()
                self.created_ids['students'].append(student.id)
                print(f"    ✓ Created student: {name}")
    
    def seed_industry_partners(self):
        """Seed industry partners."""
        print("  Creating industry partners...")
        
        partners_data = [
            {
                "name": "Tata Steel Foundation",
                "type": IndustryType.CSR,
                "district": "East Singhbhum",
                "expertise": ["Rural Development", "Social Science"]
            },
            {
                "name": "Jharkhand Startup Hub",
                "type": IndustryType.INNOVATION_HUB,
                "district": "Ranchi",
                "expertise": ["AI/ML", "IoT", "Mobile Development"]
            },
            {
                "name": "AgriTech Solutions Pvt Ltd",
                "type": IndustryType.STARTUP,
                "district": "Ranchi",
                "expertise": ["Agricultural Engineering", "IoT"]
            },
            {
                "name": "Clean Water Initiative",
                "type": IndustryType.NGO,
                "district": "Ranchi",
                "expertise": ["Water Engineering", "Environmental Science"]
            },
            {
                "name": "Smart City Technologies",
                "type": IndustryType.INDUSTRY,
                "district": "Ranchi",
                "expertise": ["IoT", "GIS", "Data Science"]
            },
        ]
        
        self.created_ids['industry'] = {}
        
        for partner_data in partners_data:
            existing = self.db.execute(
                select(IndustryPartner).where(IndustryPartner.organization_name == partner_data["name"])
            ).scalar_one_or_none()
            
            if not existing:
                partner = IndustryPartner(
                    organization_name=partner_data["name"],
                    type=partner_data["type"],
                    description=f"{partner_data['name']} - {partner_data['type'].value}",
                    district=partner_data["district"],
                    state="Jharkhand",
                    verification_status=VerificationStatus.VERIFIED
                )
                self.db.add(partner)
                self.db.flush()
                
                # Add expertise
                for exp_name in partner_data.get("expertise", []):
                    exp_id = self.created_ids['expertise'].get(exp_name)
                    if exp_id:
                        ind_exp = IndustryExpertise(
                            industry_id=partner.id,
                            expertise_id=exp_id,
                            proficiency_score=random.uniform(0.7, 0.95)
                        )
                        self.db.add(ind_exp)
                
                self.db.flush()
                self.created_ids['industry'][partner_data["name"]] = partner.id
                print(f"    ✓ Created industry partner: {partner_data['name']}")
            else:
                self.created_ids['industry'][partner_data["name"]] = existing.id
    
    def seed_challenges(self):
        """Seed challenges."""
        print("  Creating challenges...")
        
        challenges_data = [
            {
                "title": "Smart Irrigation System for Tribal Farmlands",
                "description": "Develop an IoT-based smart irrigation system for tribal farmers in remote areas with limited water resources.",
                "district": "Gumla",
                "category": "Agriculture",
                "subcategory": "Irrigation",
                "priority": PriorityLevel.HIGH,
                "affected_population": 5000
            },
            {
                "title": "Portable Water Quality Testing Device",
                "description": "Design a low-cost portable device for testing water quality in rural areas to ensure safe drinking water.",
                "district": "Lohardaga",
                "category": "Water Management",
                "subcategory": "Drinking Water",
                "priority": PriorityLevel.CRITICAL,
                "affected_population": 15000
            },
            {
                "title": "Telemedicine Solution for Remote Health Centers",
                "description": "Create a telemedicine platform connecting remote health centers with doctors in cities for better healthcare access.",
                "district": "Simdega",
                "category": "Healthcare",
                "subcategory": "Telemedicine",
                "priority": PriorityLevel.HIGH,
                "affected_population": 10000
            },
            {
                "title": "Solar-Powered Community Lighting",
                "description": "Install solar-powered LED lighting systems in villages without electricity access.",
                "district": "Khunti",
                "category": "Energy",
                "priority": PriorityLevel.MEDIUM,
                "affected_population": 3000
            },
            {
                "title": "Waste Management System for Urban Areas",
                "description": "Develop a smart waste segregation and management system for Ranchi city.",
                "district": "Ranchi",
                "category": "Environment",
                "subcategory": "Waste Management",
                "priority": PriorityLevel.HIGH,
                "affected_population": 50000
            },
            {
                "title": "Mobile App for Government Schemes Awareness",
                "description": "Create a multilingual mobile app to educate citizens about government schemes and benefits.",
                "district": "Ranchi",
                "category": "Public Administration",
                "priority": PriorityLevel.MEDIUM,
                "affected_population": 100000
            },
            {
                "title": "Smart Classroom for Rural Schools",
                "description": "Equip rural schools with digital learning tools and internet connectivity for better education.",
                "district": "Palamu",
                "category": "Education",
                "priority": PriorityLevel.HIGH,
                "affected_population": 8000
            },
            {
                "title": "Crop Disease Detection Using AI",
                "description": "Develop an AI-powered mobile app to detect crop diseases using image recognition.",
                "district": "Hazaribagh",
                "category": "Agriculture",
                "subcategory": "Crop Protection",
                "priority": PriorityLevel.HIGH,
                "affected_population": 20000
            },
            {
                "title": "Accessible Public Transport System",
                "description": "Design accessible bus stops and public transport for differently-abled citizens.",
                "district": "Jamshedpur",
                "category": "Accessibility",
                "priority": PriorityLevel.MEDIUM,
                "affected_population": 5000
            },
            {
                "title": "Disaster Early Warning System",
                "description": "Create an early warning system for floods and natural disasters using IoT sensors.",
                "district": "Deoghar",
                "category": "Disaster Management",
                "priority": PriorityLevel.CRITICAL,
                "affected_population": 25000
            },
        ]
        
        self.created_ids['challenges'] = []
        citizen_users = [uid for email, uid in self.created_ids['users'].items() if 'example.com' in email]
        
        for idx, challenge_data in enumerate(challenges_data, 1):
            challenge_code = f"CH{datetime.now().year}{idx:04d}"
            
            existing = self.db.execute(
                select(Challenge).where(Challenge.challenge_code == challenge_code)
            ).scalar_one_or_none()
            
            if not existing:
                challenge = Challenge(
                    challenge_code=challenge_code,
                    submitted_by=random.choice(citizen_users) if citizen_users else None,
                    title=challenge_data["title"],
                    description=challenge_data["description"],
                    status=random.choice([ChallengeStatus.VALIDATED, ChallengeStatus.MATCHING, ChallengeStatus.ACCEPTED]),
                    priority_level=challenge_data["priority"],
                    priority_score=random.uniform(0.6, 0.95),
                    district=challenge_data["district"],
                    block=f"{challenge_data['district']} Block",
                    affected_population=challenge_data["affected_population"]
                )
                self.db.add(challenge)
                self.db.flush()
                
                # Add category
                category_id = self.created_ids['categories'].get(challenge_data["category"])
                if category_id:
                    challenge_cat = ChallengeCategory(
                        challenge_id=challenge.id,
                        category_id=category_id
                    )
                    self.db.add(challenge_cat)
                
                # Add AI analysis (simulated)
                ai_analysis = ChallengeAIAnalysis(
                    challenge_id=challenge.id,
                    model_name="gpt-4",
                    model_version="2024-01",
                    summary=f"AI analysis summary for {challenge_data['title']}",
                    primary_domain=challenge_data["category"],
                    severity_score=random.uniform(0.5, 0.9),
                    urgency_score=random.uniform(0.4, 0.9),
                    affected_population_estimate=challenge_data["affected_population"],
                    extracted_skills=["AI/ML", "IoT", "Data Science"],
                    recommended_solution_types=["Technology", "Innovation"],
                    confidence_score=random.uniform(0.7, 0.95)
                )
                self.db.add(ai_analysis)
                
                # Add university assignments
                universities = list(self.created_ids['universities'].values())
                if universities:
                    for _ in range(random.randint(1, 3)):
                        assignment = ChallengeAssignment(
                            challenge_id=challenge.id,
                            university_id=random.choice(universities),
                            assignment_score=random.randint(60, 95),
                            reason=f"Strong expertise in {challenge_data['category']} and relevant facilities",
                            status=random.choice([AssignmentStatus.RECOMMENDED, AssignmentStatus.INVITED])
                        )
                        self.db.add(assignment)
                
                self.db.flush()
                self.created_ids['challenges'].append(challenge.id)
                print(f"    ✓ Created challenge: {challenge_data['title']}")
            else:
                self.created_ids['challenges'].append(existing.id)
    
    def seed_projects(self):
        """Seed projects for challenges."""
        print("  Creating projects...")
        
        if not self.created_ids['challenges'] or not self.created_ids['universities']:
            print("    ⏭ Skipping projects (no challenges or universities)")
            return
        
        # Create 3-5 projects
        for i in range(min(5, len(self.created_ids['challenges']))):
            challenge_id = self.created_ids['challenges'][i]
            university_id = random.choice(list(self.created_ids['universities'].values()))
            
            existing = self.db.execute(
                select(Project).where(
                    Project.challenge_id == challenge_id,
                    Project.university_id == university_id
                )
            ).scalar_one_or_none()
            
            if not existing:
                project = Project(
                    challenge_id=challenge_id,
                    university_id=university_id,
                    name=f"Project Solution {i+1}",
                    description="Comprehensive solution for the challenge",
                    status=random.choice([ProjectStatus.PLANNING, ProjectStatus.PROPOSAL, ProjectStatus.APPROVED]),
                    start_date=date.today() - timedelta(days=random.randint(1, 30)),
                    expected_end_date=date.today() + timedelta(days=random.randint(90, 180)),
                    budget=random.randint(100000, 500000)
                )
                self.db.add(project)
                self.db.flush()
                
                # Add project members
                if self.created_ids['faculty']:
                    member = ProjectMember(
                        project_id=project.id,
                        user_id=self.db.execute(
                            select(Faculty.user_id).where(Faculty.id == random.choice(self.created_ids['faculty']))
                        ).scalar(),
                        role=ProjectMemberRole.FACULTY
                    )
                    self.db.add(member)
                
                if self.created_ids['students']:
                    for _ in range(random.randint(2, 4)):
                        student_user_id = self.db.execute(
                            select(Student.user_id).where(Student.id == random.choice(self.created_ids['students']))
                        ).scalar()
                        if student_user_id:
                            member = ProjectMember(
                                project_id=project.id,
                                user_id=student_user_id,
                                role=ProjectMemberRole.STUDENT
                            )
                            self.db.add(member)
                
                # Add milestones
                milestones_data = [
                    ("Research and Planning", MilestoneStatus.COMPLETED, 100),
                    ("Prototype Development", MilestoneStatus.IN_PROGRESS, 60),
                    ("Testing and Validation", MilestoneStatus.PENDING, 0),
                    ("Deployment", MilestoneStatus.PENDING, 0),
                ]
                
                for ms_name, ms_status, completion in milestones_data:
                    milestone = ProjectMilestone(
                        project_id=project.id,
                        name=ms_name,
                        description=f"{ms_name} phase",
                        start_date=date.today() - timedelta(days=random.randint(1, 60)),
                        deadline=date.today() + timedelta(days=random.randint(30, 90)),
                        status=ms_status,
                        completion_percentage=completion
                    )
                    self.db.add(milestone)
                
                # Add impact metrics
                metrics_data = [
                    ("Number of Beneficiaries", 0, 1000, 0),
                    ("Cost Savings", 0, 500000, 0),
                    ("Time Efficiency", 0, 80, 0),
                ]
                
                for metric_name, baseline, target, actual in metrics_data:
                    metric = ImpactMetric(
                        project_id=project.id,
                        metric_name=metric_name,
                        baseline_value=baseline,
                        target_value=target,
                        actual_value=actual,
                        verification_status=VerificationStatus.PENDING
                    )
                    self.db.add(metric)
                
                print(f"    ✓ Created project for challenge {i+1}")


def main():
    """Main entry point."""
    db = SessionLocal()
    try:
        seeder = Seeder(db)
        seeder.run()
    finally:
        db.close()


if __name__ == "__main__":
    main()
