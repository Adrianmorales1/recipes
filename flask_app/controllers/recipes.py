from flask_app import app
from flask_app.models.user import User
from flask_app.models.recipe import Recipe
from flask import Flask, request, redirect, session, render_template, flash

@app.route('/create')
def create_recipe():
    return render_template('add_new.html')

@app.route('/add/recipe', methods = ['POST'])
def add_recipe():
    if not Recipe.validate_recipe(request.form):
        return redirect('/create')
    
    recipe_data = {
        'user_id' : session['user_id'],
        'name' : request.form['name'],
        'description' : request.form['description'],
        'instruction' : request.form['instruction'],
        'date_made' : request.form['date_made'],
        'under_time' : request.form['under_time']
    }

    Recipe.save_recipe(recipe_data)
    return redirect('/dashboard')

@app.route('/edit/<int:id>')
def edit(id):
    if not User.validate_session(session):
        return redirect('/')
    data = {
        'id' : id
    }

    return render_template('edit_recipe.html', recipe = Recipe.get_recipe_by_id(data))

@app.route('/delete/<int:id>')
def delete(id):
    if not User.validate_session(session):
        return redirect('/')
    data = {
        'id' : id
    }
    Recipe.delete_recipe(data)
    return redirect('/dashboard')


@app.route('/update/<int:id>', methods = ['POST'])
def update(id):
    id = request.form['id']
    if not Recipe.validate_recipe(request.form):
        return redirect('/edit/'+id)
    Recipe.update_recipe(request.form)

    return redirect('/dashboard')

@app.route('/show/<int:id>')
def show(id):
    data = {
        'id' : id
    }
    data2 = {
        'id' : session['user_id']
    }
    user_d = User.get_user_by_id(data2)
    recipe_data = Recipe.get_recipe_by_id(data)
    return render_template('view_recipe.html', recipe = recipe_data, user = user_d)

@app.route('/recipes/<int:id>/favorite', methods = ['POST'])
def favorite(id):
    Recipe.favorite(request.form)
    return redirect('/dashboard')

@app.route('/recipes/<int:id>/unfavorite', methods = ['POST'])
def unfavorite(id):
    Recipe.unfavorite(request.form)
    return redirect('/dashboard')
