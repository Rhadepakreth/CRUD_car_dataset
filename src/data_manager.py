import pandas as pd
import os
import sqlite3

class DataManager:
    def __init__(self, data_file_path=None):
        if data_file_path is None:
            # Construire un chemin absolu vers le fichier de données par défaut
            self.data_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'car_dataset.csv'))
        else:
            self.data_file_path = data_file_path

    def load_data(self):
        """Charge les données depuis le fichier CSV."""
        try:
            df = pd.read_csv(self.data_file_path)
            return df
        except FileNotFoundError:
            print(f"Erreur: Le fichier {self.data_file_path} n'a pas été trouvé.")
            return pd.DataFrame() # Retourne un DataFrame vide en cas d'erreur
        except Exception as e:
            print(f"Erreur lors du chargement des données: {e}")
            return pd.DataFrame()

    def save_data(self, df):
        """Sauvegarde les données dans le fichier CSV."""
        try:
            df.to_csv(self.data_file_path, index=False)
            print("Données sauvegardées avec succès.")
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des données: {e}")

    def create_car(self, new_car_data):
        """Ajoute une nouvelle voiture au dataset."""
        df = self.load_data()
        new_car_df = pd.DataFrame([new_car_data])
        # Utiliser pd.concat pour ajouter la nouvelle voiture
        df = pd.concat([df, new_car_df], ignore_index=True)
        self.save_data(df)
        print("Nouvelle voiture ajoutée.")
        # Retourner la dernière ligne ajoutée (la nouvelle voiture)
        if not df.empty:
            return df.iloc[-1].to_dict()
        return None

    def get_all_cars(self):
        """Récupère toutes les voitures du dataset."""
        return self.load_data()

    def get_car_by_index(self, index):
        """Récupère une voiture par son index."""
        df = self.load_data()
        if not df.empty and 0 <= index < len(df):
            return df.iloc[index].to_dict()
        else:
            # Le message d'erreur est géré par l'appelant ou ici si nécessaire
            # print(f"Aucune voiture trouvée à l'index {index}.") 
            return None

    def update_car(self, index, updated_car_data):
        """Met à jour les informations d'une voiture existante par son index."""
        df = self.load_data()
        if not df.empty and 0 <= index < len(df):
            for key, value in updated_car_data.items():
                if key in df.columns:
                    df.loc[index, key] = value
                else:
                    print(f"Attention: La colonne '{key}' n'existe pas et n'a pas été mise à jour.")
            self.save_data(df)
            print(f"Voiture à l'index {index} mise à jour.")
            return df.iloc[index].to_dict()
        else:
            # Le message d'erreur est géré par l'appelant ou ici si nécessaire
            # print(f"Aucune voiture trouvée à l'index {index} pour la mise à jour.")
            return None

    def delete_car(self, index):
        """Supprime une voiture du dataset par son index."""
        df = self.load_data()
        if not df.empty and 0 <= index < len(df):
            car_deleted = df.iloc[index].to_dict()
            df = df.drop(index).reset_index(drop=True)
            self.save_data(df)
            print(f"Voiture à l'index {index} supprimée.")
            return car_deleted
        else:
            # Le message d'erreur est géré par l'appelant ou ici si nécessaire
            # print(f"Aucune voiture trouvée à l'index {index} pour la suppression.")
            return None

    def search_cars(self, attribute, value):
        """Recherche des voitures en fonction d'un attribut et d'une valeur."""
        df = self.load_data()
        if df.empty:
            print("La source de données est vide.")
            return pd.DataFrame()

        if attribute not in df.columns:
            print(f"L'attribut '{attribute}' n'existe pas.")
            return pd.DataFrame()

        try:
            # Tenter de convertir la valeur de recherche au type de la colonne si possible
            # Cela est important pour les comparaisons numériques
            if pd.api.types.is_numeric_dtype(df[attribute]):
                value_to_search = type(df[attribute].dropna().iloc[0])(value) if not df[attribute].dropna().empty else value
            elif pd.api.types.is_string_dtype(df[attribute]):
                value_to_search = str(value)
            else:
                value_to_search = value # Pour d'autres types, utiliser la valeur telle quelle

            # Pour les chaînes de caractères, effectuer une recherche insensible à la casse et partielle (contient)
            if pd.api.types.is_string_dtype(df[attribute]):
                result_df = df[df[attribute].astype(str).str.contains(value_to_search, case=False, na=False)]
            else:
                result_df = df[df[attribute] == value_to_search]
            
            return result_df
        except ValueError:
            print(f"La valeur '{value}' n'est pas compatible avec le type de l'attribut '{attribute}'.")
            return pd.DataFrame()
        except Exception as e:
            print(f"Une erreur est survenue lors de la recherche: {e}")
            return pd.DataFrame()


class SQLiteDataManager:
    def __init__(self, db_file_path=None):
        if db_file_path is None:
            self.db_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'cars.db'))
        else:
            self.db_file_path = db_file_path
        # Créer le dossier 'data' s'il n'existe pas
        os.makedirs(os.path.dirname(self.db_file_path), exist_ok=True)
        self._create_table_if_not_exists()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_file_path)
        conn.row_factory = sqlite3.Row  # Pour accéder aux colonnes par nom
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
            cursor.execute('''
                INSERT INTO cars (name, year, selling_price, km_driven, fuel, seller_type, transmission, owner)
                VALUES (:name, :year, :selling_price, :km_driven, :fuel, :seller_type, :transmission, :owner)
            ''', new_car_data)
            conn.commit()
            car_id = cursor.lastrowid
            print(f"Nouvelle voiture ajoutée avec l'ID {car_id}.")
            return self.get_car_by_id(car_id)
        except sqlite3.Error as e:
            print(f"Erreur SQLite lors de la création de la voiture: {e}")
            return None
        finally:
            conn.close()

    def search_cars(self, attribute, value):
        """Recherche des voitures en fonction d'un attribut et d'une valeur dans SQLite."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Valider que l'attribut est une colonne connue pour éviter les injections SQL
        # et pour s'assurer que la recherche est possible.
        # Les colonnes valides sont celles définies dans _create_table_if_not_exists
        # plus 'id' qui est la clé primaire.
        valid_columns = ['id', 'name', 'year', 'selling_price', 'km_driven', 'fuel', 'seller_type', 'transmission', 'owner']
        if attribute not in valid_columns:
            print(f"L'attribut '{attribute}' n'est pas valide pour la recherche.")
            return pd.DataFrame() # Retourner un DataFrame vide

        try:
            # Pour SQLite, la recherche de chaînes avec LIKE est plus flexible.
            # Pour les nombres, une comparaison directe est nécessaire.
            # Nous devons essayer de convertir la valeur en nombre si l'attribut est numérique.
            query = f"SELECT * FROM cars WHERE {attribute} LIKE ?" # Utiliser LIKE pour les chaînes
            search_value = f"%{value}%" # Recherche partielle pour les chaînes

            # Si l'attribut est numérique, tenter une conversion et utiliser une comparaison exacte
            # Note: Cela suppose que vous connaissez les types de vos colonnes.
            # Une approche plus robuste vérifierait le type de la colonne dans le schéma de la DB.
            if attribute in ['year', 'selling_price', 'km_driven', 'id']:
                try:
                    numeric_value = int(value) # ou float(value) si applicable
                    query = f"SELECT * FROM cars WHERE {attribute} = ?"
                    search_value = numeric_value
                except ValueError:
                    print(f"La valeur '{value}' doit être un nombre pour l'attribut '{attribute}'.")
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

    def get_all_cars(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM cars")
            cars = cursor.fetchall()
            # Convertir les objets Row en une liste de dictionnaires
            cars_list = [dict(row) for row in cars]
            return pd.DataFrame(cars_list) # Retourner un DataFrame pour la cohérence
        except sqlite3.Error as e:
            print(f"Erreur SQLite lors de la récupération de toutes les voitures: {e}")
            return pd.DataFrame()  # Retourne un DataFrame vide en cas d'erreur
        finally:
            conn.close()

    def search_cars(self, attribute, value):
        """Recherche des voitures en fonction d'un attribut et d'une valeur dans SQLite."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Valider que l'attribut est une colonne connue pour éviter les injections SQL
        # et pour s'assurer que la recherche est possible.
        # Les colonnes valides sont celles définies dans _create_table_if_not_exists
        # plus 'id' qui est la clé primaire.
        valid_columns = ['id', 'name', 'year', 'selling_price', 'km_driven', 'fuel', 'seller_type', 'transmission', 'owner']
        if attribute not in valid_columns:
            print(f"L'attribut '{attribute}' n'est pas valide pour la recherche.")
            return pd.DataFrame() # Retourner un DataFrame vide

        try:
            # Pour SQLite, la recherche de chaînes avec LIKE est plus flexible.
            # Pour les nombres, une comparaison directe est nécessaire.
            # Nous devons essayer de convertir la valeur en nombre si l'attribut est numérique.
            query = f"SELECT * FROM cars WHERE {attribute} LIKE ?" # Utiliser LIKE pour les chaînes
            search_value = f"%{value}%" # Recherche partielle pour les chaînes

            # Si l'attribut est numérique, tenter une conversion et utiliser une comparaison exacte
            # Note: Cela suppose que vous connaissez les types de vos colonnes.
            # Une approche plus robuste vérifierait le type de la colonne dans le schéma de la DB.
            if attribute in ['year', 'selling_price', 'km_driven', 'id']:
                try:
                    numeric_value = int(value) # ou float(value) si applicable
                    query = f"SELECT * FROM cars WHERE {attribute} = ?"
                    search_value = numeric_value
                except ValueError:
                    print(f"La valeur '{value}' doit être un nombre pour l'attribut '{attribute}'.")
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

    def search_cars(self, attribute, value):
        """Recherche des voitures en fonction d'un attribut et d'une valeur dans SQLite."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Valider que l'attribut est une colonne connue pour éviter les injections SQL
        # et pour s'assurer que la recherche est possible.
        # Les colonnes valides sont celles définies dans _create_table_if_not_exists
        # plus 'id' qui est la clé primaire.
        valid_columns = ['id', 'name', 'year', 'selling_price', 'km_driven', 'fuel', 'seller_type', 'transmission', 'owner']
        if attribute not in valid_columns:
            print(f"L'attribut '{attribute}' n'est pas valide pour la recherche.")
            return pd.DataFrame() # Retourner un DataFrame vide

        try:
            # Pour SQLite, la recherche de chaînes avec LIKE est plus flexible.
            # Pour les nombres, une comparaison directe est nécessaire.
            # Nous devons essayer de convertir la valeur en nombre si l'attribut est numérique.
            query = f"SELECT * FROM cars WHERE {attribute} LIKE ?" # Utiliser LIKE pour les chaînes
            search_value = f"%{value}%" # Recherche partielle pour les chaînes

            # Si l'attribut est numérique, tenter une conversion et utiliser une comparaison exacte
            # Note: Cela suppose que vous connaissez les types de vos colonnes.
            # Une approche plus robuste vérifierait le type de la colonne dans le schéma de la DB.
            if attribute in ['year', 'selling_price', 'km_driven', 'id']:
                try:
                    numeric_value = int(value) # ou float(value) si applicable
                    query = f"SELECT * FROM cars WHERE {attribute} = ?"
                    search_value = numeric_value
                except ValueError:
                    print(f"La valeur '{value}' doit être un nombre pour l'attribut '{attribute}'.")
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

    def update_car(self, car_id, updated_car_data):
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            # Vérifier d'abord si la voiture existe
            if self.get_car_by_id(car_id) is None:
                print(f"Aucune voiture trouvée avec l'ID {car_id} pour la mise à jour.")
                return None

            set_clause_parts = []
            values = []
            for key, value in updated_car_data.items():
                # Assurez-vous que la clé est une colonne valide pour éviter les injections SQL
                # et qu'elle n'est pas 'id'
                if key in ['name', 'year', 'selling_price', 'km_driven', 'fuel', 'seller_type', 'transmission', 'owner']:
                    set_clause_parts.append(f"{key} = ?")
                    values.append(value)
            
            if not set_clause_parts:
                print("Aucune donnée valide fournie pour la mise à jour.")
                return self.get_car_by_id(car_id) # Retourner l'original si rien n'est changé

            set_clause = ", ".join(set_clause_parts)
            query = f"UPDATE cars SET {set_clause} WHERE id = ?"
            values.append(car_id)
            
            cursor.execute(query, tuple(values))
            conn.commit()
            
            if cursor.rowcount > 0:
                print(f"Voiture ID {car_id} mise à jour.")
                return self.get_car_by_id(car_id)
            else:
                # Ce cas peut arriver si les données fournies sont identiques aux données existantes
                # ou si l'ID n'a pas été trouvé (déjà géré ci-dessus, mais double sécurité)
                print(f"Aucune voiture trouvée avec l'ID {car_id} pour la mise à jour, ou aucune donnée n'a changé.")
                return self.get_car_by_id(car_id) # Retourner l'état actuel
        except sqlite3.Error as e:
            print(f"Erreur SQLite lors de la mise à jour de la voiture ID {car_id}: {e}")
            return None
        finally:
            conn.close()

    def search_cars(self, attribute, value):
        """Recherche des voitures en fonction d'un attribut et d'une valeur dans SQLite."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Valider que l'attribut est une colonne connue pour éviter les injections SQL
        # et pour s'assurer que la recherche est possible.
        # Les colonnes valides sont celles définies dans _create_table_if_not_exists
        # plus 'id' qui est la clé primaire.
        valid_columns = ['id', 'name', 'year', 'selling_price', 'km_driven', 'fuel', 'seller_type', 'transmission', 'owner']
        if attribute not in valid_columns:
            print(f"L'attribut '{attribute}' n'est pas valide pour la recherche.")
            return pd.DataFrame() # Retourner un DataFrame vide

        try:
            # Pour SQLite, la recherche de chaînes avec LIKE est plus flexible.
            # Pour les nombres, une comparaison directe est nécessaire.
            # Nous devons essayer de convertir la valeur en nombre si l'attribut est numérique.
            query = f"SELECT * FROM cars WHERE {attribute} LIKE ?" # Utiliser LIKE pour les chaînes
            search_value = f"%{value}%" # Recherche partielle pour les chaînes

            # Si l'attribut est numérique, tenter une conversion et utiliser une comparaison exacte
            # Note: Cela suppose que vous connaissez les types de vos colonnes.
            # Une approche plus robuste vérifierait le type de la colonne dans le schéma de la DB.
            if attribute in ['year', 'selling_price', 'km_driven', 'id']:
                try:
                    numeric_value = int(value) # ou float(value) si applicable
                    query = f"SELECT * FROM cars WHERE {attribute} = ?"
                    search_value = numeric_value
                except ValueError:
                    print(f"La valeur '{value}' doit être un nombre pour l'attribut '{attribute}'.")
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

    def delete_car(self, car_id):
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            car_to_delete = self.get_car_by_id(car_id)
            if not car_to_delete:
                print(f"Aucune voiture trouvée avec l'ID {car_id} pour la suppression.")
                return None

            cursor.execute("DELETE FROM cars WHERE id = ?", (car_id,))
            conn.commit()
            if cursor.rowcount > 0:
                print(f"Voiture ID {car_id} supprimée.")
                return car_to_delete  # Retourne les données de la voiture supprimée
            # Ce cas ne devrait pas arriver si get_car_by_id a trouvé la voiture
            return None
        except sqlite3.Error as e:
            print(f"Erreur SQLite lors de la suppression de la voiture ID {car_id}: {e}")
            return None
        finally:
            conn.close()

    def search_cars(self, attribute, value):
        """Recherche des voitures en fonction d'un attribut et d'une valeur dans SQLite."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Valider que l'attribut est une colonne connue pour éviter les injections SQL
        # et pour s'assurer que la recherche est possible.
        # Les colonnes valides sont celles définies dans _create_table_if_not_exists
        # plus 'id' qui est la clé primaire.
        valid_columns = ['id', 'name', 'year', 'selling_price', 'km_driven', 'fuel', 'seller_type', 'transmission', 'owner']
        if attribute not in valid_columns:
            print(f"L'attribut '{attribute}' n'est pas valide pour la recherche.")
            return pd.DataFrame() # Retourner un DataFrame vide

        try:
            # Pour SQLite, la recherche de chaînes avec LIKE est plus flexible.
            # Pour les nombres, une comparaison directe est nécessaire.
            # Nous devons essayer de convertir la valeur en nombre si l'attribut est numérique.
            query = f"SELECT * FROM cars WHERE {attribute} LIKE ?" # Utiliser LIKE pour les chaînes
            search_value = f"%{value}%" # Recherche partielle pour les chaînes

            # Si l'attribut est numérique, tenter une conversion et utiliser une comparaison exacte
            # Note: Cela suppose que vous connaissez les types de vos colonnes.
            # Une approche plus robuste vérifierait le type de la colonne dans le schéma de la DB.
            if attribute in ['year', 'selling_price', 'km_driven', 'id']:
                try:
                    numeric_value = int(value) # ou float(value) si applicable
                    query = f"SELECT * FROM cars WHERE {attribute} = ?"
                    search_value = numeric_value
                except ValueError:
                    print(f"La valeur '{value}' doit être un nombre pour l'attribut '{attribute}'.")
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


# Pour conserver la compatibilité avec les anciens appels directs ou pour des tests rapides
# Ces fonctions peuvent être retirées si elles ne sont plus nécessaires.
_default_manager = DataManager()

def load_data():
    return _default_manager.load_data()

def save_data(df):
    _default_manager.save_data(df)

def create_car(new_car_data):
    return _default_manager.create_car(new_car_data)

def get_all_cars():
    return _default_manager.get_all_cars()

def get_car_by_index(index):
    return _default_manager.get_car_by_index(index)

def update_car(index, updated_car_data):
    return _default_manager.update_car(index, updated_car_data)

def delete_car(index):
    return _default_manager.delete_car(index)

if __name__ == '__main__':
    # Exemples d'utilisation avec la classe DataManager
    manager = DataManager()
    print("Chargement initial des données...")
    cars_df = manager.load_data()
    if not cars_df.empty:
        print(f"Nombre total de voitures: {len(cars_df)}")
        print("Premières 5 voitures:")
        print(cars_df.head())

        # # Exemple d'ajout
        # print("\nAjout d'une nouvelle voiture...")
        # nouvelle_voiture = {
        # 'name': 'Test Car Class',
        # 'year': 2024,
        # 'selling_price': 120000,
        # 'km_driven': 50,
        # 'fuel': 'Electric',
        # 'seller_type': 'Dealer',
        # 'transmission': 'Automatic',
        # 'owner': 'First Owner'
        # }
        # added_car = manager.create_car(nouvelle_voiture)
        # if added_car:
        #     print("Voiture ajoutée:", added_car)
        # print(manager.get_all_cars().tail(1))

        # # Exemple de lecture par index
        # print("\nLecture de la voiture à l'index 0...")
        # car = manager.get_car_by_index(0)
        # if car: print(car)
        # else: print("Voiture non trouvée.")

        # # Exemple de mise à jour
        # print("\nMise à jour de la voiture à l'index 0...")
        # updated_details = {'selling_price': 70000, 'km_driven': 80000}
        # updated_car = manager.update_car(0, updated_details)
        # if updated_car: print(updated_car)
        # else: print("Mise à jour échouée ou voiture non trouvée.")
        # car = manager.get_car_by_index(0)
        # if car: print(car)
        # else: print("Voiture non trouvée.")

        # # Exemple de suppression
        # print("\nSuppression de la voiture à l'index (nouveau) 0...")
        # # Assurez-vous que l'index est valide après d'éventuelles modifications
        # current_cars = manager.get_all_cars()
        # if not current_cars.empty:
        #     deleted_car = manager.delete_car(0)
        #     if deleted_car: print("Voiture supprimée:", deleted_car)
        #     else: print("Suppression échouée ou voiture non trouvée.")
        #     print(manager.get_all_cars().head())
        # else:
        #     print("Aucune voiture à supprimer.")
    else:
        print("Impossible de charger les données pour les exemples.")