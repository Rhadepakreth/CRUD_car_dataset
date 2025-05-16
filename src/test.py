import pandas as pd
from data_manager import CsvDataSource, CsvCarRepository, SQLiteCarRepository


# Tests unitaires pour le projet de gestion de voitures
# La logique de haut niveau dépend des abstractions (CarRepository), pas des implémentations concrètes.
def main_app_logic(repository: CarRepository):
    print("--- Toutes les voitures ---")
    all_cars = repository.get_all_cars()
    print(all_cars.head() if not all_cars.empty else "Aucune voiture trouvée.")

    print("\n--- Création d'une voiture ---")
    new_car = {
        'name': 'SuperCar ModelX', 'year': 2024, 'selling_price': 90000,
        'km_driven': 100, 'fuel': 'Electric', 'seller_type': 'Dealer',
        'transmission': 'Automatic', 'owner': 'First Owner'
    }
    created_car = repository.create_car(new_car)
    if created_car:
        print(f"Voiture créée: {created_car}")
        car_id_to_test = created_car.get('id') if isinstance(repository, SQLiteCarRepository) else len(all_cars) # CSV index vs SQLite ID
        if car_id_to_test is not None:
            print(f"\n--- Voiture par ID ({car_id_to_test}) ---")
            car = repository.get_car_by_id(car_id_to_test)
            print(car if car else f"Aucune voiture trouvée avec l'ID {car_id_to_test}.")

            print(f"\n--- Mise à jour de la voiture ID ({car_id_to_test}) ---")
            updated_data = {'selling_price': 85000, 'km_driven': 500}
            updated_car = repository.update_car(car_id_to_test, updated_data)
            print(f"Voiture mise à jour: {updated_car}" if updated_car else "Échec de la mise à jour.")

            print(f"\n--- Recherche de voitures (name='SuperCar') ---")
            found_cars = repository.search_cars('name', 'SuperCar')
            print(found_cars.head() if not found_cars.empty else "Aucune voiture correspondante.")

            # print(f"\n--- Suppression de la voiture ID ({car_id_to_test}) ---")
            # deleted_car = repository.delete_car(car_id_to_test)
            # print(f"Voiture supprimée: {deleted_car}" if deleted_car else "Échec de la suppression.")

if __name__ == '__main__':
    # Utilisation avec CSV
    print("\n******** UTILISATION AVEC CSV ********")
    csv_data_source = CsvDataSource()
    csv_repo = CsvCarRepository(csv_data_source)
    main_app_logic(csv_repo)

    # Utilisation avec SQLite
    print("\n******** UTILISATION AVEC SQLITE ********")
    sqlite_repo = SQLiteCarRepository()
    main_app_logic(sqlite_repo)
