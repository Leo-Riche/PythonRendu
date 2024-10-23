Démarrer l'environnement de développement  : 
env/Scripts/activate

Installer les modules dans requirements.txt : 
pip install -r requirements.txt

Lancer le script présent dans dans l'environnement :
python .\scrapping.py


PHASE 1 : 
Récupération de l'url de la page d'un livre sur la page d'accueil
Une fois l'url dédiée, je récupère toutes les informations nécessaires sur le livre
J'ajoute toutes les informations dans un fichier csv : book_data.csv

PHASE 2 :
Récupération de l'url d'une catégorie de livre sur la page d'accueil
Une fois l'url dédiée, je récupère tous les livres et toutes leurs informations.
J'ajoute toutes les informations dans un fichier csv : book_data.csv

PHASE 3 :
Récupération des url des images de chaque livre
Une fois les url récupérés, création des images
Ajout des images dans le dossier "images"

PHASE 4 : 
Récupération de tous les url de chaque catégories sur la page d'accueil
Une fois les url récupérées, je récupère tous les livres et toutes leurs informations.
J'ajoute toutes les informations dans un fichier csv avec le nom de la catégorie dédiée.
Puis, je récupère des url des images de chaque livre de chaque catégorie.
Une fois les url récupérées, je crée les images
J'ajoute les images dans le dossier "images"