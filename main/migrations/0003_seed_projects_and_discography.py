from django.db import migrations


PROJECTS = [
    {
        "title": "Multimodal Rice Land-Suitability Research",
        "description": "Co-authored a low-resource system that prioritizes rice-land suitability for field verification in Kapuas Regency. It combines Sentinel-2 ResNet-18 embeddings with soil, climate, topographic, and hydrological features through late fusion.",
        "period": "2026 - Ongoing",
        "organization": "GEMASTIK Data Mining",
        "link_label": "Research summary",
        "link_url": "https://drive.google.com/file/d/1FhNL9Kn0hoJR_7mxKKwo-KKJo4QNccVH/view?usp=sharing",
        "tags": ["PyTorch", "ResNet-18", "Spatial CV", "SHAP", "Grad-CAM"],
    },
    {
        "title": "Music Instrument Recognition",
        "description": "Created and hosted a Kaggle competition for recognizing 21 instruments in polyphonic audio. Designed the annotations, train/test structure, multi-label submission format, and Macro F1 evaluation for class-imbalanced classification.",
        "period": "Jul - Aug 2026",
        "organization": "DATATHON 2026",
        "link_label": "View competition",
        "link_url": "https://www.kaggle.com/competitions/datathon-2026-hs-track-task-2-music-instrument-recognition-copy/overview",
        "tags": ["Music Information Retrieval", "Audio ML", "Multi-label Classification"],
    },
    {
        "title": "Indonesian LLM Knowledge Probe",
        "description": "Built a reproducible factual question-answering evaluation using 200 TyDi QA Indonesian questions, cached model outputs, and Indonesian versus English prompt conditions. Manual review showed where literal matching understates open-ended answer quality.",
        "period": "May 2026",
        "organization": "RISTEK Data Science & AI",
        "link_label": "Research summary",
        "link_url": "https://drive.google.com/file/d/1EKjFC9hsgHV94bj8JfNmjmGkb3v4EWJ_/view?usp=sharing",
        "tags": ["LLM Evaluation", "TyDi QA", "Prompt Evaluation"],
    },
    {
        "title": "Personal Portfolio Website",
        "description": "A responsive Django portfolio presenting my work across data, AI/ML, and music.",
        "period": "2026",
        "organization": "CSGE602022",
        "link_label": "Open site",
        "link_url": "https://rafael-arlen-myportfolio.pws.cs.ui.ac.id/",
        "tags": ["Django", "HTML", "CSS"],
    },
]

ENTRIES = [
    ("Harmoni Nusantara", "A musical work that won FLS2N provincial third-place result, with vocals by Rahmadini Vania Hasna A., band by Padzband 80, and orchestra by Padzchestra.", "Original song", "FLS2N 2024", "HARMONI_NUSANTARA_-_Rafael_Arlen_Wijanarko_-_Juara_3_FLS2N_Cipta_Lagu_SMA_2024_Tingkat_Provinsi_DIY.mp3", ["Writer", "Arranger", "Producer"], [("Official lyric video", "https://www.youtube.com/watch?v=FDkH-TcKMQY"), ("Performance video", "https://youtu.be/DmBs803btvY?si=fzTamd_65uqZ0hmS")]),
    ("Merangkai Sejarah", "An original song written by me and my friend, Feodora Elysia, for Padmanaba 80.", "Original song", "Padmanaba 80", "Merangkai_Sejarah_Padmanaba_80_Official_Lyric_Video.mp3", ["Writer", "Arranger", "Producer"], [("Open on Spotify", "https://open.spotify.com/track/5HYmNTfOePMdNdk43c0nN5?si=0352d83e941448f2")]),
    ("Mekar", "An original song/anthem written by me for Massa Padmanaba.", "Original song", "Massa Padmanaba", "Mekar_Anthem_Massa_Padmanaba_Official_Lyric_Video.mp3", ["Writer", "Arranger", "Producer"], [("Official lyric video", "https://www.youtube.com/watch?v=WBfnHn-40io")]),
    ("Breaking Horizon", "An original orchestral composition about freedom that feels so close yet so far.", "Original song", "Personal Project", "Breaking_Horizon_Original_CompositionFull_Orchestration.mp3", ["Writer", "Composer"], [("Score playback", "https://www.youtube.com/watch?v=aIk8HbBF9ys")]),
    ("Anak Jalanan", "An original theme song for SEGI Fest 2025 musical: Anak Jalanan.", "Original Song", "SEGI Fest 2025", "Anak_Jalanan_-_Theme_Song_Musikal_Jejak_Kata_Di_Lorong_Kota_Official_Audio.mp3", ["Co-Arranger", "Performer"], [("Official audio", "https://www.youtube.com/watch?v=24p-2l1klDY")]),
    ("Beast", "An original theme song for Pentas Besar Jubah Macan 2024: Enervated.", "Theme Song", "Pentas Besar Jubah Macan 2024: Enervated", "Beast_Theme_for_Pentas_Besar_Jubah_Macan_2024_Enervated.mp3", ["Writer", "Composer", "Conductor"], [("Score playback", "https://www.youtube.com/watch?v=oYD3lSO5u1w")]),
    ("Phantom's Final", "An original theme song for Pentas Besar Jubah Macan 2023: Masquarade.", "Theme Song", "Pentas Besar Jubah Macan 2023: Masquarade", "Phantoms_Final_Closing_of_Pentas_Besar_Jubah_Macan_2023_Masquarade.mp3", ["Writer", "Composer"], [("Score playback", "https://www.youtube.com/watch?v=Otn8LEwSgqk")]),
]


def seed_content(apps, schema_editor):
    Project = apps.get_model("main", "Project")
    ProjectTag = apps.get_model("main", "ProjectTag")
    DiscographyEntry = apps.get_model("main", "DiscographyEntry")
    DiscographyRole = apps.get_model("main", "DiscographyRole")
    DiscographyLink = apps.get_model("main", "DiscographyLink")

    for order, project_data in enumerate(PROJECTS, start=1):
        tags = project_data["tags"]
        project_defaults = {key: value for key, value in project_data.items() if key != "tags"}
        project, _ = Project.objects.get_or_create(title=project_data["title"], defaults={**project_defaults, "order": order})
        for tag_order, label in enumerate(tags, start=1):
            ProjectTag.objects.get_or_create(project=project, label=label, defaults={"order": tag_order})

    for order, (title, description, release_type, context, audio_filename, roles, links) in enumerate(ENTRIES, start=1):
        entry, _ = DiscographyEntry.objects.get_or_create(
            title=title,
            defaults={"description": description, "release_type": release_type, "context": context, "audio_filename": audio_filename, "order": order},
        )
        for role_order, label in enumerate(roles, start=1):
            DiscographyRole.objects.get_or_create(entry=entry, label=label, defaults={"order": role_order})
        for link_order, (label, url) in enumerate(links, start=1):
            DiscographyLink.objects.get_or_create(entry=entry, label=label, defaults={"url": url, "order": link_order})


def unseed_content(apps, schema_editor):
    apps.get_model("main", "Project").objects.filter(title__in=[project["title"] for project in PROJECTS]).delete()
    apps.get_model("main", "DiscographyEntry").objects.filter(title__in=[entry[0] for entry in ENTRIES]).delete()


class Migration(migrations.Migration):
    dependencies = [("main", "0002_discographyentry_project_discographylink_and_more")]
    operations = [migrations.RunPython(seed_content, unseed_content)]
