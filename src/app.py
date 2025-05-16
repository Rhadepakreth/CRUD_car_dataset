from data_manager import DataManager, SQLiteDataManager

# Initialiser le gestionnaire de données - Sera fait dans main()
# data_manager = DataManager()
global data_manager # Déclarer data_manager comme global pour y accéder dans les fonctions si nécessaire
data_manager = None
global source_type_label
source_type_label = "index" # Par défaut à index pour CSV

def print_menu():
    """Affiche le menu des options CRUD."""
    global source_type_label
    print("\n--- Menu CRUD Voitures ---")
    print("1. Lister toutes les voitures")
    print(f"2. Afficher une voiture (par {source_type_label})")
    print("3. Ajouter une nouvelle voiture")
    print(f"4. Mettre à jour une voiture (par {source_type_label})")
    print(f"5. Supprimer une voiture (par {source_type_label})")
    print("6. Rechercher un véhicule")
    print("0. Quitter")

def get_car_details_from_user(is_update=False):
    """Demande à l'utilisateur les détails d'une voiture."""
    details = {}
    print("\nVeuillez entrer les détails de la voiture:")
    # Pour la mise à jour, certains champs peuvent être optionnels
    # Pour la création, tous les champs sont requis (ou gérés avec des valeurs par défaut si nécessaire)

    name = input("Nom (ex: Maruti Swift Dzire VDI): ")
    if name or not is_update: details['name'] = name

    while True:
        year_str = input("Année (ex: 2017): ")
        if not year_str and is_update: break
        try:
            details['year'] = int(year_str)
            break
        except ValueError:
            print("Année invalide. Veuillez entrer un nombre.")

    while True:
        price_str = input("Prix de vente (ex: 600000): ")
        if not price_str and is_update: break
        try:
            details['selling_price'] = int(price_str)
            break
        except ValueError:
            print("Prix invalide. Veuillez entrer un nombre.")

    while True:
        km_str = input("Kilomètres parcourus (ex: 46507): ")
        if not km_str and is_update: break
        try:
            details['km_driven'] = int(km_str)
            break
        except ValueError:
            print("Kilométrage invalide. Veuillez entrer un nombre.")

    fuel = input("Carburant (Petrol, Diesel, CNG, LPG, Electric): ")
    if fuel or not is_update: details['fuel'] = fuel

    seller_type = input("Type de vendeur (Individual, Dealer, Trustmark Dealer): ")
    if seller_type or not is_update: details['seller_type'] = seller_type

    transmission = input("Transmission (Manual, Automatic): ")
    if transmission or not is_update: details['transmission'] = transmission

    owner = input("Propriétaire (First Owner, Second Owner, Third Owner, Fourth & Above Owner, Test Drive Car): ")
    if owner or not is_update: details['owner'] = owner

    return {k: v for k, v in details.items() if v} # Ne retourne que les champs remplis pour la MAJ

def main():
    """Fonction principale de l'application CLI."""
    global data_manager
    global source_type_label

    while True:
        source_choice = input("Choisir la source de données (1: CSV, 2: SQLite, 0: Quitter): ").strip()
        if source_choice == '1':
            data_manager = DataManager()
            source_type_label = "index"
            print("Source de données sélectionnée: CSV")
            break
        elif source_choice == '2':
            data_manager = SQLiteDataManager()
            source_type_label = "ID"
            print("Source de données sélectionnée: SQLite")
            # S'assurer que la table est créée si elle n'existe pas (déjà géré dans __init__ de SQLiteDataManager)
            # data_manager._create_table_if_not_exists() # Appel explicite si nécessaire
            break
        elif source_choice == '0':
            print("Au revoir !")
            return
        else:
            print("Choix de source invalide. Veuillez réessayer.")

    while True:
        print_menu()
        # Afficher le nombre actuel de voitures pour aider l'utilisateur
        all_cars_df = data_manager.get_all_cars()
        if not all_cars_df.empty:
            print(f"(Nombre actuel de voitures: {len(all_cars_df)})")
        else:
            print("(Aucune voiture dans la base de données pour le moment)")
        choice = input("Entrez votre choix: ")

        if choice == '1': # Lister toutes les voitures
            print("\n--- Liste de toutes les voitures ---")
            cars = data_manager.get_all_cars()
            if not cars.empty:
                print(cars.to_string())
            else:
                print("Aucune voiture dans la base de données.")

        elif choice == '2': # Afficher une voiture par index
            cars_df = data_manager.get_all_cars()
            if cars_df.empty:
                print("Aucune voiture à afficher.")
            else:
                try:
                    if source_type_label == "ID":
                        entity_id = int(input(f"Entrez l'{source_type_label} de la voiture à afficher: "))
                        car = data_manager.get_car_by_id(entity_id)
                    else: # CSV utilise l'index
                        index_max = len(cars_df) - 1
                        entity_id = int(input(f"Entrez l'{source_type_label} de la voiture à afficher (0-{index_max}): "))
                        car = data_manager.get_car_by_index(entity_id)
                    
                    if car:
                        print("\n--- Détails de la voiture ---")
                        # Pour SQLite, l'ID est une colonne, pour CSV, c'est l'index du DataFrame
                        if source_type_label == "ID" and 'id' in car:
                            print(f"ID: {car['id']}")
                        elif source_type_label == "index":
                             print(f"Index: {entity_id}") # Afficher l'index utilisé pour la recherche CSV

                        for key, value in car.items():
                            if key == 'id' and source_type_label == "ID": continue # Déjà affiché
                            print(f"{key.replace('_', ' ').capitalize()}: {value}")
                    else:
                        print(f"Aucune voiture trouvée à l'{source_type_label} {entity_id}.")
                except ValueError:
                    print(f"{source_type_label} invalide. Veuillez entrer un nombre.")

        elif choice == '3': # Ajouter une nouvelle voiture
            new_car_data = get_car_details_from_user()
            # Vérifier si tous les champs nécessaires sont présents pour une création
            required_fields = ['name', 'year', 'selling_price', 'km_driven', 'fuel', 'seller_type', 'transmission', 'owner']
            if all(field in new_car_data for field in required_fields):
                data_manager.create_car(new_car_data)
            else:
                print("Données incomplètes. Tous les champs sont requis pour ajouter une voiture.")

        elif choice == '4': # Mettre à jour une voiture
            cars_df = data_manager.get_all_cars()
            if cars_df.empty:
                print("Aucune voiture à mettre à jour.")
            else:
                try:
                    if source_type_label == "ID":
                        entity_id = int(input(f"Entrez l'{source_type_label} de la voiture à mettre à jour: "))
                        car_to_update = data_manager.get_car_by_id(entity_id)
                    else: # CSV utilise l'index
                        index_max = len(cars_df) - 1
                        entity_id = int(input(f"Entrez l'{source_type_label} de la voiture à mettre à jour (0-{index_max}): "))
                        car_to_update = data_manager.get_car_by_index(entity_id)

                    if car_to_update:
                        print(f"\nMise à jour de la voiture à l'{source_type_label} {entity_id}:")
                        if source_type_label == "ID" and 'id' in car_to_update:
                            print(f"ID: {car_to_update['id']}")
                        elif source_type_label == "index":
                             print(f"Index: {entity_id}")
                        for key, value in car_to_update.items():
                            if key == 'id' and source_type_label == "ID": continue
                            print(f"{key.replace('_', ' ').capitalize()}: {value}")
                        
                        updated_data = get_car_details_from_user(is_update=True)
                        if updated_data: # Si l'utilisateur a fourni des données à mettre à jour
                            if source_type_label == "ID":
                                data_manager.update_car(entity_id, updated_data)
                            else:
                                data_manager.update_car(entity_id, updated_data) # CSV update_car prend aussi l'index
                        else:
                            print("Aucune modification fournie.")
                    else:
                        print(f"Aucune voiture trouvée à l'{source_type_label} {entity_id} pour la mise à jour.")
                except ValueError:
                    print(f"{source_type_label} invalide. Veuillez entrer un nombre.")

        elif choice == '5': # Supprimer une voiture
            cars_df = data_manager.get_all_cars()
            if cars_df.empty:
                print("Aucune voiture à supprimer.")
            else:
                try:
                    if source_type_label == "ID":
                        entity_id = int(input(f"Entrez l'{source_type_label} de la voiture à supprimer: "))
                        # Pour SQLite, delete_car attend un ID
                        deleted_car = data_manager.delete_car(entity_id)
                    else: # CSV utilise l'index
                        index_max = len(cars_df) - 1
                        entity_id = int(input(f"Entrez l'{source_type_label} de la voiture à supprimer (0-{index_max}): "))
                        deleted_car = data_manager.delete_car(entity_id)

                    if deleted_car:
                        print(f"Voiture à l'{source_type_label} {entity_id} supprimée.")
                    else:
                        # Le message d'erreur spécifique est généralement géré dans le DataManager
                        # Mais on peut ajouter un message générique ici si delete_car retourne None sans imprimer
                        print(f"Aucune voiture trouvée à l'{source_type_label} {entity_id} pour la suppression ou la suppression a échoué.")
                except ValueError:
                    print(f"{source_type_label} invalide. Veuillez entrer un nombre.")

        elif choice == '6': # Rechercher un véhicule
            print("\n--- Rechercher un véhicule ---")
            # Définir les attributs de recherche possibles
            # Pour CSV, les colonnes du DataFrame. Pour SQLite, les colonnes de la table.
            # On peut obtenir les colonnes du DataFrame pour les deux cas après un get_all_cars()
            # ou définir une liste fixe si on préfère.
            all_cars_sample = data_manager.get_all_cars()
            if all_cars_sample.empty:
                print("Aucune voiture dans la base de données pour définir les critères de recherche.")
            else:
                # Exclure 'id' pour CSV car il n'est pas un attribut direct de recherche comme pour SQLite
                # et source_type_label est déjà utilisé pour l'affichage/MAJ/suppression par ID/index.
                # Pour SQLite, 'id' est un attribut valide.
                possible_attributes = [col for col in all_cars_sample.columns if col != 'id' or source_type_label == "ID"]
                if not possible_attributes:
                    print("Impossible de déterminer les attributs de recherche.")
                else:
                    print("Choisissez un attribut pour la recherche:")
                    for i, attr in enumerate(possible_attributes):
                        print(f"{i + 1}. {attr.replace('_', ' ').capitalize()}")
                    
                    attr_choice_str = input("Votre choix d'attribut (numéro): ")
                    try:
                        attr_choice_idx = int(attr_choice_str) - 1
                        if 0 <= attr_choice_idx < len(possible_attributes):
                            search_attribute = possible_attributes[attr_choice_idx]
                            search_value = input(f"Entrez la valeur à rechercher pour '{search_attribute.replace('_', ' ').capitalize()}': ")
                            
                            results_df = data_manager.search_cars(search_attribute, search_value)
                            
                            if not results_df.empty:
                                print("\n--- Résultats de la recherche ---")
                                print(results_df.to_string())
                            else:
                                print("Aucune voiture ne correspond à vos critères de recherche.")
                        else:
                            print("Choix d'attribut invalide.")
                    except ValueError:
                        print("Choix d'attribut invalide. Veuillez entrer un nombre.")

        elif choice == '0': # Quitter
            print("Au revoir !")
            break

        else:
            print("Choix invalide. Veuillez réessayer.")

if __name__ == '__main__':
    # S'assurer que le fichier de données existe ou est créé s'il est vide
    # data_manager.load_data() # Peut être appelé pour initialiser/vérifier le fichier au démarrage
    main()