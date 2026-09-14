import calendar
import datetime

from django.core.management.base import BaseCommand

from main.models import Experience


EXPERIENCES = [
    ("Mercor", "English Music & Lyrics Expert", "Aug 2026 - Present", "freelance", "Data annotator role for music production and songwriting.", False),
    ("RISTEK Fasilkom UI", "Member, Data Science and Artificial Intelligence SIG", "Mar 2026 - Present", "seasonal", "Member of the Data Science and Artificial Intelligence Special Interest Group.", False),
    ("RISTEK DATATHON 2026", "Problem Setter and Quality Controller", "Apr 2026 - Aug 2026", "volunteer", "Designed data science competition problems for RISTEK DATATHON 2026, which attracted more than 1,000 participants.", True),
    ("RISTEK SISTECH 2026", "MLOps Teaching Assistant", "Jul 2026", "volunteer", "Supported students in machine learning operations concepts, workflows, and practical implementation.", True),
    ("Faculty of Computer Science UI", "Teaching Assistant for Intro to Digital System", "Jul 2026 - Present", "contract", "Teaching Assistant for Intro to Digital System (CSCM601150).", False),
    ("BEM Fasilkom UI", "Deputy of Student Academic Department", "May 2026 - Present", "seasonal", "Deputy in the student academic department.", False),
    ("Dasar-Dasar Pemrograman 0", "Mentor", "May 2026 - Aug 2026", "volunteer", "Mentored introductory programming participants.", True),
    ("OSUI Mahawaditra", "Vice Head of Bibliography", "Jan 2026 - Present", "seasonal", "Managed orchestral sheet-music archives, composed and arranged music, and taught music theory.", False),
    ("OSUI Mahawaditra", "Principal Trombonist", "Sep 2025 - Present", "seasonal", "Principal trombonist in the orchestra.", False),
    ("OSUI Mahawaditra", "Vice Project Officer, Musik Senja 2025", "Sep 2025 - Dec 2025", "volunteer", "Led Musik Senja 2025 project.", True),
    ("aimasukptn", "UTBK and TKA Mentor", "Nov 2025 - Present", "contract", "Taught UTBK subjects and TKA Mathematics, reaching 120 attendance in one live class session.", False),
    ("FORTE Pelajar Kota Yogyakarta", "Advisory Board Chairman", "Aug 2024 - Jan 2026", "seasonal", "Led the advisory board.", True),
    ("FORTE Pelajar Kota Yogyakarta", "Founder and Chairman", "Nov 2023 - Aug 2024", "seasonal", "Founded the inter-high-school orchestra organization and led a collaborative concert involving six schools.", True),
    ("Collaboration Concert 2024: Elithiya", "Initiator and Executive Director", "Dec 2023 - May 2024", "volunteer", "Developed artistic direction and repertoire, arranged music for orchestra, and performed as pianist.", True),
    ("Open House Fasilkom UI", "Staff, Event Division", "Aug 2025 - Nov 2025", "volunteer", "Supported event operations and planning.", True),
    ("Grand Concert 2025: Orlaphera", "Guest Conductor", "Sep 2024 - Jan 2025", "contract", "Guest conductor for Grand Concert 2025: Orlaphera.", True),
    ("Padzchestra", "Chairman", "Aug 2023 - Aug 2024", "seasonal", "Led orchestral production, rehearsals, operations, and external collaborations.", True),
    ("Grand Concert 2024: Celastria", "Executive Music Director, Composer, Conductor and Pianist", "Sep 2023 - Jan 2024", "contract", "Developed artistic direction, composed Celastria Overture, performed, and conducted the concert encore.", True),
    ("OSIS Padmanaba", "Staff of Arts and Culture Division", "Nov 2022 - Nov 2024", "seasonal", "Supported arts and culture division activities.", True),
    ("Pentas Besar Jubah Macan 2024: Enervated", "Conductor, Assistant Music Director and Composer", "Jun 2023 - May 2024", "volunteer", "Contributed as conductor, assistant music director, and composer.", True),
    ("Pentas Besar Jubah Macan 2023: Masquerade", "Assistant Music Director and Pianist", "Dec 2022 - May 2023", "volunteer", "Contributed as assistant music director and pianist.", True),
]


def completed_at(period):
    month, year = period.split(" - ")[-1].split()
    month_number = list(calendar.month_abbr).index(month)
    return datetime.datetime(
        int(year),
        month_number,
        calendar.monthrange(int(year), month_number)[1],
        tzinfo=datetime.timezone.utc,
    )


class Command(BaseCommand):
    help = "Create or update the versioned portfolio experience seed data."

    def handle(self, *args, **options):
        created = 0
        updated = 0

        for organization, position, period, category, description, completed in EXPERIENCES:
            _, was_created = Experience.objects.update_or_create(
                organization=organization,
                position=position,
                period=period,
                defaults={
                    "title": f"{organization}: {position}",
                    "category": category,
                    "description": description,
                    "ended_at": completed_at(period) if completed else None,
                },
            )
            created += was_created
            updated += not was_created

        self.stdout.write(self.style.SUCCESS(f"Seeded {created} new and updated {updated} existing experiences."))
