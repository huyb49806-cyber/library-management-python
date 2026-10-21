import random
from django.core.management.base import BaseCommand
from faker import Faker
from catalog.models import Author, Language, Genre, Book, BookInstance

class Command(BaseCommand):
    help = 'Tạo dữ liệu mẫu tự động cho hệ thống thư viện'

    def handle(self, *args, **kwargs):
        fake = Faker()
        
        languages = ['Tiếng Việt', 'Tiếng Anh', 'Tiếng Pháp', 'Tiếng Nhật']
        lang_objs = []
        for lang in languages:
            obj, _ = Language.objects.get_or_create(name=lang)
            lang_objs.append(obj)
        self.stdout.write(self.style.SUCCESS(f'Đã tạo {len(lang_objs)} ngôn ngữ.'))

        genres = ['Công nghệ thông tin', 'Tiểu thuyết', 'Khoa học', 'Lịch sử', 'Kinh tế']
        genre_objs = []
        for g in genres:
            obj, _ = Genre.objects.get_or_create(name=g)
            genre_objs.append(obj)
        self.stdout.write(self.style.SUCCESS(f'Đã tạo {len(genre_objs)} thể loại.'))

        author_objs = []
        for _ in range(50):
            author = Author.objects.create(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                date_of_birth=fake.date_of_birth(minimum_age=25, maximum_age=80)
            )
            author_objs.append(author)
        self.stdout.write(self.style.SUCCESS('Đã tạo 50 tác giả.'))

        book_objs = []
        for _ in range(100):
            book = Book.objects.create(
                title=fake.catch_phrase(),
                summary=fake.text(max_nb_chars=200),
                isbn=fake.isbn13().replace("-", ""), 
                author=random.choice(author_objs),
                language=random.choice(lang_objs)
            )
            book.genre.set(random.sample(genre_objs, random.randint(1, 3)))
            book_objs.append(book)
        self.stdout.write(self.style.SUCCESS('Đã tạo 100 đầu sách.'))

        instance_count = 0
        statuses = ['a', 'o', 'd', 'r'] 
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        sample_users = list(User.objects.all()[:10]) 

        for book in book_objs:
            for _ in range(random.randint(2, 5)):
                status_choice = random.choice(statuses)
                
                instance_data = {
                    'book': book,
                    'imprint': fake.company(),
                    'status': status_choice,
                }

                if status_choice == 'o' and sample_users:
                    instance_data['borrower'] = random.choice(sample_users)
                    instance_data['due_back'] = fake.date_between(start_date='-10d', end_date='+20d')

                BookInstance.objects.create(**instance_data)
                instance_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Đã tạo {instance_count} bản sao sách.'))