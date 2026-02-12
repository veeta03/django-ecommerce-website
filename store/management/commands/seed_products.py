from django.core.management.base import BaseCommand
from store.models import Product, Category

class Command(BaseCommand):
    help = "Seed sample products"

    def handle(self, *args, **kwargs):

        electronics, _ = Category.objects.get_or_create(name="Electronics", slug="electronics")
        fashion, _ = Category.objects.get_or_create(name="Fashion", slug="fashion")
        books, _ = Category.objects.get_or_create(name="Books", slug="books")

        Product.objects.create(
            name="iPhone 14 Pro",
            price=79000,
            description="Apple iPhone 14 Pro with A16 chip and 48MP camera.",
            stock=10,
            category=electronics
        )

        Product.objects.create(
            name="Dell Inspiron 15",
            price=65000,
            description="Dell laptop with 8GB RAM and 512GB SSD.",
            stock=5,
            category=electronics
        )

        Product.objects.create(
            name="Men's Casual Shirt",
            price=1299,
            description="Slim fit cotton shirt.",
            stock=25,
            category=fashion
        )

        Product.objects.create(
            name="Python Programming Book",
            price=499,
            description="Complete guide to Python programming.",
            stock=50,
            category=books
        )

        self.stdout.write(self.style.SUCCESS("Sample products added successfully!"))
