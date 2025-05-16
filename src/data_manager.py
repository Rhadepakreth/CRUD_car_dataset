import pandas as pd
import os

# Construire un chemin absolu vers le fichier de données
DATA_FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'car_dataset.csv'))

def load_data():
    """Charge les données depuis le fichier CSV."""
    try:
        df = pd.read_csv(DATA_FILE_PATH)
        return df
    except FileNotFoundError:
        print(f"Erreur: Le fichier {DATA_FILE_PATH} n'a pas été trouvé.")
        return pd.DataFrame() # Retourne un DataFrame vide en cas d'erreur

def save_data(df):
    """Sauvegarde les données dans le fichier CSV."""
    try:
        df.to_csv(DATA_FILE_PATH, index=False)
        print("Données sauvegardées avec succès.")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde des données: {e}")

def create_car(new_car_data):
    """Ajoute une nouvelle voiture au dataset."""
    df = load_data()
    # S'assurer que new_car_data est un DataFrame ou une Series pour l'ajout
    # Pour cet exemple, supposons que new_car_data est un dictionnaire
    new_car_df = pd.DataFrame([new_car_data])
    df = pd.concat([df, new_car_df], ignore_index=True)
    save_data(df)
    print("Nouvelle voiture ajoutée.")
    return df.iloc[-1].to_dict() # Retourne la voiture ajoutée

def get_all_cars():
    """Récupère toutes les voitures du dataset."""
    return load_data()

def get_car_by_index(index):
    """Récupère une voiture par son index."""
    df = load_data()
    if not df.empty and 0 <= index < len(df):
        return df.iloc[index].to_dict()
    else:
        print(f"Aucune voiture trouvée à l'index {index}.")
        return None

def update_car(index, updated_car_data):
    """Met à jour les informations d'une voiture existante par son index."""
    df = load_data()
    if not df.empty and 0 <= index < len(df):
        for key, value in updated_car_data.items():
            if key in df.columns:
                df.loc[index, key] = value
            else:
                print(f"Attention: La colonne '{key}' n'existe pas et n'a pas été mise à jour.")
        save_data(df)
        print(f"Voiture à l'index {index} mise à jour.")
        return df.iloc[index].to_dict()
    else:
        print(f"Aucune voiture trouvée à l'index {index} pour la mise à jour.")
        return None

def delete_car(index):
    """Supprime une voiture du dataset par son index."""
    df = load_data()
    if not df.empty and 0 <= index < len(df):
        car_deleted = df.iloc[index].to_dict()
        df = df.drop(index).reset_index(drop=True)
        save_data(df)
        print(f"Voiture à l'index {index} supprimée.")
        return car_deleted
    else:
        print(f"Aucune voiture trouvée à l'index {index} pour la suppression.")
        return None

if __name__ == '__main__':
    # Exemples d'utilisation (peuvent être retirés ou commentés)
    print("Chargement initial des données...")
    cars_df = load_data()
    if not cars_df.empty:
        print(f"Nombre total de voitures: {len(cars_df)}")
        print("Premières 5 voitures:")
        print(cars_df.head())

        # Exemple d'ajout
        # print("\nAjout d'une nouvelle voiture...")
        # nouvelle_voiture = {
        # 'name': 'Test Car',
        # 'year': 2023,
        # 'selling_price': 100000,
        # 'km_driven': 100,
        # 'fuel': 'Petrol',
        # 'seller_type': 'Individual',
        # 'transmission': 'Manual',
        # 'owner': 'First Owner'
        # }
        # create_car(nouvelle_voiture)
        # print(load_data().tail(1))

        # Exemple de lecture par index
        # print("\nLecture de la voiture à l'index 0...")
        # print(get_car_by_index(0))

        # Exemple de mise à jour
        # print("\nMise à jour de la voiture à l'index 0...")
        # update_car(0, {'selling_price': 65000, 'km_driven': 75000})
        # print(get_car_by_index(0))

        # Exemple de suppression
        # print("\nSuppression de la voiture à l'index (nouveau) 0...")
        # delete_car(0)
        # print(load_data().head())
    else:
        print("Impossible de charger les données pour les exemples.")