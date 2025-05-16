import pandas as pd
import os
import sqlite3
from abc import ABC, abstractmethod

# --- Principles SOLID --- #

# Interface Segregation Principle (ISP) & Single Responsibility Principle (SRP)
# DataSource: Responsable uniquement du chargement et de la sauvegarde des données brutes.
class DataSource(ABC):
    @abstractmethod
    def load_data(self):
        """Charge les données depuis la source."""
        pass

    @abstractmethod
    def save_data(self, data):
        """Sauvegarde les données dans la source."""
        pass

# CarRepository: Responsable des opérations CRUD spécifiques aux voitures.
class CarRepository(ABC):
    @abstractmethod
    def create_car(self, new_car_data):
        pass

    @abstractmethod
    def get_all_cars(self):
        pass

    @abstractmethod
    def get_car_by_id(self, car_id):
        # Pour CSV, l'ID sera l'index. Pour SQLite, ce sera la clé primaire.
        pass

    @abstractmethod
    def update_car(self, car_id, updated_car_data):
        pass

    @abstractmethod
    def delete_car(self, car_id):
        pass

    @abstractmethod
    def search_cars(self, attribute, value):
        pass


# --- CSV Implementation --- #

# Single Responsibility Principle (SRP)
# CsvDataSource: Gère spécifiquement la lecture/écriture des fichiers CSV.
class CsvDataSource(DataSource):
    def __init__(self, file_path=None):
        if file_path is None:
            self.file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'car_dataset.csv'))
        else:
            self.file_path = file_path
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

    def load_data(self):
        try:
            return pd.read_csv(self.file_path)
        except FileNotFoundError:
            print(f"Erreur: Le fichier {self.file_path} n'a pas été trouvé.")
            return pd.DataFrame()
        except Exception as e:
            print(f"Erreur lors du chargement des données CSV: {e}")
            return pd.DataFrame()

    def save_data(self, df):
        try:
            df.to_csv(self.file_path, index=False)
            print("Données CSV sauvegardées avec succès.")
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des données CSV: {e}")

# Liskov Substitution Principle (LSP) & Dependency Inversion Principle (DIP)
# CsvCarRepository dépend de l'abstraction DataSource, pas d'une implémentation concrète.
class CsvCarRepository(CarRepository):
    def __init__(self, data_source: DataSource):
        self.data_source = data_source

    def create_car(self, new_car_data):
        df = self.data_source.load_data()
        new_car_df = pd.DataFrame([new_car_data])
        df = pd.concat([df, new_car_df], ignore_index=True)
        self.data_source.save_data(df)
        print("Nouvelle voiture ajoutée au CSV.")
        if not df.empty:
            return df.iloc[-1].to_dict()
        return None

    def get_all_cars(self):
        return self.data_source.load_data()

    def get_car_by_id(self, index): # Pour CSV, l'ID est l'index
        df = self.data_source.load_data()
        if not df.empty and 0 <= index < len(df):
            return df.iloc[index].to_dict()
        return None

    def update_car(self, index, updated_car_data): # Pour CSV, l'ID est l'index
        df = self.data_source.load_data()
        if not df.empty and 0 <= index < len(df):
            for key, value in updated_car_data.items():
                if key in df.columns:
                    df.loc[index, key] = value
                else:
                    print(f"Attention: La colonne CSV '{key}' n'existe pas et n'a pas été mise à jour.")
            self.data_source.save_data(df)
            print(f"Voiture à l'index CSV {index} mise à jour.")
            return df.iloc[index].to_dict()
        return None

    def delete_car(self, index): # Pour CSV, l'ID est l'index
        df = self.data_source.load_data()
        if not df.empty and 0 <= index < len(df):
            car_deleted = df.iloc[index].to_dict()
            df = df.drop(index).reset_index(drop=True)
            self.data_source.save_data(df)
            print(f"Voiture à l'index CSV {index} supprimée.")
            return car_deleted
        return None

    def search_cars(self, attribute, value):
        df = self.data_source.load_data()
        if df.empty:
            print("La source de données CSV est vide.")
            return pd.DataFrame()

        if attribute not in df.columns:
            print(f"L'attribut CSV '{attribute}' n'existe pas.")
            return pd.DataFrame()

        try:
            if pd.api.types.is_numeric_dtype(df[attribute]):
                value_to_search = type(df[attribute].dropna().iloc[0])(value) if not df[attribute].dropna().empty else value
            elif pd.api.types.is_string_dtype(df[attribute]):
                value_to_search = str(value)
            else:
                value_to_search = value

            if pd.api.types.is_string_dtype(df[attribute]):
                result_df = df[df[attribute].astype(str).str.contains(value_to_search, case=False, na=False)]
            else:
                result_df = df[df[attribute] == value_to_search]
            return result_df
        except ValueError:
            print(f"La valeur '{value}' n'est pas compatible avec le type de l'attribut CSV '{attribute}'.")
            return pd.DataFrame()
        except Exception as e:
            print(f"Une erreur est survenue lors de la recherche CSV: {e}")
            return pd.DataFrame()


# --- SQLite Implementation --- #

# SQLiteDataManager (sera adapté pour devenir SQLiteCarRepository)
# Il gère déjà sa propre connexion et la création de table (SRP pour la configuration DB)
# Open/Closed Principle (OCP): On pourrait étendre avec d'autres types de DB sans modifier CarRepository.

class SQLiteCarRepository(CarRepository):
    def __init__(self, db_file_path=None):
        if db_file_path is None:
            self.db_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'cars.db'))
        else:
            self.db_file_path = db_file_path
        os.makedirs(os.path.dirname(self.db_file_path), exist_ok=True)
        self._create_table_if_not_exists()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_file_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _create_table_if_not_exists(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cars (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                year INTEGER,
                selling_price INTEGER,
                km_driven INTEGER,
                fuel TEXT,
                seller_type TEXT,
                transmission TEXT,
                owner TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def create_car(self, new_car_data):
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            # S'assurer que toutes les clés attendues sont présentes, avec des valeurs par défaut si nécessaire
            # pour éviter les erreurs si new_car_data ne les contient pas toutes.
            # Ceci est un exemple, adaptez selon les colonnes NOT NULL et les valeurs par défaut souhaitées.
            cols = ['name', 'year', 'selling_price', 'km_driven', 'fuel', 'seller_type', 'transmission', 'owner']
            car_data_for_db = {col: new_car_data.get(col) for col in cols}
            
            cursor.execute(f'''
                INSERT INTO cars ({', '.join(cols)})
                VALUES (:{', :'.join(cols)})
            ''', car_data_for_db)
            conn.commit()
            car_id = cursor.lastrowid
            print(f"Nouvelle voiture ajoutée à SQLite avec l'ID {car_id}.")
            return self.get_car_by_id(car_id)
        except sqlite3.Error as e:
            print(f"Erreur SQLite lors de la création de la voiture: {e}")
            return None
        finally:
            conn.close()

    def get_all_cars(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM cars")
            cars = cursor.fetchall()
            cars_list = [dict(row) for row in cars]
            return pd.DataFrame(cars_list)
        except sqlite3.Error as e:
            print(f"Erreur SQLite lors de la récupération de toutes les voitures: {e}")
            return pd.DataFrame()
        finally:
            conn.close()

    def get_car_by_id(self, car_id):
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM cars WHERE id = ?", (car_id,))
            car = cursor.fetchone()
            if car:
                return dict(car)
            return None
        except sqlite3.Error as e:
            print(f"Erreur SQLite lors de la récupération de la voiture ID {car_id}: {e}")
            return None
        finally:
            conn.close()

    def update_car(self, car_id, updated_car_data):
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            if self.get_car_by_id(car_id) is None:
                print(f"Aucune voiture trouvée avec l'ID SQLite {car_id} pour la mise à jour.")
                return None

            set_clause_parts = []
            values = []
            valid_columns = ['name', 'year', 'selling_price', 'km_driven', 'fuel', 'seller_type', 'transmission', 'owner']
            for key, value in updated_car_data.items():
                if key in valid_columns:
                    set_clause_parts.append(f"{key} = ?")
                    values.append(value)
            
            if not set_clause_parts:
                print("Aucune donnée SQLite valide fournie pour la mise à jour.") 
                return self.get_car_by_id(car_id)

            set_clause = ", ".join(set_clause_parts)
            query = f"UPDATE cars SET {set_clause} WHERE id = ?"
            values.append(car_id)
            
            cursor.execute(query, tuple(values))
            conn.commit()
            
            if cursor.rowcount > 0:
                print(f"Voiture ID SQLite {car_id} mise à jour.")
            return self.get_car_by_id(car_id)
        except sqlite3.Error as e:
            print(f"Erreur SQLite lors de la mise à jour de la voiture ID {car_id}: {e}")
            return None
        finally:
            conn.close()

    def delete_car(self, car_id):
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            car_to_delete = self.get_car_by_id(car_id)
            if not car_to_delete:
                print(f"Aucune voiture trouvée avec l'ID SQLite {car_id} pour la suppression.")
                return None

            cursor.execute("DELETE FROM cars WHERE id = ?", (car_id,))
            conn.commit()
            if cursor.rowcount > 0:
                print(f"Voiture ID SQLite {car_id} supprimée.")
                return car_to_delete
            return None
        except sqlite3.Error as e:
            print(f"Erreur SQLite lors de la suppression de la voiture ID {car_id}: {e}")
            return None
        finally:
            conn.close()

    def search_cars(self, attribute, value):
        conn = self._get_connection()
        cursor = conn.cursor()
        valid_columns = ['id', 'name', 'year', 'selling_price', 'km_driven', 'fuel', 'seller_type', 'transmission', 'owner']
        if attribute not in valid_columns:
            print(f"L'attribut SQLite '{attribute}' n'est pas valide pour la recherche.")
            return pd.DataFrame()

        try:
            query = f"SELECT * FROM cars WHERE {attribute} LIKE ?"
            search_value = f"%{value}%"

            if attribute in ['year', 'selling_price', 'km_driven', 'id']:
                try:
                    numeric_value = int(value)
                    query = f"SELECT * FROM cars WHERE {attribute} = ?"
                    search_value = numeric_value
                except ValueError:
                    print(f"La valeur '{value}' doit être un nombre pour l'attribut SQLite '{attribute}'.")
                    return pd.DataFrame()
            
            cursor.execute(query, (search_value,))
            cars = cursor.fetchall()
            cars_list = [dict(row) for row in cars]
            return pd.DataFrame(cars_list)
        except sqlite3.Error as e:
            print(f"Erreur SQLite lors de la recherche des voitures: {e}")
            return pd.DataFrame()
        finally:
            conn.close()

# Exemple d'utilisation (Dependency Inversion Principle)
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

    # Nettoyage optionnel des fichiers de données de test
    # try:
    #     if os.path.exists(csv_data_source.file_path):
    #         os.remove(csv_data_source.file_path)
    #         print(f"Fichier CSV de test supprimé: {csv_data_source.file_path}")
    #     if os.path.exists(sqlite_repo.db_file_path):
    #         os.remove(sqlite_repo.db_file_path)
    #         print(f"Fichier SQLite de test supprimé: {sqlite_repo.db_file_path}")
    # except Exception as e:
    #     print(f"Erreur lors du nettoyage des fichiers de test: {e}")