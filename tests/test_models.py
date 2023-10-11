# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db, DataValidationError
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    #
    # ADD YOUR TEST CASES HERE
    #
    def test_read_a_product(self):
        """It should read a product from the database"""
        product = ProductFactory()

        # Add a log message for debugging errors
        logging.info(f"Created product: {product}")

        # Set the ID of the product object to None and create it
        product.id = None
        product.create()

        # Assert that the product ID is not None
        self.assertIsNotNone(product.id)

        # Fetch the product back from the database
        fetched_product = Product.find(product.id)

        # Assert the properties of the found product are correct
        self.assertEqual(fetched_product.id, product.id)
        self.assertEqual(fetched_product.name, product.name)
        self.assertEqual(fetched_product.description, product.description)
        self.assertEqual(fetched_product.price, product.price)

    def test_update_a_product(self):
        """ It should update a product in the database """
        # Create a Product object using the ProductFactory
        product = ProductFactory()

        # Add a log message for debugging errors
        logging.info(f"Created product: {product}")

        # Set the ID of the product object to None and create it
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)

        # Log the product object after it has been created
        logging.info(f"Created product with ID: {product.id}, Description: {product.description}")
        original_id = product.id

        # Attempt to update the product object with an empty ID
        with self.assertRaises(DataValidationError):
            product.id = None
            product.update()

        # Update the description property of the product object
        updated_description = "Updated Description"
        product.description = updated_description
        product.id = original_id
        product.update()

        # Assert that the id and description properties have been updated correctly
        self.assertEqual(product.id, original_id)
        self.assertEqual(product.description, updated_description)

        # Fetch all products from the database
        all_products = Product.all()

        # Assert that there is only one product in the system
        self.assertEqual(len(all_products), 1)

        # Assert that the fetched product has the original id but updated description
        fetched_product = all_products[0]
        self.assertEqual(fetched_product.id, product.id)
        self.assertEqual(fetched_product.description, updated_description)

    def test_delete_a_product(self):
        """ It should delete a particular product from the database """
        # Create a Product
        product = ProductFactory()
        product.create()

        # Assert that there is only one product
        all_products = Product.all()
        self.assertEqual(len(all_products), 1)

        # Remove the product
        Product.delete(product)

        # Assert that the product has been removed
        all_products = Product.all()
        self.assertEqual(len(all_products), 0)

    def test_list_all_products(self):
        """ It should return all products in the database """
        # Retrieve all products from the database and assign them to the products variable
        products = Product.all()

        # Assert there are no products in the database at the beginning of the test case
        self.assertEqual(len(products), 0)

        # Create five products and save them to the database
        for _ in range(5):
            product = ProductFactory()
            product.create()

        # Fetching all products from the database again and assert the count is 5
        products = Product.all()
        self.assertEqual(len(products), 5)

    def test_find_product_by_name(self):
        """ It should return a product when searched for by name """
        # Create a batch of 5 Product objects using the ProductFactory and save them to the database.
        for _ in range(5):
            product = ProductFactory()
            product.create()

        # Retrieve the name of the first product in the products list
        all_products = Product.all()
        first_product_name = all_products[0].name

        # Count the number of occurrences of the product name in the list
        count = len([product for product in all_products if product.name == first_product_name])

        # Retrieve products from the database that have the specified name.
        found_products = Product.find_by_name(first_product_name)

        # Assert if the count of the found products matches the expected count.
        self.assertEqual(found_products.count(), count)

        # Assert that each product’s name matches the expected name.
        for product in found_products:
            self.assertEqual(product.name, first_product_name)

    def test_find_product_by_availability(self):
        """ It should find Products by availability """
        # Create a batch of 10 Product objects using the ProductFactory and save them to the database.
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()

        # Retrieve the availability of the first product in the products list
        first_product_available = products[0].available

        # Count the number of occurrences of the product availability in the list
        count = len([product for product in products if product.available == first_product_available])

        # Retrieve products from the database that have the specified availability.
        found_products = Product.find_by_availability(first_product_available)

        # Assert if the count of the found products matches the expected count.
        self.assertEqual(found_products.count(), count)

        # Assert that each product's availability matches the expected availability.
        for product in found_products:
            self.assertEqual(product.available, first_product_available)

    def test_find_product_by_category(self):
        """ It should find a product by category """
        # Create a batch of 10 Product objects using the ProductFactory and save them to the database.
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()

        # Retrieve the category of the first product in the products list
        category = products[0].category

        # Count the number of occurrences of the product that have the same category in the list.
        count = len([product for product in products if product.category == category])

        # Retrieve products from the database that have the specified category.
        found = Product.find_by_category(category)

        # Assert if the count of the found products matches the expected count.
        self.assertEqual(found.count(), count)

        # Assert that each product's category matches the expected category.
        for product in found:
            self.assertEqual(product.category, category)

    def test_serialize(self):
        """It should serialize a Product into a dictionary"""
        # Create a Product object using the ProductFactory
        product = ProductFactory()

        # Serialize the product object into a dictionary
        product_dict = product.serialize()

        # Check that the dictionary contains the expected keys and values
        self.assertIsInstance(product_dict, dict)
        self.assertEqual(product_dict["id"], product.id)
        self.assertEqual(product_dict["name"], product.name)
        self.assertEqual(product_dict["description"], product.description)
        self.assertEqual(product_dict["price"], str(product.price))
        self.assertEqual(product_dict["available"], product.available)
        self.assertEqual(product_dict["category"], product.category.name)

    def test_deserialize(self):
        """It should deserialize a dictionary into a Product object"""
        # Create a dictionary containing Product data
        product_data = {
            "name": "Test",
            "description": "This is a test",
            "price": 12.99,
            "available": True,
            "category": "TOOLS",
        }

        # Create a new Product object and deserialize the dictionary into it
        product = Product()

        # Test for invalid available data
        product_data["available"] = 10
        with self.assertRaises(DataValidationError):
            product.deserialize(product_data)
        product_data["available"] = True

        # Test for invalid category data
        product_data["category"] = "ELECTRONICS"
        with self.assertRaises(DataValidationError):
            product.deserialize(product_data)
        product_data["category"] = "TOOLS"

        # Test for invalid available data
        product.deserialize(product_data)

        # Check that the Product object has been deserialized correctly
        self.assertEqual(product.name, product_data["name"])
        self.assertEqual(product.description, product_data["description"])
        self.assertEqual(product.price, product_data["price"])
        self.assertEqual(product.available, product_data["available"])
        self.assertEqual(product.category, Category.TOOLS)

    def test_find_by_price(self):
        """It should return all Products with the given price"""
        # Create a batch of 10 Product objects using the ProductFactory and save them to the database.
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()

        # Retrieve the price of the first product in the products list
        first_product_price = products[0].price

        # Count the number of occurrences of the product price in the list
        count = len([product for product in products if product.price == first_product_price])

        # Retrieve products from the database that have the specified price.
        found_products = Product.find_by_price(first_product_price)

        # Assert if the count of the found products matches the expected count.
        self.assertEqual(found_products.count(), count)
