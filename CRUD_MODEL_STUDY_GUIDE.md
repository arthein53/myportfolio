# Panduan Membuat Model dan CRUD Baru di Django

Panduan belajar untuk project `myportfolio`.

## Ringkasan Alur

Urutan implementasi fitur baru:

1. Buat **model** di `main/models.py`.
2. Jalankan **migration**.
3. Buat **ModelForm** di `main/forms.py`.
4. Buat view **Create, Read, Update, Delete** di `main/views.py`.
5. Daftarkan URL di `main/urls.py`.
6. Buat template di folder `templates/`.
7. Daftarkan model ke Django Admin jika diperlukan.
8. Buat dan jalankan test.

> Hafalan utama: **Model → Migration → Form → View → URL → Template → Test**.

---

# Contoh Fitur: Achievement

Fitur ini menyimpan pencapaian dengan data berikut:

- judul pencapaian;
- organisasi penerbit;
- tanggal pencapaian;
- deskripsi.

## Pemetaan CRUD

| Operasi | Method | URL | Hasil |
|---|---|---|---|
| Read | `GET` | `/achievements/` | Menampilkan daftar achievement |
| Create form | `GET` | `/achievements/add/` | Menampilkan form kosong |
| Create data | `POST` | `/achievements/add/` | Menyimpan object baru |
| Update form | `GET` | `/achievements/<id>/update/` | Menampilkan data lama dalam form |
| Update data | `POST` | `/achievements/<id>/update/` | Mengubah object lama |
| Delete | `POST` | `/achievements/<id>/delete/` | Menghapus object |

---

# 1. Membuat Model

Tambahkan ke `main/models.py`:

```python
class Achievement(models.Model):
    title = models.CharField(max_length=255)
    issuer = models.CharField(max_length=255)
    achieved_at = models.DateField()
    description = models.TextField(blank=True)

    class Meta:
        ordering = ("-achieved_at", "title")

    def __str__(self):
        return self.title
```

## Penjelasan

### `CharField`

```python
title = models.CharField(max_length=255)
```

Digunakan untuk teks pendek. `max_length` menentukan panjang maksimum data.

### `DateField`

```python
achieved_at = models.DateField()
```

Menyimpan tanggal tanpa jam.

### `TextField`

```python
description = models.TextField(blank=True)
```

Digunakan untuk teks panjang. `blank=True` berarti field boleh kosong ketika divalidasi oleh form.

### `Meta.ordering`

```python
ordering = ("-achieved_at", "title")
```

Achievement diurutkan berdasarkan tanggal terbaru. Tanda `-` berarti descending.

### `__str__`

```python
def __str__(self):
    return self.title
```

Menentukan representasi object yang mudah dibaca di Django Admin dan Django shell.

---

# 2. Menjalankan Migration

Setelah mengubah model, jalankan:

```bash
env/bin/python manage.py makemigrations
env/bin/python manage.py migrate
```

## Perbedaan perintah

### `makemigrations`

Membuat file instruksi perubahan database berdasarkan perubahan di `models.py`.

Contoh file yang dihasilkan:

```text
main/migrations/0008_achievement.py
```

### `migrate`

Menjalankan instruksi migration ke database sehingga tabel benar-benar dibuat.

> Mengubah `models.py` saja belum mengubah database.

---

# 3. Membuat ModelForm

Ubah import pada `main/forms.py`:

```python
from main.models import Achievement, DiscographyEntry, Experience, Project
```

Tambahkan form:

```python
class AchievementForm(ModelForm):
    write_secret = forms.CharField(
        label="Password",
        required=False,
        widget=PasswordInput(
            attrs={
                "autocomplete": "off",
                "placeholder": "Portfolio password",
            }
        ),
        help_text="Required to save changes. This value is never stored.",
    )

    class Meta:
        model = Achievement
        fields = [
            "title",
            "issuer",
            "achieved_at",
            "description",
        ]
        widgets = {
            "title": TextInput(
                attrs={"placeholder": "Hackathon Winner"}
            ),
            "issuer": TextInput(
                attrs={"placeholder": "Universitas Indonesia"}
            ),
            "achieved_at": forms.DateInput(
                attrs={"type": "date"}
            ),
            "description": Textarea(
                attrs={
                    "placeholder": "Describe the achievement",
                    "rows": 4,
                }
            ),
        }
```

## Fungsi ModelForm

`ModelForm` menangani:

- pembuatan input berdasarkan model;
- validasi data;
- konversi tipe data;
- penyimpanan dengan `form.save()`;
- penyediaan pesan error.

`write_secret` tidak dimasukkan ke `Meta.fields` karena bukan field model. Nilai tersebut hanya digunakan untuk otorisasi dan tidak disimpan ke database.

---

# 4. Menambahkan Import pada Views

Ubah import di `main/views.py`:

```python
from .forms import (
    AchievementForm,
    DiscographyForm,
    ExperienceForm,
    ProjectForm,
)
from .models import Achievement, DiscographyEntry, Experience, Project
```

---

# 5. Membuat Read View

Tambahkan ke `main/views.py`:

```python
def show_achievements(request):
    achievements = Achievement.objects.all()

    return render(
        request,
        "achievements.html",
        {
            "name": "Arlen",
            "achievement_list": achievements,
        },
    )
```

## Alur request dan response

```text
GET /achievements/
        ↓
show_achievements(request)
        ↓
Achievement.objects.all()
        ↓
render achievements.html
        ↓
HTTP 200 + HTML
```

`Achievement.objects.all()` menghasilkan `QuerySet` berisi seluruh object Achievement.

---

# 6. Membuat Create View

Tambahkan ke `main/views.py`:

```python
def create_achievement(request):
    form = AchievementForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        submitted_secret = form.cleaned_data["write_secret"]

        if not has_valid_write_secret(request, submitted_secret):
            form.add_error("write_secret", "Invalid write code.")
        else:
            form.save()
            messages.success(
                request,
                "Achievement added successfully.",
            )
            return redirect("main:show_achievements")

    return render(
        request,
        "achievement_form.html",
        {
            "name": "Arlen",
            "form": form,
            "page_title": "Add achievement",
            "submit_label": "Save achievement",
        },
    )
```

## Saat menerima GET

```python
form = AchievementForm(request.POST or None)
```

Pada GET, `request.POST` kosong sehingga form dibuat tanpa data dan ditampilkan sebagai form kosong.

## Saat menerima POST

Urutannya:

1. data `request.POST` dimasukkan ke form;
2. `form.is_valid()` memvalidasi data;
3. write secret diperiksa;
4. `form.save()` membuat object baru;
5. success message disimpan;
6. browser diarahkan ke halaman daftar.

## Jika form tidak valid

View kembali merender template yang sama. Form mempertahankan input user dan menampilkan pesan error.

---

# 7. Membuat Update View

Tambahkan ke `main/views.py`:

```python
def update_achievement(request, achievement_id):
    achievement = get_object_or_404(
        Achievement,
        pk=achievement_id,
    )

    form = AchievementForm(
        request.POST or None,
        instance=achievement,
    )

    if request.method == "POST" and form.is_valid():
        submitted_secret = form.cleaned_data["write_secret"]

        if not has_valid_write_secret(request, submitted_secret):
            form.add_error("write_secret", "Invalid write code.")
        else:
            form.save()
            messages.success(
                request,
                "Achievement updated successfully.",
            )
            return redirect("main:show_achievements")

    return render(
        request,
        "achievement_form.html",
        {
            "name": "Arlen",
            "form": form,
            "page_title": "Update achievement",
            "submit_label": "Update achievement",
        },
    )
```

## `get_object_or_404`

```python
achievement = get_object_or_404(
    Achievement,
    pk=achievement_id,
)
```

Perintah ini mencari achievement berdasarkan primary key. Jika object tidak ditemukan, Django mengembalikan HTTP `404 Not Found`.

## `instance=achievement`

```python
form = AchievementForm(
    request.POST or None,
    instance=achievement,
)
```

`instance` memberi tahu form bahwa object lama harus diubah.

Perbedaan utama:

```python
AchievementForm(request.POST or None)
```

Digunakan untuk **create**.

```python
AchievementForm(request.POST or None, instance=achievement)
```

Digunakan untuk **update**.

Tanpa `instance`, `form.save()` akan membuat object baru, bukan mengubah object lama.

---

# 8. Membuat Delete View

Tambahkan ke `main/views.py`:

```python
def delete_achievement(request, achievement_id):
    achievement = get_object_or_404(
        Achievement,
        pk=achievement_id,
    )

    if request.method == "POST":
        submitted_secret = request.POST.get("password", "")

        if has_valid_write_secret(request, submitted_secret):
            achievement.delete()
            messages.success(
                request,
                "Achievement deleted successfully.",
            )
        else:
            messages.error(
                request,
                "Invalid password. Nothing was deleted.",
            )

    return redirect("main:show_achievements")
```

## Mengapa delete menggunakan POST?

Delete mengubah state database. Request GET seharusnya hanya membaca data dan tidak menimbulkan perubahan.

Gunakan form:

```html
<form method="post">
```

Jangan gunakan link GET untuk menghapus data.

## Mengambil data POST dengan aman

```python
request.POST.get("password", "")
```

Jika field `password` tidak tersedia, hasilnya string kosong dan tidak menimbulkan `KeyError`.

---

# 9. Mendaftarkan URL

Tambahkan view baru ke import dalam `main/urls.py`:

```python
from main.views import (
    create_achievement,
    delete_achievement,
    show_achievements,
    update_achievement,
)
```

Gabungkan dengan import view lain yang sudah ada.

Tambahkan URL ke `urlpatterns`:

```python
path(
    "achievements/",
    show_achievements,
    name="show_achievements",
),
path(
    "achievements/add/",
    create_achievement,
    name="create_achievement",
),
path(
    "achievements/<int:achievement_id>/update/",
    update_achievement,
    name="update_achievement",
),
path(
    "achievements/<int:achievement_id>/delete/",
    delete_achievement,
    name="delete_achievement",
),
```

## Path parameter

URL berikut:

```python
path(
    "achievements/<int:achievement_id>/update/",
    update_achievement,
)
```

harus cocok dengan parameter fungsi:

```python
def update_achievement(request, achievement_id):
```

Untuk request:

```text
/achievements/3/update/
```

Django memanggil:

```python
update_achievement(request, achievement_id=3)
```

---

# 10. Membuat Template Daftar

Buat `templates/achievements.html`:

```django
{% extends "base.html" %}

{% block meta %}
    <title>Achievements | {{ name }}</title>
{% endblock meta %}

{% block content %}
<main>
    <section class="section">
        <div class="container">
            <h1>Achievements</h1>

            <a
                href="{% url 'main:create_achievement' %}"
                class="button"
            >
                Add achievement
            </a>

            {% if messages %}
                {% for message in messages %}
                    <p class="project-message">
                        {{ message }}
                    </p>
                {% endfor %}
            {% endif %}

            <div>
                {% for achievement in achievement_list %}
                    <article>
                        <h2>{{ achievement.title }}</h2>
                        <p>{{ achievement.issuer }}</p>
                        <p>
                            {{ achievement.achieved_at|date:"d M Y" }}
                        </p>
                        <p>{{ achievement.description }}</p>

                        <a
                            href="{% url 'main:update_achievement' achievement.pk %}"
                            class="button button-secondary"
                        >
                            Edit
                        </a>

                        <form
                            method="post"
                            action="{% url 'main:delete_achievement' achievement.pk %}"
                        >
                            {% csrf_token %}

                            <label>
                                Password
                                <input
                                    type="password"
                                    name="password"
                                    required
                                >
                            </label>

                            <button
                                type="submit"
                                class="button button-danger"
                            >
                                Delete
                            </button>
                        </form>
                    </article>
                {% empty %}
                    <p>No achievements added yet.</p>
                {% endfor %}
            </div>
        </div>
    </section>
</main>
{% endblock content %}
```

## Hubungan context dan template

View mengirim:

```python
{
    "achievement_list": achievements,
}
```

Template membacanya dengan:

```django
{% for achievement in achievement_list %}
```

Nama context harus sama.

## CSRF token

Semua form POST internal Django harus memiliki:

```django
{% csrf_token %}
```

Tanpa token yang valid, Django biasanya mengembalikan HTTP `403 Forbidden`.

---

# 11. Membuat Template Form Reusable

Buat `templates/achievement_form.html`:

```django
{% extends "base.html" %}

{% block meta %}
    <title>{{ page_title }} | {{ name }}</title>
{% endblock meta %}

{% block content %}
<main>
    <section class="section project-form-section">
        <div class="container">
            <h1>{{ page_title }}</h1>

            <form method="post" class="project-form">
                {% csrf_token %}

                {% for field in form %}
                    <div class="form-group">
                        <label for="{{ field.id_for_label }}">
                            {{ field.label }}
                        </label>

                        {{ field }}

                        {% if field.help_text %}
                            <p class="form-help">
                                {{ field.help_text }}
                            </p>
                        {% endif %}

                        {% for error in field.errors %}
                            <p class="form-error">
                                {{ error }}
                            </p>
                        {% endfor %}
                    </div>
                {% endfor %}

                <div class="project-form-actions">
                    <button type="submit" class="button">
                        {{ submit_label }}
                    </button>

                    <a
                        href="{% url 'main:show_achievements' %}"
                        class="button button-secondary"
                    >
                        Cancel
                    </a>
                </div>
            </form>
        </div>
    </section>
</main>
{% endblock content %}
```

Template yang sama digunakan oleh create dan update. Perbedaannya berasal dari context:

| Context | Create | Update |
|---|---|---|
| `page_title` | Add achievement | Update achievement |
| `submit_label` | Save achievement | Update achievement |
| `form` | Form kosong | Form berisi data lama |

---

# 12. Mendaftarkan Model ke Django Admin

Ubah `main/admin.py`:

```python
from django.contrib import admin

from main.models import (
    Achievement,
    DiscographyEntry,
    Experience,
    Project,
)

admin.site.register(Achievement)
```

Setelah didaftarkan, achievement juga dapat dikelola melalui `/admin/`.

---

# 13. Menambahkan Link Navigasi

Tambahkan ke `templates/base.html` jika dibutuhkan:

```django
<a href="{% url 'main:show_achievements' %}">
    Achievements
</a>
```

Link navigasi tidak membuat URL. URL tetap harus didaftarkan di `main/urls.py`.

---

# 14. Membuat Test CRUD

Tambahkan model ke import dalam `main/tests.py`:

```python
from main.models import Achievement, DiscographyEntry, Experience, Project
```

Tambahkan test:

```python
@override_settings(PROJECT_WRITE_SECRET="test-write-secret")
class AchievementCrudTest(TestCase):
    def setUp(self):
        self.achievement = Achievement.objects.create(
            title="Hackathon Winner",
            issuer="Universitas Indonesia",
            achieved_at="2026-09-20",
            description="Won a university hackathon.",
        )

    def test_achievement_list(self):
        response = self.client.get(
            reverse("main:show_achievements")
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "achievements.html",
        )
        self.assertContains(
            response,
            self.achievement.title,
        )

    def test_create_achievement(self):
        response = self.client.post(
            reverse("main:create_achievement"),
            {
                "title": "Competition Finalist",
                "issuer": "Fasilkom UI",
                "achieved_at": "2026-09-22",
                "description": "Reached the final round.",
                "write_secret": "test-write-secret",
            },
        )

        self.assertRedirects(
            response,
            reverse("main:show_achievements"),
        )
        self.assertTrue(
            Achievement.objects.filter(
                title="Competition Finalist"
            ).exists()
        )

    def test_update_achievement(self):
        response = self.client.post(
            reverse(
                "main:update_achievement",
                args=[self.achievement.pk],
            ),
            {
                "title": "Updated Winner",
                "issuer": "Universitas Indonesia",
                "achieved_at": "2026-09-20",
                "description": "Updated description.",
                "write_secret": "test-write-secret",
            },
        )

        self.assertRedirects(
            response,
            reverse("main:show_achievements"),
        )

        self.achievement.refresh_from_db()
        self.assertEqual(
            self.achievement.title,
            "Updated Winner",
        )

    def test_delete_achievement(self):
        response = self.client.post(
            reverse(
                "main:delete_achievement",
                args=[self.achievement.pk],
            ),
            {
                "password": "test-write-secret",
            },
        )

        self.assertRedirects(
            response,
            reverse("main:show_achievements"),
        )
        self.assertFalse(
            Achievement.objects.filter(
                pk=self.achievement.pk
            ).exists()
        )
```

Jalankan test:

```bash
env/bin/python manage.py test
```

---

# Pola CRUD Minimal untuk Kuis

## Model

```python
class Item(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
```

## Form

```python
class ItemForm(ModelForm):
    class Meta:
        model = Item
        fields = ["name"]
```

## Read

```python
def show_items(request):
    items = Item.objects.all()
    return render(
        request,
        "items.html",
        {"items": items},
    )
```

## Create

```python
def create_item(request):
    form = ItemForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("main:show_items")

    return render(
        request,
        "item_form.html",
        {"form": form},
    )
```

## Update

```python
def update_item(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    form = ItemForm(request.POST or None, instance=item)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("main:show_items")

    return render(
        request,
        "item_form.html",
        {"form": form},
    )
```

## Delete

```python
def delete_item(request, item_id):
    item = get_object_or_404(Item, pk=item_id)

    if request.method == "POST":
        item.delete()

    return redirect("main:show_items")
```

## URLs

```python
path("items/", show_items, name="show_items"),
path("items/add/", create_item, name="create_item"),
path(
    "items/<int:item_id>/update/",
    update_item,
    name="update_item",
),
path(
    "items/<int:item_id>/delete/",
    delete_item,
    name="delete_item",
),
```

---

# Create vs Update

## Create

```python
form = AchievementForm(request.POST or None)
```

Tidak memiliki `instance`. Jika disimpan, Django membuat row baru dengan operasi SQL `INSERT`.

## Update

```python
achievement = get_object_or_404(
    Achievement,
    pk=achievement_id,
)
form = AchievementForm(
    request.POST or None,
    instance=achievement,
)
```

Memiliki `instance`. Jika disimpan, Django mengubah row lama dengan operasi SQL `UPDATE`.

> Hafalan: **create tanpa instance, update dengan instance**.

---

# Pola Post/Redirect/Get

Setelah POST berhasil, gunakan redirect:

```python
form.save()
return redirect("main:show_achievements")
```

Alurnya:

```text
POST form
   ↓
Server menyimpan data
   ↓
HTTP 302 Redirect
   ↓
Browser melakukan GET
   ↓
Halaman daftar ditampilkan
```

Manfaatnya adalah refresh halaman tidak mengirim ulang POST dan tidak membuat data duplikat.

---

# Kesalahan yang Sering Terjadi

## 1. Lupa migration

Gejala:

```text
no such table
```

Solusi:

```bash
python manage.py makemigrations
python manage.py migrate
```

## 2. Lupa `instance` saat update

Kode salah:

```python
form = ItemForm(request.POST or None)
```

Akibatnya update justru membuat object baru.

Kode benar:

```python
form = ItemForm(request.POST or None, instance=item)
```

## 3. Nama parameter URL berbeda dengan view

URL:

```python
path("items/<int:item_id>/update/", update_item)
```

View harus menerima `item_id`:

```python
def update_item(request, item_id):
```

## 4. Lupa `{% csrf_token %}`

Semua form POST internal harus memiliki:

```django
{% csrf_token %}
```

## 5. Melakukan delete melalui GET

Delete harus menggunakan form POST agar membuka URL biasa tidak menghapus data.

## 6. Lupa mendaftarkan URL

View yang sudah dibuat belum dapat diakses jika belum ditambahkan ke `urlpatterns`.

## 7. Nama context tidak sama

View:

```python
{"items": items}
```

Template harus menggunakan:

```django
{% for item in items %}
```

## 8. Menggunakan `render()` setelah POST berhasil

Gunakan redirect untuk mengikuti pola Post/Redirect/Get:

```python
return redirect("main:show_items")
```

---

# Checklist Sebelum Selesai

- [ ] Model sudah dibuat.
- [ ] `makemigrations` sudah dijalankan.
- [ ] `migrate` sudah dijalankan.
- [ ] ModelForm sudah dibuat.
- [ ] Read view sudah mengambil queryset.
- [ ] Create view menggunakan form tanpa `instance`.
- [ ] Update view menggunakan `get_object_or_404` dan `instance`.
- [ ] Delete hanya berjalan ketika method adalah POST.
- [ ] URL untuk seluruh CRUD sudah didaftarkan.
- [ ] Template list dan form sudah dibuat.
- [ ] Semua form POST memiliki `{% csrf_token %}`.
- [ ] Setelah POST berhasil, view melakukan redirect.
- [ ] Test sudah dibuat dan dijalankan.

---

# Jawaban Lisan untuk Dosen

> Untuk membuat fitur CRUD baru, saya mulai dengan mendefinisikan model dan menjalankan `makemigrations` serta `migrate`. Setelah itu saya membuat `ModelForm` untuk validasi dan konversi data. Saya membuat read view menggunakan queryset, create view menggunakan form tanpa instance, update view menggunakan `get_object_or_404` dan instance, serta delete view yang hanya menghapus ketika request method adalah POST. Setiap view didaftarkan di `urls.py`, dihubungkan dengan template, lalu diuji menggunakan Django `TestCase`.

## Hafalan Super Singkat

> **Create tanpa instance, update dengan instance, delete hanya POST, read menggunakan queryset, dan setelah POST berhasil lakukan redirect.**
