"""
وكيل الموارد البشرية (HR) - Yonah Ashkenaz
فرز CV + إعلانات توظيف + أسئلة مقابلات + سياسات
"""

import os
import pandas as pd
from datetime import datetime


# ============================================================
# قوالب HR
# ============================================================

JOB_TEMPLATES = {
    "developer": {
        "ar": "مطور برمجيات",
        "fr": "Développeur",
        "skills": ["Python", "JavaScript", "Git", "SQL", "REST APIs"],
        "experience": "2-5 سنوات",
    },
    "accountant": {
        "ar": "محاسب",
        "fr": "Comptable",
        "skills": ["Excel", "Sage", "TVA", "CNSS", "Bilan"],
        "experience": "2-4 سنوات",
    },
    "sales": {
        "ar": "مندوب مبيعات",
        "fr": "Commercial",
        "skills": ["CRM", "Negotiation", "Prospection", "Closing"],
        "experience": "1-3 سنوات",
    },
    "marketing": {
        "ar": "مسؤول تسويق",
        "fr": "Responsable Marketing",
        "skills": ["SEO", "Social Media", "Content", "Analytics"],
        "experience": "2-4 سنوات",
    },
    "hr": {
        "ar": "مسؤول موارد بشرية",
        "fr": "Responsable RH",
        "skills": ["Recruitment", "Payroll", "Training", "Labor Law"],
        "experience": "2-5 سنوات",
    },
}

INTERVIEW_QUESTIONS = {
    "general": [
        ("ar", "حدثني عن نفسك وخبراتك السابقة."),
        ("fr", "Parlez-moi de vous et de votre expérience."),
        ("en", "Tell me about yourself and your experience."),
        ("ar", "لماذا تريد العمل معنا؟"),
        ("fr", "Pourquoi voulez-vous travailler avec nous?"),
        ("en", "Why do you want to work with us?"),
        ("ar", "ما هي نقاط قوتك وضعفك؟"),
        ("fr", "Quels sont vos points forts et vos faiblesses?"),
        ("en", "What are your strengths and weaknesses?"),
        ("ar", "أين ترى نفسك بعد 5 سنوات؟"),
        ("fr", "Où vous voyez-vous dans 5 ans?"),
        ("en", "Where do you see yourself in 5 years?"),
    ],
    "technical": [
        ("ar", "صف لي أصعب مشروع عملت عليه."),
        ("fr", "Décrivez le projet le plus difficile sur lequel vous avez travaillé."),
        ("en", "Describe the most difficult project you worked on."),
        ("ar", "كيف تتعامل مع المواعيد النهائية الضيقة؟"),
        ("fr", "Comment gérez-vous les délais serrés?"),
        ("en", "How do you handle tight deadlines?"),
        ("ar", "كيف تحل مشكلة مع فريق لا يتعاون؟"),
        ("fr", "Comment résolvez-vous un problème avec une équipe non coopérative?"),
        ("en", "How do you solve a problem with a non-cooperative team?"),
    ],
}


class HRAgent:
    def __init__(self):
        self.cvs = []
        self.analysis = {}

    # ============================================
    # 1. فرز السير الذاتية
    # ============================================
    def load_cvs(self, file_path):
        """تحميل ملف Excel فيه معلومات المرشحين"""
        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)
            df.columns = [str(c).strip() for c in df.columns]
            self.cvs = df.to_dict('records')
            return {"success": True, "count": len(self.cvs), "columns": list(df.columns)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def screen_cvs(self, required_skills, min_experience=0, lang='ar'):
        """فرز المرشحين حسب المهارات والخبرة"""
        if not self.cvs:
            return []

        # اكتشاف الأعمدة
        first_cv = self.cvs[0]
        cols = {k.lower(): k for k in first_cv.keys()}

        name_col = cols.get('name') or cols.get('nom') or cols.get('الاسم')
        skills_col = cols.get('skills') or cols.get('compétences') or cols.get('المهارات')
        exp_col = cols.get('experience') or cols.get('expérience') or cols.get('الخبرة')
        email_col = cols.get('email') or cols.get('البريد')

        screened = []
        for cv in self.cvs:
            score = 0
            matched_skills = []

            # حساب نقاط المهارات
            if skills_col:
                cv_skills = str(cv.get(skills_col, '')).lower()
                for skill in required_skills:
                    if skill.lower() in cv_skills:
                        score += 20
                        matched_skills.append(skill)

            # حساب نقاط الخبرة
            years = 0
            if exp_col:
                try:
                    years = float(cv.get(exp_col, 0))
                except:
                    years = 0
                if years >= min_experience:
                    score += min(years * 5, 40)

            screened.append({
                "name": cv.get(name_col, "—") if name_col else "—",
                "email": cv.get(email_col, "—") if email_col else "—",
                "experience": years,
                "matched_skills": matched_skills,
                "score": score,
            })

        # ترتيب حسب النقاط
        screened.sort(key=lambda x: x['score'], reverse=True)
        self.analysis = screened
        return screened

    # ============================================
    # 2. كتابة إعلان توظيف
    # ============================================
    def generate_job_posting(self, job_type, company_name="الشركة", lang='ar'):
        """توليد إعلان توظيف احترافي"""
        template = JOB_TEMPLATES.get(job_type, JOB_TEMPLATES["developer"])

        if lang == 'ar':
            posting = f"""
📢 إعلان توظيف: {template['ar']}

🏢 الشركة: {company_name}
📍 الموقع: المغرب
💼 نوع العقد: دوام كامل

📋 المهام:
• تنفيذ المهام المتعلقة بـ {template['ar']}
• التعاون مع الفريق
• تحقيق الأهداف الشهرية

✅ المتطلبات:
• خبرة {template['experience']}
• إتقان: {', '.join(template['skills'])}
• اللغات: العربية، الفرنسية
• مهارات التواصل

🎁 ما نقدمه:
• راتب تنافسي
• تأمين صحي (AMO)
• بيئة عمل ديناميكية
• فرص تطوير

📧 للتقديم:
أرسل سيرتك الذاتية إلى: hr@company.ma
"""
        elif lang == 'fr':
            posting = f"""
📢 Offre d'emploi : {template['fr']}

🏢 Entreprise : {company_name}
📍 Lieu : Maroc
💼 Type : Temps plein

📋 Missions :
• Assurer les tâches de {template['fr']}
• Collaborer avec l'équipe
• Atteindre les objectifs mensuels

✅ Profil recherché :
• Expérience : {template['experience']}
• Maîtrise : {', '.join(template['skills'])}
• Langues : Arabe, Français
• Bon relationnel

🎁 Ce que nous offrons :
• Salaire compétitif
• AMO
• Environnement dynamique
• Opportunités d'évolution

📧 Postuler :
Envoyez votre CV à : hr@company.ma
"""
        else:
            posting = f"""
📢 Job Opening: {template['fr']}

🏢 Company: {company_name}
📍 Location: Morocco
💼 Type: Full-time

📋 Responsibilities:
• Perform {template['fr']} tasks
• Collaborate with team
• Achieve monthly goals

✅ Requirements:
• Experience: {template['experience']}
• Skills: {', '.join(template['skills'])}
• Languages: Arabic, French
• Good communication

🎁 We offer:
• Competitive salary
• Health insurance
• Dynamic environment
• Growth opportunities

📧 Apply:
Send your CV to: hr@company.ma
"""
        return posting

    # ============================================
    # 3. أسئلة المقابلة
    # ============================================
    def get_interview_questions(self, category='general', lang='ar'):
        """توليد أسئلة المقابلة حسب اللغة"""
        questions = INTERVIEW_QUESTIONS.get(category, INTERVIEW_QUESTIONS['general'])
        # فلترة حسب اللغة
        filtered = [q[1] for q in questions if q[0] == lang]
        return filtered

    # ============================================
    # 4. تحليل المرشحين
    # ============================================
    def get_top_candidates(self, limit=5):
        """أفضل المرشحين"""
        if not self.analysis:
            return []
        return self.analysis[:limit]

    def get_statistics(self):
        """إحصائيات الفرز"""
        if not self.analysis:
            return {}

        total = len(self.analysis)
        avg_score = sum(c['score'] for c in self.analysis) / total if total > 0 else 0
        avg_exp = sum(c['experience'] for c in self.analysis) / total if total > 0 else 0

        return {
            "total_candidates": total,
            "average_score": round(avg_score, 1),
            "average_experience": round(avg_exp, 1),
            "top_candidate": self.analysis[0]['name'] if self.analysis else "—",
            "top_score": self.analysis[0]['score'] if self.analysis else 0,
        }


if __name__ == "__main__":
    print("✅ hr.py جاهز")
    print(f"📋 قوالب الوظائف: {len(JOB_TEMPLATES)}")
    print(f"❓ أسئلة مقابلة: {sum(len(v) for v in INTERVIEW_QUESTIONS.values())}")
