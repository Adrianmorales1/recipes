from os import stat
from flask_app import app
from flask_app.models.recipe import Recipe
from flask_app.config.mysqlconnection import connectToMySQL
from flask import Flask, flash, session
import re

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
class User:
    db = "recipes_db"

    def __init__(self, data):
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.password = data['password']

        self.recipes = []

    @classmethod
    def get_user_by_id(cls, data):
        query = "SELECT * FROM users WHERE id = %(id)s"
        results = connectToMySQL(cls.db).query_db(query, data)

        if len(results) < 1:
            return False
        row = results[0]
        user = cls(row)
        return user
    
    @classmethod
    def get_user_by_email(cls,data):
        query = "SELECT * FROM users WHERE email = %(email)s"
        results = connectToMySQL(cls.db).query_db(query, data)

        if len(results) < 1:
            return False
        row = results[0]
        user = cls(row)
        return user

    @classmethod
    def save_user(cls,data):
        query = "INSERT INTO users (first_name, last_name, email, password) VALUES (%(first_name)s, %(last_name)s, %(email)s, %(password)s)"
        result = connectToMySQL(cls.db).query_db(query,data)
        return result

    @staticmethod
    def validate_reg(data):
        is_valid = True
        user_id = User.get_user_by_email(data)
        if user_id:
            flash('Email is already in db!', 'register')
            is_valid = False
        if len(data['first_name']) < 3:
            flash('First name must be at least 3 characters', 'register')
            is_valid = False
        if len(data['last_name']) < 3:
            flash('Last name must be at least 3 characters', 'register')
            is_valid = False
        if not EMAIL_REGEX.match(data['email']):
            flash("Invalid email address!", 'register')
            is_valid = False
        if len(data['password']) < 8:
            flash('Password must be at least 8 characters', 'register')
        if data['password'] != data['confirm_password']:
            flash('Passwords do not match!', 'register')
            is_valid = False
        
        return is_valid

    @staticmethod
    def validate_login(data):
        is_valid = True
        user_in_db = User.get_user_by_email(data)
        if not user_in_db:
            flash('Email is not associated with an account!','login')
            is_valid = False
            return is_valid
        if not User.get_user_by_email(data):
            flash('Invalid Email address','login')
            is_valid = False
            return is_valid
        if len(data['password']) < 8:
            flash('password must be at least 8 characters long','login')
            is_valid = False
        
        return is_valid

    def validate_session(data):
        is_valid = True
        if "user_id" not in data:
            flash('must be logged in to go through other files', 'session')
            is_valid = False
        return is_valid