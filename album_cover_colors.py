import numpy as np
from sklearn.cluster import MiniBatchKMeans
from skimage import io
from PIL import Image
import requests
import matplotlib.pyplot as plt
from supabase_helper import get_latest_track
from collections import Counter

def get_album_colors(url, viz):
    kmeans = MiniBatchKMeans(n_clusters=5, random_state=0, batch_size=500, max_iter=1000)

    image = Image.open(requests.get(url, stream=True).raw)
    image_array = np.array(image)

    pixel_array = image_array.reshape(image_array.shape[0] * image_array.shape[1], image_array.shape[2])

    kmeans.fit(pixel_array)

    colors = np.array(kmeans.cluster_centers_.astype(int))

    labels = kmeans.predict(pixel_array)

    counts = Counter(labels)

    sorted_colors = sorted(zip(counts.values(), colors), reverse=True)

    sorted_colors_list = [color for count, color in sorted_colors]

    if viz:
        fig, ax = plt.subplots(2, 1)
        ax[0].imshow([sorted_colors_list], aspect='auto')
        ax[0].set_xticks([])
        ax[0].set_yticks([])
        ax[1].imshow(image)
        plt.show()

    def is_grey(color, tolerance=40):
        """Checks if a color is considered grey."""
        r, g, b = color
        return abs(r - g) <= tolerance and abs(g - b) <= tolerance and abs(r - b) <= tolerance

    def is_dark(color, threshold=100):
        """Checks if a color is considered dark."""
        r, g, b = color
        return (r * 0.299 + g * 0.587 + b * 0.114) < threshold  # Calculate luminance

    # Try to find a non-grey and non-dark color first
    ideal_color = None
    for color in sorted_colors_list:
        if not is_grey(color) and not is_dark(color):
            ideal_color = color.tolist()
            break

    # If no suitable color is found, pick the most common non-dark color
    if ideal_color is None:
        for color in sorted_colors_list:
            if not is_dark(color):
                ideal_color = color.tolist()
                break

    # If all colors are dark or grey, use the most common color
    if ideal_color is None:
        ideal_color = [192, 192, 192]

    return ideal_color

# Example usage:
# track = get_latest_track()
# url = track.get('album_cover_url')
# get_album_colors(url, True)