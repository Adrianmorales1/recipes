from flask_app import app
from flask_app.models import user
from flask import flash
from flask_app.config.mysqlconnection import connectToMySQL

class Recipe:
    db = "recipes_db"

    def __init__(self,data):
        self.id = data['id']
        self.name = data['name']
        self.instruction = data['instruction']
        self.description = data['description']
        self.date_made = data['date_made']
        self.under_time = data['under_time']
        self.creator = None

        self.user_ids_who_favorited = []
        self.users_who_favorited = []

    @classmethod
    def get_recipe_by_id(cls, data):
        query = "SELECT * FROM recipes JOIN users ON recipes.user_id = users.id WHERE recipes.id = %(id)s"
        results = connectToMySQL(cls.db).query_db(query, data)

        if len(results) < 1:
            return False
        row = results[0]
        recipe = cls(row)
        
        one_recipe_user_info = {
                "id" : row['users.id'],
                "first_name" : row['first_name'],
                "last_name" : row['last_name'],
                "email" : row['email'],
                "password" : row['password'],
                "created_at" : row['users.created_at'],
                "updated_at" : row['users.updated_at']
            }

        user_data = user.User(one_recipe_user_info)

        recipe.creator = user_data

        return recipe

    @classmethod
    def save_recipe(cls,data):
        query = "INSERT INTO recipes (user_id, name, instruction, description, date_made, under_time ) VALUES (%(user_id)s, %(name)s, %(instruction)s, %(description)s, %(date_made)s, %(under_time)s)"
        result = connectToMySQL(cls.db).query_db(query,data)
        return result

    @classmethod
    def update_recipe(cls,data):
        query = "UPDATE recipes SET name = %(name)s, description = %(description)s, instruction = %(instruction)s, date_made = %(date_made)s, under_time = %(under_time)s WHERE id = %(id)s"
        result = connectToMySQL(cls.db).query_db(query,data)
    
    @classmethod
    def delete_recipe(cls, data):
        query = 'DELETE FROM recipes WHERE id = %(id)s'
        user_id = connectToMySQL(cls.db).query_db(query,data)
    
    @classmethod
    def favorite(cls, data):
        query = "INSERT INTO favorited_recipes (user_id, recipe_id) VALUES (%(user_id)s, %(recipe_id)s)"
        result = connectToMySQL(cls.db).query_db(query, data)
        return result
    
    @classmethod
    def unfavorite(cls, data):
        query = "DELETE FROM favorited_recipes WHERE user_id = %(user_id)s AND recipe_id = %(recipe_id)s"
        result = connectToMySQL(cls.db).query_db(query, data)


    @classmethod
    def get_all_recipes_with_user(cls):
        query = """SELECT * FROM recipes JOIN users AS creators on recipes.user_id = creators.id
                    LEFT JOIN favorited_recipes ON recipes.id = favorited_recipes.recipe_id
                    LEFT JOIN users AS users_who_favorited ON favorited_recipes.user_id = users_who_favorited.id;
                """
        results = connectToMySQL(cls.db).query_db(query)

        all_recipes = []

        for row in results:
            new_recipe = True
            user_who_favorited_data = {
                "id" : row['users_who_favorited.id'],
                "first_name" : row['users_who_favorited.first_name'],
                "last_name" : row['users_who_favorited.last_name'],
                "email" : row['users_who_favorited.email'],
                "password" : row['users_who_favorited.password'],
                "created_at" : row['users_who_favorited.created_at'],
                "updated_at" : row['users_who_favorited.updated_at']
            }

            number_of_recipes = len(all_recipes)
            if number_of_recipes > 0:
                last_review = all_recipes[number_of_recipes - 1]
                if last_review.id == row['id']:
                    last_review.user_ids_who_favorited.append(row['users_who_favorited.id'])
                    last_review.users_who_favorited.append(user.User(user_who_favorited_data))
                    new_recipe = False
            
            if new_recipe:
                one_recipe = cls(row)

                one_recipe_user_info = {
                    "id" : row['creators.id'],
                    "first_name" : row['first_name'],
                    "last_name" : row['last_name'],
                    "email" : row['email'],
                    "password" : row['password'],
                    "created_at" : row['creators.created_at'],
                    "updated_at" : row['creators.updated_at']
                }

                user_data = user.User(one_recipe_user_info)

                one_recipe.creator = user_data

                if row['users_who_favorited.id']:
                    one_recipe.user_ids_who_favorited.append(row['users_who_favorited.id'])
                    one_recipe.users_who_favorited.append(user.User(user_who_favorited_data))

                all_recipes.append(one_recipe)
        return all_recipes

    @staticmethod
    def validate_recipe(data):
        is_valid = True
        if len(data['name']) < 3:
            flash('Name of Recipe must be at least 3 characters', 'recipe')
            is_valid = False
        if len(data['description']) < 3:
            flash('Description of Recipe must be at least 3 characters', 'recipe')
            is_valid = False
        if len(data['instruction']) < 3:
            flash('Instruction of Recipe must be at least 3 characters', 'recipe')
            is_valid = False
        if not data['date_made']:
            flash('Date Cooked/Made must be filled', 'recipe')
            is_valid = False
        if not 'under_time' in data:
            flash('Please select if it was Under 30 minutes', 'recipe')
            is_valid = False
        return is_valid

    @staticmethod
    def validate_edit_delete(user, other_user):
        is_valid = True
        if user['id'] != other_user['id']:
            flash('Returned to Login form', 'session')
            is_valid = False
        return is_valid
