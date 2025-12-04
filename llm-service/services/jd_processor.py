import io
import re
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class JobDescription:
    raw_text: str
    title: Optional[str] = None
    company: Optional[str] = None
    required_skills: List[str] = None
    preferred_skills: List[str] = None
    experience_level: Optional[str] = None
    responsibilities: List[str] = None
    domain: Optional[str] = None
    key_technologies: List[str] = None
    
    def __post_init__(self):
        if self.required_skills is None:
            self.required_skills = []
        if self.preferred_skills is None:
            self.preferred_skills = []
        if self.responsibilities is None:
            self.responsibilities = []
        if self.key_technologies is None:
            self.key_technologies = []


class JDProcessor:
    """Processes job description PDFs and extracts relevant information."""
    
    # Domain keywords mapping
    DOMAIN_KEYWORDS = {
        "software_engineering": [
            "software engineer", "developer", "programmer", "full stack",
            "backend", "frontend", "web developer", "mobile developer"
        ],
        "data_science": [
            "data scientist", "machine learning", "ml engineer", "ai engineer",
            "deep learning", "nlp", "computer vision", "data analyst"
        ],
        "devops": [
            "devops", "sre", "site reliability", "platform engineer",
            "infrastructure", "cloud engineer", "kubernetes", "docker"
        ],
        "product_management": [
            "product manager", "product owner", "pm", "product lead",
            "product strategy", "roadmap", "agile", "scrum master"
        ],
        "design": [
            "ui designer", "ux designer", "product designer", "visual designer",
            "interaction designer", "design system", "figma", "user research"
        ],
        "data_engineering": [
            "data engineer", "etl", "data pipeline", "data warehouse",
            "spark", "airflow", "kafka", "data infrastructure"
        ],
        "security": [
            "security engineer", "cybersecurity", "penetration testing",
            "security analyst", "infosec", "soc analyst", "threat"
        ],
        "qa_testing": [
            "qa engineer", "test engineer", "quality assurance", "automation testing",
            "selenium", "test lead", "sdet", "quality analyst"
        ],
        "project_management": [
            "project manager", "program manager", "delivery manager",
            "technical program manager", "tpm", "pmp", "project lead"
        ],
        "sales": [
            "sales", "account executive", "business development", "sales engineer",
            "customer success", "account manager", "revenue"
        ],
        "marketing": [
            "marketing", "growth", "content marketing", "seo", "sem",
            "digital marketing", "brand manager", "marketing analyst"
        ],
        "hr": [
            "hr", "human resources", "recruiter", "talent acquisition",
            "people operations", "hrbp", "compensation", "benefits"
        ],
        "finance": [
            "finance", "financial analyst", "accountant", "controller",
            "fp&a", "treasury", "audit", "tax"
        ],
        "operations": [
            "operations", "business operations", "ops manager", "supply chain",
            "logistics", "procurement", "vendor management"
        ],
        "customer_support": [
            "customer support", "customer service", "support engineer",
            "technical support", "help desk", "customer experience"
        ],
        "legal": [
            "legal", "lawyer", "attorney", "counsel", "compliance",
            "contract", "paralegal", "regulatory"
        ],
        "executive": [
            "cto", "ceo", "cfo", "vp engineering", "director", "head of",
            "chief", "executive", "leadership"
        ]
    }
    
    # Technology keywords for skill extraction
    TECHNOLOGY_KEYWORDS = {
        "languages": [
            "python", "java", "javascript", "typescript", "go", "golang", "rust",
            "c++", "c#", "ruby", "php", "swift", "kotlin", "scala", "r"
        ],
        "frameworks": [
            "react", "angular", "vue", "node.js", "django", "flask", "spring",
            "express", ".net", "rails", "laravel", "fastapi", "next.js"
        ],
        "databases": [
            "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
            "dynamodb", "cassandra", "sqlite", "oracle", "sql server"
        ],
        "cloud": [
            "aws", "azure", "gcp", "google cloud", "heroku", "digitalocean",
            "cloudflare", "vercel", "netlify"
        ],
        "devops_tools": [
            "docker", "kubernetes", "k8s", "terraform", "ansible", "jenkins",
            "github actions", "gitlab ci", "circleci", "prometheus", "grafana"
        ],
        "data_tools": [
            "spark", "hadoop", "airflow", "kafka", "snowflake", "databricks",
            "pandas", "numpy", "tensorflow", "pytorch", "scikit-learn"
        ]
    }
    
    # Experience level keywords
    EXPERIENCE_LEVELS = {
        "entry": ["entry level", "junior", "graduate", "fresher", "0-2 years", "new grad"],
        "mid": ["mid level", "intermediate", "2-5 years", "3-5 years", "experienced"],
        "senior": ["senior", "lead", "5+ years", "7+ years", "principal", "staff"],
        "executive": ["director", "vp", "head of", "chief", "c-level", "executive"]
    }

    def __init__(self, claude_client=None):
        self.claude_client = claude_client
    
    async def process_pdf(self, pdf_content: bytes) -> JobDescription:
        """Process PDF content and extract job description."""
        text = self._extract_text_from_pdf(pdf_content)
        return await self.process_text(text)
    
    def _extract_text_from_pdf(self, pdf_content: bytes) -> str:
        """Extract text from PDF bytes."""
        try:
            import pypdf
            pdf_reader = pypdf.PdfReader(io.BytesIO(pdf_content))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except ImportError:
            # Fallback: try pdfplumber
            try:
                import pdfplumber
                with pdfplumber.open(io.BytesIO(pdf_content)) as pdf:
                    text = ""
                    for page in pdf.pages:
                        text += page.extract_text() or ""
                    return text
            except ImportError:
                raise ImportError("Please install pypdf or pdfplumber: pip install pypdf pdfplumber")
    
    async def process_text(self, text: str) -> JobDescription:
        """Process raw JD text and extract structured information."""
        text_lower = text.lower()
        
        # Extract domain
        domain = self._detect_domain(text_lower)
        
        # Extract experience level
        experience = self._detect_experience_level(text_lower)
        
        # Extract technologies
        technologies = self._extract_technologies(text_lower)
        
        # Extract skills using patterns
        required_skills, preferred_skills = self._extract_skills(text)
        
        # Extract responsibilities
        responsibilities = self._extract_responsibilities(text)
        
        # Extract title (first line or common patterns)
        title = self._extract_title(text)
        
        # If Claude client available, enhance with AI extraction
        if self.claude_client:
            enhanced = await self._enhance_with_ai(text)
            if enhanced.get("title"):
                title = enhanced["title"]
            if enhanced.get("required_skills"):
                required_skills = list(set(required_skills + enhanced["required_skills"]))
            if enhanced.get("responsibilities"):
                responsibilities = enhanced["responsibilities"][:5]
        
        return JobDescription(
            raw_text=text,
            title=title,
            domain=domain,
            experience_level=experience,
            required_skills=required_skills[:15],  # Limit to top 15
            preferred_skills=preferred_skills[:10],
            responsibilities=responsibilities[:10],
            key_technologies=technologies[:20]
        )
    
    def _detect_domain(self, text: str) -> str:
        """Detect the job domain from text."""
        domain_scores = {}
        
        for domain, keywords in self.DOMAIN_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text)
            if score > 0:
                domain_scores[domain] = score
        
        if domain_scores:
            return max(domain_scores, key=domain_scores.get)
        return "general"
    
    def _detect_experience_level(self, text: str) -> str:
        """Detect required experience level."""
        for level, keywords in self.EXPERIENCE_LEVELS.items():
            for kw in keywords:
                if kw in text:
                    return level
        return "mid"  # Default to mid-level
    
    def _extract_technologies(self, text: str) -> List[str]:
        """Extract mentioned technologies."""
        found = []
        for category, techs in self.TECHNOLOGY_KEYWORDS.items():
            for tech in techs:
                if tech in text:
                    found.append(tech)
        return list(set(found))
    
    def _extract_skills(self, text: str) -> tuple:
        """Extract required and preferred skills."""
        required = []
        preferred = []
        
        lines = text.split('\n')
        in_required = False
        in_preferred = False
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # Detect section headers
            if any(kw in line_lower for kw in ["required", "must have", "requirements", "qualifications"]):
                in_required = True
                in_preferred = False
                continue
            elif any(kw in line_lower for kw in ["preferred", "nice to have", "bonus", "plus"]):
                in_required = False
                in_preferred = True
                continue
            elif any(kw in line_lower for kw in ["responsibilities", "about", "company", "benefits"]):
                in_required = False
                in_preferred = False
                continue
            
            # Extract bullet points
            if line.strip().startswith(('-', '•', '*', '·')) or re.match(r'^\d+\.', line.strip()):
                skill = re.sub(r'^[-•*·\d.]+\s*', '', line).strip()
                if len(skill) > 5 and len(skill) < 200:
                    if in_required:
                        required.append(skill)
                    elif in_preferred:
                        preferred.append(skill)
        
        return required, preferred
    
    def _extract_responsibilities(self, text: str) -> List[str]:
        """Extract job responsibilities."""
        responsibilities = []
        lines = text.split('\n')
        in_responsibilities = False
        
        for line in lines:
            line_lower = line.lower().strip()
            
            if any(kw in line_lower for kw in ["responsibilities", "what you'll do", "role", "duties"]):
                in_responsibilities = True
                continue
            elif any(kw in line_lower for kw in ["requirements", "qualifications", "about", "benefits"]):
                in_responsibilities = False
                continue
            
            if in_responsibilities and line.strip().startswith(('-', '•', '*', '·')):
                resp = re.sub(r'^[-•*·]+\s*', '', line).strip()
                if len(resp) > 10:
                    responsibilities.append(resp)
        
        return responsibilities
    
    def _extract_title(self, text: str) -> str:
        """Extract job title."""
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        
        # Common title patterns
        title_patterns = [
            r"^(senior|junior|lead|staff|principal)?\s*(software|data|product|design|devops|qa|project)?\s*(engineer|developer|manager|analyst|designer|scientist|architect)",
            r"job\s*title\s*[:\-]?\s*(.+)",
            r"position\s*[:\-]?\s*(.+)",
            r"role\s*[:\-]?\s*(.+)"
        ]
        
        for line in lines[:10]:  # Check first 10 lines
            for pattern in title_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    return match.group(0).strip()
        
        # Return first non-empty line as fallback
        return lines[0] if lines else "Unknown Position"
    
    async def _enhance_with_ai(self, text: str) -> Dict:
        """Use Claude to enhance extraction."""
        prompt = """Extract structured information from this job description.
Return JSON with:
{
  "title": "Job title",
  "required_skills": ["skill1", "skill2"],
  "responsibilities": ["resp1", "resp2"]
}

Job Description:
""" + text[:3000]  # Limit text length
        
        try:
            response = await self.claude_client.generate_text(
                system_prompt="You extract structured data from job descriptions. Return only valid JSON.",
                user_message=prompt,
                temperature=0.3
            )
            import json
            return json.loads(response)
        except:
            return {}
    
    def generate_interview_context(self, jd: JobDescription) -> str:
        """Generate context string for interview question generation."""
        context_parts = []
        
        if jd.title:
            context_parts.append(f"Position: {jd.title}")
        
        if jd.domain:
            context_parts.append(f"Domain: {jd.domain.replace('_', ' ').title()}")
        
        if jd.experience_level:
            context_parts.append(f"Level: {jd.experience_level.title()}")
        
        if jd.key_technologies:
            context_parts.append(f"Technologies: {', '.join(jd.key_technologies[:10])}")
        
        if jd.required_skills:
            context_parts.append(f"Key Skills: {', '.join(jd.required_skills[:5])}")
        
        if jd.responsibilities:
            context_parts.append(f"Key Responsibilities: {'; '.join(jd.responsibilities[:3])}")
        
        return "\n".join(context_parts)


# Expanded topic list for various domains
INTERVIEW_TOPICS = {
    # Software Engineering
    "algorithms": {
        "name": "Algorithms & Data Structures",
        "domain": "software_engineering",
        "skills": ["problem solving", "complexity analysis", "optimization"]
    },
    "system_design": {
        "name": "System Design",
        "domain": "software_engineering",
        "skills": ["scalability", "distributed systems", "architecture"]
    },
    "frontend": {
        "name": "Frontend Development",
        "domain": "software_engineering",
        "skills": ["react", "javascript", "css", "web performance"]
    },
    "backend": {
        "name": "Backend Development",
        "domain": "software_engineering",
        "skills": ["apis", "databases", "microservices", "caching"]
    },
    "mobile": {
        "name": "Mobile Development",
        "domain": "software_engineering",
        "skills": ["ios", "android", "react native", "flutter"]
    },
    
    # Data Science & ML
    "machine_learning": {
        "name": "Machine Learning",
        "domain": "data_science",
        "skills": ["supervised learning", "deep learning", "model evaluation"]
    },
    "data_analysis": {
        "name": "Data Analysis",
        "domain": "data_science",
        "skills": ["statistics", "visualization", "sql", "pandas"]
    },
    "nlp": {
        "name": "Natural Language Processing",
        "domain": "data_science",
        "skills": ["text processing", "transformers", "embeddings"]
    },
    
    # DevOps & Infrastructure
    "devops": {
        "name": "DevOps & CI/CD",
        "domain": "devops",
        "skills": ["docker", "kubernetes", "ci/cd", "infrastructure as code"]
    },
    "cloud": {
        "name": "Cloud Architecture",
        "domain": "devops",
        "skills": ["aws", "azure", "gcp", "cloud security"]
    },
    "sre": {
        "name": "Site Reliability Engineering",
        "domain": "devops",
        "skills": ["monitoring", "incident response", "capacity planning"]
    },
    
    # Product & Design
    "product_management": {
        "name": "Product Management",
        "domain": "product_management",
        "skills": ["roadmapping", "prioritization", "user research", "metrics"]
    },
    "ux_design": {
        "name": "UX Design",
        "domain": "design",
        "skills": ["user research", "wireframing", "usability testing"]
    },
    "product_design": {
        "name": "Product Design",
        "domain": "design",
        "skills": ["visual design", "interaction design", "design systems"]
    },
    
    # Data Engineering
    "data_engineering": {
        "name": "Data Engineering",
        "domain": "data_engineering",
        "skills": ["etl", "data pipelines", "data warehousing", "spark"]
    },
    "data_modeling": {
        "name": "Data Modeling",
        "domain": "data_engineering",
        "skills": ["schema design", "normalization", "dimensional modeling"]
    },
    
    # Security
    "security": {
        "name": "Cybersecurity",
        "domain": "security",
        "skills": ["threat modeling", "penetration testing", "security architecture"]
    },
    "appsec": {
        "name": "Application Security",
        "domain": "security",
        "skills": ["owasp", "secure coding", "vulnerability assessment"]
    },
    
    # QA & Testing
    "qa_automation": {
        "name": "QA Automation",
        "domain": "qa_testing",
        "skills": ["test automation", "selenium", "api testing", "ci integration"]
    },
    "qa_manual": {
        "name": "Manual Testing",
        "domain": "qa_testing",
        "skills": ["test planning", "exploratory testing", "bug reporting"]
    },
    
    # Project & Program Management
    "project_management": {
        "name": "Project Management",
        "domain": "project_management",
        "skills": ["planning", "risk management", "stakeholder management"]
    },
    "agile": {
        "name": "Agile & Scrum",
        "domain": "project_management",
        "skills": ["scrum", "kanban", "sprint planning", "retrospectives"]
    },
    
    # Business Roles
    "sales": {
        "name": "Sales",
        "domain": "sales",
        "skills": ["prospecting", "negotiation", "pipeline management", "closing"]
    },
    "marketing": {
        "name": "Marketing",
        "domain": "marketing",
        "skills": ["campaign management", "analytics", "content strategy"]
    },
    "customer_success": {
        "name": "Customer Success",
        "domain": "customer_support",
        "skills": ["onboarding", "retention", "relationship management"]
    },
    
    # HR & People
    "recruiting": {
        "name": "Recruiting & Talent Acquisition",
        "domain": "hr",
        "skills": ["sourcing", "interviewing", "employer branding"]
    },
    "hr_general": {
        "name": "Human Resources",
        "domain": "hr",
        "skills": ["employee relations", "performance management", "compliance"]
    },
    
    # Finance
    "finance": {
        "name": "Finance & Accounting",
        "domain": "finance",
        "skills": ["financial analysis", "budgeting", "forecasting"]
    },
    "fp_and_a": {
        "name": "FP&A",
        "domain": "finance",
        "skills": ["financial modeling", "variance analysis", "reporting"]
    },
    
    # Operations
    "operations": {
        "name": "Business Operations",
        "domain": "operations",
        "skills": ["process optimization", "vendor management", "analytics"]
    },
    
    # Leadership
    "leadership": {
        "name": "Leadership & Management",
        "domain": "executive",
        "skills": ["team building", "strategy", "decision making", "communication"]
    },
    "behavioral": {
        "name": "Behavioral Interview",
        "domain": "general",
        "skills": ["communication", "teamwork", "problem solving", "adaptability"]
    },
    
    # Dynamic - for JD-based interviews
    "dynamic": {
        "name": "Custom (Based on Job Description)",
        "domain": "dynamic",
        "skills": []
    }
}


def get_topic_list() -> List[Dict]:
    """Get list of available topics for frontend."""
    return [
        {
            "id": topic_id,
            "name": topic_data["name"],
            "domain": topic_data["domain"]
        }
        for topic_id, topic_data in INTERVIEW_TOPICS.items()
    ]


def get_topics_by_domain(domain: str) -> List[Dict]:
    """Get topics filtered by domain."""
    return [
        {
            "id": topic_id,
            "name": topic_data["name"],
            "domain": topic_data["domain"]
        }
        for topic_id, topic_data in INTERVIEW_TOPICS.items()
        if topic_data["domain"] == domain or domain == "all"
    ]
