import numpy as np
from sklearn.cluster import MiniBatchKMeans
from skimage import io
from PIL import Image
import requests
import matplotlib.pyplot as plt
from supabase_helper import get_latest_track
from collections import Counter

def get_album_colors(url, bool):
    kmeans = MiniBatchKMeans(n_clusters=8, random_state=0, batch_size=500, max_iter=1000)

    image = Image.open(requests.get(url, stream=True).raw)
    image_array = np.array(image)

    pixel_array = image_array.reshape(image_array.shape[0] * image_array.shape[1], image_array.shape[2])

    kmeans.fit(pixel_array)

    colors = np.array(kmeans.cluster_centers_.astype(int))

    labels = kmeans.predict(pixel_array)

    counts = Counter(labels)

    sorted_colors = sorted(zip(counts.values(), colors), reverse=True)

    sorted_colors_list = [color for count, color in sorted_colors]

    if bool:
        fig, ax = plt.subplots(2, 1)

        ax[0].imshow([sorted_colors_list], aspect='auto')

        ax[0].set_xticks([])
        ax[0].set_yticks([])

        ax[1].imshow(image)

        plt.show()

    def is_dark(color, threshold=100):  # You can adjust the threshold
        """Checks if a color is considered dark."""
        r, g, b = color
        return (r * 0.299 + g * 0.587 + b * 0.114) < threshold #calculate luminance

    ideal_color = None
    for color in sorted_colors_list:
        if not is_dark(color):
            ideal_color = color.tolist()
            break  # Found a suitable color, so exit the loop

    if ideal_color is None:
        # If all colors are dark, you might want to return a default light color,
        # or handle this situation differently.
        ideal_color = [200, 200, 200] #default light grey

    #print(ideal_color)

    return ideal_color

track = get_latest_track()
url = track.get('album_cover_url')

get_album_colors(url, True)