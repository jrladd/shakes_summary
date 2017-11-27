#! /usr/bin/env python3

import glob, pickle, flickrapi
from random import shuffle, sample
from bs4 import BeautifulSoup
from secrets import api_key, api_secret
from requests.exceptions import ConnectionError


def get_all_shakespeare():
    """
    Build list of all lines in the Shakespeare corpus. Need only run this once,
    as it creates a pickle object of the lines. Must use TEI Simple version of
    texts to avoid getting speech headers and other non-line bits of text.
    """
    shakespeare = glob.glob('FolgerDigitalTexts_TEISimple_Complete/*.xml')

    lines_by_text = []
    for s in shakespeare:
        with open(s, 'r') as xml:
            soup = BeautifulSoup(xml, 'xml')
            lines = [' '.join([w.text for w in l.select('w')]) for l in soup.select('l')]
            print(lines)
            lines_by_text.append(lines)


    all_lines = sum(lines_by_text, [])
    with open('shakeslines.pickle', 'wb') as f:
        pickle.dump(all_lines, f)

def create_five_chunks():
    with open('shakeslines.pickle', 'rb') as f:
        all_lines = [a.replace("\u2019", "'") for a in pickle.load(f)]
        shuffle(all_lines)
        i = 0
        five_chunks = []
        while i < len(all_lines):
            five_chunks.append(all_lines[i:i+6])
            i += 5
    return five_chunks

def get_photo_ids(page_number):
    """
    Use Flickr API to get IDs of Yellowback images. Must already initialize API w/ keys.
    """
    photos = flickr.people.getPhotos(user_id='129713776@N02', per_page="500", page=page_number)
    photo_ids = [p['id'] for p in photos['photos']['photo']]
    return photo_ids

def match_with_text(photo_ids, five_chunks):
    """
    Create Markdown list of objects with image URLs and random
    chunks of shakespeare texts.
    """
    md_file = []
    for i,f in zip(photo_ids, sample(five_chunks, len(photo_ids))):
        try:
            img = flickr.photos.getSizes(photo_id=i)
            copy_img = img
            image_url = [i['source'] for i in copy_img['sizes']['size'] if i['label'] == "Medium"][0]
            f.insert(0,"![]("+image_url+")")
            print("\n\n".join(f))
            md_file.append("\n\n".join(f))
        except (ConnectionError, flickrapi.exceptions.FlickrError) as e:
            pass
    return md_file

if __name__ == "__main__":

    # Initialize Flickr API with cache
    flickr = flickrapi.FlickrAPI(api_key, api_secret, format='parsed-json')
    flickr.cache = flickrapi.SimpleCache(timeout=300, max_entries=200)

    # Get random chunks of five lines
    five_chunks = create_five_chunks()

    # Do the next bit 3 times for a high enough word count
    all_photo_ids = []
    for n in range(1,4):
        photo_ids = get_photo_ids(n)
        all_photo_ids.extend(photo_ids)

    # Put it all together!
    md_file = match_with_text(all_photo_ids, five_chunks)


    with open('shakes_summary.md', 'w') as f:
        f.write("\n\n".join(md_file))
