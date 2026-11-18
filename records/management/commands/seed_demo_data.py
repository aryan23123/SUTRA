from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError

from documents.models import Document
from records.models import Category, InformationRecord, Tag


DEMO_MARKER = "[SUTRA DEMO]"

CATEGORIES = (
    ("Placement Preparation", "Placement timelines, practice plans, and application research."),
    ("Projects & Development", "Build notes, project plans, implementation details, and release checklists."),
    ("Internships & Applications", "Research and preparation material for internship opportunities."),
    ("Resume & Career", "Working drafts and practical career-development checklists."),
    ("Technical Interview Preparation", "Revision notes and practice plans for technical interviews."),
    ("University & Academics", "Course notes, semester planning, and university submission checklists."),
    ("Certifications & Courses", "Self-paced study plans for courses and professional certifications."),
    ("Events & Activities", "Planning notes for campus events, clubs, and student activities."),
    ("Personal Learning", "Longer-term learning goals and independent study plans."),
    ("Important Documents", "An index for keeping useful academic and career documents easy to find."),
)

TAG_NAMES = (
    "DEMO DATA",
    "DSA",
    "C++",
    "Python",
    "Django",
    "React",
    "JavaScript",
    "SQL",
    "DBMS",
    "Operating Systems",
    "Computer Networks",
    "Full Stack",
    "Backend",
    "Frontend",
    "GitHub",
    "Resume",
    "Interview",
    "Aptitude",
    "HR Round",
    "Internship",
    "Placement 2026",
    "Final Year",
    "LPU",
    "Project Documentation",
    "High Priority",
    "In Progress",
)

RECORDS = (
    {
        "title": "TCS NQT 2026 Preparation Plan",
        "category": "Placement Preparation",
        "status": "active",
        "tags": ("Aptitude", "DSA", "Placement 2026", "LPU", "High Priority"),
        "description": (
            "A fictional final-year LPU B.Tech CSE student's preparation outline; "
            "it does not represent an application, test attempt, or company outcome.\n\n"
            "Focus areas: quantitative aptitude, verbal ability, logical reasoning, "
            "and timed programming practice. Keep separate notes for questions that "
            "need a second attempt, and record practice scores without treating them "
            "as a prediction of a hiring result.\n\n"
            "Next steps: choose three weekly practice blocks, review errors on Sunday, "
            "and verify the current test format from official public sources before "
            "making a final schedule."
        ),
    },
    {
        "title": "DSA Practice Tracker — Arrays to Dynamic Programming",
        "category": "Placement Preparation",
        "status": "active",
        "tags": ("DSA", "C++", "Python", "Interview", "In Progress", "DEMO DATA"),
        "description": (
            "A reusable practice tracker for a fictional student preparing for "
            "entry-level software interviews.\n\n"
            "Topics: arrays and strings; two pointers and sliding windows; hashing; "
            "stacks and queues; binary search; trees and graphs; recursion; and "
            "introductory dynamic programming. For each problem, note the first "
            "approach, complexity, one edge case, and the reason a later revision "
            "is needed.\n\n"
            "Current stage: consolidating arrays, strings, and hash maps before "
            "moving to trees. Next: solve a small set of timed problems, then revisit "
            "missed questions after two days and again the following week."
        ),
    },
    {
        "title": "Cognizant GenC Aptitude & Coding Practice",
        "category": "Placement Preparation",
        "status": "draft",
        "tags": ("Aptitude", "C++", "Python", "Placement 2026", "LPU"),
        "description": (
            "Demonstration preparation notes only; no application or selection is "
            "being claimed. Use this page to organize aptitude drills, basic coding "
            "patterns, and communication practice for a campus hiring season.\n\n"
            "Practice list: percentages, ratios, time and work, number series, "
            "string manipulation, array traversal, and input/output handling. Keep "
            "a short log of the question type, time spent, and what to revise.\n\n"
            "Next: confirm any role-specific eligibility and test details from the "
            "company's official careers information before using this plan."
        ),
    },
    {
        "title": "Placement Application Research — India 2026",
        "category": "Placement Preparation",
        "status": "active",
        "tags": ("Placement 2026", "LPU", "Resume", "High Priority"),
        "description": (
            "A research board for a fictional LPU student to compare fresher roles "
            "without implying that any application has been submitted.\n\n"
            "For each company or role, capture the official careers link, job title, "
            "location, eligibility wording, required skills, application deadline "
            "if published, and the date the information was checked. Keep company "
            "claims out of this note unless they are verified on an official page.\n\n"
            "Next: shortlist roles that match the student's current skills, tailor "
            "a resume draft, and move only verified opportunities into a personal "
            "application tracker."
        ),
    },
    {
        "title": "HR Interview Questions — Answer Workbook",
        "category": "Technical Interview Preparation",
        "status": "draft",
        "tags": ("Interview", "HR Round", "Resume", "LPU"),
        "description": (
            "A private drafting space for concise, truthful interview responses. "
            "The example persona is fictional; replace every answer with the "
            "student's own experience before using it.\n\n"
            "Prompts to prepare: introduce yourself; explain a project decision; "
            "describe a challenge and what you learned; discuss a subject you are "
            "currently improving; and explain what kind of first role you are "
            "seeking. Keep answers specific, avoid memorized claims, and prepare "
            "one thoughtful question about the team or role.\n\n"
            "Next: draft bullet points, read them aloud, and remove any statement "
            "that cannot be supported with a real example."
        ),
    },
    {
        "title": "Technical Interview Checklist — Java, DBMS & OS",
        "category": "Technical Interview Preparation",
        "status": "active",
        "tags": ("Interview", "DBMS", "Operating Systems", "Computer Networks", "SQL"),
        "description": (
            "A topic checklist for entry-level software engineering interview "
            "revision. It is a study aid, not a record of an interview attended.\n\n"
            "DBMS: keys, normalization, joins, indexes, and transaction basics. "
            "Operating systems: processes versus threads, scheduling, memory, and "
            "deadlocks. Networking: DNS, HTTP request flow, TCP basics, and common "
            "status codes. Programming: explain a solution, complexity, and edge "
            "cases before optimizing.\n\n"
            "Next: prepare a one-minute explanation for each topic, then test recall "
            "with short questions rather than rereading the same notes."
        ),
    },
    {
        "title": "Information Management System — Sutra",
        "category": "Projects & Development",
        "status": "active",
        "tags": ("Django", "Python", "Backend", "SQL", "Project Documentation", "LPU"),
        "description": (
            "Demonstration project brief for Sutra, a Django information-management "
            "workspace. The goal is to keep records, tags, categories, and documents "
            "organized in one searchable place.\n\n"
            "Stack: Python, Django, Django templates, and SQLite for local "
            "development. The project is split into accounts, records, and documents "
            "apps. Existing flows include registration and login, record CRUD, "
            "category and tag management, filters, exports, and authenticated "
            "document downloads.\n\n"
            "Progress notes: review the dashboard with realistic content, verify "
            "repeatable demo seeding, and keep the README aligned with setup steps. "
            "Next: run the test suite after each feature and check empty states on "
            "a clean database."
        ),
    },
    {
        "title": "Full Stack Developer Portfolio Roadmap",
        "category": "Projects & Development",
        "status": "active",
        "tags": ("Full Stack", "React", "JavaScript", "Django", "GitHub", "Frontend"),
        "description": (
            "A staged plan for a fictional student portfolio that presents a few "
            "well-explained projects instead of a long list of unfinished demos.\n\n"
            "Plan: choose a simple responsive layout; write clear project summaries; "
            "link each project to its source repository; include setup instructions "
            "and screenshots only when they are the student's own; and note the "
            "trade-offs made in each build. Potential practice stack: React for a "
            "small UI, Django for a server-rendered app, and SQLite or PostgreSQL "
            "depending on project needs.\n\n"
            "Next: finish one project README, check mobile layout, and ask a peer "
            "to follow the setup instructions from a clean checkout."
        ),
    },
    {
        "title": "Student Expense Tracker — Django Project Plan",
        "category": "Projects & Development",
        "status": "draft",
        "tags": ("Django", "Python", "SQL", "Backend", "Project Documentation"),
        "description": (
            "An original practice-project outline for tracking sample monthly "
            "expenses. Use fictional entries only; do not enter bank credentials "
            "or sensitive financial details.\n\n"
            "Minimum scope: add, edit, and categorize an expense; filter a date "
            "range; show totals by category; and export a small report. Model ideas "
            "include an amount, date, category, and optional note. Validate positive "
            "amounts and show an empty state before any entries exist.\n\n"
            "Next: sketch the model and form, then write tests for filtering and "
            "invalid amounts before styling charts."
        ),
    },
    {
        "title": "Final Year Project — Technical Documentation",
        "category": "Projects & Development",
        "status": "active",
        "tags": ("Final Year", "Project Documentation", "Django", "Python", "LPU"),
        "description": (
            "A documentation outline for a fictional final-year CSE project at "
            "Lovely Professional University, Phagwara. It is not an official "
            "university submission or assessment record.\n\n"
            "Sections to maintain: problem statement; intended users; requirements; "
            "architecture diagram; data model; key workflows; test approach; "
            "limitations; and future work. Keep screenshots and diagrams original, "
            "and distinguish implemented features from planned work.\n\n"
            "Next: update the implementation status after each milestone, verify "
            "references, and check the current faculty-provided format before "
            "preparing any formal submission."
        ),
    },
    {
        "title": "GitHub Profile & Repository Checklist",
        "category": "Resume & Career",
        "status": "active",
        "tags": ("GitHub", "Resume", "Python", "Full Stack", "High Priority"),
        "description": (
            "A practical checklist for presenting coursework and personal builds "
            "clearly. This is a preparation note, not a claim about a real student's "
            "profile or contribution history.\n\n"
            "For each repository: use a descriptive name; add a short README with "
            "purpose, stack, setup, and known limitations; remove local databases, "
            "credentials, and generated files; and make sure the license and "
            "attribution are appropriate. Pin a small number of complete projects "
            "rather than every lab exercise.\n\n"
            "Next: review one repository from a fresh clone and confirm its "
            "instructions work without private files."
        ),
    },
    {
        "title": "Summer Internship Research Tracker",
        "category": "Internships & Applications",
        "status": "active",
        "tags": ("Internship", "Resume", "Placement 2026", "LPU"),
        "description": (
            "A research template for a fictional student exploring summer software "
            "internships in India. It does not claim that any company has been "
            "contacted or that an application is underway.\n\n"
            "Track only verified public information: role title, location or remote "
            "policy, eligibility, listed skills, official application page, date "
            "checked, and questions to resolve. Skill gaps to review may include "
            "data structures, Git, SQL, one backend framework, and communicating "
            "project decisions.\n\n"
            "Next: update the resume draft, shortlist roles that match current "
            "eligibility, and follow each organization's official application "
            "instructions."
        ),
    },
    {
        "title": "Software Developer Internship — Application Prep",
        "category": "Internships & Applications",
        "status": "draft",
        "tags": ("Internship", "Resume", "GitHub", "Interview"),
        "description": (
            "A reusable preparation packet for a possible software developer "
            "internship application. No application, interview, or selection is "
            "claimed by this fictional example.\n\n"
            "Before applying: compare the role requirements with completed "
            "coursework; select two projects that can be explained honestly; check "
            "repository READMEs; prepare a concise resume version; and write down "
            "any questions about location, dates, and eligibility. Keep a follow-up "
            "date only after a real application is submitted.\n\n"
            "Next: replace this checklist with verified role details and remove "
            "items that do not apply."
        ),
    },
    {
        "title": "Software Engineer Resume — Working Draft",
        "category": "Resume & Career",
        "status": "draft",
        "tags": ("Resume", "Full Stack", "GitHub", "Final Year"),
        "description": (
            "A resume structure for a fictional final-year B.Tech CSE student. "
            "This is not a real person's resume and contains no personal contact "
            "information, registration number, or employment claim.\n\n"
            "Suggested sections: education; technical skills the student can "
            "demonstrate; two or three projects with concrete contributions; "
            "coursework relevant to the role; and verified certifications. Use "
            "measurable outcomes only when they are real and can be explained.\n\n"
            "Next: tailor the skills and project order to a specific role, check "
            "spelling and links, and export a readable one-page PDF from the "
            "student's own editor."
        ),
    },
    {
        "title": "LinkedIn Profile Improvement Checklist",
        "category": "Resume & Career",
        "status": "active",
        "tags": ("Resume", "GitHub", "Internship", "Placement 2026"),
        "description": (
            "A neutral checklist for a student who wants a clear professional "
            "profile before beginning a job or internship search.\n\n"
            "Review the headline for role interests rather than unverified claims; "
            "write a short About section in the student's own words; add projects "
            "with a brief explanation and working links; list skills that can be "
            "supported with coursework or practice; and check that public contact "
            "details are intentional.\n\n"
            "Next: ask a trusted peer to proofread for clarity and remove any "
            "personal information that should not be public."
        ),
    },
    {
        "title": "INT253 Django Practical Notes",
        "category": "University & Academics",
        "status": "active",
        "tags": ("Django", "Python", "SQL", "LPU", "Final Year"),
        "description": (
            "Study notes organized around the Django practical workflow: project "
            "settings and apps; URL patterns and views; templates and inheritance; "
            "forms, CSRF, and post/redirect/get; models, migrations, and ORM "
            "relationships; and authentication with protected routes.\n\n"
            "For each practical, record the command used, the file changed, one "
            "common error, and a small test that proves the behavior. Keep examples "
            "local and use fictional data. This note is a personal study aid, not "
            "an official LPU handout.\n\n"
            "Next: run migrations on a disposable database and explain how a "
            "ModelForm maps to the model fields."
        ),
    },
    {
        "title": "CSE Final Semester Study & Submission Checklist",
        "category": "University & Academics",
        "status": "active",
        "tags": ("Final Year", "LPU", "High Priority", "Project Documentation"),
        "description": (
            "A planning checklist for a fictional final-semester CSE student at "
            "LPU Phagwara. Confirm all dates, evaluation rules, and submission "
            "formats in current university or faculty communications; this page "
            "is not an official calendar.\n\n"
            "Weekly review: list upcoming assessments, lab work, project milestones, "
            "and revision blocks. For each task, note the next concrete action, "
            "dependencies, and a realistic time estimate. Reserve time to check "
            "required file formats and submission links before deadlines.\n\n"
            "Next: copy only verified dates from the current course information "
            "and review the list at the start of each week."
        ),
    },
    {
        "title": "Cloud Fundamentals — Certification Study Plan",
        "category": "Certifications & Courses",
        "status": "draft",
        "tags": ("Python", "SQL", "In Progress"),
        "description": (
            "A vendor-neutral study plan for learning cloud concepts before "
            "choosing a certification. It does not indicate enrollment in or "
            "completion of any certification.\n\n"
            "Topics: regions and availability zones; identity and access basics; "
            "compute, storage, and managed databases; networking fundamentals; "
            "monitoring; and cost awareness. Use free official learning material "
            "and avoid entering payment details into unverified sites.\n\n"
            "Next: complete one topic at a time, make a small architecture sketch, "
            "and decide whether a specific certification is useful for the roles "
            "the student is researching."
        ),
    },
    {
        "title": "LPU Tech Fest — Participation Planner",
        "category": "Events & Activities",
        "status": "draft",
        "tags": ("LPU", "Final Year", "In Progress"),
        "description": (
            "A fictional campus-event planning note for organizing time around "
            "classes and project work. It does not claim attendance at a specific "
            "event or represent official LPU event information.\n\n"
            "Before committing: check the current event notice, schedule, venue, "
            "registration requirements, and team responsibilities through official "
            "channels. Keep a short checklist for preparation and a note on how "
            "participation fits around coursework.\n\n"
            "Next: add only confirmed details and remove this plan if the event "
            "does not fit the semester schedule."
        ),
    },
    {
        "title": "Python to Full Stack — Personal Learning Roadmap",
        "category": "Personal Learning",
        "status": "active",
        "tags": ("Python", "Django", "React", "JavaScript", "Full Stack", "In Progress"),
        "description": (
            "A self-study sequence for a fictional student building practical "
            "software skills alongside university work.\n\n"
            "Sequence: strengthen Python and testing basics; build a small Django "
            "application with forms and relational data; learn HTTP and JSON; add "
            "a focused JavaScript or React interface; and practice Git workflows, "
            "SQL queries, and deployment concepts. Build one small project at each "
            "stage rather than collecting tutorials without applying them.\n\n"
            "Next: choose a weekly time budget, finish the Django CRUD exercise, "
            "and write down what remains unclear before adding another framework."
        ),
    },
    {
        "title": "Important Documents Index — Final Year",
        "category": "Important Documents",
        "status": "active",
        "tags": ("Final Year", "LPU", "Resume", "Project Documentation"),
        "description": (
            "A private index for a student's own academic and career files. Store "
            "only documents the student is authorized to keep; do not upload "
            "someone else's identity documents or sensitive records into a demo "
            "workspace.\n\n"
            "Suggested groups: current resume drafts; project notes; course "
            "materials; public certificates; and application preparation. Use "
            "clear filenames, note the source and date, and keep a separate secure "
            "backup for any sensitive originals.\n\n"
            "Next: review each file's contents before upload and remove personal "
            "data from demonstration copies."
        ),
    },
)

SAMPLE_DOCUMENTS = (
    {
        "record": "Software Engineer Resume — Working Draft",
        "title": "Sample — Software Engineer Resume",
        "filename": "Sample_Software_Engineer_Resume.txt",
        "content": """[SAMPLE DOCUMENT — DEMONSTRATION ONLY]
This is an original resume outline for a fictional final-year B.Tech CSE student.
It contains no real contact details, registration number, work history, or claims.

PROFILE
Final-year computer science student interested in backend and full-stack software
development. Replace this summary with accurate information before personal use.

EDUCATION
B.Tech, Computer Science and Engineering
Fictional university entry — add verified dates and details yourself.

PROJECTS
Sutra — Information Management System
- Built a Django workspace for categorized records, tags, and documents.
- Describe only features you implemented and can explain in an interview.

SKILLS
Python, Django, SQL, Git, JavaScript
Keep only skills you can demonstrate with a project or practical exercise.

Reminder: this sample is not a real resume and must not be submitted as one.
""",
    },
    {
        "record": "DSA Practice Tracker — Arrays to Dynamic Programming",
        "title": "Sample — DSA Interview Revision Notes",
        "filename": "DSA_Interview_Revision_Notes.txt",
        "content": """[SAMPLE DOCUMENT — DEMONSTRATION ONLY]
Original revision prompts for a fictional student. No interview or hiring outcome
is represented.

ARRAYS AND STRINGS
- State the input constraints before choosing an approach.
- Check empty input, one item, duplicates, and boundary indices.
- Compare a direct scan with sorting or a hash-based approach.

TWO POINTERS AND SLIDING WINDOWS
- Identify whether the window can grow and shrink monotonically.
- Explain what each pointer represents and when it moves.

TREES AND GRAPHS
- Choose DFS or BFS based on the question.
- Track visited nodes and explain the memory trade-off.

DYNAMIC PROGRAMMING
- Define the state in one sentence.
- Write the transition and base cases before coding.
- Test the smallest input and one repeated-subproblem example.

Practice loop: solve, explain complexity, record one mistake, revisit after two
days. These notes are study prompts, not official company questions.
""",
    },
    {
        "record": "Information Management System — Sutra",
        "title": "Sample — Django Project Documentation",
        "filename": "Django_Project_Documentation.txt",
        "content": """[SAMPLE DOCUMENT — DEMONSTRATION ONLY]
Original project overview for Sutra, a Django information-management application.

OBJECTIVE
Keep notes and reference material organized as records with categories, tags,
statuses, and related documents.

TECHNOLOGY
Python and Django; Django templates and forms; SQLite for local development.

APPLICATIONS
- accounts: registration, login, and logout
- records: categories, tags, searchable records, dashboard, and exports
- documents: validated uploads and authenticated downloads

CORE WORKFLOW
Create a record, assign an optional category and useful tags, attach an original
PDF, DOCX, or TXT file, then search or filter the workspace later.

NEXT REVIEW
Run the test suite, verify empty states on a clean database, and keep demo data
clearly marked. This document does not claim that every planned improvement is
already implemented.
""",
    },
    {
        "record": "Summer Internship Research Tracker",
        "title": "Sample — Internship Application Tracker",
        "filename": "Internship_Application_Tracker.txt",
        "content": """[SAMPLE DOCUMENT — DEMONSTRATION ONLY]
Blank research template for a fictional student exploring software internships
in India. It does not indicate that any application has been submitted.

For each opportunity, verify and record:
- organization and role from an official careers page
- location, dates, eligibility, and listed skills
- official application link and the date it was checked
- resume version to prepare and project links to review
- next action, only after the student decides to apply

Research checklist:
[ ] Confirm the role is still open on the official source.
[ ] Compare eligibility with current academic details.
[ ] Tailor the resume truthfully to the listed work.
[ ] Check links and remove private information from shared files.
[ ] Record a follow-up date only after a real submission.

Never infer an application, interview, offer, or selection from this sample.
""",
    },
    {
        "record": "Technical Interview Checklist — Java, DBMS & OS",
        "title": "Sample — Technical Interview Checklist",
        "filename": "Technical_Interview_Checklist.txt",
        "content": """[SAMPLE DOCUMENT — DEMONSTRATION ONLY]
Revision checklist for a fictional entry-level software engineering candidate.

PROGRAMMING
[ ] Explain the approach before writing code.
[ ] Cover edge cases and time/space complexity.
[ ] Use clear names and test a small example.

DBMS AND SQL
[ ] Explain primary and foreign keys.
[ ] Compare common joins and describe normalization.
[ ] Discuss indexes and transaction basics.

OPERATING SYSTEMS AND NETWORKS
[ ] Distinguish a process from a thread.
[ ] Explain deadlock conditions at a high level.
[ ] Trace a browser request using DNS, HTTP, and TCP concepts.

PROJECT DISCUSSION
[ ] State the problem, personal contribution, design choice, and limitation.
[ ] Do not claim features or outcomes that were not implemented.

Use this as a study checklist; it is not an official employer test.
""",
    },
    {
        "record": "Full Stack Developer Portfolio Roadmap",
        "title": "Sample — Full Stack Project Overview",
        "filename": "Full_Stack_Project_Overview.txt",
        "content": """[SAMPLE DOCUMENT — DEMONSTRATION ONLY]
An original outline for presenting a small full-stack student project.

PROJECT SUMMARY
Describe one real problem the application solves and who would use it.

DESIGN
List the main pages, responsive behavior, accessibility choices, and empty states.

IMPLEMENTATION
Frontend: record the UI framework and key components actually used.
Backend: summarize routes, validation, authentication, and error handling.
Data: list the models and important relationships.

QUALITY
Include a small set of meaningful tests, setup instructions, and known limitations.
Do not include secrets, local databases, or another person's data in a repository.

NEXT REVIEW
Ask a peer to follow the README from a clean checkout and note where instructions
are unclear. Replace this outline with details from the student's own project.
""",
    },
    {
        "record": "TCS NQT 2026 Preparation Plan",
        "title": "Sample — Placement Preparation Roadmap",
        "filename": "Placement_Preparation_Roadmap.txt",
        "content": """[SAMPLE DOCUMENT — DEMONSTRATION ONLY]
A balanced preparation outline for a fictional LPU student. It does not represent
an application, test attempt, or company result.

WEEKLY AREAS
- Quantitative aptitude and logical reasoning
- Reading comprehension and written communication
- Data structures and timed coding practice
- Resume review and project explanations

STUDY LOOP
1. Pick a small, measurable topic for each practice block.
2. Record errors and the underlying concept, not only the score.
3. Revisit difficult questions later in the week.
4. Keep time for coursework, rest, and project work.

Before using a company-specific plan, verify current test details and eligibility
through official public sources. Practice scores are not a hiring prediction.
""",
    },
    {
        "record": "Final Year Project — Technical Documentation",
        "title": "Sample — Final Year Project Checklist",
        "filename": "Final_Year_Project_Checklist.txt",
        "content": """[SAMPLE DOCUMENT — DEMONSTRATION ONLY]
Planning checklist for a fictional final-year CSE project at LPU Phagwara. This
is not an official university document or submission checklist.

PROJECT MATERIAL
[ ] State the problem and intended users.
[ ] Keep requirements separate from future ideas.
[ ] Draw the architecture and data model.
[ ] Explain implemented features and known limitations.
[ ] Include original diagrams and properly attributed references.

REVIEW
[ ] Run tests from a clean local setup.
[ ] Confirm the README and setup steps are current.
[ ] Check the latest faculty-provided format and deadlines.
[ ] Remove personal data and credentials from shared copies.

Use current university communications for official requirements and dates.
""",
    },
)


class Command(BaseCommand):
    help = "Create clearly marked Sutra student demo data for an existing user."

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            required=True,
            help="Existing active account to own the demonstration records.",
        )

    def handle(self, *args, **options):
        username = options["username"]
        user = get_user_model()._default_manager.filter(username=username).first()
        if user is None or not user.is_active:
            raise CommandError(
                f"No active account named {username!r} exists. Create an account "
                "first; this command never creates accounts."
            )

        categories = {}
        created_categories = 0
        for name, description in CATEGORIES:
            category, created = Category.objects.get_or_create(
                name=name,
                defaults={"description": description},
            )
            categories[name] = category
            created_categories += int(created)

        tags = {}
        created_tags = 0
        for name in TAG_NAMES:
            tag, created = Tag.objects.get_or_create(name=name)
            tags[name] = tag
            created_tags += int(created)

        records = {}
        created_records = 0
        reused_demo_records = 0
        skipped_conflicts = 0
        for item in RECORDS:
            existing = InformationRecord.objects.filter(
                title=item["title"],
                created_by=user,
            ).first()
            if existing is not None:
                if DEMO_MARKER not in existing.description:
                    skipped_conflicts += 1
                    self.stderr.write(
                        self.style.WARNING(
                            f"Skipped existing non-demo record {item['title']!r}; "
                            "it was not changed."
                        )
                    )
                    continue
                records[item["title"]] = existing
                reused_demo_records += 1
                continue

            record = InformationRecord.objects.create(
                title=item["title"],
                description=f"{DEMO_MARKER} Fictional student workspace example. "
                f"No real application, interview, offer, or academic result is "
                f"represented.\n\n{item['description']}",
                status=item["status"],
                category=categories[item["category"]],
                created_by=user,
            )
            record.tags.add(
                tags["DEMO DATA"],
                *(tags[tag_name] for tag_name in item["tags"]),
            )
            records[item["title"]] = record
            created_records += 1

        created_documents = 0
        existing_documents = 0
        for item in SAMPLE_DOCUMENTS:
            record = records.get(item["record"])
            if record is None:
                continue
            if Document.objects.filter(record=record, title=item["title"]).exists():
                existing_documents += 1
                continue

            document = Document(
                title=item["title"],
                record=record,
                uploaded_by=user,
            )
            content = f"{DEMO_MARKER}\n{item['content']}"
            document.file.save(
                item["filename"],
                ContentFile(content.encode("utf-8")),
                save=False,
            )
            document.save()
            created_documents += 1

        self.stdout.write(
            self.style.SUCCESS(
                "Sutra demo data complete: "
                f"{created_categories} categories and {created_tags} tags created; "
                f"{created_records} records created, {reused_demo_records} existing "
                f"demo records reused, {skipped_conflicts} user records skipped; "
                f"{created_documents} sample documents created, "
                f"{existing_documents} existing documents reused."
            )
        )
