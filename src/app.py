import data_manager

def print_menu():
    """Affiche le menu des options CRUD."""
    print("\n--- Menu CRUD Voitures ---")
    print("1. Lister toutes les voitures")
    print("2. Afficher une voiture (par index)")
    print("3. Ajouter une nouvelle voiture")
    print("4. Mettre à jour une voiture (par index)")
    print("5. Supprimer une voiture (par index)")
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
    while True:
        print_menu()
        choice = input("Entrez votre choix: ")

        if choice == '1': # Lister toutes les voitures
            print("\n--- Liste de toutes les voitures ---")
            cars = data_manager.get_all_cars()
            if not cars.empty:
                print(cars.to_string())
            else:
                print("Aucune voiture dans la base de données.")

        elif choice == '2': # Afficher une voiture par index
            try:
                index = int(input("Entrez l'index de la voiture à afficher: "))
                car = data_manager.get_car_by_index(index)
                if car:
                    print("\n--- Détails de la voiture ---")
                    for key, value in car.items():
                        print(f"{key.replace('_', ' ').capitalize()}: {value}")
            except ValueError:
                print("Index invalide. Veuillez entrer un nombre.")

        elif choice == '3': # Ajouter une nouvelle voiture
            new_car_data = get_car_details_from_user()
            # Vérifier si tous les champs nécessaires sont présents pour une création
            required_fields = ['name', 'year', 'selling_price', 'km_driven', 'fuel', 'seller_type', 'transmission', 'owner']
            if all(field in new_car_data for field in required_fields):
                data_manager.create_car(new_car_data)
            else:
                print("Données incomplètes. Tous les champs sont requis pour ajouter une voiture.")

        elif choice == '4': # Mettre à jour une voiture
            try:
                index = int(input("Entrez l'index de la voiture à mettre à jour: "))
                car_to_update = data_manager.get_car_by_index(index)
                if car_to_update:
                    print(f"\nMise à jour de la voiture à l'index {index}:")
                    for key, value in car_to_update.items():
                        print(f"{key.replace('_', ' ').capitalize()}: {value}")
                    updated_data = get_car_details_from_user(is_update=True)
                    if updated_data: # Si l'utilisateur a fourni des données à mettre à jour
                        data_manager.update_car(index, updated_data)
                    else:
                        print("Aucune modification fournie.")
                # else: get_car_by_index gère déjà le message d'erreur
            except ValueError:
                print("Index invalide. Veuillez entrer un nombre.")

        elif choice == '5': # Supprimer une voiture
            try:
                index = int(input("Entrez l'index de la voiture à supprimer: "))
                data_manager.delete_car(index)
            except ValueError:
                print("Index invalide. Veuillez entrer un nombre.")

        elif choice == '0': # Quitter
            print("Au revoir !")
            break

        else:
            print("Choix invalide. Veuillez réessayer.")

if __name__ == '__main__':
    # S'assurer que le fichier de données existe ou est créé s'il est vide
    # data_manager.load_data() # Peut être appelé pour initialiser/vérifier le fichier au démarrage
    main()