# Détection des traces de particules dans une chambre à brouillard
#
# Principe : on mesure la luminosité moyenne des images d'une vidéo SANS source
# radioactive pour définir un seuil (moyenne + 2 écarts-types), puis on analyse
# la vidéo AVEC source : chaque image plus lumineuse que ce seuil est comptée
# comme une détection et sauvegardée.

import os
import sys

import cv2
import numpy as np

# Chemins d'accès (relatifs au dossier du script, à adapter si besoin)
DOSSIER = os.path.dirname(os.path.abspath(__file__))
VIDEO_SANS_SOURCE = os.path.join(DOSSIER, "video_without_source.avi")
VIDEO_AVEC_SOURCE = os.path.join(DOSSIER, "video_with_source.avi")
DOSSIER_SORTIE = os.path.join(DOSSIER, "detected_frames")

# Nombre d'écarts-types au-dessus du bruit de fond pour déclarer une détection
K_SIGMA = 2

os.makedirs(DOSSIER_SORTIE, exist_ok=True)


# --- 1. Vidéo sans source : mesure du bruit de fond -------------------------

cap_sans_source = cv2.VideoCapture(VIDEO_SANS_SOURCE)
if not cap_sans_source.isOpened():
    sys.exit(f"Erreur : impossible d'ouvrir la vidéo sans source ({VIDEO_SANS_SOURCE})")

luminosites = []
while True:
    ret, image = cap_sans_source.read()
    if not ret:
        break
    gris = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    luminosites.append(np.mean(gris))
cap_sans_source.release()

if not luminosites:
    sys.exit("Erreur : aucune image lue dans la vidéo sans source.")

moyenne_fond = np.mean(luminosites)
ecart_type_fond = np.std(luminosites)
seuil = moyenne_fond + K_SIGMA * ecart_type_fond

print(f"Bruit de fond : moyenne = {moyenne_fond:.2f}, écart-type = {ecart_type_fond:.2f}")
print(f"Seuil de détection : {seuil:.2f}")


# --- 2. Vidéo avec source : détection des images au-dessus du seuil ---------

cap_avec_source = cv2.VideoCapture(VIDEO_AVEC_SOURCE)
if not cap_avec_source.isOpened():
    sys.exit(f"Erreur : impossible d'ouvrir la vidéo avec source ({VIDEO_AVEC_SOURCE})")

nb_images = 0
nb_detections = 0
while True:
    ret, image = cap_avec_source.read()
    if not ret:
        break
    nb_images += 1

    gris = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    luminosite = np.mean(gris)

    if luminosite > seuil:
        nb_detections += 1
        nom_fichier = os.path.join(DOSSIER_SORTIE, f"detection_{nb_detections:04d}.png")
        cv2.imwrite(nom_fichier, image)
        print(f"Détection {nb_detections} (image {nb_images}) : luminosité = {luminosite:.2f}")
cap_avec_source.release()


# --- 3. Bilan ----------------------------------------------------------------

print(f"\nImages analysées : {nb_images}")
print(f"Détections : {nb_detections}")
if nb_images:
    print(f"Taux de détection : {100 * nb_detections / nb_images:.1f} %")
