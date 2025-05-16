from flask import Flask, render_template, request, redirect, url_for, flash
from data_manager import CsvDataSource, CsvCarRepository, SQLiteCarRepository, CarRepository # Assurez-vous que CarRepository est importé si utilisé comme type hint
import pandas as pd # Ajouté pour la manipulation potentielle de DataFrame dans les routes

app = Flask(__name__)
app.secret_key = "votre_cle_secrete_ici" # Important pour les messages flash

# Variables globales pour le data_manager et le type de source
data_manager = None
source_type_label = "index" # Par défaut à index pour CSV
# Champs requis pour la création d'une voiture, utile pour la validation de formulaire
REQUIRED_FIELDS = ['name', 'year', 'selling_price', 'km_driven', 'fuel', 'seller_type', 'transmission', 'owner']

# Les fonctions CLI comme print_menu et get_car_details_from_user ne sont plus utilisées directement par Flask.
# La logique de get_car_details_from_user sera adaptée dans les routes POST.

@app.route('/')
def index():
    global data_manager, source_type_label
    if not data_manager:
        flash("La source de données n'est pas initialisée. Veuillez redémarrer l'application.", "error")
        return redirect(url_for('configure_source')) # Rediriger vers une page de configuration si nécessaire

    cars_df = data_manager.get_all_cars()
    
    # Préparer les données pour l'affichage
    # Assurer que 'id' est bien l'identifiant à utiliser pour les liens, que ce soit l'index (CSV) ou l'ID (SQLite)
    if not cars_df.empty:
        if source_type_label == "index": # CSV
            # Pour CSV, l'index du DataFrame est l'ID que nous utilisons.
            # Ajoutons-le comme une colonne pour un accès facile dans le template.
            cars_df_processed = cars_df.reset_index().rename(columns={'index': 'display_id'})
        else: # SQLite
            # Pour SQLite, la colonne 'id' est l'ID.
            cars_df_processed = cars_df.rename(columns={'id': 'display_id'})
        cars_list = cars_df_processed.to_dict(orient='records')
    else:
        cars_list = []
        
    return render_template('index.html', cars=cars_list, source_type_label=source_type_label, all_columns=REQUIRED_FIELDS + (['display_id'] if source_type_label == 'ID' else []))

@app.route('/car/<car_id_str>')
def car_detail(car_id_str):
    global data_manager
    try:
        car_id = int(car_id_str)
        car = data_manager.get_car_by_id(car_id)
        if car:
            # Si c'est CSV, l'ID passé est l'index, qui n'est pas une colonne dans le dict 'car'
            # Si c'est SQLite, 'id' est une clé dans le dict 'car'
            display_id_in_car = car.get('id') if source_type_label == "ID" else car_id
            return render_template('car_detail.html', car=car, car_id=display_id_in_car, source_type_label=source_type_label)
        else:
            flash(f"Voiture avec l'{source_type_label} {car_id} non trouvée.", "warning")
            return redirect(url_for('index'))
    except ValueError:
        flash(f"'{source_type_label}' invalide.", "error")
        return redirect(url_for('index'))

@app.route('/add', methods=['GET', 'POST'])
def add_car():
    global data_manager
    if request.method == 'POST':
        new_car_data = {field: request.form.get(field) for field in REQUIRED_FIELDS}
        
        # Validation simple (vérifier si tous les champs requis sont remplis)
        # Une validation plus robuste serait nécessaire pour une application en production
        missing_fields = [field for field, value in new_car_data.items() if not value]
        if missing_fields:
            flash(f"Les champs suivants sont requis : {', '.join(missing_fields)}", "error")
            return render_template('car_form.html', car=new_car_data, action="add", source_type_label=source_type_label, required_fields=REQUIRED_FIELDS)

        # Conversion des types pour les champs numériques
        try:
            new_car_data['year'] = int(new_car_data['year'])
            new_car_data['selling_price'] = int(new_car_data['selling_price'])
            new_car_data['km_driven'] = int(new_car_data['km_driven'])
        except ValueError:
            flash("Année, Prix de vente et Kilomètres parcourus doivent être des nombres.", "error")
            return render_template('car_form.html', car=new_car_data, action="add", source_type_label=source_type_label, required_fields=REQUIRED_FIELDS)

        created_car = data_manager.create_car(new_car_data)
        if created_car:
            flash("Voiture ajoutée avec succès!", "success")
        else:
            flash("Erreur lors de l'ajout de la voiture.", "error")
        return redirect(url_for('index'))
    
    # Pour GET request
    return render_template('car_form.html', car={}, action="add", source_type_label=source_type_label, required_fields=REQUIRED_FIELDS)

@app.route('/update/<car_id_str>', methods=['GET', 'POST'])
def update_car(car_id_str):
    global data_manager, source_type_label
    try:
        car_id = int(car_id_str)
    except ValueError:
        flash(f"'{source_type_label}' invalide.", "error")
        return redirect(url_for('index'))

    car_to_update = data_manager.get_car_by_id(car_id)
    if not car_to_update:
        flash(f"Voiture avec l'{source_type_label} {car_id} non trouvée.", "warning")
        return redirect(url_for('index'))

    if request.method == 'POST':
        updated_car_data = {}
        for field in REQUIRED_FIELDS:
            value = request.form.get(field)
            if value: # Seulement inclure les champs qui ont une valeur
                updated_car_data[field] = value
        
        # Conversion des types pour les champs numériques si présents
        try:
            if 'year' in updated_car_data:
                updated_car_data['year'] = int(updated_car_data['year'])
            if 'selling_price' in updated_car_data:
                updated_car_data['selling_price'] = int(updated_car_data['selling_price'])
            if 'km_driven' in updated_car_data:
                updated_car_data['km_driven'] = int(updated_car_data['km_driven'])
        except ValueError:
            flash("Année, Prix de vente et Kilomètres parcourus doivent être des nombres valides.", "error")
            # Re-passer les données originales et les données soumises pour correction
            form_data = car_to_update.copy()
            form_data.update(request.form.to_dict()) # Surcharger avec les valeurs du formulaire
            return render_template('car_form.html', car=form_data, car_id=car_id, action="update", source_type_label=source_type_label, required_fields=REQUIRED_FIELDS)

        if not updated_car_data:
            flash("Aucune donnée fournie pour la mise à jour.", "info")
            return redirect(url_for('update_car', car_id_str=car_id_str))

        result = data_manager.update_car(car_id, updated_car_data)
        if result:
            flash("Voiture mise à jour avec succès!", "success")
        else:
            flash("Erreur lors de la mise à jour de la voiture.", "error")
        return redirect(url_for('index'))

    # Pour GET request
    return render_template('car_form.html', car=car_to_update, car_id=car_id, action="update", source_type_label=source_type_label, required_fields=REQUIRED_FIELDS)

@app.route('/delete/<car_id_str>', methods=['POST']) # Changé en POST pour la sécurité
def delete_car(car_id_str):
    global data_manager, source_type_label
    try:
        car_id = int(car_id_str)
        deleted_car = data_manager.delete_car(car_id)
        if deleted_car:
            flash(f"Voiture {source_type_label} {car_id} supprimée avec succès.", "success")
        else:
            flash(f"Erreur lors de la suppression de la voiture {source_type_label} {car_id} ou voiture non trouvée.", "error")
    except ValueError:
        flash(f"'{source_type_label}' invalide.", "error")
    return redirect(url_for('index'))

@app.route('/search', methods=['GET', 'POST'])
def search_cars_route():
    global data_manager
    if request.method == 'POST':
        search_attribute = request.form.get('attribute')
        search_value = request.form.get('value')

        if not search_attribute or not search_value:
            flash("Veuillez spécifier un attribut et une valeur pour la recherche.", "warning")
            return redirect(url_for('search_cars_route'))

        results_df = data_manager.search_cars(search_attribute, search_value)
        
        if not results_df.empty:
            if source_type_label == "index": # CSV
                results_df_processed = results_df.reset_index().rename(columns={'index': 'display_id'})
            else: # SQLite
                results_df_processed = results_df.rename(columns={'id': 'display_id'})
            search_results = results_df_processed.to_dict(orient='records')
            flash(f"{len(search_results)} voiture(s) trouvée(s).", "info")
        else:
            search_results = []
            flash("Aucune voiture ne correspond à vos critères de recherche.", "info")
        
        # Réutiliser index.html pour afficher les résultats ou créer un search_results.html dédié
        return render_template('index.html', cars=search_results, source_type_label=source_type_label, is_search_results=True, all_columns=REQUIRED_FIELDS + (['display_id'] if source_type_label == 'ID' else []))

    # Pour GET request, afficher le formulaire de recherche
    # Obtenir les colonnes possibles pour la recherche
    sample_cars_df = data_manager.get_all_cars()
    if not sample_cars_df.empty:
        possible_attributes = [col for col in sample_cars_df.columns if col != 'id' or source_type_label == "ID"]
    else:
        possible_attributes = REQUIRED_FIELDS # Fallback si la DB est vide
        
    return render_template('search_form.html', possible_attributes=possible_attributes)


# Configuration initiale de la source de données (appelée avant de démarrer l'app)
# Supprimer la fonction configure_data_source existante et remplacer par :
@app.before_request
def check_data_source():
    global data_manager
    if not data_manager and request.endpoint != 'configure_source':
        return redirect(url_for('configure_source'))

@app.route('/configure-source', methods=['GET', 'POST'])
def configure_source():
    global data_manager, source_type_label
    
    if request.method == 'POST':
        source_choice = request.form.get('source_choice')
        if source_choice == '1':
            csv_data_source = CsvDataSource()
            data_manager = CsvCarRepository(csv_data_source)
            source_type_label = "index"
            flash("Source de données configurée : CSV", "success")
        elif source_choice == '2':
            data_manager = SQLiteCarRepository()
            source_type_label = "ID"
            flash("Source de données configurée : SQLite", "success")
        else:
            flash("Sélection invalide", "error")
            return redirect(url_for('configure_source'))
        
        return redirect(url_for('index'))
    
    return render_template('config_modal.html')

if __name__ == '__main__':
    app.run(debug=True)  # Supprimer l'appel à configure_data_source()